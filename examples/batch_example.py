#!/usr/bin/env python3
"""
Batch processing example: Generate multiple videos concurrently.

This example demonstrates the power of async batch processing,
generating multiple videos simultaneously with automatic concurrency control.
"""

import asyncio

from video_generation import generate_videos_batch


async def main():
    """Generate multiple videos concurrently."""

    print("🎬 Batch Video Generation Example\n")

    # Define multiple prompts to generate
    prompts = [
        "A cat playing with a ball of yarn in a sunny garden",
        "Ocean waves crashing against rocky cliffs at sunset",
        "A bustling city street with people walking and cars passing by",
        "A peaceful forest with sunlight filtering through the trees",
        "A chef preparing a gourmet meal in a professional kitchen",
    ]

    print(f"Generating {len(prompts)} videos concurrently...\n")

    # Generate all videos with concurrency control (max 3 at a time)
    batch_result = await generate_videos_batch(
        prompts=prompts,
        output_dir="examples/output/batch",
        concurrent_limit=3,  # Generate 3 videos at a time
    )

    # Print detailed results
    print("\n" + "="*60)
    print("📊 BATCH RESULTS")
    print("="*60)
    print(f"Total videos: {batch_result.total}")
    print(f"Successful: {batch_result.successful}")
    print(f"Failed: {batch_result.failed}")
    print(f"Success rate: {batch_result.success_rate:.1f}%")
    print(f"Total time: {batch_result.total_time:.1f}s")
    print()

    # Show successful videos
    if batch_result.successful > 0:
        print("✅ Successful videos:")
        for response in batch_result.get_successful_videos():
            print(f"  - {response.video_path} ({response.file_size_mb:.2f} MB)")
        print()

    # Show failed videos
    if batch_result.has_failures:
        print("❌ Failed videos:")
        for response in batch_result.get_failed_videos():
            print(f"  - Error: {response.error}")
        print()


if __name__ == "__main__":
    asyncio.run(main())
