import os
import requests
import json
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

class AI:
    def __init__(self):
        self.config = None  # Будет установлено позже из main.py
        self.proxies = None  # Будет установлено при установке конфига

    def send_request(self, prompt, d=bool):
        if not self.config:
            raise Exception("Config not set")

        # Установка прокси из конфига
        if 'proxy' in self.config:
            self.proxies = self.config['proxy']
            os.environ['HTTPS_PROXY'] = self.config['proxy']['https']
            os.environ['HTTP_PROXY'] = self.config['proxy']['http']

        genai.configure(api_key=self.config['gemini_api'])

        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 8192,
            "response_schema": { 
                "type": "OBJECT",
                "enum": [],
                "required": ["Заголовок заметки", "Заметка", "Комментарий", "Изменения", "Теги"],
                "properties": {
                    "Заголовок заметки": {"type": "STRING"},
                    "Заметка": {"type": "STRING"},
                    "Комментарий": {"type": "STRING"},
                    "Изменения": {"type": "STRING"},
                    "Теги": {"type": "STRING"},
                }
            },
            "response_mime_type": "application/json",
        }

        safety_settings = {
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
        }

        system_instruction = (
            f"Цель: Удалить всю воду и убрать НЕНУЖНЫЕ ссылки (например на телеграмм каналы)"
            f"Заголовок должен быть очень кратким 1-3 слова и НЕ используй теги в заголовке "
            f"ВЕСЬ ТЕКСТ (!) должен быть в markdown "
            f"и что бы красиво выглядело и пожалуйста выделяй важные слова жирным шрифтом, "
            f"НО (!) не делай жирный заголовок НИКОГДА, "
            f"(если будут ссылки типа 'тут'(или подобные) и ссылка, сделатй что бы был кликабельный текст и тд и вёл на правльный сайт). "
            f"сделай так что бы заметка была более читабельной благодаря markdown переносам строк (только \\n) и тд "
            f"Заголовок должен быть коротким и понятным, а заметка информативной. "
            f"Иногда добавляй эмодзи что бы было лучше выглядело "
            f"ставь подходящие хэштеги, вот список:{self.config['tags']} "
            f"НЕ ЗАБЫВАЙ вставлять РАБОЧИЕ ссылки НА САЙТЫ "
            f"ОБЯЗАТЕЛЬНО (!) выбери хэштеги "
            f"НЕ ПРИДУМЫВАЙ САМ ХЭШТЕГИ "
        )
        print(prompt)
        request_data = {
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": 'system_instruction: ' + system_instruction + '\n' + 'prompt: ' + prompt
                        }
                    ]
                }
            ],
            "generationConfig": generation_config,
        }

        request_json = json.dumps(request_data)
        endpoint = f"https://generativelanguage.googleapis.com/v1beta/models/{self.config['gemini_model']}:generateContent?key={self.config['gemini_api']}"
        headers = {'Content-Type': 'application/json'}

        response = requests.post(
            endpoint, 
            headers=headers, 
            data=request_json,
            proxies=self.proxies if self.proxies else None,
            verify=False if self.proxies else True
        )

        if response.status_code == 200:
            return json.loads(response.text)['candidates'][0]['content']['parts'][0]['text']
        else:
            raise Exception(f"Error: {response.status_code} - {response.text}")

    def process_and_upload(self, ai=bool):
        if not self.config:
            raise Exception("Config not set")

        chat_id = self.config['chat_id']
        
        try:
            # Читаем из файла с учетом chat_id
            with open(f'1_{chat_id}.txt', 'r', encoding='utf-8') as file:
                input_text = file.read()
        except FileNotFoundError:
            raise Exception(f"File '1_{chat_id}.txt' not found.")

        try:
            for i in range(5):
                try:
                    print(f'Попытка {i+1}')
                    processed_text = self.send_request(input_text, d=True)
                    data = json.loads(processed_text)
                    break
                except Exception as e:
                    print(e)
                    data = None
                    pass
            if data is None:
                raise Exception("Failed to process with Gemini")

            data["Заголовок заметки"] = data["Заголовок заметки"].replace(":", "-").replace("/", "-")
            filename = f'{chat_id}_{data["Заголовок заметки"]}.md'

            # Сохраняем файл с учетом chat_id
            with open(filename, 'w', encoding='utf-8') as file:
                tags = data["Теги"].split()
                file.write(data['Заметка'] + '\n\n' + 'Теги: ' + (' '.join(tags)).replace('[', '').replace(']', '').replace("'", '').replace('"', ''))

            # Обработка медиафайлов
            files = [
                f for f in os.listdir()
                if os.path.isfile(os.path.join(f)) and 
                f.startswith(str(chat_id)) and  # Проверяем префикс chat_id
                os.path.splitext(f)[1].lower() in {'.jpg', '.jpeg', '.png', '.webm', '.mp4'}
            ]

            with open(filename, 'r', encoding='utf-8') as f:
                data["Заметка"] = f.read()

            for i in files:
                try:
                    clean_filename = i[len(str(chat_id)) + 1:]  # Удаляем chat_id_ из имени файла
                    data["Заметка"] = f'![[{clean_filename}]]\n\n' + data["Заметка"]
                except Exception as e:
                    print(f"Error processing file {i}: {e}")
                    pass

            with open(filename, 'w', encoding='utf-8') as f:
                f.write(data["Заметка"])

        except Exception as e:
            raise Exception(f"An error occurred: {e}")
