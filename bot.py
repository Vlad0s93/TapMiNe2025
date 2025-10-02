import json
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio

TOKEN = "8451357175:AAEpPLysIpO4m2LmPNRvyxs7_jRAYsfiBhU"
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

ACCOUNTS_FILE = "accounts.json"

# Завантаження/збереження акаунтів
def load_accounts():
    try:
        with open(ACCOUNTS_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_accounts(accounts):
    with open(ACCOUNTS_FILE, "w") as f:
        json.dump(accounts, f)

accounts = load_accounts()

def ensure_account(user_id):
    if str(user_id) not in accounts:
        accounts[str(user_id)] = {"balance": 0.0}
        save_accounts(accounts)
    return accounts[str(user_id)]

# Старт
@dp.message(Command("start"))
async def start(message: types.Message):
    ensure_account(message.from_user.id)
    kb = InlineKeyboardBuilder()
    kb.button(text="🎮 Грати (тапалки)", web_app=WebAppInfo(url="https://YOUR_DOMAIN/tap_game.html"))
    await message.answer("Привіт! Натисни кнопку, щоб заробити монети.", reply_markup=kb.as_markup())

# Обробка результату гри
@dp.message(F.content_type == "web_app_data")
async def game_result(message: types.Message):
    data = json.loads(message.web_app_data.data)
    acc = ensure_account(message.from_user.id)

    if "taps" in data:
        taps = data["taps"]
        earned = round(taps * 1.5, 2)
        acc["balance"] += earned
        save_accounts(accounts)
        await message.answer(f"🎉 Гра завершена! Ти заробив {earned} монет.\nБаланс: {acc['balance']:.2f}")

    if "withdraw" in data:
        await message.answer(f"💰 Вивід монет запитано! Поточний баланс: {acc['balance']:.2f}\nАдміністратор обробить вивід вручну.")

# Баланс
@dp.message(Command("balance"))
async def balance(message: types.Message):
    acc = ensure_account(message.from_user.id)
    await message.answer(f"💰 Твій баланс: {acc['balance']:.2f} монет")

# Запуск бота
if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)

    asyncio.run(dp.start_polling(bot))
