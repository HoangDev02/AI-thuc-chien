import litellm
import os
import json

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = os.getenv("THUCCHIEN_API_KEY")


def generate_text(prompt: str = None, model: str = "litellm_proxy/gemini-2.5-pro", config_file: str = "prompt_config.json") -> str:
    """
    Generate text using AI model.

    Args:
        prompt: The text prompt for generation (optional, will read from config_file if not provided)
        model: The model to use (default: litellm_proxy/gemini-2.5-pro)
        config_file: Path to JSON config file containing prompt and model settings

    Returns:
        Generated text content
    """
    # Load config from JSON file if prompt is not provided
    if prompt is None:
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
                prompt = config.get('prompt', '')
                model = config.get('model', model)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file '{config_file}' not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON format in '{config_file}'")
    
    litellm.api_base = AI_API_BASE

    response = litellm.completion(
        model=model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        api_key=AI_API_KEY
    )

    return response.choices[0].message.content


# --- Example usage ---
if __name__ == "__main__":
    # Sử dụng prompt từ file JSON
    result = generate_text()
    print(result)
    
    # Hoặc có thể override prompt trực tiếp
    # result = generate_text("Viết một đoạn văn ngắn về tầm quan trọng của AI.")
    # print(result)