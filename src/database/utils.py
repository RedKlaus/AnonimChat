from loguru import logger

from src.init_data import config


def log_debug(message: str):
    if config.config_data.database.log_debug:
        logger.debug(message)
