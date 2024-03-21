import requests 
from discord_logger import send_exception_to_discord, send_message_to_discord
from wallets_list import wallets
from datetime import datetime, timezone
import requests
import tldextract
import re
from urllib.parse import urlparse
from dotenv import load_dotenv
import os

load_dotenv()

log_webhook_url = os.getenv("LOG_WEBHOOK_URL")

def hour_range(unix_timestamp):
    # Convert unix timestamp to datetime object in UTC
    dt_object = datetime.fromtimestamp(unix_timestamp, tz=timezone.utc)
    # Extract the hour from datetime object
    hour = dt_object.hour
    
    # Calculate the range based on the hour
    start_range = (hour - 3) % 24
    end_range = (hour + 3) % 24

    # Format and print the output
    response = f"#{start_range}-{end_range}"
    print(response)
    send_message_to_discord(response, log_webhook_url, 0xfcb9ca)
    return response

def findLastTransaction(contract: str):
    try:
        page = 1
        url = f"https://api.solana.fm/v0/accounts/{contract}/transfers"
        send_message_to_discord(f"Checking for last transaction: {url}", log_webhook_url, 0xfcb9ca)
        print(url)

        response = requests.get(url + "?page=1").json()
        try:
            total_page = 1
            if 'pagination' in response and 'totalPages' in response["pagination"]:
                total_page = response["pagination"]["totalPages"] if response["pagination"]["totalPages"] else 1
                print(total_page)
        except Exception as e:
            print(f"Error: {e}")
            send_exception_to_discord(e, log_webhook_url)
            total_page = 1

        send_message_to_discord(f"[URL]({url}) - Total Pages: {total_page}", log_webhook_url, 0xfcb9ca)
        
        print(page)
        if page == 1 and 'results' in response:
            if len(response["results"]) > 0:
                lastTransaction = response["results"][-1]
                return lastTransaction
            else:
                return None

        response = requests.get(url + f"?page={total_page}").json()

        if 'results' in response:
            if len(response["results"]) > 0:
                lastTransaction = response["results"][-1]
                return lastTransaction
            else:
                return None
    except Exception as e:
        print(f"Error: {e}")
        send_exception_to_discord(e, log_webhook_url)
    return None


def get_source_name(wallets, source):
    for key, value in wallets.items():    
        if value.strip().lower() == source.strip().lower():
            return key
    return source

def getFundsSource(contract: str):
    try:
        lastTransaction = findLastTransaction(contract)
        print(f"Last Transaction: {lastTransaction}")
        if lastTransaction and "data" in lastTransaction:
            print(lastTransaction["data"])
            source = lastTransaction["data"][0]["source"] if "source" in lastTransaction["data"][0] else ""

            amount = ""
            amount_int = ""
            timestamp = ""
            time_response = ""
            for data in lastTransaction["data"]:
                if "action" in data and data["action"] == "transfer":
                    amount = data["amount"] if "amount" in data else ""
                    timestamp = data.get("timestamp", 0)

            print(f"Source: {source} - Amount: {amount} - Timestamp: {timestamp}")
            
            # divide amount to 10^9 and round to 4 decimal places

            if amount:
                all_decimals = f"{float(amount):g}"
                amount = round(float(amount) / 1000000000, 2)
                amount_int = int(round(float(amount)))

            print(f"Source: {source} - Amount: {amount}")
            # get the key from wallets if the value matches with source
            source_name = get_source_name(wallets, source)
            print(f"Source Name: {source_name}")
            if amount_int:
                return_response = spam_response = f"#{source_name} #{amount} #{source_name}-{amount_int - 1}-{amount_int + 1} #{source_name}-{amount_int - 2}-{amount_int + 2} #{amount_int - 1}-{amount_int + 1} #{amount_int - 2}-{amount_int + 2}"
            else:
                return_response = spam_response = f"#{source_name}"
            print(f"Return Response: {return_response}")
            send_message_to_discord(spam_response, log_webhook_url, 0xfcb9ca)

            if timestamp:
                time_response = hour_range(timestamp)
            return source, return_response, time_response
        else:
            return "", "", ""
    except Exception as e:
        print(f"Error: {e}")
        send_exception_to_discord(e, log_webhook_url)
        return "", "", ""