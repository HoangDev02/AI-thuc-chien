"""
Pydantic models for type safety and data validation.

Provides structured data models for requests, responses, and status tracking.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class VideoStatus(str, Enum):
    """Video generation status."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class VideoRequest(BaseModel):
    """Request model for video generation."""

    prompt: str = Field(..., min_length=1, max_length=2000)
    model: str = Field(default="veo-3.0-generate-preview")
    output_path: Path | None = None
    image_path: Path | None = None  # Path to input image file

    @field_validator("prompt")
    @classmethod
    def validate_prompt(cls, v: str) -> str:
        """Validate and clean prompt."""
        prompt = v.strip()
        if not prompt:
            raise ValueError("Prompt cannot be empty or whitespace")
        return prompt

    @field_validator("output_path")
    @classmethod
    def validate_output_path(cls, v: Path | None) -> Path | None:
        """Validate output path."""
        if v is not None:
            if v.suffix.lower() != ".mp4":
                raise ValueError("Output file must have .mp4 extension")
            # Ensure parent directory exists or can be created
            if v.parent and not v.parent.exists():
                v.parent.mkdir(parents=True, exist_ok=True)
        return v

    @field_validator("image_path")
    @classmethod
    def validate_image_path(cls, v: Path | None) -> Path | None:
        """Validate image path."""
        if v is not None:
            if not v.exists():
                raise ValueError(f"Image file does not exist: {v}")
            # Check if it's a valid image file
            valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
            if v.suffix.lower() not in valid_extensions:
                raise ValueError(f"Image file must have one of these extensions: {valid_extensions}")
        return v


class OperationStatus(BaseModel):
    """Model for tracking operation status."""

    operation_name: str
    status: VideoStatus = VideoStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    elapsed_time: float | None = None
    video_uri: str | None = None
    error: str | None = None
    error_details: dict[str, Any] | None = None

    def mark_completed(self, video_uri: str) -> None:
        """Mark operation as completed."""
        self.status = VideoStatus.COMPLETED
        self.video_uri = video_uri
        self.completed_at = datetime.now()
        self.elapsed_time = (self.completed_at - self.started_at).total_seconds()

    def mark_failed(self, error: str, error_details: dict[str, Any] | None = None) -> None:
        """Mark operation as failed."""
        self.status = VideoStatus.FAILED
        self.error = error
        self.error_details = error_details
        self.completed_at = datetime.now()
        self.elapsed_time = (self.completed_at - self.started_at).total_seconds()

    def mark_timeout(self, max_wait_time: float) -> None:
        """Mark operation as timed out."""
        self.status = VideoStatus.TIMEOUT
        self.error = f"Operation timed out after {max_wait_time} seconds"
        self.completed_at = datetime.now()
        self.elapsed_time = (self.completed_at - self.started_at).total_seconds()

    model_config = {"use_enum_values": True}


class VideoResponse(BaseModel):
    """Response model for video generation."""

    success: bool
    video_path: Path | None = None
    operation_name: str | None = None
    video_uri: str | None = None
    file_size_mb: float | None = None
    generation_time: float | None = None
    error: str | None = None
    error_details: dict[str, Any] | None = None

    @property
    def is_success(self) -> bool:
        """Check if generation was successful."""
        return self.success and self.video_path is not None

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with Path as string."""
        data = self.model_dump()
        if self.video_path:
            data["video_path"] = str(self.video_path)
        return data


class BatchResult(BaseModel):
    """Result model for batch video generation."""

    total: int
    successful: int
    failed: int
    results: list[VideoResponse]
    total_time: float | None = None

    @property
    def success_rate(self) -> float:
        """Calculate success rate percentage."""
        return (self.successful / self.total * 100) if self.total > 0 else 0.0

    @property
    def has_failures(self) -> bool:
        """Check if any videos failed."""
        return self.failed > 0

    def get_successful_videos(self) -> list[VideoResponse]:
        """Get list of successful video responses."""
        return [r for r in self.results if r.is_success]

    def get_failed_videos(self) -> list[VideoResponse]:
        """Get list of failed video responses."""
        return [r for r in self.results if not r.is_success]

    def summary(self) -> str:
        """Generate human-readable summary."""
        return (
            f"Batch Results: {self.successful}/{self.total} successful "
            f"({self.success_rate:.1f}% success rate)"
        )


class DownloadProgress(BaseModel):
    """Model for tracking download progress."""

    total_bytes: int | None = None
    downloaded_bytes: int = 0
    percentage: float = 0.0
    speed_mbps: float | None = None

    def update(self, chunk_size: int, elapsed_time: float | None = None) -> None:
        """Update download progress."""
        self.downloaded_bytes += chunk_size
        if self.total_bytes and self.total_bytes > 0:
            self.percentage = (self.downloaded_bytes / self.total_bytes) * 100

        if elapsed_time and elapsed_time > 0:
            # Calculate speed in MB/s
            mb_downloaded = self.downloaded_bytes / (1024 * 1024)
            self.speed_mbps = mb_downloaded / elapsed_time
