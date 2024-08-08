from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
from github import Github
import os

# Токены
TELEGRAM_[REDACTED] = 'your_telegram_bot_token'
GITHUB_[REDACTED] = 'your_github_token'

# Инициализация клиентов
g = Github(GITHUB_[REDACTED])

def clean_content(content: str) -> str:
    # Удаляем потенциально опасные шаблоны (это только пример, для реального использования вам нужно будет адаптировать его)
    sensitive_patterns = ["[REDACTED]", "[REDACTED]", "[REDACTED]"]
    for pattern in sensitive_patterns:
        content = content.replace(pattern, "[REDACTED]")
    return content

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('Привет! Отправь мне файл, и я загружу его на GitHub.')

async def handle_file(update: Update, context: CallbackContext):
    document = update.message.document
    file_name = document.file_name

    # Скачивание файла
    file = await context.bot.get_file(document.file_id)
    file_path = file_name  # Сохраним файл в текущей директории с его оригинальным именем
    await file.download_to_drive(file_path)

    # Создание репозитория на GitHub
    user = g.get_user()
    repo_name = file_name
    existing_repo = None

    try:
        existing_repo = user.get_repo(repo_name)
    except:
        pass  # Если репозитория нет, исключение будет проигнорировано

    # Если репозиторий существует, добавляем суффикс
    if existing_repo:
        repo_name += "-1"
        counter = 1
        while True:
            try:
                user.get_repo(repo_name)
                counter += 1
                repo_name = f"{file_name}-{counter}"
            except:
                break

    repo = user.create_repo(repo_name)

    # Загрузка файла в репозиторий с указанием кодировки
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        cleaned_content = clean_content(content)
        try:
            repo.create_file(file_name, "Initial commit", cleaned_content)
        except Exception as e:
            await update.message.reply_text(f'Ошибка при загрузке файла: {str(e)}')
            return

    await update.message.reply_text(f'Файл загружен в репозиторий: https://github.com/{user.login}/{repo_name}')

def main():
    # Создание приложения
    application = Application.builder().token(TELEGRAM_[REDACTED]).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))

    # Запуск бота
    application.run_polling()

if __name__ == '__main__':
    main()