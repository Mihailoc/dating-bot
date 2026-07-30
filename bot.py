import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = os.getenv('BOT_TOKEN')
SMARTLINK = os.getenv('SMARTLINK_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Словарь со всеми текстами на разных языках
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
    },
    'de': {
        'welcome': "Hallo! 👋\nWillkommen bei **MatchFinder**.\n\nFinde Männer in deiner Nähe in unter 30 Sekunden.\n🔒 *100% Anonym & Kostenlos*",
        'btn_start': "Suche starten 🚀",
        'q_age': "Schritt 1/2: Wie alt bist du?",
        'q_goal': "Schritt 2/2: Wonach suchst du heute?",
        'goals': ["Feste Beziehung 🤍", "Zwangloses / Spaß 🔥", "Neue Freunde ☕️"],
        'searching': "⏳ *Suche nach verifizierten Profilen in deiner Nähe...*\n\n**Fertig!** Wir haben **14 aktive Matches** gefunden. 🥂\n\nKlicke unten für deine kostenlose Registrierung:",
        'btn_link': "👉 MATCHES ANSEHEN"
    },
    'fr': {
        'welcome': "Salut ! 👋\nBienvenue sur **MatchFinder**.\n\nTrouve des mecs près de chez toi en moins de 30 secondes.\n🔒 *100% Anonyme & Gratuit*",
        'btn_start': "Commencer 🚀",
        'q_age': "Étape 1/2 : Quel âge as-tu ?",
        'q_goal': "Étape 2/2 : Que recherches-tu aujourd'hui ?",
        'goals': ["Relation sérieuse 🤍", "Plan sympa / Fun 🔥", "Nouveaux amis ☕️"],
        'searching': "⏳ *Recherche de profils vérifiés près de chez toi...*\n\n**Terminé !** Nous avons trouvé **14 profils actifs**. 🥂\n\nClique ci-dessous pour t'inscrire gratuitement :",
        'btn_link': "👉 VOIR LES PROFILS"
    }
}

# 1. СТАРТ: Выбор языка
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        InlineKeyboardButton("🇺🇸 English", callback_data="lang_en"),
        InlineKeyboardButton("🇪🇸 Español", callback_data="lang_es"),
        InlineKeyboardButton("🇩🇪 Deutsch", callback_data="lang_de"),
        InlineKeyboardButton("🇫🇷 Français", callback_data="lang_fr")
    )
    await message.answer("Please select your language / Por favor elige tu idioma:", reply_markup=keyboard)

# 2. ПРИВЕТСТВИЕ НА ВЫБРАННОМ ЯЗЫКЕ
@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def process_lang(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS[lang]
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(t['btn_start'], callback_data=f"step1_{lang}"))
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id, 
        t['welcome'], 
        parse_mode="Markdown", 
        reply_markup=keyboard
    )

# 3. ШАГ 1: ВОЗРАСТ
@dp.callback_query_handler(lambda c: c.data.startswith('step1_'))
async def process_step1(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS[lang]
    
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("18-24", callback_data=f"step2_{lang}"),
        InlineKeyboardButton("25-34", callback_data=f"step2_{lang}"),
        InlineKeyboardButton("35+", callback_data=f"step2_{lang}")
    )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t['q_age'], reply_markup=keyboard)

# 4. ШАГ 2: ЦЕЛЬ
@dp.callback_query_handler(lambda c: c.data.startswith('step2_'))
async def process_step2(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS[lang]
    
    keyboard = InlineKeyboardMarkup(row_width=1)
    for goal in t['goals']:
        keyboard.add(InlineKeyboardButton(goal, callback_data=f"final_{lang}"))
        
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, t['q_goal'], reply_markup=keyboard)

# 5. ФИНАЛ И ВЫДАЧА СМАРТЛИНКИ
@dp.callback_query_handler(lambda c: c.data.startswith('final_'))
async def process_final(callback_query: types.CallbackQuery):
    lang = callback_query.data.split('_')[1]
    t = TEXTS[lang]
    
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(t['btn_link'], url=SMARTLINK))
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id, 
        t['searching'], 
        parse_mode="Markdown",
        reply_markup=keyboard
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
