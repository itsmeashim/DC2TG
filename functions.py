from discord_logger import send_message_to_discord, send_exception_to_discord
from discord_functions import process_message
from solana_functions import getFundsSource
import requests
import json
from telegram_functions import sendTgMessage
from dotenv import load_dotenv
import os

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")

def check_response(response, prev_id, latest_message_id, channel_id, guild_id):
    try:
        latest_message = response
        prev_id = latest_message_id if not prev_id else prev_id
        new_id = int(latest_message['id'])

        # prev_id = 0
        if int(prev_id) < int(new_id):
            print(f"New Message: {new_id}")
            token_data = process_message(latest_message)

            if not token_data:
                return new_id

            source, solana_response, time_response = getFundsSource(token_data['creator_address'])

            if solana_response and source:
                token_data['source'] = source if source else 'Unknown Source'
                token_data['solana_response'] = solana_response if solana_response else ''

            if time_response:
                token_data['time_response'] = time_response
            
            send_message_to_discord(json.dumps(token_data, indent=4), log_webhook_url)

            sendTgMessage(token_data)

            return new_id

    except Exception as e:
        send_exception_to_discord(e, log_webhook_url)
    return prev_id

