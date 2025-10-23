from openai import OpenAI
from pathlib import Path
import os

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = os.getenv("THUCCHIEN_API_KEY")


def generate_speech(prompt: str, model: str = "gemini-2.5-flash-preview-tts", voice: str = "alloy", output_path: str = None) -> str:
    """
    Generate speech audio from text using AI model.

    Args:
        prompt: The text to convert to speech
        model: The model to use (default: gemini-2.5-flash-preview-tts)
        voice: Voice to use for speech (default: alloy)
        output_path: Path to save audio file (default: speech_from_openai.mp3)

    Returns:
        Path to saved audio file
    """
    client = OpenAI(
        api_key=AI_API_KEY,
        base_url=AI_API_BASE
    )

    if output_path is None:
        speech_file_path = Path(__file__).parent / "speech_from_openai.mp3"
    else:
        speech_file_path = Path(output_path)

    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=prompt
    )

    response.stream_to_file(speech_file_path)
    print(f"File âm thanh đã được lưu tại: {speech_file_path}")

    return str(speech_file_path)


# --- Example usage ---
if __name__ == "__main__":
    audio_file = generate_speech("Hôm nay là một ngày đẹp trời để lập trình.")
    print(f"Generated audio: {audio_file}")