import os
import base64
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap
import io

def generate_image(prompt: str) -> str:
    """Generate image using ProxyAPI.ru via OpenAI SDK or fallback to PIL"""
    # Try ProxyAPI.ru (OpenAI-compatible) using OpenAI SDK
    api_key = os.getenv("PROXYAPI_KEY")
    
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(
                api_key=api_key,
                base_url="https://api.proxyapi.ru/openai/v1"
            )
            
            response = client.images.generate(
                model="gpt-image-2",
                prompt=prompt[:500],
                n=1,
                size="1024x1024"
            )
            
            image_data = None
            if response.data and len(response.data) > 0:
                if response.data[0].b64_json:
                    image_data = base64.b64decode(response.data[0].b64_json)
                elif response.data[0].url:
                    img_resp = requests.get(response.data[0].url, timeout=30)
                    img_resp.raise_for_status()
                    image_data = img_resp.content
            
            if image_data:
                # Save image
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
                os.makedirs(temp_dir, exist_ok=True)
                timestamp = int(time.time())
                image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(image_data)
                
                return f"/static/generated/image_{timestamp}.jpg"
                
        except Exception as e:
            print(f"ProxyAPI error: {e}")
    
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
