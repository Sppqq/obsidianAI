import datetime
import os
import re
import subprocess
import json
import telebot
from telebot import types
import time

# Импорт AI класса
from AI import AI

files = ['last.txt', 'send.txt', 're.txt', '1.txt']

# Проверка и создание config.json
if not os.path.exists('config.json'):
    with open('config.json', 'w', encoding='utf-8') as f:
        h = {
            "user1": {
                "chat_id": 12345,
                "bot_token": "YOUR_BOT_TOKEN",
                "gemini_api": "YOUR_GEMINI_API",
                "gemini_model": "pro",
                "tags": ["#код", "#учёба", "#файлы", "#нейронка", "#прочее"],
                "db_app_key": "your-key",
                "db_app_secret": "your-secret",
                "db_redirect_uri": "http://localhost:8080",
                "proxy": {
                    "http": "http://vyWVVn:718sxT@94.131.54.206:9491",
                    "https": "http://vyWVVn:718sxT@94.131.54.206:9491"
                }
            },
            "user2": {
                "chat_id": 67890,
                "bot_token": "YOUR_BOT_TOKEN",
                "gemini_api": "YOUR_GEMINI_API",
                "gemini_model": "pro",
                "tags": ["#работа", "#заметки", "#файлы", "#важное", "#прочее"],
                "db_app_key": "your-key",
                "db_app_secret": "your-secret",
                "db_redirect_uri": "http://localhost:8080",
            }
        }
        json.dump(h, f, indent=4)
    print('Файл "config.json" создан, настройте его вручную.')
    exit()

# Загрузка конфига
config = json.load(open('config.json', 'r', encoding='utf-8'))
USERS = {
    config['user1']['chat_id']: config['user1'],
    config['user2']['chat_id']: config['user2']
}

# Инициализация бота
bot = telebot.TeleBot(config['user1']['bot_token'])

# Словарь для хранения last_message_id
last_messages = {
    config['user1']['chat_id']: None,
    config['user2']['chat_id']: None
}

# Создание необходимых файлов для каждого пользователя
for user_id in USERS.keys():
    for file in files:
        filename = f'{file.split(".")[0]}_{user_id}.txt'
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write('')

def html_to_markdown(html_text):
    """Конвертирует HTML в Markdown."""
    if not html_text:
        return ""
    html_text = html_text.replace('\n', '<br>')
    html_text = re.sub(r'<b>(.*?)</b>', r'**\1**', html_text)
    html_text = re.sub(r'<strong>(.*?)</strong>', r'**\1**', html_text)
    html_text = re.sub(r'<a href="(.*?)">(.*?)</a>', r'[\2](\1)', html_text)
    markdown_text = html_text.replace('<br>', '\n\n')
    markdown_text = re.sub(r'\]\s*\(', r'](', markdown_text)
    return markdown_text

