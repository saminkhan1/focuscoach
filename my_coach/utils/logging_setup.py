import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

_LOGGING_INITIALIZED = False

def setup_logging(
    logger_name: Optional[str] = None,
    log_file: Optional[str] = None,
    log_level: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging with industry-standard practices.
    Should be called once at application startup.
    """
    global _LOGGING_INITIALIZED
    
    # Get settings from environment with defaults
    env = os.getenv("ENV", "development")
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_dir = Path("logs")
    
    # Configure root logger only once
    if not _LOGGING_INITIALIZED:
        # Create logs directory if it doesn't exist
        log_dir.mkdir(exist_ok=True)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, log_level.upper()))
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)-12s | %(levelname)-8s | %(message)s | [%(filename)s:%(lineno)d]',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Console handler (always enabled)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        root_logger.addHandler(console_handler)
        
        # File handlers for production/staging
        if env in ["production", "staging"]:
            # Regular file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_dir / (log_file or "app.log"),
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(file_handler)
            
            # Error file handler
            error_handler = logging.handlers.RotatingFileHandler(
                log_dir / "error.log",
                maxBytes=10*1024*1024,
                backupCount=5
            )
            error_handler.setLevel(logging.ERROR)
            error_handler.setFormatter(detailed_formatter)
            root_logger.addHandler(error_handler)
        
        _LOGGING_INITIALIZED = True
    
    # Return logger for the specified name
    return logging.getLogger(logger_name)