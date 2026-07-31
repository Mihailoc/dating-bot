import os
import json
import urllib.request
from http.server import BaseHTTPRequestHandler

# Токен из BotFather
API_TOKEN = os.getenv('BOT_TOKEN', '8923328373:AAGUNQWKNU5XJ36gSvk7HfOfLSJqaLJcHws').strip()
SMARTLINK = os.getenv('SMARTLINK_URL', '').strip()

TEXTS = {
    'en': {
        'welcome': "Hey there! 👋\nWelcome to **MatchFinder**.\n\nLet’s find real local guys near you in under 30 seconds.\n🔒 *100% Anonymous & Free*",
        'btn_start': "Start Matching 🚀",
        'q_age': "Step 1/2: How old are you?",
        'q_goal': "Step 2/2: What are you looking for today?",
        'goals': ["Serious Relationship 🤍", "Casual / Fun 🔥", "New Friends ☕️"],
        'searching': "⏳ *Searching verified profiles in your area...*\n\n**Done!** We found **14 active matches** near you right now. 🥂\n\nTap below to complete your free registration:",
        'btn_link': "👉 VIEW LOCAL MATCHES"
    },
    'es': {
        'welcome': "¡Hola! 👋\nBienvenido a **MatchFinder**.\n\nEncuentra chicos cerca de ti en menos de 30 segundos.\n🔒 *100% Anónimo y Gratis*",
        'btn_start': "Empezar Buscar 🚀",
        'q_age': "Paso 1/2: ¿Cuántos años tienes?",
        'q_goal': "Paso 2/2: ¿Qué estás buscando hoy?",
        'goals': ["Relación seria 🤍", "Algo casual / Diversión 🔥", "Nuevos amigos ☕️"],
        'searching': "⏳ *Buscando perfiles verificados cerca de ti...*\n\n**¡Listo!** Encontramos **14 perfiles activos** cerca de ti. 🥂\n\nToca abajo para completar tu registro gratis:",
        'btn_link': "👉 VER PERFILES CERCANOS"
    }
}

def send_tg(method, payload):
    url = f"https://api.telegram.org/bot{API_TOKEN}/{method}"
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            return response.read()
    except Exception as e:
        print(f"Error TG request ({method}): {e}")

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            
            if post_data:
                update = json.loads(post_data.decode('utf-8'))
                
                # 1. Команда /start
                if 'message' in update:
                    msg = update['message']
                    chat_id = msg['chat']['id']
                    text = msg.get('text', '')
                    
                    if text.startswith('/start'):
                        payload = {
                            'chat_id': chat_id,
                            'text': "Please select your language / Por favor elige tu idioma:",
                            'reply_markup': {
                                'inline_keyboard': [
                                    [
                                        {'text': "🇺🇸 English", 'callback_data': "lang_en"},
                                        {'text': "🇪🇸 Español", 'callback_data': "lang_es"}
                                    ]
                                ]
                            }
                        }
                        send_tg('sendMessage', payload)

                # 2. Обработка кнопок
                elif 'callback_query' in update:
                    cb = update['callback_query']
                    cb_id = cb['id']
                    chat_id = cb['message']['chat']['id']
                    data = cb.get('data', '')

                    send_tg('answerCallbackQuery', {'callback_query_id': cb_id})

                    if data.startswith('lang_'):
                        lang = data.split('_')[1]
                        t = TEXTS.get(lang, TEXTS['en'])
                        payload = {
                            'chat_id': chat_id,
                            'text': t['welcome'],
                            'parse_mode': 'Markdown',
                            'reply_markup': {
                                'inline_keyboard': [[{'text': t['btn_start'], 'callback_data': f"step1_{lang}"}]]
                            }
                        }
                        send_tg('sendMessage', payload)

                    elif data.startswith('step1_'):
                        lang = data.split('_')[1]
                        t = TEXTS.get(lang, TEXTS['en'])
                        payload = {
                            'chat_id': chat_id,
                            'text': t['q_age'],
                            'reply_markup': {
                                'inline_keyboard': [[
                                    {'text': "18-24", 'callback_data': f"step2_{lang}"},
                                    {'text': "25-34", 'callback_data': f"step2_{lang}"},
                                    {'text': "35+", 'callback_data': f"step2_{lang}"}
                                ]]
                            }
                        }
                        send_tg('sendMessage', payload)

                    elif data.startswith('step2_'):
                        lang = data.split('_')[1]
                        t = TEXTS.get(lang, TEXTS['en'])
                        buttons = [[{'text': goal, 'callback_data': f"final_{lang}"}] for goal in t['goals']]
                        payload = {
                            'chat_id': chat_id,
                            'text': t['q_goal'],
                            'reply_markup': {'inline_keyboard': buttons}
                        }
                        send_tg('sendMessage', payload)

                    elif data.startswith('final_'):
                        lang = data.split('_')[1]
                        t = TEXTS.get(lang, TEXTS['en'])
                        target_url = SMARTLINK if SMARTLINK else "https://google.com"
                        payload = {
                            'chat_id': chat_id,
                            'text': t['searching'],
                            'parse_mode': 'Markdown',
                            'reply_markup': {
                                'inline_keyboard': [[{'text': t['btn_link'], 'url': target_url}]]
                            }
                        }
                        send_tg('sendMessage', payload)

        except Exception as err:
            print(f"Server error: {err}")

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'ok')

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Bot Status: Active')
