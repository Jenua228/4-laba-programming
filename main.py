from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from aiogram.handlers import MessageHandler
import requests
import logging
from aiogram import *
from aiogram.fsm.context import FSMContext
from aiogram import Bot, types, Dispatcher, Router
from aiogram.filters import CommandStart, Command, CommandObject
from aiogram.enums import ParseMode
import sys
import asyncio
from aiogram import F
from os import getenv
from aiogram.types import Message
from aiogram.utils.markdown import hbold

TOKEN = "6631264819:AAFpl9lbitMJxkRLw1-cGK46zHT4T9lC9rc"
bot = Bot(token=TOKEN)
dp = Dispatcher()
url = "https://api.spoonacular.com/recipes/findByIngredients?apiKey=a9d06e678b5a4d869b8d064b937b16d0"

@dp.message(CommandStart())
async def start(msg: types.Message):
    await bot.send_message(msg.chat.id, '<b>Hello!</b> I`m the cook bot. I can help you to find the recipe with you favourite ingredients\n<b>Enter the "/args" and your ingredients to see the recipe</b>', parse_mode=ParseMode.HTML)

@dp.message(F.text, Command("args"))
async def args(msg: types.Message, command: CommandObject, state: FSMContext):
    ingredients = {'ingredients': command.args, 'number': 5, 'ranking': 2, 'ignorePantry': False}
    response = requests.get(url, params=ingredients)
    await state.set_data(data=response.json())
    data = response.json()
    if not data:
        text = "Nothing found in API. Try again"
    else:
        text = '<b>You can cook the:</b>\n' + '\n'.join([d['title'] for d in data]) +'\n<b>Click the button with the recipe you like to see the recipe</b>'

    kb = [
        [types.KeyboardButton(text=d['title']) for d in data]
    ]
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True, one_time_keyboard=True
    )
    await bot.send_message(msg.chat.id, text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

@dp.message(F.text)
async def message(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    text = ""
    result = []
    photo = None

    if not data:
        text = 'You should type the /args first'
    elif msg.text.upper() not in [d['title'].upper() for d in data]:
        text = 'You should pick the recipe from the list'
    else:
        for d in data:
            if msg.text.upper() == d["title"].upper():
                for t in d["usedIngredients"]:
                    result.append(
                        t["original"]
                    )
                for t in d["missedIngredients"]:
                    result.append(
                        t["original"]
                    )
                photo = d["image"]
                text = "<b>The recipe:</b>\n" + '\n'.join(result)
                print(data)
    await bot.send_message(msg.chat.id, text, parse_mode=ParseMode.HTML)
    if photo is not None:
        await bot.send_photo(msg.chat.id, photo=photo)

async def main() -> None:
    # Initialize Bot instance with a default parse mode which will be passed to all API calls
    bot = Bot(TOKEN, parse_mode=ParseMode.HTML)
    # And the run events dispatching
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

