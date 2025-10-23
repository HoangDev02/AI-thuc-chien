"""
Async video generator with batch processing support.

Modern implementation using httpx, tenacity, and rich for professional video generation.
"""

import asyncio
import time
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.progress import (
    BarColumn,
    DownloadColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeRemainingColumn,
    TransferSpeedColumn,
)
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from video_generation.config import (
    DEFAULT_BASE_URL,
    DEFAULT_CONCURRENT_LIMIT,
    DEFAULT_DOWNLOAD_TIMEOUT,
    DEFAULT_MAX_WAIT_TIME,
    DEFAULT_MODEL,
    DEFAULT_REQUEST_TIMEOUT,
    DOWNLOAD_CHUNK_SIZE,
    INITIAL_POLL_INTERVAL,
    MAX_POLL_INTERVAL,
    MAX_RETRY_ATTEMPTS,
    POLL_BACKOFF_MULTIPLIER,
    RETRY_MAX_WAIT,
    RETRY_MIN_WAIT,
    get_api_key,
    get_base_url,
)
from video_generation.exceptions import (
    APIError,
    DownloadError,
    OperationNotFoundError,
    TimeoutError,
    ValidationError,
)
from video_generation.models import (
    BatchResult,
    OperationStatus,
    VideoRequest,
    VideoResponse,
    VideoStatus,
)
from video_generation.utils import generate_filename, parse_video_uri

console = Console()


