"""
Configuration module for video generation.

Centralizes all constants, default values, and configuration settings.
"""

import os
from typing import Final

# API Configuration
DEFAULT_BASE_URL: Final[str] = "https://api.thucchien.ai/gemini/v1beta"
DEFAULT_MODEL: Final[str] = "veo-3.0-generate-preview"
API_KEY_ENV_VAR: Final[str] = "THUCCHIEN_API_KEY"
LITELLM_BASE_URL_ENV: Final[str] = "LITELLM_BASE_URL"
LITELLM_API_KEY_ENV: Final[str] = "LITELLM_API_KEY"

# Timeout Configuration (seconds)
DEFAULT_MAX_WAIT_TIME: Final[int] = 600  # 10 minutes
DEFAULT_REQUEST_TIMEOUT: Final[int] = 30  # 30 seconds per request
DEFAULT_DOWNLOAD_TIMEOUT: Final[int] = 300  # 5 minutes for download

# Polling Configuration
INITIAL_POLL_INTERVAL: Final[float] = 10.0  # Start with 10 seconds
MAX_POLL_INTERVAL: Final[float] = 30.0  # Cap at 30 seconds
POLL_BACKOFF_MULTIPLIER: Final[float] = 1.2

# Download Configuration
DOWNLOAD_CHUNK_SIZE: Final[int] = 8192  # 8KB chunks
PROGRESS_UPDATE_THRESHOLD: Final[int] = 1024 * 1024  # Update every 1MB

# Retry Configuration
MAX_RETRY_ATTEMPTS: Final[int] = 3
RETRY_MIN_WAIT: Final[int] = 1  # seconds
RETRY_MAX_WAIT: Final[int] = 10  # seconds

# Batch Processing Configuration
DEFAULT_CONCURRENT_LIMIT: Final[int] = 5  # Process 5 videos at a time
MAX_CONCURRENT_LIMIT: Final[int] = 10  # Hard limit

# File Configuration
DEFAULT_OUTPUT_FILENAME: Final[str] = "generated_video.mp4"
MAX_FILENAME_LENGTH: Final[int] = 50


def get_api_key() -> str:
    """
    Get API key from environment variables.

    Returns:
        API key from THUCCHIEN_API_KEY or LITELLM_API_KEY env vars

    Raises:
        ValueError: If no API key is found
    """
    api_key = os.getenv(API_KEY_ENV_VAR) or os.getenv(LITELLM_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            f"API key not found. Set {API_KEY_ENV_VAR} or {LITELLM_API_KEY_ENV} "
            "environment variable."
        )
    return api_key


def get_base_url() -> str:
    """
    Get base URL from environment or use default.

    Returns:
        Base URL for API requests
    """
    return os.getenv(LITELLM_BASE_URL_ENV, DEFAULT_BASE_URL)
