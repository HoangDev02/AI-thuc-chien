#!/usr/bin/env python3
"""
Basic example: Generate a single video synchronously.

This is the simplest way to use the video generation API,
compatible with the original interface.
"""

from video_generation import generate_video


def main():
    """Generate a single video using the simple sync API."""

    print("🎬 Basic Video Generation Example\n")

    # Simple one-liner video generation
    prompt = "A cat playing with a ball of yarn in a sunny garden"

    print(f"Generating video with prompt: '{prompt}'\n")

    video_path = generate_video(
        prompt=prompt,
        output_path="examples/output/cat_playing.mp4"  # Optional: specify output path
    )

    if video_path:
        print(f"\n✅ Success! Video saved to: {video_path}")
    else:
        print("\n❌ Video generation failed")


if __name__ == "__main__":
    main()
