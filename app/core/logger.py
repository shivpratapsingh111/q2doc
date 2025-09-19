# External imports
import logging, os

# Local imports
from app.config.config import LOGS_DIR

# -- Colored Formatter for console --
class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": "\033[94m",  # Blue
        "INFO": "\033[92m",  # Green
        "WARNING": "\033[93m",  # Yellow
        "ERROR": "\033[91m",  # Red
        "CRITICAL": "\033[41m",  # Red background
    }
    RESET = "\033[0m"

    def format(self, record):
        levelname = record.levelname
        color = self.COLORS.get(levelname, self.RESET)
        record.levelname = f"{color}{levelname}{self.RESET}"
        return super().format(record)


# -- Logger setup function --
def setup_logger(name, log_file_path, enable_debug: bool = False):
    # Create the logger instance
    logger = logging.getLogger(name)

    os.makedirs(LOGS_DIR, exist_ok=True)

    log_level = logging.DEBUG if enable_debug else logging.INFO
    logger.setLevel(log_level)

    logger.propagate = False

    # Prevent duplicate log entries
    if not logger.hasHandlers():
        log_format = "%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s"

        # File handler (plain)
        file_handler = logging.FileHandler(f"{LOGS_DIR}/{log_file_path}", mode="a")
        file_handler.setFormatter(logging.Formatter(log_format))

        # Console handler (colored)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(ColorFormatter(log_format))

        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
