import requests
import json
import os
import pickle
import time

class DropboxUploader:
    """Класс для работы с Dropbox API."""
    
    def __init__(self, app_key, app_secret, redirect_uri, chat_id, session_file=None):
        """Инициализирует объект DropboxUploader.

        Args:
            app_key: Ключ приложения Dropbox
            app_secret: Секрет приложения Dropbox
            redirect_uri: URI перенаправления
            chat_id: ID пользователя в Telegram
            session_file: Имя файла для сохранения данных сессии
        """
        self.AUTH_URL = 'https://www.dropbox.com/oauth2/authorize'
        self.TOKEN_URL = 'https://api.dropboxapi.com/oauth2/token'
        self.APP_KEY = app_key
        self.APP_SECRET = app_secret
        self.REDIRECT_URI = redirect_uri
        self.chat_id = chat_id
        self.session_file = session_file or f'session_{chat_id}.pickle'
        self.session = self.authorize()

    def authorize(self):
        """Авторизуется в Dropbox и возвращает сессию."""
        
        if os.path.exists(self.session_file):
            with open(self.session_file, 'rb') as f:
                return pickle.load(f)

        auth_url = f'{self.AUTH_URL}?client_id={self.APP_KEY}&response_type=code&redirect_uri={self.REDIRECT_URI}'
        
        with open(f'send_{self.chat_id}.txt', 'w', encoding='utf-8') as f:
            f.write(auth_url)

        code = None
        while code is None:
            if os.path.exists(f'code.txt'):
                code = open('code.txt', 'r', encoding='utf-8').read()
                with open(f'send_{self.chat_id}.txt', 'w', encoding='utf-8') as f:
                    f.write('code')
                os.remove('code.txt')
            elif len(requests.get(f'https://api.sppq.site/api/dropbox/get_code').text) == 43:
                code = requests.get(f'https://api.sppq.site/api/dropbox/get_code').text
                requests.get(f'https://api.sppq.site/api/dropbox/clear_code')
            else:
                try:
                    with open(f're_{self.chat_id}.txt', 'r', encoding='utf-8') as f:
                        code = f.read()

                    if len(code) != 43:
                        code = None
                        time.sleep(5)
                except:
                    time.sleep(5)
                    continue

        with open(f're_{self.chat_id}.txt', 'w', encoding='utf-8') as f:
            f.write('')

        data = {
            'code': code,
            'grant_type': 'authorization_code',
            'client_id': self.APP_KEY,
            'client_secret': self.APP_SECRET,
            'redirect_uri': self.REDIRECT_URI,
        }
        
        response = requests.post(self.TOKEN_URL, data=data)
        response.raise_for_status()
        access_token = response.json()['access_token']

        session = requests.Session()
        session.headers.update({'Authorization': f'Bearer {access_token}'})

        with open(self.session_file, 'wb') as f:
            pickle.dump(session, f)

        return session

    def upload_file(self, local_path, dropbox_path):
        """Загружает файл в Dropbox.

        Args:
            local_path: Путь к локальному файлу
            dropbox_path: Путь к файлу в Dropbox
        """
        url = 'https://content.dropboxapi.com/2/files/upload'
        headers = {
            **self.session.headers,
            'Dropbox-API-Arg': json.dumps({'path': dropbox_path, 'mode': 'add'}),
            'Content-Type': 'application/octet-stream'
        }
        
        with open(local_path, 'rb') as f:
            response = self.session.post(url, headers=headers, data=f)
        response.raise_for_status()
        return True