class VeoVideoGenerator:
    """
    Advanced async video generator with batch processing support.

    Features:
    - Async/await for concurrent operations
    - Retry mechanism with exponential backoff
    - Rich progress bars for downloads
    - Connection pooling for performance
    - Type-safe with Pydantic models

    Example:
        # Single video generation
        async with VeoVideoGenerator() as generator:
            response = await generator.generate_video_async("A cat playing")
            print(f"Video saved to: {response.video_path}")

        # Batch processing
        async with VeoVideoGenerator() as generator:
            batch_result = await generator.generate_batch(
                ["Cat playing", "Ocean waves", "City street"]
            )
            print(f"Success rate: {batch_result.success_rate}%")
    """

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = DEFAULT_REQUEST_TIMEOUT,
        max_retries: int = MAX_RETRY_ATTEMPTS,
    ):
        """
        Initialize the video generator.

        Args:
            base_url: API base URL (defaults to env or constant)
            api_key: API key (defaults to env variable)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts for failed requests
        """
        self.base_url = base_url or get_base_url()
        self.api_key = api_key or get_api_key()
        self.timeout = timeout
        self.max_retries = max_retries

        self.headers = {
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
        }

        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "VeoVideoGenerator":
        """Async context manager entry."""
        self._client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout),
            limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self._client:
            await self._client.aclose()

    @property
    def client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            raise RuntimeError(
                "VeoVideoGenerator must be used as async context manager. "
                "Use: async with VeoVideoGenerator() as generator:"
            )
        return self._client

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        reraise=True,
    )
    async def _upload_image(self, image_path: Path) -> str | None:
        """
        Upload image file to Google AI Studio.

        Args:
            image_path: Path to image file

        Returns:
            Uploaded file URI or None if failed

        Raises:
            APIError: If upload fails
        """
        try:
            console.print(f"[blue]📤 Uploading image: {image_path}[/blue]")
            
            # Read image file
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            # Upload to Google AI Studio files API
            upload_url = f"{self.base_url}/files"
            
            files = {
                "file": (image_path.name, image_data, "image/jpeg")
            }
            
            response = await self.client.post(
                upload_url,
                headers={"x-goog-api-key": self.api_key},
                files=files
            )
            response.raise_for_status()
            
            upload_result = response.json()
            file_uri = upload_result.get("file", {}).get("uri")
            
            if file_uri:
                console.print(f"[green]✅ Image uploaded successfully: {file_uri}[/green]")
                return file_uri
            else:
                console.print("[red]❌ Failed to get file URI from upload response[/red]")
                return None
                
        except Exception as e:
            console.print(f"[red]❌ Failed to upload image: {e}[/red]")
            raise APIError(f"Image upload failed: {e}")

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        reraise=True,
    )
    async def _initiate_generation(self, prompt: str, image_uri: str | None = None) -> str:
        """
        Initiate video generation with retry mechanism.

        Args:
            prompt: Text description for video generation
            image_uri: Optional URI of uploaded image

        Returns:
            Operation name for tracking

        Raises:
            APIError: If API request fails
            ValidationError: If prompt is invalid
        """
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt cannot be empty", field="prompt")

        url = f"{self.base_url}/models/{DEFAULT_MODEL}:predictLongRunning"
        
        # Build payload with optional image
        instance_data = {"prompt": prompt.strip()}
        if image_uri:
            instance_data["image"] = {"uri": image_uri}
            console.print(f"[cyan]🎬 Generating video with image:[/cyan] '{prompt[:50]}...'")
        else:
            console.print(f"[cyan]🎬 Generating video:[/cyan] '{prompt[:50]}...'")
        
        payload = {"instances": [instance_data]}

        try:
            response = await self.client.post(url, headers=self.headers, json=payload)
            response.raise_for_status()

            data = response.json()
            operation_name = data.get("name")

            if not operation_name:
                raise APIError(
                    "No operation name returned from API",
                    status_code=response.status_code,
                    response_data=data,
                )

            console.print(f"[green]✅ Generation started:[/green] {operation_name}")
            return operation_name

        except httpx.HTTPStatusError as e:
            error_data = {}
            try:
                error_data = e.response.json()
            except Exception:
                error_data = {"text": e.response.text}

            raise APIError(
                f"API request failed: {e}",
                status_code=e.response.status_code,
                response_data=error_data,
            ) from e

    async def _poll_operation(
        self, operation_name: str, max_wait_time: int = DEFAULT_MAX_WAIT_TIME
    ) -> str:
        """
        Poll operation status until completion.

        Args:
            operation_name: Operation to monitor
            max_wait_time: Maximum wait time in seconds

        Returns:
            Video URI when complete

        Raises:
            TimeoutError: If operation exceeds max wait time
            APIError: If operation fails or returns error
        """
        console.print("[yellow]⏳ Waiting for video generation to complete...[/yellow]")

        operation_url = f"{self.base_url}/{operation_name}"
        start_time = time.time()
        poll_interval = INITIAL_POLL_INTERVAL

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task(
                "Generating video...", total=max_wait_time, completed=0
            )

            while True:
                elapsed = time.time() - start_time

                if elapsed >= max_wait_time:
                    raise TimeoutError(
                        f"Operation timed out after {max_wait_time} seconds",
                        elapsed_time=elapsed,
                    )

                # Update progress
                progress.update(task, completed=min(elapsed, max_wait_time))

                try:
                    response = await self.client.get(operation_url, headers=self.headers)
                    response.raise_for_status()

                    data = response.json()

                    # Check for errors
                    if "error" in data:
                        raise APIError(
                            "Video generation failed",
                            response_data=data.get("error"),
                        )

                    # Check if complete
                    if data.get("done", False):
                        try:
                            video_uri = data["response"]["generateVideoResponse"][
                                "generatedSamples"
                            ][0]["video"]["uri"]
                            console.print(
                                f"[green]🎉 Video generation complete![/green] "
                                f"({elapsed:.1f}s)"
                            )
                            return video_uri
                        except KeyError as e:
                            raise APIError(
                                f"Could not extract video URI: {e}",
                                response_data=data,
                            ) from e

                except httpx.HTTPStatusError as e:
                    console.print(f"[yellow]⚠️  Polling error: {e}, retrying...[/yellow]")

                # Wait before next poll with exponential backoff
                await asyncio.sleep(poll_interval)
                poll_interval = min(poll_interval * POLL_BACKOFF_MULTIPLIER, MAX_POLL_INTERVAL)

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(MAX_RETRY_ATTEMPTS),
        wait=wait_exponential(multiplier=1, min=RETRY_MIN_WAIT, max=RETRY_MAX_WAIT),
        reraise=True,
    )
    async def _download_video(self, video_uri: str, output_path: Path) -> Path:
        """
        Download video with progress tracking and retry.

        Args:
            video_uri: URI of video to download
            output_path: Local path to save video

        Returns:
            Path to downloaded video file

        Raises:
            DownloadError: If download fails
        """
        console.print(f"[cyan]⬇️  Downloading video to:[/cyan] {output_path}")

        # Parse and construct download URL
        download_url = parse_video_uri(video_uri, self.base_url)
        console.print(f"[dim]Download URL: {download_url}[/dim]")

        try:
            # Stream download with progress bar
            async with self.client.stream(
                "GET",
                download_url,
                headers=self.headers,
                timeout=httpx.Timeout(DEFAULT_DOWNLOAD_TIMEOUT),
            ) as response:
                response.raise_for_status()

                # Get total size from headers
                total_size = int(response.headers.get("content-length", 0))

                with Progress(
                    TextColumn("[bold blue]{task.description}"),
                    BarColumn(),
                    DownloadColumn(),
                    TransferSpeedColumn(),
                    TimeRemainingColumn(),
                    console=console,
                ) as progress:
                    download_task = progress.add_task(
                        "Downloading", total=total_size if total_size > 0 else None
                    )

                    # Ensure parent directory exists
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    downloaded_bytes = 0
                    with open(output_path, "wb") as f:
                        async for chunk in response.aiter_bytes(
                            chunk_size=DOWNLOAD_CHUNK_SIZE
                        ):
                            if chunk:
                                f.write(chunk)
                                downloaded_bytes += len(chunk)
                                progress.update(download_task, advance=len(chunk))

            # Verify download
            if not output_path.exists():
                raise DownloadError(
                    "Downloaded file does not exist",
                    video_uri=video_uri,
                )

            file_size = output_path.stat().st_size
            if file_size == 0:
                output_path.unlink()
                raise DownloadError(
                    "Downloaded file is empty",
                    video_uri=video_uri,
                )

            file_size_mb = file_size / (1024 * 1024)
            console.print(
                f"[green]✅ Download complete![/green] "
                f"Size: {file_size_mb:.2f} MB"
            )

            return output_path

        except httpx.HTTPStatusError as e:
            raise DownloadError(
                f"Download failed with status {e.response.status_code}",
                video_uri=video_uri,
            ) from e
        except Exception as e:
            if output_path.exists():
                output_path.unlink()
            raise DownloadError(
                f"Download failed: {e}",
                video_uri=video_uri,
            ) from e

    async def generate_video_async(
        self, prompt: str, output_path: Path | str | None = None, image_path: Path | str | None = None
    ) -> VideoResponse:
        """
        Generate a single video asynchronously.

        Args:
            prompt: Text description for video
            output_path: Optional output file path
            image_path: Optional path to input image file

        Returns:
            VideoResponse with generation results

        Example:
            async with VeoVideoGenerator() as gen:
                response = await gen.generate_video_async("A cat playing", image_path="cat.jpg")
                if response.is_success:
                    print(f"Saved to: {response.video_path}")
        """
        start_time = time.time()

        try:
            # Validate request
            request = VideoRequest(prompt=prompt, output_path=output_path, image_path=image_path)

            # Generate filename if not provided
            if request.output_path is None:
                request.output_path = Path(generate_filename(prompt))

            # Step 1: Upload image if provided
            image_uri = None
            if request.image_path:
                image_uri = await self._upload_image(request.image_path)

            # Step 2: Initiate generation
            operation_name = await self._initiate_generation(request.prompt, image_uri)

            # Step 3: Poll for completion
            video_uri = await self._poll_operation(operation_name)

            # Step 4: Download video
            video_path = await self._download_video(video_uri, request.output_path)

            # Calculate metrics
            generation_time = time.time() - start_time
            file_size_mb = video_path.stat().st_size / (1024 * 1024)

            return VideoResponse(
                success=True,
                video_path=video_path,
                operation_name=operation_name,
                video_uri=video_uri,
                file_size_mb=file_size_mb,
                generation_time=generation_time,
            )

        except Exception as e:
            generation_time = time.time() - start_time
            error_details = {}
            if hasattr(e, "details"):
                error_details = e.details

            return VideoResponse(
                success=False,
                error=str(e),
                error_details=error_details,
                generation_time=generation_time,
            )

    async def generate_batch(
        self,
        prompts: list[str],
        output_dir: Path | str | None = None,
        concurrent_limit: int = DEFAULT_CONCURRENT_LIMIT,
        image_paths: list[Path | str | None] | None = None,
    ) -> BatchResult:
        """
        Generate multiple videos concurrently.

        Args:
            prompts: List of text prompts
            output_dir: Optional directory for output files
            concurrent_limit: Maximum concurrent generations
            image_paths: Optional list of image paths (one per prompt)

        Returns:
            BatchResult with aggregated results

        Example:
            async with VeoVideoGenerator() as gen:
                result = await gen.generate_batch([
                    "A cat playing",
                    "Ocean waves",
                    "City street"
                ], image_paths=["cat.jpg", None, "city.jpg"])
                print(result.summary())
        """
        console.print(
            f"\n[bold cyan]{'='*60}[/bold cyan]\n"
            f"[bold cyan]🎬 BATCH VIDEO GENERATION[/bold cyan]\n"
            f"[bold cyan]{'='*60}[/bold cyan]\n"
            f"Total videos: {len(prompts)}\n"
            f"Concurrent limit: {concurrent_limit}\n"
        )

        start_time = time.time()
        output_dir_path = Path(output_dir) if output_dir else Path.cwd()
        output_dir_path.mkdir(parents=True, exist_ok=True)

        # Create semaphore for concurrency control
        semaphore = asyncio.Semaphore(concurrent_limit)

        async def _generate_with_limit(prompt: str, index: int) -> VideoResponse:
            async with semaphore:
                output_file = output_dir_path / generate_filename(prompt, index=index)
                image_path = image_paths[index] if image_paths and index < len(image_paths) else None
                console.print(f"\n[cyan]Starting video {index + 1}/{len(prompts)}[/cyan]")
                if image_path:
                    console.print(f"[blue]With image: {image_path}[/blue]")
                return await self.generate_video_async(prompt, output_file, image_path)

        # Execute all generations concurrently (with limit)
        tasks = [
            _generate_with_limit(prompt, idx) for idx, prompt in enumerate(prompts)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=False)

        # Calculate statistics
        total_time = time.time() - start_time
        successful = sum(1 for r in results if r.is_success)
        failed = len(results) - successful

        batch_result = BatchResult(
            total=len(prompts),
            successful=successful,
            failed=failed,
            results=results,
            total_time=total_time,
        )

        # Print summary
        console.print(
            f"\n[bold cyan]{'='*60}[/bold cyan]\n"
            f"[bold green]🎉 BATCH COMPLETE![/bold green]\n"
            f"[bold cyan]{'='*60}[/bold cyan]\n"
            f"{batch_result.summary()}\n"
            f"Total time: {total_time:.1f}s\n"
        )

        return batch_result


