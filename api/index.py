import os
import json
from asyncio import run
from aiogram import Bot, Dispatcher, types

API_TOKEN = os.getenv('BOT_TOKEN')
SMARTLINK = os.getenv('SMARTLINK_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Мультиязычные тексты
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

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        types.InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es")
    )
    await message.answer("Please select your language / Por favor elige tu idioma:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def process_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(t['btn_start'], callback_data=f"step1_{lang}"))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t['welcome'], parse_mode="Markdown", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('step1_'))
async def process_step1(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        types.InlineKeyboardButton("18-24", callback_data=f"step2_{lang}"),
        types.InlineKeyboardButton("25-34", callback_data=f"step2_{lang}"),
        types.InlineKeyboardButton("35+", callback_data=f"step2_{lang}")
    )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t['q_age'], reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('step2_'))
async def process_step2(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    for goal in t['goals']:
        keyboard.add(types.InlineKeyboardButton(goal, callback_data=f"final_{lang}"))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t['q_goal'], reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('final_'))
async def process_final(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(t['btn_link'], url=SMARTLINK))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t['searching'], parse_mode="Markdown", reply_markup=keyboard)

# Точка входа для Vercel (Serverless)
from http.server import BaseHTTPRequestHandler

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update = types.Update.de_json(json.loads(post_data.decode('utf-8')))
        
        run(dp.process_update(update))
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
