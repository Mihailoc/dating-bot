import os
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Забираем токен из настроек сервера для безопасности
API_TOKEN = os.getenv('BOT_TOKEN')
SMARTLINK = os.getenv('SMARTLINK_URL')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Start Matching 🚀", callback_data="step1"))
    await message.answer(
        "Hey there! 👋\nWelcome to **MatchFinder US**.\n\n"
        "Let’s find real local guys near you in under 30 seconds.\n"
        "🔒 *100% Anonymous & Free*", 
        parse_mode="Markdown", 
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == 'step1')
async def process_step1(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=3)
    keyboard.add(
        InlineKeyboardButton("18-24", callback_data="step2"),
        InlineKeyboardButton("25-34", callback_data="step2"),
        InlineKeyboardButton("35+", callback_data="step2")
    )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Step 1/2: How old are you?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'step2')
async def process_step2(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("Serious Relationship 🤍", callback_data="final"),
        InlineKeyboardButton("Casual / Fun 🔥", callback_data="final"),
        InlineKeyboardButton("New Friends ☕️", callback_data="final")
    )
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Step 2/2: What are you looking for today?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'final')
async def process_final(callback_query: types.CallbackQuery):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("👉 VIEW LOCAL MATCHES", url=SMARTLINK))
    
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(
        callback_query.from_user.id, 
        "⏳ *Searching verified profiles in your area...*\n\n"
        "**Done!** We found **14 active matches** near you right now. 🥂\n\n"
        "Tap the button below to complete your free registration:", 
        parse_mode="Markdown",
        reply_markup=keyboard
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