def download_file(file_id, filename):
    """Скачивает файл из Telegram."""
    file_info = bot.get_file(file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    with open(filename, 'wb') as f:
        f.write(downloaded_file)

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        bot.reply_to(message, "У вас нет доступа к этому боту.")
        return
        
    user_config = USERS[chat_id]
    welcome_text = (
        f"👋 Добро пожаловать!\n\n"
        f"🏷 Ваши текущие теги:\n"
        f"{', '.join(user_config['tags'])}\n\n"
        f"Команды:\n"
        f"/tags - управление тегами\n"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(commands=['tags'])
def show_tags(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        return
    
    user_tags = USERS[chat_id]['tags']
    if not user_tags:
        bot.reply_to(message, "У вас пока нет тегов.")
        return
        
    current_tag_index = 0
    markup = types.InlineKeyboardMarkup()
    
    # Кнопки навигации и удаления
    nav_buttons = [
        types.InlineKeyboardButton("⬅️", callback_data=f"prev_{current_tag_index}"),
        types.InlineKeyboardButton("❌", callback_data=f"delete_{current_tag_index}"),
        types.InlineKeyboardButton("➡️", callback_data=f"next_{current_tag_index}")
    ]
    markup.row(*nav_buttons)
    
    # Кнопка добавления нового тега
    markup.row(types.InlineKeyboardButton("➕ Добавить тег", callback_data="add_tag"))
    
    bot.reply_to(message, f"Тег {current_tag_index + 1}/{len(user_tags)}:\n{user_tags[current_tag_index]}", 
                reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    chat_id = call.message.chat.id
    if chat_id not in USERS:
        return
        
    user_tags = USERS[chat_id]['tags']
    
    # Сначала проверяем специальные команды
    if call.data == "add_tag":
        msg = bot.edit_message_text(
            "Отправьте новый тег (с # или без):", 
            chat_id=chat_id, 
            message_id=call.message.message_id
        )
        bot.register_next_step_handler(msg, process_new_tag)
        return
    
    # Затем обрабатываем команды с индексами
    try:
        current_index = int(call.data.split('_')[1]) if '_' in call.data else 0
    except ValueError:
        current_index = 0
    
    if call.data.startswith("next"):
        current_index = (current_index + 1) % len(user_tags)
    elif call.data.startswith("prev"):
        current_index = (current_index - 1) % len(user_tags)
    elif call.data.startswith("delete"):
        tag_to_delete = user_tags[current_index]
        USERS[chat_id]['tags'].remove(tag_to_delete)
        save_config()
        if not user_tags:
            bot.edit_message_text(
                "Все теги удалены.", 
                chat_id=chat_id, 
                message_id=call.message.message_id
            )
            return
        current_index = min(current_index, len(user_tags) - 1)

    if user_tags:
        markup = types.InlineKeyboardMarkup()
        nav_buttons = [
            types.InlineKeyboardButton("⬅️", callback_data=f"prev_{current_index}"),
            types.InlineKeyboardButton("❌", callback_data=f"delete_{current_index}"),
            types.InlineKeyboardButton("➡️", callback_data=f"next_{current_index}")
        ]
        markup.row(*nav_buttons)
        markup.row(types.InlineKeyboardButton("➕ Добавить тег", callback_data="add_tag"))
        
        bot.edit_message_text(
            f"Тег {current_index + 1}/{len(user_tags)}:\n{user_tags[current_index]}", 
            chat_id=chat_id, 
            message_id=call.message.message_id,
            reply_markup=markup
        )

def process_new_tag(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        return
        
    new_tag = message.text
    if not new_tag.startswith('#'):
        new_tag = '#' + new_tag
        
    if new_tag in USERS[chat_id]['tags']:
        bot.reply_to(message, "Такой тег уже существует!")
        return
        
    USERS[chat_id]['tags'].append(new_tag)
    save_config()
    bot.reply_to(message, f"Тег {new_tag} успешно добавлен!")

def save_config():
    """Сохраняет текущую конфигурацию в файл."""
    config_data = {
        "user1": USERS[config['user1']['chat_id']],
        "user2": USERS[config['user2']['chat_id']]
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(config_data, f, indent=4, ensure_ascii=False)

@bot.message_handler(content_types=['text', 'photo', 'audio', 'video', 'document'])
def handle_messages(message):
    chat_id = message.chat.id
    if chat_id not in USERS:
        return
    
    user_config = USERS[chat_id]
    start_time = datetime.datetime.now()
    caption = None  # Инициализируем caption значением по умолчанию

    try:
        # Обработка текста сообщения
        if message.html_text:
            text = message.html_text
            caption = html_to_markdown(text)
            with open(f're_{chat_id}.txt', 'w', encoding='utf-8') as f:
                f.write(text)
            if len(text) == 43:
                bot.delete_message(chat_id, last_messages[chat_id])
                bot.delete_message(chat_id, message.message_id)
                return

        # Обработка медиафайлов с подписями
        if message.photo:
            file_id = message.photo[-1].file_id
            download_file(file_id, f'{chat_id}_{file_id}.jpg')
            caption = caption or message.html_caption
            if message.html_caption:
                caption = html_to_markdown(message.html_caption)
            print(f"Фото сохранено для пользователя {chat_id}!\n{caption}")
        if message.audio:
            file_id = message.audio.file_id
            download_file(file_id, f'{chat_id}_{file_id}.mp3')
            caption = caption or message.html_caption
            if message.html_caption:
                caption = html_to_markdown(message.html_caption)
            print(f"Аудио сохранено для пользователя {chat_id}!\n{caption}")
            
        if message.video:
            file_id = message.video.file_id
            download_file(file_id, f'{chat_id}_{file_id}.mp4')
            caption = caption or message.html_caption
            if message.html_caption:
                caption = html_to_markdown(message.html_caption)
            print(f"Видео сохранено для пользователя {chat_id}!\n{caption}")
            
        if message.document:
            file_id = message.document.file_id
            download_file(file_id, f'{chat_id}_{message.document.file_name}')
            caption = caption or message.html_caption
            if message.html_caption:
                caption = html_to_markdown(message.html_caption)
            print(f"Файл сохранен для пользователя {chat_id}!\n{caption}")

        if not caption:
            return

        # Сохранение текста
        with open(f'1_{chat_id}.txt', 'w', encoding='utf-8') as f:
            f.write(caption)

        bot.reply_to(message, "Заметка сохранена!")
        end_time_1 = datetime.datetime.now()

        # Обработка AI
        ai_instance = AI()
        ai_instance.config = user_config
        ai_instance.process_and_upload(ai=False)

        end_time_2 = datetime.datetime.now()
        
        with open(f'last_{chat_id}.txt', 'w', encoding='utf-8') as f:
            f.write('1')
        
        sent = bot.send_message(
            chat_id,
            f"Время выполнения: {end_time_1 - start_time} | {end_time_2 - start_time}"
        )
        last_messages[chat_id] = sent.message_id
        
        print(f'Готово для пользователя {chat_id}')

        # Обработка ответов на сообщения
        if message.reply_to_message and message.reply_to_message.message_id == last_messages[chat_id]:
            with open(f're_{chat_id}.txt', 'w', encoding='utf-8') as f:
                f.write(message.text)
            print(f"Reply получен и сохранен в re_{chat_id}.txt: {message.text}")

    except Exception as e:
        print(f"Произошла ошибка для пользователя {chat_id}: {e}")
        bot.reply_to(message, f"Произошла ошибка! {e}")

def check_send_file():
    """Проверяет send.txt каждые 5 секунд и отправляет содержимое."""
    while True:
        for chat_id in USERS.keys():
            try:
                filename = f'send_{chat_id}.txt'
                if os.path.exists(filename):
                    with open(filename, 'r', encoding='utf-8') as f:
                        message_text = f.read().strip()
                    if message_text:
                        if message_text == 'code':
                            bot.delete_message(chat_id, last_messages[chat_id])
                            bot.send_message(chat_id, 'Код получен!')
                        else:
                            sent = bot.send_message(chat_id, message_text)
                            last_messages[chat_id] = sent.message_id
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write("")
            except Exception as e:
                print(f"Error checking send file for user {chat_id}: {e}")
        time.sleep(1)

subprocess.Popen(['python', 'pooling.py'])
import threading
threading.Thread(target=check_send_file, daemon=True).start()

while True:
    try:
        print('Запуск обсидиана...')  
        bot.polling(none_stop=True)
    except:
        pass