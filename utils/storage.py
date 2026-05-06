import json
import os

FAVORITES_FILE = os.path.join(os.path.dirname(__file__), "..", "favorites.json")

def load_favorites():
    """Загружает избранные посты из файла"""
    if not os.path.exists(FAVORITES_FILE):
        return []
    try:
        with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_favorite(post_data):
    """Сохраняет пост в избранное"""
    favorites = load_favorites()
    # Добавляем ID и время
    import time
    post_data["id"] = int(time.time() * 1000)
    post_data["saved_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    favorites.append(post_data)
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)
    return post_data["id"]

def delete_favorite(post_id):
    """Удаляет пост из избранного"""
    favorites = load_favorites()
    favorites = [p for p in favorites if p.get("id") != post_id]
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def clear_favorites():
    """Очищает все избранное"""
    with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)
