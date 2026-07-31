import os
import json
import asyncio
from http.server import BaseHTTPRequestHandler
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv('BOT_TOKEN')
SMARTLINK = os.getenv('SMARTLINK_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

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

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🇺🇸 English", callback_data="lang_en"),
         InlineKeyboardButton(text="🇪🇸 Español", callback_data="lang_es")]
    ])
    await message.answer("Please select your language / Por favor elige tu idioma:", reply_markup=kb)

@dp.callback_query(F.data.startswith("lang_"))
async def process_lang(callback: types.CallbackQuery):
    lang = callback.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['btn_start'], callback_data=f"step1_{lang}")]
    ])
    await callback.answer()
    await callback.message.answer(t['welcome'], parse_mode="Markdown", reply_markup=kb)

@dp.callback_query(F.data.startswith("step1_"))
async def process_step1(callback: types.CallbackQuery):
    lang = callback.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="18-24", callback_data=f"step2_{lang}"),
         InlineKeyboardButton(text="25-34", callback_data=f"step2_{lang}"),
         InlineKeyboardButton(text="35+", callback_data=f"step2_{lang}")]
    ])
    await callback.answer()
    await callback.message.answer(t['q_age'], reply_markup=kb)

@dp.callback_query(F.data.startswith("step2_"))
async def process_step2(callback: types.CallbackQuery):
    lang = callback.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    buttons = [[InlineKeyboardButton(text=goal, callback_data=f"final_{lang}")] for goal in t['goals']]
    kb = InlineKeyboardMarkup(inline_keyboard=buttons)
    await callback.answer()
    await callback.message.answer(t['q_goal'], reply_markup=kb)

@dp.callback_query(F.data.startswith("final_"))
async def process_final(callback: types.CallbackQuery):
    lang = callback.data.split('_')[1]
    t = TEXTS.get(lang, TEXTS['en'])
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t['btn_link'], url=SMARTLINK)]
    ])
    await callback.answer()
    await callback.message.answer(t['searching'], parse_mode="Markdown", reply_markup=kb)

# Обработчик запросов Vercel Serverless
class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        update_dict = json.loads(post_data.decode('utf-8'))
        
        update = types.Update(**update_dict)
        asyncio.run(dp.feed_update(bot, update))
        
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'ok')
