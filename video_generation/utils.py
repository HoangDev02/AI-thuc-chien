"""
Utility functions for video generation.

Provides helper functions for filename generation, URL parsing, and validation.
"""

import re
import time
from pathlib import Path


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Sanitize text for use in filename.

    Args:
        text: Text to sanitize
        max_length: Maximum length of sanitized text

    Returns:
        Sanitized filename-safe string

    Example:
        >>> sanitize_filename("A cat playing! @home")
        'A_cat_playing_home'
    """
    # Remove special characters, keep alphanumeric and spaces
    safe_text = re.sub(r"[^\w\s-]", "", text)

    # Replace spaces and multiple underscores with single underscore
    safe_text = re.sub(r"[\s_]+", "_", safe_text)

    # Remove leading/trailing underscores
    safe_text = safe_text.strip("_")

    # Truncate to max length
    if len(safe_text) > max_length:
        safe_text = safe_text[:max_length].rstrip("_")

    return safe_text or "video"


def generate_filename(
    prompt: str, index: int | None = None, timestamp: bool = True
) -> str:
    """
    Generate a filename from prompt.

    Args:
        prompt: Video generation prompt
        index: Optional index for batch processing
        timestamp: Whether to include timestamp

    Returns:
        Generated filename with .mp4 extension

    Example:
        >>> generate_filename("A cat playing", index=1)
        'veo_A_cat_playing_1_1234567890.mp4'
    """
    safe_prompt = sanitize_filename(prompt, max_length=30)

    parts = ["veo", safe_prompt]

    if index is not None:
        parts.append(str(index))

    if timestamp:
        parts.append(str(int(time.time())))

    filename = "_".join(parts) + ".mp4"
    return filename


def parse_video_uri(video_uri: str, base_url: str) -> str:
    """
    Convert Google API video URI to LiteLLM proxy download URL.

    Args:
        video_uri: Original video URI from Google API
        base_url: LiteLLM proxy base URL

    Returns:
        Download URL for LiteLLM proxy

    Example:
        >>> uri = "https://generativelanguage.googleapis.com/v1beta/files/abc123"
        >>> base = "https://api.thucchien.ai/gemini/v1beta"
        >>> parse_video_uri(uri, base)
        'https://api.thucchien.ai/gemini/download/v1beta/files/abc123'
    """
    # Extract relative path from Google URI
    if video_uri.startswith("https://generativelanguage.googleapis.com/"):
        relative_path = video_uri.replace(
            "https://generativelanguage.googleapis.com/", ""
        )
    else:
        relative_path = video_uri

    # Convert base URL for download endpoint
    if base_url.endswith("/v1beta"):
        base_path = base_url.replace("/v1beta", "/download")
    else:
        base_path = base_url

    # Construct download URL
    download_url = f"{base_path}/{relative_path}"

    return download_url


def validate_prompt(prompt: str) -> tuple[bool, str | None]:
    """
    Validate video generation prompt.

    Args:
        prompt: Prompt to validate

    Returns:
        Tuple of (is_valid, error_message)

    Example:
        >>> validate_prompt("A cat playing")
        (True, None)
        >>> validate_prompt("")
        (False, "Prompt cannot be empty")
    """
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"

    if len(prompt) > 2000:
        return False, "Prompt exceeds maximum length of 2000 characters"

    # Check for minimum meaningful content
    if len(prompt.strip()) < 3:
        return False, "Prompt too short (minimum 3 characters)"

    return True, None


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        Formatted string (e.g., "1.5 MB")

    Example:
        >>> format_file_size(1536000)
        '1.46 MB'
    """
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def format_duration(seconds: float) -> str:
    """
    Format duration in human-readable format.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted string (e.g., "1m 30s")

    Example:
        >>> format_duration(90.5)
        '1m 30s'
    """
    if seconds < 60:
        return f"{seconds:.1f}s"

    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)

    if minutes < 60:
        return f"{minutes}m {remaining_seconds}s"

    hours = minutes // 60
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"
