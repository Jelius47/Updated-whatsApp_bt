import logging
import json
import requests
import re
from dotenv import load_dotenv
import os
from flask import jsonify

# This is the responsible function from GeminAi to the use
from app.services.gemin_configuration import generate_response

# Load environment variables
load_dotenv()
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
RECIPIENT_WAID = os.getenv("RECIPIENT_WAID")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")
VERSION = os.getenv("VERSION")
APP_ID = os.getenv("APP_ID")
APP_SECRET = os.getenv("APP_SECRET")


# Utility function to log HTTP response details
def log_http_response(response):
    logging.info(f"Status: {response.status_code}")
    logging.info(f"Content-type: {response.headers.get('content-type')}")
    logging.info(f"Body: {response.text}")


# Construct a text message payload for the WhatsApp API
def get_text_message_input(recipient, text):
    return json.dumps({
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": recipient,
        "type": "text",
        "text": {"preview_url": False, "body": text},
    })


# Where integration with WhatsApp API to send the response back
import requests

def send_whatsapp_message(recipient_waid, message):
    url = f"https://graph.facebook.com/v13.0/{os.getenv('PHONE_NUMBER_ID')}/messages"
    headers = {
        "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": recipient_waid,
        "type": "text",
        "text": {"body": message}
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        logging.info(f"Message sent to {recipient_waid}")
    else:
        logging.error(f"Failed to send message to {recipient_waid}: {response.text}")


# Process text to match WhatsApp message style (e.g., replacing brackets, formatting text)
def process_text_for_whatsapp(text):
    # Remove brackets and their content
    text = re.sub(r"\【.*?\】", "", text).strip()

    # Replace double asterisks with single asterisks (for bold formatting in WhatsApp)
    whatsapp_style_text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)

    return whatsapp_style_text


# Handle incoming WhatsApp message and respond
def process_whatsapp_message(body):
    try:
        wa_id = body["entry"][0]["changes"][0]["value"]["contacts"][0]["wa_id"]
        name = body["entry"][0]["changes"][0]["value"]["contacts"][0]["profile"]["name"]
        message_body = body["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]

        logging.info(f"Received message from {name} ({wa_id}): {message_body}")

        # Process and respond
        response = generate_response(message_body, wa_id, name)
        formatted_response = process_text_for_whatsapp(response)

        # Send the response
        # data = get_text_message_input(RECIPIENT_WAID, formatted_response)
        send_whatsapp_message(wa_id,formatted_response)
    except KeyError as e:
        logging.error(f"KeyError during message processing: {e}")
    except Exception as e:
        logging.error(f"Unexpected error during message processing: {e}")


# Check if the incoming event is a valid WhatsApp message
def is_valid_whatsapp_message(body):
    try:
        return (
            body.get("object") == "whatsapp_business_account" and
            "entry" in body and
            "changes" in body["entry"][0] and
            "value" in body["entry"][0]["changes"][0] and
            "messages" in body["entry"][0]["changes"][0]["value"]
        )
    except KeyError:
        return False


# # Generate a simple response (you can replace this with your AI assistant or custom logic)
# def generate_response(message):
#     # Here we simply return the message in uppercase as a response
#     return message.upper()
