# Video Generation - Quick Start Guide

## Installation

```bash
# Install dependencies with UV
uv sync

# Set API key
export THUCCHIEN_API_KEY="your-api-key"
```

## Usage Examples

### 1. Simple (Backward Compatible)

```python
from video_generation import generate_video

# One line - that's it!
video_path = generate_video("A cat playing with yarn")
print(f"Saved to: {video_path}")
```

### 2. Async (Better Performance)

```python
import asyncio
from video_generation import VeoVideoGenerator

async def main():
    async with VeoVideoGenerator() as gen:
        response = await gen.generate_video_async("Ocean waves")

        print(f"Video: {response.video_path}")
        print(f"Size: {response.file_size_mb:.2f} MB")
        print(f"Time: {response.generation_time:.1f}s")

asyncio.run(main())
```

### 3. Batch Processing (Multiple Videos)

```python
import asyncio
from video_generation import generate_videos_batch

async def main():
    prompts = [
        "A cat playing",
        "Ocean waves",
        "City street",
    ]

    # Generate 3 videos concurrently
    result = await generate_videos_batch(prompts, concurrent_limit=3)

    print(f"✅ Success: {result.successful}/{result.total}")
    print(f"⏱️  Total time: {result.total_time:.1f}s")

    # Show successful videos
    for video in result.get_successful_videos():
        print(f"   {video.video_path}")

asyncio.run(main())
```

## Key Features

| Feature | Description |
|---------|-------------|
| **Async/Await** | Non-blocking concurrent operations |
| **Batch Processing** | Generate multiple videos simultaneously |
| **Auto Retry** | 3 automatic retries with exponential backoff |
| **Progress Bars** | Beautiful real-time progress tracking |
| **Type Safety** | Full Pydantic validation |
| **Error Handling** | Structured exceptions with details |

## Performance

```
Sequential (old):     5 videos in 50 minutes
Concurrent (new):     5 videos in 15 minutes
                      ↓ 70% faster! ↓
```

## File Structure

```
video_generation/          # Main package
├── generator.py          # Async video generator
├── models.py            # Pydantic models
├── exceptions.py        # Custom exceptions
├── config.py           # Configuration
└── utils.py            # Helper functions

examples/                 # Usage examples
├── basic_example.py    # Simple sync
├── async_example.py    # Async with details
├── batch_example.py    # Batch processing
└── advanced_batch.py   # Production-ready

video_generation.py       # Backward compatible wrapper
```

## Common Patterns

### With Custom Output Path

```python
response = await gen.generate_video_async(
    "A cat playing",
    output_path="videos/cat.mp4"
)
```

### With Error Handling

```python
try:
    response = await gen.generate_video_async(prompt)
    if response.is_success:
        print(f"Success: {response.video_path}")
    else:
        print(f"Failed: {response.error}")
except VideoGenerationError as e:
    print(f"Error: {e}")
```

### Batch with Output Directory

```python
result = await generate_videos_batch(
    prompts=["Cat", "Ocean", "City"],
    output_dir="videos/batch/",
    concurrent_limit=5
)
```

## Environment Variables

```bash
# Required
export THUCCHIEN_API_KEY="your-key"

# Optional
export LITELLM_BASE_URL="https://api.thucchien.ai/gemini/v1beta"
export LITELLM_API_KEY="alternative-key"
```

## Troubleshooting

### API Key Not Found
```bash
export THUCCHIEN_API_KEY="your-api-key-here"
```

### Timeout Issues
```python
# Increase timeout
VeoVideoGenerator(timeout=120)  # 2 minutes
```

### Concurrent Limit
```python
# Reduce concurrent videos if hitting rate limits
generate_videos_batch(prompts, concurrent_limit=2)
```

## Next Steps

1. Try `examples/basic_example.py`
2. Read `examples/README.md` for detailed examples
3. Check `VIDEO_GENERATION_OPTIMIZATION.md` for technical details
4. Explore the source code in `video_generation/`

## Run Examples

```bash
# Basic sync example
python examples/basic_example.py

# Async with details
python examples/async_example.py

# Batch processing (3-5 videos)
python examples/batch_example.py

# Advanced batch (8 videos with analytics)
python examples/advanced_batch.py

# Original interface (backward compatible)
python video_generation.py
```

## API Reference

### VeoVideoGenerator

```python
async with VeoVideoGenerator(
    base_url: str | None = None,      # API base URL
    api_key: str | None = None,       # API key
    timeout: int = 30,                # Request timeout
    max_retries: int = 3              # Retry attempts
) as gen:
    # Your code here
```

### generate_video (Sync)

```python
video_path = generate_video(
    prompt: str,                      # Video description
    model: str = "veo-3.0-...",      # Model name
    output_path: str | None = None,  # Output file path
    base_url: str | None = None,     # API URL
    api_key: str | None = None       # API key
) -> str  # Returns path or empty string
```

### generate_videos_batch (Async)

```python
result = await generate_videos_batch(
    prompts: list[str],              # List of descriptions
    output_dir: str | None = None,   # Output directory
    concurrent_limit: int = 5,       # Max concurrent
    base_url: str | None = None,     # API URL
    api_key: str | None = None       # API key
) -> BatchResult
```

## Response Objects

### VideoResponse

```python
response.success          # bool
response.video_path       # Path | None
response.file_size_mb     # float | None
response.generation_time  # float | None
response.video_uri        # str | None
response.error           # str | None
response.is_success      # bool (property)
```

### BatchResult

```python
result.total             # int (total videos)
result.successful        # int (successful count)
result.failed           # int (failed count)
result.total_time       # float (total time)
result.success_rate     # float (percentage)
result.summary()        # str (formatted summary)
result.get_successful_videos()  # list[VideoResponse]
result.get_failed_videos()      # list[VideoResponse]
```

---

**Ready to generate videos? Start with `examples/basic_example.py`!**
