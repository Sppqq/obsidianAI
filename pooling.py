import os
import time
import json

# Загрузка конфига для получения списка пользователей
config = json.load(open(f'{os.getcwd()}/config.json', 'r', encoding='utf-8'))
USERS = {
    config['user1']['chat_id']: config['user1'],
    config['user2']['chat_id']: config['user2']
}

while True:
    for chat_id in USERS.keys():
        try:
            with open(f'{os.getcwd()}/last_{chat_id}.txt', 'r') as f:
                try:
                    last = int(f.read())
                except:
                    with open(f'{os.getcwd()}/last_{chat_id}.txt', 'w') as f:
                        f.write('0')
                    last = 0
                
                if last == 1:
                    with open(f'{os.getcwd()}/last_{chat_id}.txt', 'w') as f:
                        f.write('0')
                    os.system(f'python {os.getcwd()}/Upload.py {chat_id}')
                if last == 0:
                    time.sleep(1)
        except Exception as e:
            print(f"Error processing user {chat_id}: {e}")
            continue
    time.sleep(1)