import requests
import json
import base64
import os

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai/v1"
AI_API_KEY = "<your_api_key>" # Thay bằng API key của bạn

# Đọc cấu hình từ file JSON
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "prompt_config.json")
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

config = load_config()
IMAGE_SAVE_PATH = config["image_save_path"]

# --- Bước 1: Gọi API để tạo hình ảnh ---
url = f"{AI_API_BASE}/chat/completions"
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {AI_API_KEY}"
}
data = {
  "model": config["model"],
  "messages": [
      {
          "role": "user",
          "content": config["prompt"]
      }
  ]
}

try:
  response = requests.post(url, headers=headers, data=json.dumps(data))
  response.raise_for_status()

  result = response.json()
  # Trích xuất dữ liệu ảnh base64 từ response
  base64_string = result['choices'][0]['message']['images'][0]['image_url']['url']
  print("Image data received successfully.")

  # --- Bước 2: Giải mã và lưu hình ảnh ---
  # Loại bỏ tiền tố 'data:image/png;base64,' nếu có
  if ',' in base64_string:
      header, encoded = base64_string.split(',', 1)
  else:
      encoded = base64_string

  image_data = base64.b64decode(encoded)

  with open(IMAGE_SAVE_PATH, 'wb') as f:
      f.write(image_data)
  
  print(f"Image saved to {IMAGE_SAVE_PATH}")

except requests.exceptions.RequestException as e:
  print(f"An error occurred: {e}")
  print(f"Response body: {response.text if 'response' in locals() else 'No response'}")
except (KeyError, IndexError) as e:
  print(f"Failed to parse image data from response: {e}")
  print(f"Response body: {response.text if 'response' in locals() else 'No response'}")