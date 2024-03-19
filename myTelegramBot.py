import os
import configparser
import time
import asyncio
from telegram import Bot
import requests
from telegram.ext import Application
from datetime import datetime

def get_trending_coins(api_key):
    url = 'https://api.coingecko.com/api/v3/search/trending'
    headers = {'x-cg-demo-api-key': api_key}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        trending_coins_info = []
        for coin in data['coins'][:10]:  # Limit to top 10 trending coins
            item = coin['item']
            # Extracting nested 'data' content
            coin_details = item['data']
            # Attempt to safely get the description
            content = coin_details.get('content')
            description = 'No description available.'  # Default
            if content is not None:  # Ensures that content is not None
                description = content.get('description', 'No description available.')

            price_change_percentage_24h_usd = coin_details['price_change_percentage_24h'].get('usd', 'N/A') if 'price_change_percentage_24h' in coin_details else 'N/A'
            coin_data = {
                'name': item['name'],
                'symbol': item['symbol'],
                'market_cap_rank': item['market_cap_rank'],
                'price': coin_details.get('price', 'N/A'),
                'price_change_percentage_24h_usd': price_change_percentage_24h_usd,
                'market_cap': coin_details.get('market_cap', 'N/A'),
                'total_volume': coin_details.get('total_volume', 'N/A'),
                'description': description,
            }
            trending_coins_info.append(coin_data)
        return trending_coins_info
    else:
        print(f"Error fetching trending coins: {response.status_code} - {response.text}")
        return None


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
    config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))
    bot_token = config['TELEGRAM']['BOT_TOKEN']
    chat_id = config['TELEGRAM']['CHAT_ID']
    api_key = config['COINGECKO']['API_KEY']
    crypto_ids = ['bitcoin', 'ethereum', 'solana', 'algorand', 'filecoin']  # Add or remove tokens as desired

    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d %H:%M:%S")  # Formats the date and time
    prices_data = get_crypto_prices(api_key, crypto_ids)
    price_message = "<b>Current Token Prices:</b>\n"
    price_message += f"<i>Updated on {formatted_date}</i>\n\n"
    if prices_data:
        for crypto_id in crypto_ids:
            price = prices_data.get(crypto_id, {}).get('usd')
            if price:
                price_message += f"<code><b>{crypto_id.capitalize()}</b>: ${price}</code>\n"
            else:
                price_message += f"<code>{crypto_id.capitalize()}: Price data unavailable</code>\n"
    else:
        price_message += "Failed to fetch prices.\n"

    # Fetch and format trending coins information
    trending_coins = get_trending_coins(api_key)
    trending_message = "<b>Top 10 Trending Coins:</b>\n"
    if trending_coins:
        for coin in trending_coins:
            trending_message += (f"<b>{coin['name']}</b> ({coin['symbol']}), "
                                 f"<b>Market Cap Rank</b>: {coin['market_cap_rank']},\n"
                                 f"<b>Price</b>: {coin['price']}, "
                                 f"<b>24h Change</b>: {coin['price_change_percentage_24h_usd']}%,\n"
                                 f"<b>Market Cap</b>: {coin['market_cap']}, "
                                 f"<b>Total Volume</b>: {coin['total_volume']}\n"
                                 f"Description: {coin['description']}\n\n")
    else:
        trending_message += "Failed to fetch trending coins data.\n"

    # Combine the messages
    message = price_message + "\n" + trending_message

    # Send the combined message to Telegram
    await send_message_to_telegram(chat_id, message, bot_token)
    # await asyncio.sleep(3600)  # Wait for 1 hour before sending the next update

if __name__ == '__main__':
    asyncio.run(main())
