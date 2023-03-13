import requests
import json
import argparse
import telebot

TELEGRAM_TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'
REVOLUT_TOKEN = 'YOUR_REVOLUT_API_TOKEN'


# Инициализируем бота
bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Определяем аргументы командной строки
parser = argparse.ArgumentParser(description='Set upper and lower threshold for the cryptocurrency price change')
parser.add_argument('--upper', type=float, help='Set upper threshold in percentage')
parser.add_argument('--lower', type=float, help='Set lower threshold in percentage')

# Список криптовалют для отслеживания
CRYPTO_LIST = ['BTC', 'ETH', 'LTC']

# Функция для получения текущей цены криптовалюты с Revolut API
def get_crypto_price(currency):
    headers = {
        'Authorization': 'Bearer ' + REVOLUT_TOKEN
    }
    response = requests.get(f'https://api.revolut.com/partner-exchange/quotes/{currency}USD', headers=headers)
    data = json.loads(response.text)
    price = data['rate']
    return price

# Функция для отправки сообщения в Telegram
def send_telegram_message(message):
    bot.send_message(chat_id='YOUR_TELEGRAM_CHAT_ID', text=message)

# Функция для проверки изменения цены
def check_crypto_price():
    global CRYPTO_LIST
    global upper_threshold
    global lower_threshold
    for currency in CRYPTO_LIST:
        current_price = get_crypto_price(currency)
        if current_price >= (1 + upper_threshold) or current_price <= (1 - lower_threshold):
            message = f"{currency}: {current_price}"
            send_telegram_message(message)

# Обработчик команды /set_thresholds
@bot.message_handler(commands=['set_thresholds'])
def set_thresholds(message):
    global upper_threshold
    global lower_threshold
    args = parser.parse_args(message.text.split()[1:])
    upper_threshold = args.upper
    lower_threshold = args.lower
    bot.reply_to(message, f"Thresholds set: upper={upper_threshold}, lower={lower_threshold}")

# Обработчик команды /set_crypto_list
@bot.message_handler(commands=['set_crypto_list'])
def set_crypto_list(message):
    global CRYPTO_LIST
    crypto_list = message.text.split()[1:]
    CRYPTO_LIST = [crypto.upper() for crypto in crypto_list]
    bot.reply_to(message, f"Cryptocurrencies set: {CRYPTO_LIST}")

    while True:
        try:
            check_crypto_price()
            bot.polling()
        except Exception as e:
            print(e)
    time.sleep(10) # Ждем 10 секунд перед следующей попыткой подключения.
