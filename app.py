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
ADMIN_PASSWORD = "1f"

# Путь для Render (лучше использовать /tmp для временных данных или сохранять в корне)
DATA_DIR = os.path.join(os.getcwd(), "TONIKS_BASE")
FILES = {
    "comments": "comments.json",
    "orders": "orders.json",
    "settings": "settings.json"
}

# --- ИНИЦИАЛИЗАЦИЯ FLASK ---
app = Flask(__name__, template_folder='')
app.secret_key = "toniks-secret"

# --- ИНИЦИАЛИЗАЦИЯ БОТА ---
bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- ФУНКЦИИ БАЗЫ ДАННЫХ ---
def ensure_base_exists():
    os.makedirs(DATA_DIR, exist_ok=True)
    for fname in FILES.values():
        path = os.path.join(DATA_DIR, fname)
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)

def load(name):
    ensure_base_exists()
    path = os.path.join(DATA_DIR, FILES[name])
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save(name, entry):
    data = load(name)
    data.append(entry)
    path = os.path.join(DATA_DIR, FILES[name])
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --- ЛОГИКА САМОПИНГА ---
def toniks_ping():
    # Ждем 30 секунд, чтобы сервер успел подняться
    time.sleep(30)
    url = "https://toniks.onrender.com"
    while True:
        try:
            res = requests.get(url)
            print(f"[PING] Статус: {res.status_code}")
        except Exception as e:
            print(f"[PING] Ошибка: {e}")
        time.sleep(600) # Пинг раз в 10 минут

# --- РОУТЫ FLASK ---
@app.route("/", methods=["GET", "POST"])
def home():
    role = request.args.get("role", "").strip().lower()
    comments = load("comments")
    orders = load("orders")
    
    if request.method == "POST":
        role = request.form.get("nickname", "").strip().lower()
        # Тут твоя логика обработки форм (сокращено для краткости)
        if "comment" in request.form:
            save("comments", {"nick": role, "text": request.form["comment"]})
        return redirect(f"/?role={role}")
    
    return render_template("Web.html", role=role, comments=comments, orders=orders)

# --- ЛОГИКА БОТА ---
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🚀 Сайт", web_app=WebAppInfo(url="https://toniks.onrender.com")))
    await message.answer(f"Привет, {message.from_user.first_name}!", reply_markup=builder.as_markup())

@dp.message()
async def forward_complaint(message: types.Message):
    if message.text:
        await bot.send_message(ADMIN_ID, f"📩 Новый текст: {message.text}")
        await message.answer("✅ Отправлено!")

# --- ЗАПУСК ВСЕГО ---
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

async def run_bot():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    ensure_base_exists()
    
    # 1. Запускаем Flask в отдельном потоке
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # 2. Запускаем пинг в отдельном потоке
    ping_thread = threading.Thread(target=toniks_ping, daemon=True)
    ping_thread.start()

    # 3. Основной поток отдаем под бота (asyncio)
    try:
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        print("Выключение...")








