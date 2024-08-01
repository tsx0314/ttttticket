import json

# Import the logger setup function
from logger_setup import setup_logging

# Set up the logger
logger = setup_logging()

def load_config():
    try:
        with open('config.json', 'r') as file:
            config = json.load(file)
    except FileNotFoundError as e:
        logger.error("Configuration file not found: %s", e)
        raise
    return config
