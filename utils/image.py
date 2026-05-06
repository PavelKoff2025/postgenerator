import os
import time
import requests
import base64
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_gigachat_token():
    client_id = os.getenv("GIGACHAT_CLIENT_ID")
    client_secret = os.getenv("GIGACHAT_CLIENT_SECRET")
    scope = os.getenv("GIGACHAT_SCOPE", "GIGACHAT_API_PERS")

    auth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    credentials = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {credentials}"
    }
    data = f"scope={scope}&grant_type=client_credentials"
    
    resp = requests.post(auth_url, data=data, headers=headers, timeout=10, verify=False)
    resp.raise_for_status()
    return resp.json()["access_token"]


def generate_image(prompt: str) -> str:
    """Генерирует изображение через Kandinsky API и возвращает URL для веба"""
    token = get_gigachat_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Ограничиваем длину промпта
    short_prompt = prompt[:500]
    
    # Эндпоинт для генерации (упрощенный вариант)
    api_url = "https://api.gigachat.kandinsky.com/v1/pictures"
    
    payload = {
        "model": "Kandinsky",
        "prompt": short_prompt,
        "num_images": 1
    }
    
    # Отправляем запрос на генерацию
    resp = requests.post(api_url, json=payload, headers=headers, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    
    # Получаем ID запроса
    request_id = data.get("id") or data.get("request_id")
    
    if not request_id:
        # Если сразу вернул URL изображения
        image_url = data.get("images", [None])[0]
        if image_url:
            return download_image(image_url)
        raise Exception("Не удалось получить изображение")
    
    # Ждем результат (Kandinsky использует async подход)
    status_url = f"https://api.gigachat.kandinsky.com/v1/pictures/{request_id}"
    for _ in range(10):
        time.sleep(5)
        s_resp = requests.get(status_url, headers=headers, timeout=10)
        s_data = s_resp.json()
        if s_data.get("status") == "DONE":
            image_url = s_data.get("images", [None])[0]
            if image_url:
                return download_image(image_url)
            break
    
    raise Exception("Таймаут генерации изображения")


def download_image(image_url: str) -> str:
    """Скачивает изображение и сохраняет в static/generated"""
    image_resp = requests.get(image_url, timeout=30)
    image_resp.raise_for_status()
    
    temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
    os.makedirs(temp_dir, exist_ok=True)
    
    timestamp = int(time.time())
    image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
    
    with open(image_path, "wb") as f:
        f.write(image_resp.content)
    
    # Возвращаем относительный путь для веба
    return f"/static/generated/image_{timestamp}.jpg"
