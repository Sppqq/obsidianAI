import os
import time
import json

# Определяем путь к директории скрипта
script_dir = os.path.dirname(os.path.abspath(__file__))

# Загрузка конфига для получения списка пользователей
config = json.load(open(f'{script_dir}/config.json', 'r', encoding='utf-8'))
USERS = {
    config['user1']['chat_id']: config['user1'],
    config['user2']['chat_id']: config['user2']
}

# Путь к Python в виртуальном окружении
venv_python = os.path.join(script_dir, "venv", "bin", "python3")
if not os.path.exists(venv_python):
    venv_python = os.path.join(script_dir, "venv", "bin", "python")
if not os.path.exists(venv_python):
    print(f"Не найден Python в виртуальном окружении по пути {venv_python}")
    venv_python = "/usr/bin/python3"

while True:
    for chat_id in USERS.keys():
        try:
            with open(f'{script_dir}/last_{chat_id}.txt', 'r') as f:
                try:
                    last = int(f.read())
                except:
                    with open(f'{script_dir}/last_{chat_id}.txt', 'w') as f:
                        f.write('0')
                    last = 0
                
                if last == 1:
                    with open(f'{script_dir}/last_{chat_id}.txt', 'w') as f:
                        f.write('0')
                    os.system(f'{venv_python} {script_dir}/Upload.py {chat_id}')
                if last == 0:
                    time.sleep(1)
        except Exception as e:
            print(f"Error processing user {chat_id}: {e}")
            continue
    time.sleep(1)