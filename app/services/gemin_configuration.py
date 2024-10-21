import os
import logging
import shelve
import time
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API using the API key
genai.configure(api_key=os.environ["GEMINI_API_KEY"])

# Define constants
MODEL_NAME = "gemini-1.5-flash"  # Adjust the model name as per Gemini's current offerings
SHELVE_FILE = "threads_db"  # File for storing conversation threads
SYSTEM_INSTRUCTION = os.getenv("SYSTEM_INSTRUCTION", 
                               "Respond to customer queries in a helpful and friendly manner.")  # Default system instruction if not provided

# Initialize the model with system instructions
model = genai.GenerativeModel(
    model_name=MODEL_NAME,
    system_instruction=SYSTEM_INSTRUCTION
)

# Check if a thread exists for the given WhatsApp ID (wa_id)
def check_if_thread_exists(wa_id):
    with shelve.open(SHELVE_FILE) as threads_shelf:
        return threads_shelf.get(wa_id, None)

# Store a new thread in the shelve DB
def store_thread(wa_id, thread_id):
    with shelve.open(SHELVE_FILE, writeback=True) as threads_shelf:
        threads_shelf[wa_id] = thread_id

# Run the assistant to generate a response
def run_assistant(thread_id, name, message):
    try:
        logging.info(f"Running assistant for thread: {thread_id}")

        # Start or continue the conversation
        chat = model.start_chat(
            history=[
                {"role": "user", "parts": f"Naitwa {name} nahitaji {SYSTEM_INSTRUCTION}"},
                {"role": "model", "parts": message},  # Use the user's message here
            ]
        )

        # Send the message and get the response
        response = chat.send_message(message)

        if response and response.text:
            new_message = response.text  # Fetch the generated content
            logging.info(f"Generated message: {new_message}")
            return new_message
        else:
            logging.error("No response generated.")
            return "Samahani, kuna tatizo. Tafadhali jaribu tena baadaye."

    except Exception as e:
        logging.error(f"Error running assistant: {str(e)}")
        return "Samahani, kuna tatizo. Tafadhali jaribu tena baadaye."

# Generate a response based on the user's input
def generate_response(message_body, wa_id, name):
    # Check if a conversation thread already exists for this WhatsApp user
    thread_id = check_if_thread_exists(wa_id)

    # If the thread doesn't exist, create one and store it
    if thread_id is None:
        logging.info(f"Creating a new thread for {name} with wa_id {wa_id}")
        thread_id = f"thread_{wa_id}_{int(time.time())}"  # Create a unique thread ID
        store_thread(wa_id, thread_id)
    else:
        # Retrieve the existing thread for this user
        logging.info(f"Retrieving existing thread for {name} with wa_id {wa_id}")

    # Add the user's message to the conversation thread (in-memory for now)
    logging.info(f"Processing message from {name}: {message_body}")

    # Run the assistant and get the response
    new_message = run_assistant(thread_id, name, message_body)

    return new_message
