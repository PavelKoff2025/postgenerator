import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
import base64
import io

def generate_image(prompt: str) -> str:
    """Generate image using Hugging Face Inference API or fallback to PIL"""
    # Try Hugging Face API (free tier)
    hf_token = os.getenv("HUGGINGFACE_TOKEN")
    
    if hf_token:
        try:
            # Use a popular image generation model on Hugging Face
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            headers = {"Authorization": f"Bearer {hf_token}"}
            
            # Hugging Face expects different format
            response = requests.post(
                api_url,
                headers=headers,
                json={"inputs": prompt[:200]},
                timeout=60
            )
            
            if response.status_code == 200:
                # Response is the image bytes directly
                img_data = response.content
                
                # Save image
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
                os.makedirs(temp_dir, exist_ok=True)
                timestamp = int(time.time())
                image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(img_data)
                
                return f"/static/generated/image_{timestamp}.jpg"
            else:
                print(f"Hugging Face API error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Hugging Face error: {e}")
    
    # Fallback: Generate simple PIL image with text
    try:
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='#4f46e5')
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
        
        wrapped_text = textwrap.fill(prompt[:100], width=40)
        lines = wrapped_text.split('\n')
        
        y_offset = height // 2 - (len(lines) * 30) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill='white', font=font)
            y_offset += 30
        
        temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
        os.makedirs(temp_dir, exist_ok=True)
        timestamp = int(time.time())
        image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
        image.save(image_path, "JPEG", quality=90)
        
        return f"/static/generated/image_{timestamp}.jpg"
    except Exception as e:
        print(f"PIL error: {e}")
        return ""
