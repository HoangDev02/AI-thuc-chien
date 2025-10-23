# Video Generation Examples

This directory contains examples demonstrating different ways to use the optimized video generation API.

## Setup

First, install dependencies using UV:

```bash
uv sync
```

Set your API key:

```bash
export THUCCHIEN_API_KEY="your-api-key-here"
# Or
export LITELLM_API_KEY="your-api-key-here"
```

## Examples Overview

### 1. Basic Example - Simple Sync Usage
**File:** `basic_example.py`

The simplest way to generate a video. Perfect for getting started.

```bash
python examples/basic_example.py
```

**Key Features:**
- Single function call
- Synchronous execution
- Backward compatible with original API
- Automatic filename generation

### 2. Async Example - Better Control
**File:** `async_example.py`

Uses async/await for better control and detailed response information.

```bash
python examples/async_example.py
```

**Key Features:**
- Async/await pattern
- Detailed response object
- Better error handling
- Resource management with context manager

### 3. Batch Example - Concurrent Processing
**File:** `batch_example.py`

Generate multiple videos simultaneously with automatic concurrency control.

```bash
python examples/batch_example.py
```

**Key Features:**
- Process 5 prompts concurrently
- Automatic concurrency limiting
- Aggregated results
- Success/failure tracking

**Performance:**
- Sequential: ~50 minutes for 5 videos (10 min each)
- Concurrent (limit=3): ~20 minutes for 5 videos
- **~60% time savings!**

### 4. Advanced Batch - Production Ready
**File:** `advanced_batch.py`

Advanced features for production use including custom configuration and comprehensive error handling.

```bash
python examples/advanced_batch.py
```

**Key Features:**
- Custom API configuration
- Advanced error handling
- Detailed statistics and analysis
- Partial success handling
- Processing 8 videos with limit=5

## Usage Patterns

### Pattern 1: Quick Script (Sync)

```python
from video_generation import generate_video

# One-liner generation
video_path = generate_video("A cat playing with yarn")
```

### Pattern 2: Detailed Control (Async)

```python
import asyncio
from video_generation import VeoVideoGenerator

async def main():
    async with VeoVideoGenerator() as gen:
        response = await gen.generate_video_async("Ocean waves")

        if response.is_success:
            print(f"File: {response.video_path}")
            print(f"Size: {response.file_size_mb:.2f} MB")
            print(f"Time: {response.generation_time:.1f}s")

asyncio.run(main())
```

### Pattern 3: Batch Processing

```python
import asyncio
from video_generation import generate_videos_batch

async def main():
    prompts = [
        "A cat playing",
        "Ocean waves",
        "City street",
    ]

    result = await generate_videos_batch(
        prompts=prompts,
        output_dir="videos/",
        concurrent_limit=3  # Process 3 at a time
    )

    print(f"Success rate: {result.success_rate}%")
    print(f"Total time: {result.total_time:.1f}s")

asyncio.run(main())
```

## Configuration

### Environment Variables

```bash
# Required: API key
export THUCCHIEN_API_KEY="your-key"
# or
export LITELLM_API_KEY="your-key"

# Optional: Custom base URL
export LITELLM_BASE_URL="https://api.thucchien.ai/gemini/v1beta"
```

### Programmatic Configuration

```python
from video_generation import VeoVideoGenerator

async with VeoVideoGenerator(
    base_url="https://custom-url.com/v1beta",
    api_key="custom-key",
    timeout=60,
    max_retries=5
) as gen:
    # Your code here
    pass
```

## Performance Tips

1. **Concurrent Limit**: Adjust based on your API quota
   - Start with 3-5 for testing
   - Increase to 10 for production (if quota allows)

2. **Timeout Settings**: For longer videos, increase timeout
   ```python
   VeoVideoGenerator(timeout=120)  # 2 minutes per request
   ```

3. **Retry Strategy**: The library automatically retries failed requests
   - Default: 3 retries with exponential backoff
   - Customize: `max_retries=5`

4. **Output Directory**: Pre-create directories for better performance
   ```python
   Path("videos/").mkdir(exist_ok=True)
   ```

## Troubleshooting

### Common Issues

**1. API Key Not Found**
```
ValueError: API key not found
```
**Solution:** Set `THUCCHIEN_API_KEY` or `LITELLM_API_KEY` environment variable

**2. Timeout Errors**
```
TimeoutError: Operation timed out after 600 seconds
```
**Solution:** Increase `max_wait_time` or check API status

**3. Download Failures**
```
DownloadError: Download failed with status 404
```
**Solution:** Check API configuration and video URI

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Migration from Old Code

### Old Code (v1.0)
```python
from video_generation import VeoVideoGenerator

generator = VeoVideoGenerator()
success = generator.generate_and_download("A cat playing")
```

### New Code (v2.0) - Backward Compatible
```python
from video_generation import generate_video

video_path = generate_video("A cat playing")
# Still works! Automatically uses optimized async backend
```

### New Code (v2.0) - Async
```python
import asyncio
from video_generation import VeoVideoGenerator

async def main():
    async with VeoVideoGenerator() as gen:
        response = await gen.generate_video_async("A cat playing")

asyncio.run(main())
```

## Performance Comparison

| Method | Videos | Time | Notes |
|--------|--------|------|-------|
| Sequential (old) | 5 | ~50 min | One at a time |
| Concurrent (limit=3) | 5 | ~20 min | 60% faster |
| Concurrent (limit=5) | 5 | ~15 min | 70% faster |
| Concurrent (limit=10) | 10 | ~15 min | Max efficiency |

## Next Steps

1. Start with `basic_example.py` to verify setup
2. Try `async_example.py` for better error handling
3. Use `batch_example.py` for multiple videos
4. Read the source code in `video_generation/` for advanced customization

## Support

For issues or questions:
- Check the main README
- Review the source code documentation
- Check API status at https://api.thucchien.ai/status
