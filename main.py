"""The json module allows you to encode and decode data in a convenient format.""" 
import json
import telebot
import requests
from telebot import types
from py_currency_converter import convert
from requests import Session
from auth_data import token


bot = telebot.TeleBot(token)

URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'

headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': 'YOUR_API_KEY',
}


# get price of crypto from API
def get_data():
    """finction where we write our parameters and parsing json base from coinmarketcap api url"""
    parameters = {
        'start': 1,
        'limit': 5000,
        'convert': 'USD'
    }

    session = Session()
    session.headers.update(headers)
    # parsing json
    response = session.get(URL, params=parameters, headers=headers)
    data = json.loads(response.text)

    return data['data']


@bot.message_handler(commands=['start'])
def start_message(message):
    """Function where we add buttons and writting message to user after the user starts the bot"""
    # Here we adapts the size of the buttons to their number
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    # Add button all you need
    item1 = types.KeyboardButton('₿TOP-5 Coins')
    item2 = types.KeyboardButton('💵Exchange Rate')
    markup.add(item1, item2)

    # Bot send message to user after the user starts the bot
    bot.send_message(
        message.chat.id,
        str("Hello {0.first_name}, write me the name or symbol of the coin to find out the price").format(message.from_user), reply_markup=markup
     )


@bot.message_handler(content_types=["text"])
def get_price(message):
    """All bot functionality"""
    try:
        if message.text == "₿TOP-5 Coins":
            parameters = {
                'start': 1,
                'limit': 5,
                'convert': 'USD'
            }
            session = Session()
            session.headers.update(headers)

            response = session.get(URL, params=parameters, headers=headers)

            data = json.loads(response.text)

            coins = data['data']

            output = ""

            for i in coins:
                output += i['name'] + ": " + \
                    str(round((i['quote']['USD']['price']), 5)) + "$\n"

            bot.send_message(
                message.chat.id,
                f"Price of top-5 coins:\n{output}"
            )
        elif message.text == "💵Exchange Rate":
            usd = convert(base='USD', amount=1, to=['UAH'])
            eur = convert(base='EUR', amount=1, to=['UAH'])
            gbp = convert(base='GBP', amount=1, to=['UAH'])
            pln = convert(base='PLN', amount=1, to=['UAH'])

            bot.send_message(
                message.chat.id,
                text=f"\n🇬🇧1£ GBP to 🇺🇦UAH {gbp['UAH']}₴"
                + f"\n🇺🇸1$ USD to 🇺🇦UAH {usd['UAH']}₴"
                + f"\n🇪🇺1€ EUR to 🇺🇦UAH {eur['UAH']}₴"
                + f"\n🇵🇱1zł PLN to 🇺🇦UAH {pln['UAH']}₴"
                )

        # Function that search crypto coins or tokens by name or symbol
        elif message and not str(message).isspace():
            coins = get_data()

            output = ""

            for i in coins:
                if message.text.lower() == i['name'].lower() or message.text.lower() == i['symbol'].lower():
                    output += "Price of this coin:\n" + i['name'] + ": " + str(round(
                        (i['quote']['USD']['price']), 7)) + "$ " + f"({str(round((i['quote']['USD']['percent_change_24h']), 2))}%)" + "\n"
                    break

            if not output:
                output += "Coin not found"

            bot.send_message(
                message.chat.id,
                output
            )

        else:
            bot.send_message(
                message.chat.id, "What??? Check the command dude!")

    except requests.ConnectionError as connection_error:
        print("OOPS!! Connection Error. Make sure you are connected to Internet.")
        print(str(connection_error))

    except requests.Timeout as timeout_error:
        print("OOPS!! Timeout Error")
        print(str(timeout_error))

    except requests.RequestException as request_error:
        print("OOPS!! General Error")
        print(str(request_error))
    except KeyboardInterrupt:
        print("Someone closed the program")


if __name__ == '__main__':
    # get_data()
    bot.polling(none_stop=True)
