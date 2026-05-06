import os
import base64
import requests
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_image(prompt: str) -> str:
    """Generate image using ProxyAPI.ru or fallback to PIL"""
    api_key = os.getenv("PROXYAPI_KEY")
    api_url = os.getenv("PROXYAPI_URL", "https://api.proxyapi.ru/openai/v1/images/generations")
    
    if api_key:
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "gpt-image-2",
                "prompt": prompt[:500],
                "n": 1,
                "size": "1024x1024"
            }
            
            resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            
            if "data" in data and len(data["data"]) > 0:
                img_info = data["data"][0]
                image_data = None
                
                if "b64_json" in img_info:
                    image_data = base64.b64decode(img_info["b64_json"])
                elif "url" in img_info:
                    img_resp = requests.get(img_info["url"], timeout=30)
                    img_resp.raise_for_status()
                    image_data = img_resp.content
                
                if image_data:
                    temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
                    os.makedirs(temp_dir, exist_ok=True)
                    timestamp = int(time.time())
                    image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
                    
                    with open(image_path, "wb") as f:
                        f.write(image_data)
                    
                    return f"/static/generated/image_{timestamp}.jpg"
        except Exception as e:
            print(f"ProxyAPI error: {e}")
    
    # Fallback: PIL image
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
