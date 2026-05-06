import os
import time
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_image(prompt: str) -> str:
    """Generate image using DeepSeek API or fallback to PIL"""
    # Try DeepSeek API first
    api_key = os.getenv("DEEPSEEK_API_KEY")
    api_url = os.getenv("DEEPSEEK_API_URL")
    
    if api_key and api_url:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "prompt": prompt[:500],
                "n": 1,
                "size": "1024x1024"
            }
            resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            
            # Extract image URL (adjust based on actual DeepSeek response format)
            image_url = None
            if "data" in data and len(data["data"]) > 0:
                image_url = data["data"][0].get("url") or data["data"][0].get("b64_json")
            
            if image_url:
                # Download image
                if image_url.startswith("http"):
                    img_resp = requests.get(image_url, timeout=30)
                    img_resp.raise_for_status()
                    img_data = img_resp.content
                else:
                    # Base64 encoded image
                    import base64
                    img_data = base64.b64decode(image_url)
                
                # Save image
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
                os.makedirs(temp_dir, exist_ok=True)
                timestamp = int(time.time())
                image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(img_data)
                
                return f"/static/generated/image_{timestamp}.jpg"
        except Exception as e:
            print(f"DeepSeek API error: {e}")
            # Fall through to PIL fallback
    
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
        print(f"PIL image generation error: {e}")
        return ""
