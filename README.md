# AI Thực Chiến Gateway - Python Examples

Step-by-step examples for using AI Thực Chiến gateway with Python.

## Setup

### 1. Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv env

# Activate virtual environment
# On macOS/Linux:
source env/bin/activate
# On Windows:
env\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install litellm openai requests python-dotenv
```

### 3. Configure API Key

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key:
   ```
   THUCCHIEN_API_KEY=your_actual_api_key_here
   ```

3. Get your API key from: https://thucchien.ai

### 4. Load Environment Variables

Add this to each script (or use python-dotenv):
```python
from dotenv import load_dotenv
load_dotenv()
```

## Examples

### Text Generation
**File:** `text_generation.py`
**Model:** `litellm_proxy/gemini-2.5-pro`
**Endpoint:** `https://api.thucchien.ai/chat/completions`

```bash
python text_generation.py
```

**Reusable Function:**
```python
from text_generation import generate_text

result = generate_text("Your prompt here", model="litellm_proxy/gemini-2.5-pro")
print(result)
```

Generates text responses using conversational AI.

---

### Image Generation
**File:** `image_generation.py`
**Model:** `litellm_proxy/imagen-4`
**Endpoint:** `https://api.thucchien.ai/images/generations`

```bash
python image_generation.py
```

**Reusable Function:**
```python
from image_generation import generate_images

images = generate_images("Your prompt here", model="litellm_proxy/imagen-4", n=2)
print(f"Generated images: {images}")
```

Generates images from text prompts. Output saved as `generated_image_*.png`.

---

### Text-to-Speech
**File:** `text_to_speech.py`
**Model:** `gemini-2.5-flash-preview-tts`
**Endpoint:** `https://api.thucchien.ai/audio/speech`

```bash
python text_to_speech.py
```

**Reusable Function:**
```python
from text_to_speech import generate_speech

audio_file = generate_speech("Your text here", model="gemini-2.5-flash-preview-tts", voice="alloy")
print(f"Audio saved to: {audio_file}")
```

Converts text to speech audio. Output saved as `speech_from_openai.mp3`.

**Available Voices:** `alloy`, `nova`, `echo`

---

### Video Generation
**File:** `video_generation.py`
**Model:** `veo-3.0-generate-preview`
**Endpoint:** `https://api.thucchien.ai/gemini/v1beta/models/veo-3.0-generate-preview:predictLongRunning`

```bash
python video_generation.py
```

**Reusable Function:**
```python
from video_generation import generate_video

video_file = generate_video("Your prompt here", output_path="my_video.mp4")
print(f"Video saved to: {video_file}")
```

Generates videos from text prompts (async operation). Output saved as `generated_video.mp4`.

**Note:** Video generation uses a different authentication header (`x-goog-api-key`) and polls for completion.

## API Documentation

Full documentation: https://docs.thucchien.ai/docs/user-guide

## File Structure

```
.
├── README.md
├── .env.example
├── text_generation.py
├── image_generation.py
├── video_generation.py
└── text_to_speech.py
```