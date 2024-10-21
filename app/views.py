import os
import logging
import json
from flask import Blueprint, request, jsonify, current_app
from dotenv import load_dotenv
from .decorators.security import signature_required
from .utils.whatsapp_utils import process_whatsapp_message, is_valid_whatsapp_message

# Load environment variables
load_dotenv()
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
if VERIFY_TOKEN is None:
    raise ValueError("VERIFY_TOKEN environment variable is not set.")
    
# Logging for debugging purposes
logging.basicConfig(level=logging.INFO)
logging.info(f"VERIFY_TOKEN loaded: {VERIFY_TOKEN}")

# Initialize Flask Blueprint for the webhook
webhook_blueprint = Blueprint("webhook", __name__)

def handle_message():
    """
    Handle incoming webhook events from the WhatsApp API.
    This function processes incoming WhatsApp messages and other events,
    such as delivery statuses. If the event is a valid message, it gets processed.
    Returns:
        response: JSON response and HTTP status code.
    """
    body = request.get_json()
    
    if not body:
        logging.error("Empty or invalid JSON received.")
        return jsonify({"status": "error", "message": "Invalid JSON provided"}), 400
    
    # Check if it's a WhatsApp status update (delivered, read, etc.)
    if body.get("entry", [{}])[0].get("changes", [{}])[0].get("value", {}).get("statuses"):
        logging.info("Received a WhatsApp status update.")
        return jsonify({"status": "ok"}), 200

    # Process valid WhatsApp message
    if is_valid_whatsapp_message(body):
        process_whatsapp_message(body)
        return jsonify({"status": "ok"}), 200
    else:
        logging.warning("Not a valid WhatsApp API event.")
        return jsonify({"status": "error", "message": "Not a WhatsApp API event"}), 404

def verify():
    """
    Verify the webhook from WhatsApp by matching the verify token.
    Returns:
        response: Plaintext challenge or JSON error response.
    """
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    logging.info(f"Verification request - Mode: {mode}, Token: {token}")
    logging.info(f"Expected VERIFY_TOKEN: {VERIFY_TOKEN}")  # For debugging

    if mode and token:
        # Check if mode is subscribe and the token matches the configured VERIFY_TOKEN
        
        if mode == "subscribe" and token == "abc123": #VERIFY_TOKEN was hardcoded here
            logging.info("WEBHOOK_VERIFIED")
            return challenge, 200
        else:
            logging.warning("Verification failed: token mismatch.")
            return jsonify({"status": "error", "message": "Verification failed"}), 403
    else:
        logging.error("Missing parameters for verification.")
        return jsonify({"status": "error", "message": "Missing parameters"}), 400

# Define webhook routes
@webhook_blueprint.route("/webhook", methods=["GET"])
def webhook_get():
    return verify()

@webhook_blueprint.route("/webhook", methods=["POST"])
@signature_required
def webhook_post():
    return handle_message()
