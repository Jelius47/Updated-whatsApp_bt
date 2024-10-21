import sys
import os
from dotenv import load_dotenv
import logging


# config test

def load_configurations_(app):
    # Load environment variables
    load_dotenv()

    # Load each configuration and log or raise an error if any are missing
    required_configs = [
        "ACCESS_TOKEN", 
        "YOUR_PHONE_NUMBER", 
        "APP_ID", 
        "APP_SECRET", 
        "RECIPIENT_WAID", 
        "VERSION", 
        "PHONE_NUMBER_ID", 
        "VERIFY_TOKEN"
    ]

    for config in required_configs:
        value = os.getenv(config)
        if value:
            app.config[config] = value
            logging.info(f"{config} successfully loaded")
        else:
            # Raise an error if any required config is missing
            raise ValueError(f"Missing required environment variable: {config}")


def load_configurations(app):
    load_dotenv()
    app.config["ACCESS_TOKEN"] = os.getenv("ACCESS_TOKEN")
    app.config["YOUR_PHONE_NUMBER"] = os.getenv("YOUR_PHONE_NUMBER")
    app.config["APP_ID"] = os.getenv("APP_ID")
    app.config["APP_SECRET"] = os.getenv("APP_SECRET")
    app.config["RECIPIENT_WAID"] = os.getenv("RECIPIENT_WAID")
    app.config["VERSION"] = os.getenv("VERSION")
    app.config["PHONE_NUMBER_ID"] = os.getenv("PHONE_NUMBER_ID")
    app.config["VERIFY_TOKEN"] = os.getenv("VERIFY_TOKEN")


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )
