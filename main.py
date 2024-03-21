from discord_logger import *
from discord_functions import get_response
from functions import check_response
import time
import random
import logging
from dotenv import load_dotenv
import os

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")
NEWTOKEN_ID = os.getenv("NEWTOKEN_ID")
guild_id = os.getenv("guild_id")


logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    i = 0
    newtoken_prev_id = 0

    while True:
        # Increment check count and print status
        i += 1
        print(f"Checking Now, times checked: {i}")

        try:
            newtoken_response = get_response(NEWTOKEN_ID)

            for response in newtoken_response:
                latest_message_id = newtoken_response[-1]['id']
                newtoken_new_id = check_response(response, newtoken_prev_id, latest_message_id, NEWTOKEN_ID, guild_id)
                newtoken_prev_id = newtoken_new_id if newtoken_new_id else newtoken_prev_id
        except Exception as e:
            print(f"Error: {e}")
            send_exception_to_discord(e, log_webhook_url)
            
        if not i == 1:
            time.sleep(random.uniform(25, 30))