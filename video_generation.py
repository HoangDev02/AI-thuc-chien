#!/usr/bin/env python3
"""
Video Generation - Backward Compatible Interface

This module maintains the original interface while using the optimized
async implementation under the hood.

MIGRATION GUIDE:
===============

Old usage (still works):
    from video_generation import generate_video
    video_path = generate_video("A cat playing")

New async usage (recommended):
    from video_generation import VeoVideoGenerator
    import asyncio

    async def main():
        async with VeoVideoGenerator() as gen:
            response = await gen.generate_video_async("A cat playing")
            print(f"Saved to: {response.video_path}")

    asyncio.run(main())

Batch processing (new feature):
    from video_generation import generate_videos_batch
    import asyncio

    prompts = ["Cat playing", "Ocean waves", "City street"]
    result = asyncio.run(generate_videos_batch(prompts))
    print(result.summary())

For more examples, see the examples/ directory.
"""

# Import from the new optimized package
from video_generation import (
    # Main classes
    VeoVideoGenerator,

    # Functions
    generate_video,
    generate_videos_batch,

    # Models
    VideoRequest,
    VideoResponse,
    OperationStatus,
    BatchResult,

    # Exceptions
    VideoGenerationError,
    DownloadError,
    TimeoutError,
    APIError,
)

# For backward compatibility, re-export everything
__all__ = [
    "VeoVideoGenerator",
    "generate_video",
    "generate_videos_batch",
    "VideoRequest",
    "VideoResponse",
    "OperationStatus",
    "BatchResult",
    "VideoGenerationError",
    "DownloadError",
    "TimeoutError",
    "APIError",
]


def main():
    """
    Example usage - backward compatible with original implementation.

    To run: python video_generation.py
    """
    import os

    print("=" * 70)
    print("🎬 VEO VIDEO GENERATION - OPTIMIZED VERSION 2.0")
    print("=" * 70)
    print()
    print("This is the backward-compatible interface.")
    print("For async/batch features, see examples/ directory.")
    print()

    # Example prompts
    example_prompts = [
        "A cat playing with a ball of yarn in a sunny garden",
        "Ocean waves crashing against rocky cliffs at sunset",
        "A bustling city street with people walking and cars passing by",
        "A peaceful forest with sunlight filtering through the trees"
    ]

    # Use first example
    prompt = example_prompts[0]
    print(f"🎬 Generating video with prompt:")
    print(f"   '{prompt}'")
    print()

    # Generate video using backward-compatible sync API
    video_path = generate_video(prompt)

    if video_path:
        print()
        print("=" * 70)
        print("✅ SUCCESS!")
        print("=" * 70)
        print(f"📁 Video saved to: {video_path}")
        print()
        print("💡 Try these next:")
        print("   - examples/basic_example.py     (Simple sync usage)")
        print("   - examples/async_example.py     (Async with details)")
        print("   - examples/batch_example.py     (Batch processing)")
        print("   - examples/advanced_batch.py    (Advanced features)")
        print("=" * 70)
    else:
        print()
        print("=" * 70)
        print("❌ FAILED!")
        print("=" * 70)
        print("🔧 Check your API configuration:")
        print("   - THUCCHIEN_API_KEY or LITELLM_API_KEY environment variable")
        print("   - LITELLM_BASE_URL (optional)")
        print("=" * 70)


if __name__ == "__main__":
    main()
