from dropbox_ import DropboxUploader
import os
import sys
import json

# Получаем chat_id из аргументов командной строки
chat_id = sys.argv[1]

# Загружаем конфиг
config = json.load(open(f'{os.getcwd()}/config.json', 'r', encoding='utf-8'))
USERS = {
    config['user1']['chat_id']: config['user1'],
    config['user2']['chat_id']: config['user2']
}

# Получаем конфиг пользователя
user_config = USERS[int(chat_id)]

# Инициализируем Dropbox с настройками пользователя
dbx = DropboxUploader(
    app_key=user_config['db_app_key'],
    app_secret=user_config['db_app_secret'],
    redirect_uri=user_config['db_redirect_uri'],
    chat_id=chat_id
)

def cleanup_files(path='/'):
    """Removes downloaded files after processing."""
    for filename in os.listdir(os.getcwd()+path):
        if filename.startswith(str(chat_id)) and filename.endswith(('.jpg', '.jpeg', '.png', '.webm', '.mp4', '.md', '.mp3', '.webp')):
            os.remove(os.getcwd()+path+filename)
            print(f'Файл {filename} удален')

# Загрузка файлов
for i in os.listdir():
    try:
        if i.startswith(str(chat_id)):  # Проверяем префикс chat_id
            clean_filename = i[len(str(chat_id)) + 1:]  # Удаляем chat_id_ из имени файла
            if i.endswith('.md'):
                dbx.upload_file(f'{i}', f'/Приложения/remotely-save/Obsidian Vault/{clean_filename}')
                print(f'Файл {clean_filename} успешно загружен')
                with open(f'{os.getcwd()}/send_{chat_id}.txt', 'w', encoding='utf-8') as f:
                    f.write(f'Файл {clean_filename} успешно загружен')
                os.remove(i)
            elif i.endswith(('.jpg', '.jpeg', '.png', '.webm', '.mp4', '.md', '.mp3', '.webp')):
                dbx.upload_file(f'{i}', f'/Приложения/remotely-save/Obsidian Vault/Telegram/files/{clean_filename}')
                print(f'Файл {clean_filename} успешно загружен')
                os.remove(i)
    except Exception as e:
        if 'Unauthorized' in str(e):
            try:
                os.remove(f'{os.getcwd()}/session_{chat_id}.pickle')
                print('Вы не авторизованы. Пожалуйста, авторизуйтесь.')
                with open(f'{os.getcwd()}/last_{chat_id}.txt', 'w', encoding='utf-8') as f:
                    f.write('1')
            except:
                pass
        else:
            print(f"Ошибка для пользователя {chat_id}: {e}")