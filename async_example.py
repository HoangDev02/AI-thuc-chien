#!/usr/bin/env python3
"""
Async example: Generate a single video asynchronously with detailed control.

This example shows how to use the async API for more control over
the generation process and better error handling.
"""

import asyncio
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from video_generation import VeoVideoGenerator


async def main():
    """Generate a video using the async API with context manager."""

    print("🎬 Async Video Generation Example\n")

    prompt = """
    Shot on RED Komodo 6K with 50mm lens f/4, medium wide shot from respectful distance, senior Vietnamese government officials and Communist Party leaders on elevated ceremonial platform, formal dark suits with red ties, Vietnamese flag backdrop with golden national emblem, serious dignified expressions showing gravitas, natural light supplemented with soft key lights, official state event lighting maintaining formality, professional broadcast coverage style with locked-off tripod shot for stability, deep focus showing all officials clearly, formal composition following protocol, muted professional color grading, authoritative and respectful atmosphere, ((dignified presence:1.3)), ((official gravity:1.2)), 4K 30fps, state television broadcast quality
    --no casual poses, informal framing, harsh shadows, overexposed

    """

    # Check for available images
    image_path = None
    possible_images = [
        "generated_image_infographic_5.jpg"
       
    ]
    
    for img_file in possible_images:
        if os.path.exists(img_file):
            image_path = img_file
            print(f"🖼️  Found input image: {image_path}")
            break
    
    if not image_path:
        print("ℹ️  No input image found, generating video from text prompt only")

    # Use async context manager for proper resource management
    async with VeoVideoGenerator() as generator:
        print(f"Generating video: '{prompt}'\n")

        # Generate video asynchronously with image if available
        response = await generator.generate_video_async(
            prompt=prompt, 
            output_path="examples/output/phuong_mai-1.mp4",
            image_path=image_path
        )

        # Check result with detailed response object
        if response.is_success:
            print(f"\n✅ Success!")
            print(f"📁 Video path: {response.video_path}")
            print(f"📏 File size: {response.file_size_mb:.2f} MB")
            print(f"⏱️  Generation time: {response.generation_time:.1f}s")
            print(f"🔗 Video URI: {response.video_uri}")
        else:
            print(f"\n❌ Failed!")
            print(f"Error: {response.error}")
            if response.error_details:
                print(f"Details: {response.error_details}")


if __name__ == "__main__":
    asyncio.run(main())
