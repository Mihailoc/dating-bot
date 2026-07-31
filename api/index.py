import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

API_TOKEN = os.getenv('BOT_TOKEN')

TEXTS = {
    'en': {
        'welcome': "Hi! 👋 This is a demo bot.\nSend /start again anytime to restart.",
        'echo': "You said: {}"
    },
    'ru': {
        'welcome': "Привет! 👋 Это демо-бот.\nОтправьте /start в любой момент, чтобы начать заново.",
        'echo': "Вы написали: {}"
    }
}

def send_tg(method, payload):
    url = f"https://api.telegram.org/bot{API_TOKEN}/{method}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            body = resp.read()
            print(f"TG API response: {body}")
    except Exception as e:
        # Важно: логируем ошибку, иначе в Vercel просто будет тишина
        print(f"Error TG request ({method}): {e}")


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length) if content_length else b''

            if post_data:
                update = json.loads(post_data.decode('utf-8'))
                print(f"Incoming update: {update}")  # видно в Vercel Function Logs

                if 'message' in update and 'text' in update['message']:
                    chat_id = update['message']['chat']['id']
                    text = update['message']['text']

                    if text.startswith('/start'):
                        send_tg('sendMessage', {
                            'chat_id': chat_id,
                            'text': TEXTS['ru']['welcome']
                        })
                    else:
                        send_tg('sendMessage', {
                            'chat_id': chat_id,
                            'text': TEXTS['ru']['echo'].format(text)
                        })
        except Exception as e:
            print(f"Handler error: {e}")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot is alive')
