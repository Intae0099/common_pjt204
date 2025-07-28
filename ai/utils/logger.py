
import logging
import logging.config
import os
from datetime import datetime

def setup_logger():
    LOG_DIR = "logs"
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    log_format = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
    log_file = f"{datetime.now().strftime('%Y-%m-%d')}.log"

    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.FileHandler(os.path.join(LOG_DIR, log_file), encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

def get_logger(name: str):
    return logging.getLogger(name)
