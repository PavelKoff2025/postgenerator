import os
import time
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def generate_image(prompt: str) -> str:
    """Генерирует изображение через GigaChat Vision/Kandinsky"""
    import base64
    from gigachat import GigaChat
    
    # Используем SDK для получения токена
    credentials = os.getenv("GIGACHAT_CLIENT_SECRET")
    with GigaChat(credentials=credentials, verify_ssl_certs=False) as client:
        # Получаем токен из клиента
        token = client.token
    
    # Используем другой эндпоинт для генерации изображений
    # (упрощенный вариант - может не работать без отдельного доступа к Kandinsky)
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
        
        # Проверяем, есть ли сразу URL изображения
        image_url = data.get("images", [None])[0]
        
        if not image_url and "id" in data:
            # Ждем результат (асинхронный запрос)
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
            raise Exception("Не удалось получить изображение")
        
        # Скачиваем изображение
        image_resp = requests.get(image_url, timeout=30)
        image_resp.raise_for_status()
        
        # Сохраняем в static/generated
        import os
        temp_dir = os.path.join(os.path.dirname(__file__), "..", "static", "generated")
        os.makedirs(temp_dir, exist_ok=True)
        
        timestamp = int(time.time())
        image_path = os.path.join(temp_dir, f"image_{timestamp}.jpg")
        
        with open(image_path, "wb") as f:
            f.write(image_resp.content)
        
        return f"/static/generated/image_{timestamp}.jpg"
        
    except Exception as e:
        # Если Kandinsky недоступен, создаем заглушку с текстом
        print(f"Ошибка генерации изображения: {e}")
        raise Exception("Для генерации изображений нужен отдельный доступ к Kandinsky API")
