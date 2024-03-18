import configparser
import time
import asyncio
from telegram import Bot
import requests
from telegram.ext import Application
from datetime import datetime

# CoinGecko API
def get_crypto_prices(api_key, crypto_ids=['bitcoin', 'ethereum', 'solana', 'algorand']):
    ids = ','.join(crypto_ids)  # Convert list of ids into a comma-separated string
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd'
    headers = {
        'x-cg-demo-api-key': api_key
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error fetching prices: {response.status_code} - {response.text}")
        return None  # Return None or an appropriate error indicator

# Telegram Bot
async def send_message_to_telegram(chat_id, message, bot_token):
    bot = Bot(token=bot_token)
    await bot.send_message(chat_id=chat_id, text=message, parse_mode='HTML')

async def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot_token = config['TELEGRAM']['BOT_TOKEN']
    chat_id = config['TELEGRAM']['CHAT_ID']
    api_key = config['COINGECKO']['API_KEY']
    crypto_ids = ['bitcoin', 'ethereum', 'solana', 'algorand']  # Add or remove tokens as desired

    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")  # Formats the date and time
    prices_data = get_crypto_prices(api_key, crypto_ids)
    if prices_data:
        message = "<b>Current Prices:</b>\n"
        message += "<i>Updated on {}</i>\n\n".format(formatted_date)
        for crypto_id in crypto_ids:
            price = prices_data.get(crypto_id, {}).get('usd', 'N/A')
            message += "<code>{}: ${}</code>\n".format(crypto_id.capitalize(), price)

        await send_message_to_telegram(chat_id, message, bot_token)
    else:
        print("Skipping message due to error fetching prices.")

    # await asyncio.sleep(3600)  # Wait for 1 hour before sending the next update

if __name__ == '__main__':
    asyncio.run(main())
