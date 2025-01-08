import os
import requests
import json
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# Загружаем переменные окружения из .env файла
load_dotenv()
OLLAMA_API_URL = os.getenv("OLLAMA_API_URL", "http://localhost:11434/api/chat")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Функция для перевода текста через локальную модель Ollama
def translate_to_spanish(text):
    # Подготовка данных для запроса
    payload = {
        "model": "llama3.2:latest",  # Укажите локальную модель, которую вы хотите использовать
        "messages": [
            {"role": "system", "content": "Ты переводчик с русского на испанский."},
            {"role": "user", "content": f"Переведи следующий текст с русского на испанский: \"{text}\""}
        ]
    }
    headers = {"Content-Type": "application/json"}

    try:
        # Отправляем запрос к API Ollama
        response = requests.post(OLLAMA_API_URL, json=payload, headers=headers)

        # Проверяем HTTP-статус ответа
        if response.status_code == 200:
            print("Запрос успешен! Статус:", response.status_code)
        else:
            print(f"Ошибка! Статус: {response.status_code}")
            print("Сырой ответ:", response.text)
            return "API вернул ошибку. Проверьте настройки."

        # Печатаем сырой текст ответа для отладки
        print("Сырой ответ API:", response.text)

        # Собираем полный текст ответа
        translation = ""
        for line in response.text.splitlines():
            try:
                # Парсим каждую строку как JSON
                data = json.loads(line)
                # Извлекаем содержимое сообщения
                translation += data["message"]["content"]
            except json.JSONDecodeError as e:
                print(f"Ошибка декодирования строки: {line}, {e}")

        # Возвращаем собранный перевод
        return translation.strip()

    except requests.exceptions.RequestException as e:
        print(f"Ошибка при обращении к API Ollama: {e}")
        return "Не удалось подключиться к API Ollama."

# Обработчик сообщений
async def handle_message(update: Update, context):
    user_text = update.message.text
    try:
        translated_text = translate_to_spanish(user_text)
        await update.message.reply_text(translated_text)
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке сообщения.")
        print(f"Ошибка: {e}")

# Команда /start
async def start_command(update: Update, context):
    await update.message.reply_text("Привет! Отправь мне текст на русском, и я переведу его на испанский.")

# Основная функция
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
