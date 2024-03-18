import configparser
import time
import asyncio
from telegram import Bot
import requests
from telegram.ext import Application
from datetime import datetime

# CoinGecko API
def get_crypto_prices(crypto_ids=['bitcoin', 'ethereum', 'solana', 'algorand']):
    ids = ','.join(crypto_ids)  # Convert list of ids into a comma-separated string
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd'
    response = requests.get(url)
    data = response.json()
    return data

# Telegram Bot
async def send_message_to_telegram(chat_id, message, bot_token):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message)

async def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot_token = config['TELEGRAM']['BOT_TOKEN']
    chat_id = config['TELEGRAM']['CHAT_ID']
    crypto_ids = ['bitcoin', 'ethereum', 'solana', 'algorand']  # Add or remove tokens as desired

    while True:
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")  # Formats the date and time
        prices_data = get_crypto_prices(crypto_ids)
        message = f"Current Prices as of {formatted_date}:\n"
        for crypto_id in crypto_ids:
            price = prices_data[crypto_id]['usd']
            message += f"{crypto_id.capitalize()}: ${price}\n"

        await send_message_to_telegram(chat_id, message, bot_token)
        #await asyncio.sleep(3600)  # Wait for 1 hour before sending the next update

if __name__ == '__main__':
    asyncio.run(main())
