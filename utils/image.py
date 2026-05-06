import os
import time
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generate_image(prompt: str) -> str:
    """Generate image with text overlay"""
    try:
        width, height = 800, 600
        image = Image.new('RGB', (width, height), color='#4f46e5')
        draw = ImageDraw.Draw(image)
        
        # Try to load a font
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            font = ImageFont.load_default()
        
        # Prepare text
        wrapped_text = textwrap.fill(prompt[:200], width=40)
        lines = wrapped_text.split('\n')
        
        # Draw text
        y_offset = height // 2 - (len(lines) * 30) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            draw.text((x, y_offset), line, fill='white', font=font)
            y_offset += 30
        
        # Save image
        temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = int(time.time())
        image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
        image.save(image_path, "JPEG", quality=90)
        
        return f"/static/generated/image_{timestamp}.jpg"
        
    except Exception as e:
        print(f"Image generation error: {e}")
        return ""
