from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

from utils.parser import extract_text_from_url
from utils.llm import generate_post
from utils.vk import publish_to_vk
from utils.storage import load_favorites, save_favorite, delete_favorite, clear_favorites

load_dotenv()

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/generate", methods=["POST"])
def generate():
    data = request.get_json(silent=True)
    if not data or "url" not in data:
        return jsonify({"status": "error", "message": "Некорректный запрос"}), 400

    url = data["url"].strip()
    if not url:
        return jsonify({"status": "error", "message": "URL не может быть пустым"}), 400

    try:
        text = extract_text_from_url(url)
        if not text:
            return jsonify({"status": "error", "message": "Не удалось извлечь текст из URL"}), 400
    except Exception as e:
        return jsonify({"status": "error", "message": f"Ошибка при парсинге: {str(e)}"}), 400

    try:
        result = generate_post(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": f"Ошибка генерации: {str(e)}"}), 500

@app.route("/publish-vk", methods=["POST"])
def publish_vk():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"status": "error", "message": "Некорректный запрос"}), 400
    
    text = data.get("text", "")
    hashtags = data.get("hashtags", [])
    publish_date = data.get("publish_date")
    
    try:
        result = publish_to_vk(text, hashtags, publish_date)
        return jsonify(result)
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route("/favorites", methods=["GET", "POST", "DELETE"])
def favorites():
    if request.method == "GET":
        return jsonify(load_favorites())
    
    if request.method == "POST":
        data = request.get_json(silent=True)
        if not data:
            return jsonify({"status": "error", "message": "Некорректный запрос"}), 400
        post_id = save_favorite(data)
        return jsonify({"status": "ok", "id": post_id})
    
    if request.method == "DELETE":
        post_id = request.args.get("id")
        if post_id:
            delete_favorite(int(post_id))
        else:
            clear_favorites()
        return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(debug=True, port=5002)
