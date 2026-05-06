import os
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_image(prompt: str) -> str:
    """Generate image using GigaChat/Kandinsky"""
    from gigachat import GigaChat
    
    credentials = os.getenv("GIGACHAT_CLIENT_SECRET")
    
    try:
        with GigaChat(credentials=credentials, verify_ssl_certs=False) as client:
            # Get token from GigaChat client
            token = client.token
    except Exception as e:
        raise Exception(f"Auth error: {str(e)}")
    
    # Try Kandinsky API
    api_url = "https://api.gigachat.kandinsky.com/v1/pictures"
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    short_prompt = prompt[:500]
    payload = {
        "model": "Kandinsky",
        "prompt": short_prompt,
        "num_images": 1
    }
    
    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        
        # Check if we got image URL directly
        image_url = data.get("images", [None])[0]
        
        if not image_url and "id" in data:
            # Async request - wait for result
            request_id = data["id"]
            status_url = f"https://api.gigachat.kandinsky.com/v1/pictures/{request_id}"
            for _ in range(10):
                time.sleep(5)
                s_resp = requests.get(status_url, headers=headers, timeout=10)
                s_data = s_resp.json()
                if s_data.get("status") == "DONE":
                    image_url = s_data.get("images", [None])[0]
                    break
        
        if not image_url:
            raise Exception("Failed to get image URL")
        
        # Download image
        image_resp = requests.get(image_url, timeout=30)
        image_resp.raise_for_status()
        
        # Save to static/generated
        temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = int(time.time())
        image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
        
        with open(image_path, "wb") as f:
            f.write(image_resp.content)
        
        return f"/static/generated/image_{timestamp}.jpg"
        
    except Exception as e:
        print(f"Image generation error: {e}")
        raise Exception("Image generation requires separate Kandinsky API access")
