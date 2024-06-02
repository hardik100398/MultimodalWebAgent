from src.webdriver.webdriver import WebDriver
from src.configs.logging.logging_config import setup_logging

import logging

setup_logging()
logger = logging.getLogger()


async def get_webdriver_instance():
    """
    Returns an instance of the WebDriver.

    Args:
        None

    Returns:
        WebDriver: An instance of the WebDriver.
    """
    try:
        instance = await WebDriver.getInstance()
        driver = instance.getDriver()
        return driver
    except Exception as e:
        logger.error("Failed to get WebDriver instance: %s", e, exc_info=True)
        raise
