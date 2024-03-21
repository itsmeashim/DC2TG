from discord_logger import send_message_to_discord, send_exception_to_discord
import requests
import re
import json
import tldextract
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

DC_TOKEN = os.getenv("DC_TOKEN")
log_webhook_url = os.getenv("LOG_WEBHOOK_URL")

def get_response(channel_id):
    data_reversed = []
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    header = {
        'authorization': DC_TOKEN
    }
    response = requests.get(url, headers=header).json()
    if isinstance(response, list):
        data_reversed = response[::-1]
    # print(f"Response: {data_reversed}")
    return data_reversed

def getthumbnaildomain(url):
    try:
        extracted = tldextract.extract(url)
        print(f"Extracted: {extracted}")
        if extracted.domain:
            return extracted.domain
        else:
            return None
    except Exception as e:
        print(f"Error in getthumbnaildomain: {e}")
        send_exception_to_discord(e, log_webhook_url)
        return None

def process_message(message):
    try:
        embed = message['embeds'][0] if 'embeds' in message and len(message['embeds']) > 0 else ''

        if not embed:
            return ""

        message_title = embed['title'] if 'title' in embed else ''
        message_title = re.sub(r'\[.*\]\(.*\)', '', message_title).replace('**', '').replace('\x00', '').replace("\u0000", "").strip()
        message_desc = embed['description'] if 'description' in embed else ''
        message_fields = embed['fields'] if 'fields' in embed else ''
        thumbnail_url = embed['thumbnail']['url'] if 'thumbnail' in embed else ''
        print(f"Message title: {message_title}")

        fields_values = [list(field.values()) for field in message_fields]
        print(f"Fields: {fields_values}")
        if not fields_values:
            return ""

        thumbnail_domain = getthumbnaildomain(thumbnail_url)
        print(f"Thumbnail Domain: {thumbnail_domain}")
        send_message_to_discord(f"Thumbnail Domain: {thumbnail_domain}", log_webhook_url)

        token_data = ''
        for field in fields_values:
            token_data = {
                'title': message_title,
                'description': message_desc,
                'supply': next((field['value'] for field in embed['fields'] if field['name'] == "Supply"), None),
                'token_address': next((field['value'].split('](')[0].rstrip(')').strip('[') for field in embed['fields'] if field['name'] == "Token Address"), None),
                'decimals': next((field['value'] for field in embed['fields'] if field['name'] == "Decimals"), None),
                'creator_balance': next((field['value'].split()[0] for field in embed['fields'] if field['name'] == "Creator Balance"), ""),
                'freeze_authority': next((field['value'].split(" ")[0] for field in embed['fields'] if field['name'] == "Freeze Authority"), None),
                'mint_authority': next((field['value'].split(" ")[0] for field in embed['fields'] if field['name'] == "Mint Authority"), None),
                'creator_address': next((field['value'].split('](')[0].rstrip(')').strip('[') for field in embed['fields'] if field['name'] == "Creator"), None),
                'token_name': next((field['value'] for field in embed['fields'] if field['name'] == "Token Name"), None),
                'socials': next((field['value'] for field in embed['fields'] if field['name'] == "Socials"), None),
                'gedo': next((field['value'] for field in embed['fields'] if field['name'] == "Gedo"), None),
                'thumbnail': thumbnail_domain,
                'source': 'Unknown Source',
                'solana_response': '',
                'time_response': '',
            }
        
        print(token_data)

        socials = [field['value'] for field in embed['fields'] if field['name'] == "Socials"][0] or None
        
        urls = re.findall(r'http[s]?://[^\s)\]]+', socials)

        # Domains to filter out
        filter_domains = ["twitter.com", "x.com", "discord.gg", "t.me", "instagram.com", "facebook.com", "reddit.com", "youtube.com", "tiktok.com","binance.com", "opensea.io", "rarible.com", "solsea.io", "solible.com", "solible.io", "wikipedia"]
        filtered_urls = [tldextract.extract(url).registered_domain for url in urls if tldextract.extract(url).registered_domain not in filter_domains]

        token_data['socials'] = tldextract.extract(filtered_urls[0]).registered_domain if len(filtered_urls) > 0 else None

        return token_data
    except Exception as e:
        print(f"Error: {e}")
        send_exception_to_discord(e, log_webhook_url)
        return ""
