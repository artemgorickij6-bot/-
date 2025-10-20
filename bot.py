import time
import requests

def toniks_bot(url):
    while True:
        try:
            response = requests.get(url)
            print(f"[BOT] Перешёл на {url} — статус: {response.status_code}")
        except Exception as e:
            print(f"[BOT] Ошибка: {e}")
        time.sleep(20)
toniks_bot(https://toniks.onrender.com)
print('nice BOT Actived')
