import litellm
import base64
import os
from typing import List

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = os.getenv("THUCCHIEN_API_KEY")


def generate_images(prompt: str, model: str = "litellm_proxy/imagen-4", n: int = 1, save_prefix: str = "generated_image") -> List[str]:
    """
    Generate images using AI model.

    Args:
        prompt: The text prompt for image generation
        model: The model to use (default: litellm_proxy/imagen-4)
        n: Number of images to generate (default: 1)
        save_prefix: Prefix for saved image files (default: generated_image)

    Returns:
        List of saved image file paths
    """
    response = litellm.image_generation(
        prompt=prompt,
        model=model,
        n=n,
        api_key=AI_API_KEY,
        api_base=AI_API_BASE,
    )

    saved_paths = []
    for i, image_obj in enumerate(response.data):
        b64_data = image_obj['b64_json']
        image_data = base64.b64decode(b64_data)

        save_path = f"{save_prefix}_{i+1}.png"
        with open(save_path, 'wb') as f:
            f.write(image_data)
            print(f"Image saved to {save_path}")
            saved_paths.append(save_path)

    return saved_paths


# --- Example usage ---
if __name__ == "__main__":
    images = generate_images("Generate a picture of vietnamese girl", n=2)
    print(f"Generated {len(images)} images: {images}")