import os
import requests
import time
import re

def publish_to_vk(text, hashtags, publish_date=None):
    """Публикует пост в сообщество ВК.
    
    Args:
        text: текст поста
        hashtags: список хештегов
        publish_date: Unix timestamp для отложенной публикации (опционально)
    
    Returns:
        dict со статусом и результатом
    """
    token = os.getenv("VK_ACCESS_TOKEN")
    group_id = os.getenv("VK_GROUP_ID")
    
    if not token or not group_id:
        raise Exception("Не заданы VK_ACCESS_TOKEN или VK_GROUP_ID в .env")
    
    # Убираем markdown-разметку (**жирный**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    
    # Формируем полный текст
    full_text = text
    if hashtags:
        full_text += "\n\n" + " ".join(hashtags)
    
    url = "https://api.vk.com/method/wall.post"
    params = {
        "access_token": token,
        "owner_id": f"-{group_id}",  # Для группы ID отрицательный
        "from_group": 1,
        "message": full_text,
        "v": "5.131"
    }
    
    if publish_date:
        # publish_date приходит как ISO строка или timestamp
        if isinstance(publish_date, str):
            try:
                # Пробуем распарсить как ISO
                from datetime import datetime
                dt = datetime.fromisoformat(publish_date.replace("Z", "+00:00"))
                publish_date = int(dt.timestamp())
            except:
                # Если не получилось, считаем что это уже timestamp
                publish_date = int(publish_date)
        params["publish_date"] = publish_date
    
    resp = requests.post(url, data=params, timeout=10)
    result = resp.json()
    
    if "error" in result:
        raise Exception(f"Ошибка ВК: {result['error']['error_msg']}")
    
    return {"status": "ok", "post_id": result["response"]["post_id"]}
