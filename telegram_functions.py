import requests
from dotenv import load_dotenv
import os

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")
BOT_TOKEN = os.getenv("BOT_TOKEN")
GROUP_ID = os.getenv("GROUP_ID")

def send_message_to_telegram(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": GROUP_ID,
        "text": message
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Request to Telegram API failed with status code {response.status_code}")

def format_supply(supply):
    if supply < 1_000_000:
        # For numbers less than a million, just return the number
        return str(supply)
    elif supply < 1_000_000_000:
        # For numbers in the millions, divide by 1 million and add 'm' suffix
        return f"{supply // 1_000_000}m"
    else:
        # For numbers in the billions, divide by 1 billion and add 'b' suffix
        return f"{supply // 1_000_000_000}b"

def sendTgMessage(token_data):
    supply = token_data.get('supply', '')
    supply = supply.replace(',', '_')
    supply = format_supply(int(supply))
    supply = f"#{supply}"

    decimals = token_data.get('decimals', 'N/A')
    decimal = f"#{decimals}dec"

    mint_authority = token_data['mint_authority'].lower()
    mint = '#mintE' if mint_authority == 'enabled' else ('#mintD' if mint_authority == 'disabled' else 'N/Amint')

    freeze_authority = token_data['freeze_authority'].lower()
    freeze = '#freezeE' if freeze_authority == 'enabled' else ('#freezeD' if freeze_authority == 'disabled' else 'N/Afreeze')

    thumbnail = f"#{token_data['thumbnail'] if token_data['thumbnail'] else 'N/Athumbnail'}"

    source = token_data['source'] if 'source' in token_data else 'Unknown Source'

    socials = token_data.get('socials', None)
    
    message = f"Title: {token_data['title']}\n" \
          f"Supply: {supply}\n" \
          f"Decimals: {decimal}\n" \
          f"Creator: #{token_data['creator_address']}\n" \
          f"Token Address: #{token_data['token_address']}\n" \
          f"Source: #{source}\n" \
          f"Solana Response: {token_data['solana_response']}\n" \
          f"Mint Authority: {mint}\n" \
          f"Freeze Authority: {freeze}\n" \
          f"Thumbnail: {thumbnail}\n" \
          f"time: {token_data['time_response']}\n" + \
          (f"URLS: {socials}\n" if socials else "")


    send_message_to_telegram(message)