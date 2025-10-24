import requests
import json
import base64
import os


# --- Cấu hình ---
AI_API_BASE = "https://api.thucchien.ai/v1"
AI_API_KEY = "<your_api_key>"


# --- Đọc config từ file JSON ---
config_path = "prompt_config.json"
if not os.path.exists(config_path):
   print(f"Config file {config_path} not found!")
   exit(1)


with open(config_path, 'r', encoding='utf-8') as f:
   config = json.load(f)


# --- Gọi API để tạo hình ảnh ---
url = f"{AI_API_BASE}/images/generations"
headers = {
 "Content-Type": "application/json",
 "Authorization": f"Bearer {AI_API_KEY}"
}
data = {
 "model": config.get("model", "imagen-4"),
 "prompt": config["prompt"],
 "n": 2, # Yêu cầu 2 ảnh
}


try:
 response = requests.post(url, headers=headers, data=json.dumps(data))
 response.raise_for_status()


 result = response.json()
  # --- Xử lý và lưu từng ảnh ---
 for i, image_obj in enumerate(result['data']):
     b64_data = image_obj['b64_json']
     image_data = base64.b64decode(b64_data)
    
     # Sử dụng đường dẫn từ config hoặc tạo tên file mặc định
     if "image_save_path" in config and i == 0:
         save_path = config["image_save_path"]
     else:
         save_path = f"generated_image_{i+1}.png"
    
     with open(save_path, 'wb') as f:
         f.write(image_data)
     print(f"Image saved to {save_path}")


except requests.exceptions.RequestException as e:
 print(f"An error occurred: {e}")
 print(f"Response body: {response.text if 'response' in locals() else 'No response'}")

