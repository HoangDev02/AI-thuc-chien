#!/usr/bin/env python3
"""
Complete example for Veo video generation through LiteLLM proxy.

This script demonstrates how to:
1. Generate videos using Google's Veo model
2. Poll for completion status
3. Download the generated video file

Requirements:
- LiteLLM proxy running with Google AI Studio pass-through configured
- Google AI Studio API key with Veo access

# This file is forked and adapted from: https://github.com/BerriAI/litellm/blob/main/docs/my-website/docs/proxy/veo_video_generation.md .Please refer to the original for license details.
"""

import json
import os
import time
import requests
import mimetypes
from typing import Optional, Union
from dotenv import load_dotenv

load_dotenv()

class VeoVideoGenerator:
  """Complete Veo video generation client using LiteLLM proxy."""

  def __init__(self, base_url: str = "https://api.thucchien.ai/gemini/v1beta",
               api_key: str = None):
      """   
      Initialize the Veo video generator.

      Args:
          base_url: Base URL for the LiteLLM proxy with Gemini pass-through
          api_key: API key for LiteLLM proxy authentication
      """
      self.base_url = base_url
      self.api_key = api_key or os.getenv("LITELLM_API_KEY")
      self.headers = {
          "x-goog-api-key": self.api_key,
          "Content-Type": "application/json"
      }

  def upload_image(self, image_path: str) -> Optional[str]:
      """
      Upload an image file to Google AI for use in video generation.

      Args:
          image_path: Path to the local image file

      Returns:
          File URI if successful, None otherwise
      """
      if not os.path.exists(image_path):
          print(f"❌ Image file not found: {image_path}")
          return None

      print(f"📤 Uploading image: {image_path}")

      # Detect MIME type
      mime_type, _ = mimetypes.guess_type(image_path)
      if not mime_type or not mime_type.startswith('image/'):
          print(f"❌ Invalid image file type: {mime_type}")
          return None

      # Read and encode image
      try:
          with open(image_path, 'rb') as f:
              image_data = f.read()

          file_size = len(image_data) / (1024 * 1024)  # MB
          print(f"📏 Image size: {file_size:.2f} MB")

          # Upload to Google AI Files API
          upload_url = f"{self.base_url}/files"

          # Create multipart form data
          files = {
              'file': (os.path.basename(image_path), image_data, mime_type)
          }

          # Remove Content-Type from headers for multipart upload
          upload_headers = {
              "x-goog-api-key": self.api_key
          }

          response = requests.post(upload_url, headers=upload_headers, files=files)
          response.raise_for_status()

          data = response.json()
          file_uri = data.get("file", {}).get("uri") or data.get("uri")

          if file_uri:
              print(f"✅ Image uploaded: {file_uri}")
              return file_uri
          else:
              print("❌ No file URI returned")
              print(f"Response: {json.dumps(data, indent=2)}")
              return None

      except requests.RequestException as e:
          print(f"❌ Failed to upload image: {e}")
          if hasattr(e, 'response') and e.response is not None:
              try:
                  error_data = e.response.json()
                  print(f"Error details: {json.dumps(error_data, indent=2)}")
              except:
                  print(f"Error response: {e.response.text}")
          return None
      except Exception as e:
          print(f"❌ Error reading image file: {e}")
          return None

  def prepare_image_to_video_prompt(self, text_prompt: str, image_path: str = None,
                                     image_uri: str = None, aspect_ratio: str = "16:9",
                                     duration: str = "5s") -> Optional[dict]:
      """
      Prepare a prompt for image-to-video generation.

      Args:
          text_prompt: Text description of the desired video
          image_path: Path to local image file (will be uploaded)
          image_uri: Pre-uploaded image URI (use this OR image_path)
          aspect_ratio: Video aspect ratio (e.g., "16:9", "9:16")
          duration: Video duration (e.g., "5s", "8s")

      Returns:
          Prompt dict ready for generate_video(), or None if failed
      """
      # Get image URI
      if image_path:
          image_uri = self.upload_image(image_path)
          if not image_uri:
              return None
      elif not image_uri:
          print("❌ Either image_path or image_uri must be provided")
          return None

      # Build prompt with image
      prompt = {
          "prompt": text_prompt,
          "image": {
              "fileUri": image_uri
          },
          "aspectRatio": aspect_ratio,
          "duration": duration
      }

      return prompt
  
  def generate_video(self, prompt: dict) -> Optional[str]:
      """
      Initiate video generation with Veo.

      Args:
          prompt: JSON object containing video generation parameters.
                 Example: {
                     "prompt": "A cat playing with yarn",
                     "aspectRatio": "16:9",
                     "duration": "5s"
                 }

      Returns:
          Operation name if successful, None otherwise
      """
      print(f"🎬 Generating video with prompt:")
      print(json.dumps(prompt, indent=2))

      url = f"{self.base_url}/models/veo-3.0-generate-preview:predictLongRunning"
      payload = {
          "instances": [prompt]
      }
      
      try:
          response = requests.post(url, headers=self.headers, json=payload)
          response.raise_for_status()
          
          data = response.json()
          operation_name = data.get("name")
          
          if operation_name:
              print(f"✅ Video generation started: {operation_name}")
              return operation_name
          else:
              print("❌ No operation name returned")
              print(f"Response: {json.dumps(data, indent=2)}")
              return None
              
      except requests.RequestException as e:
          print(f"❌ Failed to start video generation: {e}")
          if hasattr(e, 'response') and e.response is not None:
              try:
                  error_data = e.response.json()
                  print(f"Error details: {json.dumps(error_data, indent=2)}")
                  
                  # Check for specific authentication errors
                  if e.response.status_code == 401:
                      error_msg = error_data.get("error", {}).get("message", "")
                      if "blocked" in error_msg.lower():
                          print("\n🔧 API Key is blocked. Please:")
                          print("1. Check if your API key is valid")
                          print("2. Contact your LiteLLM proxy administrator")
                          print("3. Try using a different API key")
                      elif "token_not_found" in error_msg.lower():
                          print("\n🔧 API Key not found in database. Please:")
                          print("1. Verify your API key is correct")
                          print("2. Make sure the key is registered with the LiteLLM proxy")
                          print("3. Check if the proxy server is running correctly")
              except:
                  print(f"Error response: {e.response.text}")
          return None
  
  def wait_for_completion(self, operation_name: str, max_wait_time: int = 600) -> Optional[str]:
      """
      Poll operation status until video generation is complete.
      
      Args:
          operation_name: Name of the operation to monitor
          max_wait_time: Maximum time to wait in seconds (default: 10 minutes)
          
      Returns:
          Video URI if successful, None otherwise
      """
      print("⏳ Waiting for video generation to complete...")
      
      operation_url = f"{self.base_url}/{operation_name}"
      start_time = time.time()
      poll_interval = 10  # Start with 10 seconds
      
      while time.time() - start_time < max_wait_time:
          try:
              print(f"🔍 Polling status... ({int(time.time() - start_time)}s elapsed)")
              
              response = requests.get(operation_url, headers=self.headers)
              response.raise_for_status()
              
              data = response.json()
              
              # Check for errors
              if "error" in data:
                  print("❌ Error in video generation:")
                  print(json.dumps(data["error"], indent=2))
                  return None
              
              # Check if operation is complete
              is_done = data.get("done", False)
              
              if is_done:
                  print("🎉 Video generation complete!")
                  
                  try:
                      # Extract video URI from nested response
                      video_uri = data["response"]["generateVideoResponse"]["generatedSamples"][0]["video"]["uri"]
                      print(f"📹 Video URI: {video_uri}")
                      return video_uri
                  except KeyError as e:
                      print(f"❌ Could not extract video URI: {e}")
                      print("Full response:")
                      print(json.dumps(data, indent=2))
                      return None
              
              # Wait before next poll, with exponential backoff
              time.sleep(poll_interval)
              poll_interval = min(poll_interval * 1.2, 30)  # Cap at 30 seconds
              
          except requests.RequestException as e:
              print(f"❌ Error polling operation status: {e}")
              time.sleep(poll_interval)
      
      print(f"⏰ Timeout after {max_wait_time} seconds")
      return None
  
  def download_video(self, video_uri: str, output_filename: str = "generated_video.mp4") -> bool:
      """
      Download the generated video file.
      
      Args:
          video_uri: URI of the video to download (from Google's response)
          output_filename: Local filename to save the video
          
      Returns:
          True if download successful, False otherwise
      """
      print(f"⬇️  Downloading video...")
      print(f"Original URI: {video_uri}")
      
      # Convert Google URI to LiteLLM proxy URI
      # Example: https://generativelanguage.googleapis.com/v1beta/files/abc123 -> /gemini/download/v1beta/files/abc123:download?alt=media
      if video_uri.startswith("https://generativelanguage.googleapis.com/"):
          relative_path = video_uri.replace(
              "https://generativelanguage.googleapis.com/",
              ""
          )
      else:
          relative_path = video_uri

      # base_url: https://api.thucchien.ai/gemini/v1beta
      if self.base_url.endswith("/v1beta"):
          base_path = self.base_url.replace("/v1beta", "/download")
      else:
          base_path = self.base_url

      litellm_download_url = f"{base_path}/{relative_path}"
      print(f"Download URL: {litellm_download_url}")
      
      try:
          # Download with streaming and redirect handling
          response = requests.get(
              litellm_download_url, 
              headers=self.headers, 
              stream=True,
              allow_redirects=True  # Handle redirects automatically
          )
          response.raise_for_status()
          
          # Save video file
          with open(output_filename, 'wb') as f:
              downloaded_size = 0
              for chunk in response.iter_content(chunk_size=8192):
                  if chunk:
                      f.write(chunk)
                      downloaded_size += len(chunk)
                      
                      # Progress indicator for large files
                      if downloaded_size % (1024 * 1024) == 0:  # Every MB
                          print(f"📦 Downloaded {downloaded_size / (1024*1024):.1f} MB...")
          
          # Verify file was created and has content
          if os.path.exists(output_filename):
              file_size = os.path.getsize(output_filename)
              if file_size > 0:
                  print(f"✅ Video downloaded successfully!")
                  print(f"📁 Saved as: {output_filename}")
                  print(f"📏 File size: {file_size / (1024*1024):.2f} MB")
                  return True
              else:
                  print("❌ Downloaded file is empty")
                  os.remove(output_filename)
                  return False
          else:
              print("❌ File was not created")
              return False
              
      except requests.RequestException as e:
          print(f"❌ Download failed: {e}")
          if hasattr(e, 'response') and e.response is not None:
              print(f"Status code: {e.response.status_code}")
              print(f"Response headers: {dict(e.response.headers)}")
          return False
  
  def generate_and_download(self, prompt: dict = None, text_prompt: str = None,
                             image_path: str = None, image_uri: str = None,
                             aspect_ratio: str = "16:9", duration: str = "5s",
                             output_filename: str = None) -> bool:
      """
      Complete workflow: generate video and download it.

      Supports both text-to-video and image-to-video generation.

      Args:
          prompt: Pre-built JSON prompt (if provided, other params ignored)
          text_prompt: Text description for video generation
          image_path: Path to local image for image-to-video (optional)
          image_uri: Pre-uploaded image URI for image-to-video (optional)
          aspect_ratio: Video aspect ratio (default: "16:9")
          duration: Video duration (default: "5s")
          output_filename: Output filename (auto-generated if None)

      Returns:
          True if successful, False otherwise

      Examples:
          # Text-to-video
          generator.generate_and_download(text_prompt="A cat playing")

          # Image-to-video with local image
          generator.generate_and_download(
              text_prompt="Camera zooms in",
              image_path="photo.jpg"
          )

          # Using pre-built prompt
          generator.generate_and_download(prompt={"prompt": "A cat", ...})
      """
      # Build prompt if not provided
      if prompt is None:
          if text_prompt is None:
              print("❌ Either 'prompt' or 'text_prompt' must be provided")
              return False

          # Check if image-to-video or text-to-video
          if image_path or image_uri:
              # Image-to-video
              prompt = self.prepare_image_to_video_prompt(
                  text_prompt=text_prompt,
                  image_path=image_path,
                  image_uri=image_uri,
                  aspect_ratio=aspect_ratio,
                  duration=duration
              )
              if not prompt:
                  return False
          else:
              # Text-to-video
              prompt = {
                  "prompt": text_prompt,
                  "aspectRatio": aspect_ratio,
                  "duration": duration
              }

      # Auto-generate filename if not provided
      if output_filename is None:
          timestamp = int(time.time())
          # Extract text from prompt dict for filename
          prompt_text = prompt.get("prompt", "video")
          safe_prompt = "".join(c for c in prompt_text[:30] if c.isalnum() or c in (' ', '-', '_')).rstrip()
          mode = "image_to_video" if "image" in prompt else "text_to_video"
          output_filename = f"veo_{mode}_{safe_prompt.replace(' ', '_')}_{timestamp}.mp4"

      print("=" * 60)
      print("🎬 VEO VIDEO GENERATION WORKFLOW")
      if "image" in prompt:
          print("📸 Mode: Image-to-Video")
      else:
          print("✍️  Mode: Text-to-Video")
      print("=" * 60)

      # Step 1: Generate video
      operation_name = self.generate_video(prompt)
      if not operation_name:
          return False

      # Step 2: Wait for completion
      video_uri = self.wait_for_completion(operation_name)
      if not video_uri:
          return False

      # Step 3: Download video
      success = self.download_video(video_uri, output_filename)

      if success:
          print("=" * 60)
          print("🎉 SUCCESS! Video generation complete!")
          print(f"📁 Video saved as: {output_filename}")
          print("=" * 60)
      else:
          print("=" * 60)
          print("❌ FAILED! Video generation or download failed")
          print("=" * 60)

      return success


