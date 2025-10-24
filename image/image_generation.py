import litellm
import base64
import os
import json
from typing import List, Dict, Any

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = os.getenv("THUCCHIEN_API_KEY")


def generate_images(prompt_file: str, model: str = "litellm_proxy/imagen-4", n: int = 1, save_prefix: str = "generated_image") -> List[str]:
    """
    Generate images using AI model with prompt from JSON file.

    Args:
        prompt_file: Path to JSON file containing prompt data
        model: The model to use (default: litellm_proxy/imagen-4)
        n: Number of images to generate (default: 1)
        save_prefix: Prefix for saved image files (default: generated_image)

    Returns:
        List of saved image file paths
    """
    # Load prompt from JSON file
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompt_data = json.load(f)
    
    # Extract prompt text from JSON
    prompt = prompt_data.get('prompt', '')
    if not prompt:
        raise ValueError("JSON file must contain 'prompt' field")
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
    # Create example JSON file
    example_prompt = {
        "prompt": "Generate a picture of vietnamese girl",
        "style": "photorealistic",
        "quality": "high"
    }
    
    with open("index.json", "w", encoding="utf-8") as f:
        json.dump(example_prompt, f, ensure_ascii=False, indent=2)
    
    images = generate_images("index.json", n=2)
    print(f"Generated {len(images)} images: {images}")