# Backward compatible sync wrapper functions


def generate_video(
    prompt: str,
    model: str = DEFAULT_MODEL,
    output_path: str | None = None,
    base_url: str | None = None,
    api_key: str | None = None,
) -> str:
    """
    Generate video synchronously (backward compatible).

    Args:
        prompt: Text prompt for video generation
        model: Model to use (unused, kept for compatibility)
        output_path: Path to save video file
        base_url: API base URL
        api_key: API key

    Returns:
        Path to saved video file if successful, empty string otherwise

    Example:
        video_path = generate_video("A cat playing with yarn")
        if video_path:
            print(f"Video saved to: {video_path}")
    """

    async def _run() -> str:
        async with VeoVideoGenerator(base_url=base_url, api_key=api_key) as gen:
            response = await gen.generate_video_async(prompt, output_path)
            if response.is_success and response.video_path:
                return str(response.video_path)
            return ""

    return asyncio.run(_run())


async def generate_videos_batch(
    prompts: list[str],
    output_dir: str | None = None,
    concurrent_limit: int = DEFAULT_CONCURRENT_LIMIT,
    base_url: str | None = None,
    api_key: str | None = None,
) -> BatchResult:
    """
    Generate multiple videos asynchronously.

    Args:
        prompts: List of text prompts
        output_dir: Directory to save videos
        concurrent_limit: Maximum concurrent generations
        base_url: API base URL
        api_key: API key

    Returns:
        BatchResult with aggregated results

    Example:
        import asyncio

        prompts = ["Cat playing", "Ocean waves", "City street"]
        result = asyncio.run(generate_videos_batch(prompts))
        print(result.summary())
    """
    async with VeoVideoGenerator(base_url=base_url, api_key=api_key) as gen:
        return await gen.generate_batch(prompts, output_dir, concurrent_limit)
