import logging
from logging.handlers import RotatingFileHandler

def setup_logger(name="my_logger", log_file="log.log", level=logging.DEBUG):
    """
    Sets up a logger with both console and file handlers.
    
    :param name: Name of the logger
    :param log_file: Log file name
    :param level: Logging level (default: DEBUG)
    :return: Configured logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent adding multiple handlers if function is called multiple times
    if not logger.hasHandlers():
        # Console Handler (logs everything)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)

        # File Handler (logs only ERROR and above, with rotation)
        file_handler = RotatingFileHandler(log_file, maxBytes=5000000, encoding='utf-8')
        file_handler.setLevel(level)

        # Formatter with filename and line number
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)

        # Add handlers to the logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger
