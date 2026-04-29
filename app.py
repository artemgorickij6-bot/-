import os
import json
import time
import threading
import asyncio
import logging
import requests
from flask import Flask, request, render_template, redirect, session
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- КОНФИГУРАЦИЯ ---
TOKEN = "8505135235:AAEaGciF3qKt6hHTbwZrOPkRgQSOIwjjVvk"
ADMIN_ID = 8670014042
ADMIN_PASSWORD = "toniks123"

DATA_DIR = os.path.join(os.getcwd(), "TONIKS_BASE")
FILES = {"comments": "comments.json", "orders": "orders.json", "settings": "settings.json"}

# --- ИНИЦИАЛИЗАЦИЯ ---
app = Flask(__name__, template_folder='.')
app.secret_key = "toniks-secret"
bot = Bot(token=TOKEN)
dp = Dispatcher()

def ensure_base_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    for fname in FILES.values():
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

# --- САМОПИНГ ---
def toniks_ping():
    time.sleep(30)
    url = "https://toniks.onrender.com"
    while True:
        try:
            requests.get(url, timeout=10)
        except:
            pass
        time.sleep(600)

# --- FLASK ROUTES ---
@app.route("/")
def home():
    return render_template("Web.html")


# --- BOT HANDLERS ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(
        text="🚀 Мои проекты", 
        web_app=WebAppInfo(url="https://tg-ja7w.onrender.com")) 
    )
    builder.row(InlineKeyboardButton(
        text="📝 Оставить жалобу", 
        callback_data="write_complaint")
    )
    builder.row(InlineKeyboardButton(
        text="⭐ Поддержать звездами", 
        callback_data="donate_stars")
    )
    await message.answer(
        f"Привет, {message.from_user.first_name}!\n\n"
        "Я помогу тебе связаться с разработчиком или посмотреть его проекты.",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "write_complaint")
async def ask_complaint(callback: types.CallbackQuery):
    await callback.message.answer("Пожалуйста, напиши текст жалобы или отзыва. Я сразу передам его владельцу.")
    await callback.answer()

@dp.callback_query(F.data == "donate_stars")
async def donate_stars(callback: types.CallbackQuery):
    await callback.message.answer("Функция оплаты звездами будет доступна в следующем обновлении! 🌟")
    await callback.answer()

@dp.message(F.text, ~F.text.startswith('/'))
async def forward_complaint(message: types.Message):
    try:
        await bot.send_message(
            ADMIN_ID, 
            f"📩 **НОВАЯ ЖАЛОБА**\n\n"
            f"От: @{message.from_user.username or 'без_ника'}\n"
            f"ID: `{message.from_user.id}`\n"
            f"Текст: {message.text}"
        )
        await message.answer("✅ Спасибо! Твое сообщение отправлено разработчику.")
    except Exception as e:
        await message.answer("Ошибка при отправке.")
        print(f"Ошибка: {e}")

# --- ЗАПУСК ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def main():
    logging.basicConfig(level=logging.INFO)
    ensure_base_exists()
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=toniks_ping, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())









