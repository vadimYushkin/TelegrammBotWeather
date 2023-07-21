import requests
from geopy.geocoders import Nominatim

class WeatherAPI:
    def __init__(self, api_url, geolocator):
        self.api_url = api_url
        self.geolocator = geolocator

    def get_current_weather(self, city_name):
        location = self.geolocator.geocode(city_name)
        if location is None:
            return "Город не найден."

        params = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'current_weather': 'true',
            'city': city_name
        }

        response = requests.get(self.api_url, params=params)
        weather_data = response.json()

        current_weather = weather_data['current_weather']
        temperature = current_weather['temperature']
        windspeed = current_weather['windspeed']
        weathercode = current_weather['weathercode']

        weather_descriptions = {
            (0,): "ясно \U0001F31E",
            (1,): "преимущественно ясно \U0001f324\uFE0F",
            (2,): "переменная облачность \u26C5",
            (3,): "облачно \u2601\uFE0F",
            (45, 48): "туман \U0001f32b\uFE0F",
            (51, 53, 55, 56, 57): "изморось \u2614",
            (61, 63, 65, 66, 67): "дождь \U0001F327",
            (71, 73, 75): "снег \U0001F328 ",
            (77,): "град \U0001f4a7",
            (80, 81, 82, 85, 86): "сильный дождь \U0001F327",
            (95, 96, 99): "гроза \u26C8"
        }

        weather_description = next((value for key, value in weather_descriptions.items() if weathercode in key), "")

        if temperature > 10:
            temperature_emoji = "\U0001f642"
        else:
            temperature_emoji = "\U0001F976"

        return f"Cейчас в городе {city_name.title()} {weather_description} \nтемпература воздуха: {temperature}°C {temperature_emoji} \nскорость ветра: {windspeed}m/s"

    def get_weather_for_tomorrow(self, city_name):
        location = self.geolocator.geocode(city_name)
        if location is None:
            return "Город не найден."

        params = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timezone': 'auto',
            'daily': 'temperature_2m_max,temperature_2m_min,cloudcover_mean',
            'city': city_name
        }

        response = requests.get(self.api_url, params=params)
        weather_data = response.json()['daily']

        day = weather_data['time'][1]
        max_tmp = weather_data['temperature_2m_max'][1]
        min_tmp = weather_data['temperature_2m_min'][1]
        cloudcover_mean = weather_data['cloudcover_mean'][1]

        if cloudcover_mean > 30:
            description_clouds = "пасмурно \U0001F324"
        else:
            description_clouds = "ясно \U0001F31E"

        return f"В городе {city_name.title()} завтра: \nмаксимальная тeмпература воздуха днем {max_tmp}°C \nминимальная температура воздуха ночью {min_tmp}°C \nв этот день будет {description_clouds}"

    def get_weather_for_3_days(self, city_name):
        location = self.geolocator.geocode(city_name)
        if location is None:
            return "Город не найден."

        params = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'timezone': 'auto',
            'daily': 'temperature_2m_max,temperature_2m_min,cloudcover_mean',
            'city': city_name
        }

        response = requests.get(self.api_url, params=params)
        weather_data = response.json()['daily']

        info_seven_days = []

        for i in range(1, 4):
            day = weather_data['time'][i]
            max_tmp = weather_data['temperature_2m_max'][i]
            min_tmp = weather_data['temperature_2m_min'][i]
            cloudcover_mean = weather_data['cloudcover_mean'][i]

            if cloudcover_mean > 30:
                cloud_info = 'пасмурно \U0001F324'
            else:
                cloud_info = 'ясно \U0001F31E'

            info_seven_days.append(f'{day}: \nтeмпература воздуха от: {min_tmp}°C до: {max_tmp}°C \n{cloud_info}')

        return '\n'.join(info_seven_days)
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
        bot.send_message(message.chat.id, "Произошла ошибка при обработке запро
