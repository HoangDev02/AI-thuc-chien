#!/usr/bin/env python3
"""
Advanced batch example: Custom configuration and error handling.

This example shows advanced features including:
- Custom API configuration
- Error handling
- Progress tracking
- Partial success handling
"""

import asyncio
import os
from pathlib import Path

from video_generation import VeoVideoGenerator, VideoGenerationError


async def main():
    """Advanced batch processing with custom configuration."""

    print("🎬 Advanced Batch Video Generation\n")

    # Custom configuration
    custom_config = {
        "base_url": os.getenv("LITELLM_BASE_URL", "https://api.thucchien.ai/gemini/v1beta"),
        "api_key": os.getenv("LITELLM_API_KEY"),
        "timeout": 60,  # Custom timeout
        "max_retries": 5,  # More retries
    }

    prompts = [
        "A professional chef cooking in a modern kitchen",
        "A serene mountain landscape with snow-capped peaks",
        "A futuristic city with flying cars and neon lights",
        "A tropical beach with crystal clear water and palm trees",
        "A cozy coffee shop with people reading and working",
        "A wildlife safari with elephants and zebras",
        "A jazz band performing in a dimly lit club",
        "A farmer's market with fresh vegetables and fruits",
    ]

    output_dir = Path("examples/output/advanced_batch")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        async with VeoVideoGenerator(**custom_config) as generator:
            print(f"📝 Queued {len(prompts)} videos for generation")
            print(f"📁 Output directory: {output_dir}")
            print(f"⚙️  Concurrent limit: 5 videos at a time\n")

            # Generate videos with custom concurrency
            result = await generator.generate_batch(
                prompts=prompts,
                output_dir=output_dir,
                concurrent_limit=5,  # Process 5 at a time
            )

            # Detailed analysis
            print("\n" + "="*70)
            print("📊 DETAILED RESULTS ANALYSIS")
            print("="*70)

            # Overall statistics
            print(f"\n📈 Overall Statistics:")
            print(f"  Total videos requested: {result.total}")
            print(f"  Successfully generated: {result.successful}")
            print(f"  Failed: {result.failed}")
            print(f"  Success rate: {result.success_rate:.1f}%")
            print(f"  Total processing time: {result.total_time:.1f}s")

            if result.successful > 0:
                avg_time = sum(
                    r.generation_time for r in result.get_successful_videos()
                ) / result.successful
                avg_size = sum(
                    r.file_size_mb for r in result.get_successful_videos()
                ) / result.successful
                print(f"  Average generation time: {avg_time:.1f}s")
                print(f"  Average file size: {avg_size:.2f} MB")

            # Successful videos details
            if result.successful > 0:
                print(f"\n✅ Successfully Generated Videos ({result.successful}):")
                for idx, response in enumerate(result.get_successful_videos(), 1):
                    print(f"  {idx}. {response.video_path.name}")
                    print(f"     Size: {response.file_size_mb:.2f} MB | "
                          f"Time: {response.generation_time:.1f}s")

            # Failed videos details
            if result.has_failures:
                print(f"\n❌ Failed Videos ({result.failed}):")
                for idx, response in enumerate(result.get_failed_videos(), 1):
                    print(f"  {idx}. Error: {response.error}")
                    if response.error_details:
                        print(f"     Details: {response.error_details}")

            # Summary
            print("\n" + "="*70)
            if result.success_rate == 100.0:
                print("🎉 Perfect! All videos generated successfully!")
            elif result.success_rate >= 80.0:
                print("✅ Good! Most videos generated successfully")
            elif result.success_rate >= 50.0:
                print("⚠️  Partial success - some videos failed")
            else:
                print("❌ Many videos failed - check configuration")
            print("="*70)

    except VideoGenerationError as e:
        print(f"\n❌ Video generation error: {e}")
        if hasattr(e, 'details'):
            print(f"Details: {e.details}")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
