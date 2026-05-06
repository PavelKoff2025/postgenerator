import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

def generate_image(prompt: str) -> str:
    """Generate image using Stability AI or fallback to PIL"""
    # Try Stability AI API (free tier available)
    stability_key = os.getenv("STABILITY_API_KEY")
    
    if stability_key:
        try:
            api_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
            headers = {
                "Authorization": f"Bearer {stability_key}",
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            payload = {
                "text_prompts": [{"text": prompt[:500], "weight": 1}],
                "cfg_scale": 7,
                "height": 1024,
                "width": 1024,
                "samples": 1,
                "steps": 30
            }
            
            resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            
            # Extract base64 image
            if "artifacts" in data and len(data["artifacts"]) > 0:
                import base64
                img_data = base64.b64decode(data["artifacts"][0]["base64"])
                
                # Save image
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
                os.makedirs(temp_dir, exist_ok=True)
                timestamp = int(time.time())
                image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(img_data)
                
                return f"/static/generated/image_{timestamp}.jpg"
        except Exception as e:
            print(f"Stability AI error: {e}")
    
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
