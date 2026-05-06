# PostGen

Flask-приложение для генерации постов из лонгридов с помощью LLM.

## Быстрый старт

1. Клонируйте репозиторий и перейдите в папку:
   ```bash
   cd postgen
   ```

2. Создайте виртуальное окружение и активируйте его:
   ```bash
   python -m venv venv
   source venv/bin/activate  # macOS/Linux
   ```

3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```

4. Настройте переменные окружения:
   ```bash
   cp .env.example .env
   ```
   Откройте `.env` и укажите ваш API-ключ и URL эндпоинта LLM.

5. Запустите приложение:
   ```bash
   python app.py
   ```

6. Откройте в браузере: [http://localhost:5002](http://localhost:5002)

## Структура проекта

```
postgen/
├── app.py              # Основной файл Flask
├── utils/
│   ├── parser.py       # Парсинг текста из URL
│   └── llm.py          # Работа с LLM API
├── templates/
│   └── index.html      # Шаблон интерфейса
├── static/
│   ├── css/style.css   # Стили
│   └── js/app.js       # Клиентская логика
├── .env.example        # Пример переменных окружения
└── requirements.txt    # Зависимости
```

## Требования

- Python 3.10+
- API-ключ от LLM-провайдера (OpenRouter, Groq, YandexGPT и др.)
