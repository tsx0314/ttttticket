import json
import logging.config

# Load logging configuration from file
def setup_logging():
    with open('logging_config.json', 'r') as file:
        config_dict = json.load(file)
        logging.config.dictConfig(config_dict)
    logger = logging.getLogger(__name__)
    return logger