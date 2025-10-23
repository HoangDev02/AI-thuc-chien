#!/usr/bin/env python3
"""
Quick import test to verify package structure.

Run this after installing dependencies:
    uv sync
    python test_imports.py
"""

def test_imports():
    """Test that all imports work correctly."""
    print("Testing imports...\n")

    # Test 1: Main package imports
    print("1. Testing main package imports...")
    try:
        from video_generation import (
            VeoVideoGenerator,
            generate_video,
            generate_videos_batch,
            VideoRequest,
            VideoResponse,
            BatchResult,
            VideoGenerationError,
            APIError,
            TimeoutError,
            DownloadError,
        )
        print("   ✅ Main package imports successful")
    except ImportError as e:
        print(f"   ❌ Main package import failed: {e}")
        return False

    # Test 2: Backward compatible imports
    print("\n2. Testing backward compatible imports...")
    try:
        from video_generation import generate_video
        print("   ✅ Backward compatible import successful")
    except ImportError as e:
        print(f"   ❌ Backward compatible import failed: {e}")
        return False

    # Test 3: Submodule imports
    print("\n3. Testing submodule imports...")
    try:
        from video_generation.config import DEFAULT_BASE_URL
        from video_generation.models import VideoStatus
        from video_generation.exceptions import ValidationError
        from video_generation.utils import sanitize_filename
        print("   ✅ Submodule imports successful")
    except ImportError as e:
        print(f"   ❌ Submodule import failed: {e}")
        return False

    # Test 4: Type checking
    print("\n4. Testing type annotations...")
    try:
        from typing import get_type_hints
        hints = get_type_hints(VeoVideoGenerator.__init__)
        print(f"   ✅ Type hints available: {list(hints.keys())}")
    except Exception as e:
        print(f"   ❌ Type hints failed: {e}")
        return False

    # Test 5: Pydantic models
    print("\n5. Testing Pydantic models...")
    try:
        # Test VideoRequest validation
        req = VideoRequest(prompt="Test prompt")
        print(f"   ✅ VideoRequest created: prompt='{req.prompt}'")

        # Test validation error
        try:
            VideoRequest(prompt="")
        except Exception:
            print("   ✅ Validation correctly rejects empty prompt")

    except Exception as e:
        print(f"   ❌ Pydantic model test failed: {e}")
        return False

    # Test 6: Utility functions
    print("\n6. Testing utility functions...")
    try:
        from video_generation.utils import (
            sanitize_filename,
            generate_filename,
            validate_prompt,
        )

        safe_name = sanitize_filename("A cat playing! @home")
        assert safe_name == "A_cat_playing_home"
        print(f"   ✅ sanitize_filename: '{safe_name}'")

        filename = generate_filename("Test prompt", timestamp=False)
        assert filename.startswith("veo_")
        assert filename.endswith(".mp4")
        print(f"   ✅ generate_filename: '{filename}'")

        valid, error = validate_prompt("Valid prompt")
        assert valid is True
        print(f"   ✅ validate_prompt: valid={valid}")

    except Exception as e:
        print(f"   ❌ Utility functions test failed: {e}")
        return False

    # Test 7: Exception hierarchy
    print("\n7. Testing exception hierarchy...")
    try:
        # Test that all exceptions inherit from VideoGenerationError
        assert issubclass(APIError, VideoGenerationError)
        assert issubclass(TimeoutError, VideoGenerationError)
        assert issubclass(DownloadError, VideoGenerationError)
        print("   ✅ Exception hierarchy correct")

        # Test exception with details
        error = APIError("Test error", status_code=404, response_data={"error": "Not found"})
        assert error.status_code == 404
        print(f"   ✅ Exception details: status_code={error.status_code}")

    except Exception as e:
        print(f"   ❌ Exception hierarchy test failed: {e}")
        return False

    # Test 8: Configuration
    print("\n8. Testing configuration...")
    try:
        from video_generation.config import (
            DEFAULT_BASE_URL,
            DEFAULT_MAX_WAIT_TIME,
            DEFAULT_CONCURRENT_LIMIT,
        )
        print(f"   ✅ DEFAULT_BASE_URL: {DEFAULT_BASE_URL}")
        print(f"   ✅ DEFAULT_MAX_WAIT_TIME: {DEFAULT_MAX_WAIT_TIME}s")
        print(f"   ✅ DEFAULT_CONCURRENT_LIMIT: {DEFAULT_CONCURRENT_LIMIT}")
    except Exception as e:
        print(f"   ❌ Configuration test failed: {e}")
        return False

    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nPackage structure is correct and ready to use.")
    print("\nNext steps:")
    print("  1. Set API key: export THUCCHIEN_API_KEY='your-key'")
    print("  2. Run examples: python examples/basic_example.py")
    print("  3. Read docs: cat QUICK_START.md")
    print()

    return True


if __name__ == "__main__":
    import sys
    success = test_imports()
    sys.exit(0 if success else 1)
