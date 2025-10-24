import requests
import json

# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai"
AI_API_KEY = "sk-1234" # Thay bằng API key của bạn

# --- Đọc prompt từ file JSON ---
with open("prompt_config.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# --- Thực thi ---
url = f"{AI_API_BASE}/audio/speech"
headers = {
  "Content-Type": "application/json",
  "Authorization": f"Bearer {AI_API_KEY}"
}

response = requests.post(url, headers=headers, json=data, stream=True)

if response.status_code == 200:
  with open("speech_from_requests.mp3", "wb") as f:
      for chunk in response.iter_content(chunk_size=8192):
          f.write(chunk)
  print("File âm thanh đã được tạo thành công!")
else:
  print(f"Error: {response.status_code}")
  print(response.text)