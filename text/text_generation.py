import litellm
import os

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = os.getenv("THUCCHIEN_API_KEY")


def generate_text(prompt: str, model: str = "litellm_proxy/gemini-2.5-pro") -> str:
    """
    Generate text using AI model.

    Args:
        prompt: The text prompt for generation
        model: The model to use (default: litellm_proxy/gemini-2.5-pro)

    Returns:
        Generated text content
    """
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
    result = generate_text("Viết một đoạn văn ngắn về tầm quan trọng của AI.")
    print(result)