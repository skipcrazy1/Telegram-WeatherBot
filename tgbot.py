import os
from dotenv import load_dotenv
import telebot
# from telebot import types
from telebot.types import BotCommand
import time
from utils import get_weather_daily


load_dotenv()

BOT_TOKEN = os.environ.get('BOT_TOKEN')
bot = telebot.TeleBot(BOT_TOKEN)


bot.set_my_commands([
    BotCommand("start", "Начать работу с ботом"),
    BotCommand("weather", "Узнать погоду"),
    BotCommand("help", "Показать меню и инструкцию")
])


@bot.message_handler(commands=['help', 'menu'])
def send_help(message):
    bot_info = (
        "🧭 *Меню команд:*\n\n"
        "/start — начать общение с ботом\n"
        "/weather — узнать погоду\n"
        "/help; /menu — показать это меню\n\n"
        "👉 В разделе погоды можно ввести *today* или *tomorrow*,\n"
        "а чтобы выйти — напиши *выход*.\n\n"
        "💡 Советы:\n"
        "- Можно вызывать /weather сколько угодно раз\n"
        "- После прогноза бот спросит день заново\n"
        "- Все старые сообщения очищаются автоматически"
    )
    bot.send_message(message.chat.id, bot_info, parse_mode="Markdown")


@bot.message_handler(commands=['weather'])
def start_weather(message):
    text = "Что хотите узнать?\nВыберите: *today* или *tomorrow*"
    sent = bot.send_message(message.chat.id, text)
    bot.register_next_step_handler(sent, process_day)


def process_day(message):
    day = message.text.lower().strip()
    if day in ['выход', 'exit', 'stop']:
        return bot.send_message(message.chat.id, "Окей, будем без погоды ")
    # координаты Москвы
    lat, lon = 55.7522, 37.6156
    data = get_weather_daily(lat, lon)
    if "error" in data:
        bot.send_message(message.chat.id, "Ошибка при загрузке данных")
        return
    current = data["current"]
    daily = data["daily"]
    text = (
        f"Погода сейчас:\n"
        f"Температура: {current['temperature']}°C\n"
        f"Ветер: {current['wind_speed']} м/с\n"
        f"Влажность: {current['humidity']}%\n"
        f"Код погоды: {current['weather_code']}\n\n"
        f"Прогноз на день:\n"
        f"Макс: {daily['temp_max']}°C\n"
        f"Мин: {daily['temp_min']}°C\n"
        f"Шанс дождя: {daily['rain_chance']}%\n"
    )
    bot.send_message(message.chat.id, text)


@bot.message_handler(commands=['start', 'hello'])
def send_welcome(message):
    text = (
        "🧭 *Меню команд:*\n\n"
        "/start — начать общение с ботом\n"
        "/weather — узнать погоду\n"
        "/help; /menu — показать это меню\n\n"
    )
    bot.reply_to(message, text)


@bot.message_handler(commands=['clear'])
def clear_chat(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "🧹 Очищаю чат...")
    time.sleep(5)
    bot.delete_message(chat_id, msg.message_id)
    # Удаляем последние N сообщений (например, 100)
    deleted = 0
    for msg_id in range(message.message_id, message.message_id - 100, -1):
        try:
            bot.delete_message(chat_id, msg_id)
            deleted += 1
        except:
            pass


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "weather":
        bot.answer_callback_query(call.id)
        process_day(call.message)
    elif call.data == "about":
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "🌤 Этот бот показывает погоду по дням.\n"
            "Работает с данными открытого API")


bot.polling(none_stop=True)