def main():
  """
  Example usage of the VeoVideoGenerator.
  
  Configure these environment variables:
  - LITELLM_BASE_URL: Your LiteLLM proxy URL (default: https://api.thucchien.ai/gemini/v1beta)
  - LITELLM_API_KEY: Your LiteLLM API key (default: sk-1234)
  """
  
  # Configuration from environment or defaults
  base_url = os.getenv("LITELLM_BASE_URL", "https://api.thucchien.ai/gemini/v1beta")

  api_key = os.getenv("LITELLM_API_KEY", "sk-")
  
  # Check if API key looks valid
  if not api_key.startswith("sk-"):
      print("⚠️  Warning: API key doesn't start with 'sk-'. This might not be a valid LiteLLM API key.")
  
  print("🚀 Starting Veo Video Generation Example")
  print(f"📡 Using LiteLLM proxy at: {base_url}")
  
  # Initialize generator
  generator = VeoVideoGenerator(base_url=base_url, api_key=api_key)


  try:
    with open("index.json", "r") as f:
      example_prompts = json.load(f)
    # Use first example or get from user
    prompt = example_prompts["prompts"][0]
  except (FileNotFoundError, KeyError, IndexError) as e:
    print(f"❌ Error loading prompts from index.json: {e}")
    print("Using a simple fallback prompt...")
    prompt = {
      "prompt": "A professional news anchor speaking confidently to camera",
      "aspectRatio": "16:9",
      "duration": "5s"
    }
  print(f"🎬 Using prompt:")
  print(json.dumps(prompt, indent=2))

  image_path = "generated_image_infographic_5.jpg"
  # Generate and download video
  success = generator.generate_and_download(prompt, image_path=image_path)
  
  if success:
      print("✅ Example completed successfully!")
      print("💡 Try modifying the prompt in the script for different videos!")
  else:
      print("❌ Example failed!")
      print("🔧 Check your API Configuration")

if __name__ == "__main__":
  main()