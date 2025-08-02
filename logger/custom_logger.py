import os
import logging
from datetime import datetime
import structlog

class CustomLogger:
    _instance = None
    _initialized = False
    
    def __new__(cls, log_dir="logs"):
        if cls._instance is None:
            cls._instance = super(CustomLogger, cls).__new__(cls)
        return cls._instance
    
    def __init__(self, log_dir="logs"):
        if self._initialized:
            return
            
        # Ensure logs directory exists
        self.logs_dir = os.path.join(os.getcwd(), log_dir)
        os.makedirs(self.logs_dir, exist_ok=True)

        # Timestamped log file (for persistence) - only create once
        log_file = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
        self.log_file_path = os.path.join(self.logs_dir, log_file)
        
        # Configure logging only once
        self._configure_logging()
        self._initialized = True

    def _configure_logging(self):
        # Clear any existing handlers to avoid duplicates
        logging.getLogger().handlers.clear()
        
        # Configure logging for console + file (both JSON)
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter("%(message)s"))  # Raw JSON lines

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter("%(message)s"))

        logging.basicConfig(
            level=logging.INFO,
            format="%(message)s",  # Structlog will handle JSON rendering
            handlers=[console_handler, file_handler],
            force=True  # Force reconfiguration
        )

        # Configure structlog for JSON structured logging
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="iso", utc=True, key="timestamp"),
                structlog.processors.add_log_level,
                structlog.processors.EventRenamer(to="event"),
                structlog.processors.JSONRenderer()
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

    def get_logger(self, name=__file__):
        logger_name = os.path.basename(name)
        return structlog.get_logger(logger_name)
    
    def get_log_file_path(self):
        """Return the current log file path"""
        return self.log_file_path


# --- Usage Example ---
if __name__ == "__main__":
    logger = CustomLogger().get_logger(__file__)
    logger.info("User uploaded a file", user_id=123, filename="report.pdf")
    logger.error("Failed to process PDF", error="File not found", user_id=123)