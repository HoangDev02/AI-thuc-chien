"""
Custom exceptions for video generation operations.

Provides structured error handling with specific exception types.
"""


class VideoGenerationError(Exception):
    """Base exception for all video generation errors."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} | Details: {self.details}"
        return self.message


class APIError(VideoGenerationError):
    """Raised when API requests fail."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        response_data: dict | None = None,
    ):
        details = {}
        if status_code:
            details["status_code"] = status_code
        if response_data:
            details["response"] = response_data
        super().__init__(message, details)
        self.status_code = status_code
        self.response_data = response_data


class TimeoutError(VideoGenerationError):
    """Raised when operations exceed timeout limits."""

    def __init__(self, message: str, elapsed_time: float | None = None):
        details = {"elapsed_time": elapsed_time} if elapsed_time else {}
        super().__init__(message, details)
        self.elapsed_time = elapsed_time


class DownloadError(VideoGenerationError):
    """Raised when video download fails."""

    def __init__(
        self,
        message: str,
        video_uri: str | None = None,
        partial_bytes: int | None = None,
    ):
        details = {}
        if video_uri:
            details["video_uri"] = video_uri
        if partial_bytes:
            details["partial_bytes_downloaded"] = partial_bytes
        super().__init__(message, details)
        self.video_uri = video_uri
        self.partial_bytes = partial_bytes


class ValidationError(VideoGenerationError):
    """Raised when input validation fails."""

    def __init__(self, message: str, field: str | None = None):
        details = {"field": field} if field else {}
        super().__init__(message, details)
        self.field = field


class OperationNotFoundError(VideoGenerationError):
    """Raised when operation cannot be found or tracked."""

    def __init__(self, message: str, operation_name: str | None = None):
        details = {"operation_name": operation_name} if operation_name else {}
        super().__init__(message, details)
        self.operation_name = operation_name
