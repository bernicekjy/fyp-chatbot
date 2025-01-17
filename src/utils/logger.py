import logging

def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # Avoid duplicate handlers in nested imports
        logger.setLevel(logging.DEBUG)

        # Create a console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # Create a formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(formatter)

        # Add the handler
        logger.addHandler(console_handler)
    
    return logger
