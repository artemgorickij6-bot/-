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
app.secret_key = "toniks-secret857657655786875586756567"
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ФУНКЦИИ РАБОТЫ С БАЗОЙ ---
def ensure_base_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    for fname in FILES.values():
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f)

def load(name):
    ensure_base_exists()
    path = os.path.join(DATA_DIR, FILES[name])
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save(name, entry):
    data = load(name)
    data.append(entry)
    path = os.path.join(DATA_DIR, FILES[name])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

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
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        nick = request.form.get("nickname", "Аноним")
        if "comment" in request.form:
            save("comments", {"nick": nick, "text": request.form["comment"]})
        return redirect(f"/?role={nick}")
    
    return render_template("Web.html", 
                           comments=load("comments"), 
                           orders=load("orders"), 
                           settings=load("settings"), 
                           role=request.args.get("role", ""))

# --- BOT HANDLERS ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚀 Коменты", web_app=WebAppInfo(url="https://toniks.onrender.com")))
    builder.row(InlineKeyboardButton(text="📝 Заказать бота", callback_data="write_complaint"))
    
    await message.answer(
        f"Привет, {message.from_user.first_name}!\nЯ помогу тебе связаться с разработчиком.",
        reply_markup=builder.as_markup()
    )

@dp.callback_query(F.data == "write_complaint")
async def ask_complaint(callback: types.CallbackQuery):
    await callback.message.answer("Опишите бота, которого мы создадим для вас, и желаемую цену.")
    await callback.answer()

@dp.message(F.text, ~F.text.startswith('/'))
async def forward_complaint(message: types.Message):
    try:
        await bot.send_message(ADMIN_ID, f"📩 **ЗАКАЗ**\nОт: @{message.from_user.username}\nТекст: {message.text}")
        await message.answer("✅ Отправлено! Мы скоро свяжемся с вами.")
    except Exception as e:
        await message.answer("Ошибка отправки.")

# --- ЗАПУСК ---
def run_flask():
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 10000)))

async def main():
    logging.basicConfig(level=logging.INFO)
    ensure_base_exists()
    threading.Thread(target=run_flask, daemon=True).start()
    threading.Thread(target=toniks_ping, daemon=True).start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())










