import os
import base64
from openai import OpenAI

def generate_image(prompt: str) -> str:
    """Generate image using ProxyAPI.ru via OpenAI SDK"""
    api_key = os.getenv("PROXYAPI_KEY")
    if not api_key:
        return ""
    
    try:
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
        
        # Extract image data (ProxyAPI returns b64_json)
        if response.data and len(response.data) > 0:
            img_b64 = response.data[0].b64_json
            if img_b64:
                img_data = base64.b64decode(img_b64)
                
                # Save image
                temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
                os.makedirs(temp_dir, exist_ok=True)
                timestamp = int(time.time())
                image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
                
                with open(image_path, "wb") as f:
                    f.write(img_data)
                
                return f"/static/generated/image_{timestamp}.jpg"
                
    except Exception as e:
        print(f"ProxyAPI error: {e}")
    
    return ""
