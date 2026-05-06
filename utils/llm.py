import os
import time
import re
from gigachat import GigaChat

SYSTEM_PROMPT = """Ты — senior контент-стратег и B2B-SMM эксперт. Твоя задача — превращать лонгриды в профессиональные посты для соцсетей (Telegram, VK, LinkedIn).

ЦЕЛЕВАЯ АУДИТОРИЯ: маркетологи, предприниматели, студенты направления «Цифровой маркетинг».
ТОН: деловой, экспертный, структурированный. Без воды, клише и излишней эмоциональности. Без эмодзи. Используй профессиональную лексику уместно (метрики, конверсия, масштабирование, юнит-экономика, тренды, кейсы).

ПРАВИЛА ГЕНЕРАЦИИ:
1. ЖЁСТКИЙ ЛИМИТ: итоговый текст ВМЕСТЕ С ХЕШТЕГАМИ и пробелами — СТРОГО ≤ 2000 символов. Проверяй длину перед выдачей. Если больше — сокращай предложения, убирай второстепенное, но сохраняй суть.
2. СТРУКТУРА:
   • Заголовок-хук (1 строка) — пиши ЗАГЛАВНЫМИ БУКВАМИ только первую букву каждого слова, остальные маленькие (например: "Искусственный интеллект: ускорение маркетинга")
   • Ключевой инсайт/вывод из статьи (2–3 предложения)
   • Практическая польза или вопрос для профессиональной дискуссии (1 предложение)
   • Призыв к действию (CTA) — 1 предложение
   • 3–5 релевантных хештегов (каждый с #, через пробел в конце поста)
3. СОДЕРЖАНИЕ: выделяй только главную мысль, метрику, тренд или actionable-совет из текста. Не пересказывай статью.
4. ФОРМАТ ВЫВОДА: только готовый пост. БЕЗ Markdown, БЕЗ **жирного**, БЕЗ _курсива_, БЕЗ эмодзи, БЕЗ лишних символов. Только чистый текст с нормальным регистром.

Пример структуры (референс формата, не копировать дословно):
Искусственный интеллект: ускорение маркетинга без потери качества
Ключевая выгода: автоматизация рутинных задач повышает скорость производства рекламного контента и сокращает затраты на проверку. Создавайте базу знаний с примерами успешных материалов и настраивайте ассистента-копирайтера для работы в едином стиле вашего бренда.
Какие KPI первыми отслеживать при запуске AI-системы?
Присоединяйтесь к каналу для свежих практик внедрения технологий!
#маркетинг #ai #автоматизация #digital #стратегия

Начни генерацию сразу после получения текста статьи. Соблюдай лимит ≤ 2000 символов."""

def generate_post(article_text: str) -> dict:
    credentials = os.getenv("GIGACHAT_CLIENT_SECRET")
    
    for attempt in range(2):
        try:
            with GigaChat(credentials=credentials, verify_ssl_certs=False) as client:
                response = client.chat(
                    SYSTEM_PROMPT + "\n\nТекст статьи:\n" + article_text[:6000]
                )
                raw = response.choices[0].message.content.strip()
                break
        except Exception as e:
            if attempt == 1:
                raise
            time.sleep(1)
    
    # Убираем все следы Markdown и лишние символы
    text = raw
    # Удаляем JSON-подобные конструкции
    text = re.sub(r'\{[^{}]*\}', '', text)  # убираем { ... }
    text = re.sub(r'\[[^\[\]]*\]', '', text)  # убираем [ ... ]
    text = re.sub(r'"(text|hashtags)":\s*', '', text)  # убираем "text": и "hashtags":
    text = re.sub(r'^["\s]+|["\s]+$', '', text)  # убираем кавычки и пробелы по краям
    
    # Извлекаем хештеги (последние строки с #)
    lines = text.split('\n')
    hashtag_line = ''
    text_lines = []
    
    for line in lines:
        if line.strip().startswith('#'):
            hashtag_line = line.strip()
        else:
            text_lines.append(line)
    
    # Если хештеги не в отдельной строке, ищем в тексте
    if not hashtag_line:
        hashtag_pattern = r'#\w+'
        found = re.findall(hashtag_pattern, text)
        if found:
            hashtag_line = ' '.join(found)
            # Убираем хештеги из текста
            text = re.sub(hashtag_pattern, '', text)
    
    # Очищаем текст
    text = re.sub(r'\n\s*\n', '\n', text)  # убираем пустые строки
    text = re.sub(r' +', ' ', text).strip()  # убираем лишние пробелы
    
    # Разбираем хештеги
    if hashtag_line:
        hashtags = [h.strip() for h in hashtag_line.split() if h.strip().startswith('#')]
    else:
        hashtags = []
    
    # Удаляем дубликаты хештегов
    seen = set()
    unique_hashtags = []
    for h in hashtags:
        h_lower = h.lower()
        if h_lower not in seen:
            seen.add(h_lower)
            unique_hashtags.append(h)
    hashtags = unique_hashtags[:5]
    
    # Проверка лимита символов
    full_text = text + " " + " ".join(hashtags)
    if len(full_text) > 2000:
        max_text_len = 2000 - len(" ".join(hashtags)) - 1
        text = text[:max_text_len].rsplit(' ', 1)[0]
    
    if not hashtags:
        hashtags = ["#маркетинг", "#digital", "#стратегия"]
    
    return {"status": "ok", "text": text, "hashtags": hashtags}
