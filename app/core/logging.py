
# app/core/logging.py
import logging
import sys
from typing import Any, Dict, Optional

from loguru import logger
from pydantic import BaseModel

from app.core.config import settings


class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        logger_opt = logger.opt(depth=7, exception=record.exc_info)
        logger_opt.log(record.levelname, record.getMessage())


class LogConfig(BaseModel):
    """Logging configuration"""
    LOGGER_NAME: str = "fastapi-app"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    LOG_LEVEL: str = settings.LOG_LEVEL

    # Configure handlers
    handlers: Dict[str, Dict[str, Any]] = {
        "default": {
            "sink": sys.stderr,
            "format": LOG_FORMAT,
            "level": LOG_LEVEL,
        },
    }

    # Add file logger in production
    if settings.ENV == "prod":
        handlers["file"] = {
            "sink": "/var/log/app/app.log",
            "format": LOG_FORMAT,
            "level": LOG_LEVEL,
            "rotation": "20 MB",
            "retention": "1 month",
            "compression": "zip",
        }


def setup_logging() -> None:
    """Set up logging configuration"""
    config = LogConfig()

    # Remove default loggers
    logger.remove()

    # Configure loguru
    for handler_name, handler_config in config.handlers.items():
        logger.configure(handlers=[handler_config])

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0)
    
    # Replace logging handlers with loguru
    for _log in [
        logging.getLogger(name) 
        for name in logging.root.manager.loggerDict
        if name.startswith("uvicorn")
    ]:
        _log.handlers = [InterceptHandler()]
