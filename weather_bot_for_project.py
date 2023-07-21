from geopy.geocoders import Nominatim
import weather_API
import telebot
from telebot import types
import os
from dotenv import load_dotenv

geolocator = Nominatim(user_agent="Tester")
API_URL = 'https://api.open-meteo.com/v1/forecast?'
# создаем экземпляр класса WeatherAPI
weather_api = weather_API.WeatherAPI(API_URL, geolocator)

load_dotenv()
bot_token = os.getenv("token")
bot = telebot.TeleBot(bot_token)

# handler для старта бота
@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.send_message(message.chat.id, f"Привет! Это бот прогноза погоды. \nВведи название города: ")
    bot.register_next_step_handler(message, handle_city_input)

# функция для вывода кнопок в меню бота
def show_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=1)
    tomorrow_weather_btn = types.KeyboardButton("Погода на завтра")
    three_days_weather_btn = types.KeyboardButton("Погода на 3 дня")
    start_over_btn = types.KeyboardButton("Начать сначала")
    markup.add(tomorrow_weather_btn, three_days_weather_btn, start_over_btn)
    bot.send_message(chat_id, "Варианты прогноза по кнопке снизу \u2935: ", reply_markup=markup)

# handler на ввод пользователя
def handle_city_input(message):
    try:
        global city
        city = message.text
        location = geolocator.geocode(city)
        if location is None:
            bot.send_message(message.chat.id, "Город не найден. Введи название города еще раз: ")
            bot.register_next_step_handler(message, handle_city_input)
        elif message.text == "/start":
            bot.send_message(message.chat.id, "Некорректный ввод (необходимо ввести название города). Выберите начать сначала")
            show_menu(message.chat.id)
        else:
            weather = weather_api.get_current_weather(city)
            bot.send_message(message.chat.id, weather)
            show_menu(message.chat.id)
    except Exception as e:
        # Обработка общего исключения
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса. Попробуйте еще раз позже.")


# handler для кнопок меню
@bot.message_handler(func=lambda message: True)
def handle_menu_selection(message):
    try:
        if message.text == "Погода на завтра":
            weather = weather_api.get_weather_for_tomorrow(city)
            bot.send_message(message.chat.id, weather)
        elif message.text == "Погода на 3 дня":
            weather = weather_api.get_weather_for_3_days(city)
            bot.send_message(message.chat.id, weather)
        elif message.text == "Начать сначала":
            bot.send_message(message.chat.id, "Введите город:")
            bot.register_next_step_handler(message, handle_city_input)
        else:
            bot.send_message(message.chat.id, "Некорректный ввод. Выберите один из предложенных вариантов \u2935.")
    except Exception as e:
        # Обработка общего исключения
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса. Попробуйте еще раз позже.")

bot.polling()