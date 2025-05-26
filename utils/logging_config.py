"""
Logging configuration for AI NVCB application.

This module provides centralized logging configuration for all components
of the AI NVCB application including backend, frontend, and utilities.
"""

import os
import logging
import logging.config
from pathlib import Path
from datetime import datetime


def setup_logging(
    log_level: str = None,
    log_file: str = None,
    log_format: str = None,
    enable_file_logging: bool = True,
    enable_console_logging: bool = True
) -> None:
    """
    Setup application logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file
        log_format: Log message format
        enable_file_logging: Whether to enable file logging
        enable_console_logging: Whether to enable console logging
    """
    # Get configuration from environment
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO").upper()
    log_file = log_file or os.getenv("LOG_FILE", "logs/ai_nvcb.log")
    log_format = log_format or os.getenv(
        "LOG_FORMAT", 
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Create logs directory
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure logging
    handlers = []
    
    # Console handler
    if enable_console_logging:
        console_handler = {
            'class': 'logging.StreamHandler',
            'level': log_level,
            'formatter': 'standard',
            'stream': 'ext://sys.stdout'
        }
        handlers.append('console')
    
    # File handler
    if enable_file_logging:
        file_handler = {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': log_level,
            'formatter': 'standard',
            'filename': log_file,
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'encoding': 'utf-8'
        }
        handlers.append('file')
    
    # Logging configuration
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': log_format,
                'datefmt': '%Y-%m-%d %H:%M:%S'
            },
            'detailed': {
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s',
                'datefmt': '%Y-%m-%d %H:%M:%S'
            }
        },
        'handlers': {
            'console': console_handler if enable_console_logging else None,
            'file': file_handler if enable_file_logging else None
        },
        'loggers': {
            'ai_nvcb': {
                'level': log_level,
                'handlers': [h for h in handlers if h],
                'propagate': False
            },
            'backend': {
                'level': log_level,
                'handlers': [h for h in handlers if h],
                'propagate': False
            },
            'frontend': {
                'level': log_level,
                'handlers': [h for h in handlers if h],
                'propagate': False
            },
            'utils': {
                'level': log_level,
                'handlers': [h for h in handlers if h],
                'propagate': False
            },
            'uvicorn': {
                'level': 'INFO',
                'handlers': [h for h in handlers if h],
                'propagate': False
            },
            'fastapi': {
                'level': 'INFO',
                'handlers': [h for h in handlers if h],
                'propagate': False
            }
        },
        'root': {
            'level': log_level,
            'handlers': [h for h in handlers if h]
        }
    }
    
    # Remove None handlers
    config['handlers'] = {k: v for k, v in config['handlers'].items() if v is not None}
    
    # Apply configuration
    logging.config.dictConfig(config)
    
    # Log startup message
    logger = logging.getLogger('ai_nvcb')
    logger.info(f"Logging initialized - Level: {log_level}, File: {log_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(f"ai_nvcb.{name}")


def log_request(request_id: str, method: str, url: str, status_code: int = None, duration: float = None):
    """
    Log HTTP request information.
    
    Args:
        request_id: Unique request identifier
        method: HTTP method
        url: Request URL
        status_code: Response status code
        duration: Request duration in seconds
    """
    logger = get_logger('requests')
    
    if status_code and duration:
        logger.info(f"[{request_id}] {method} {url} -> {status_code} ({duration:.3f}s)")
    else:
        logger.info(f"[{request_id}] {method} {url}")


def log_error(error: Exception, context: str = None, request_id: str = None):
    """
    Log error information with context.
    
    Args:
        error: Exception instance
        context: Additional context information
        request_id: Request identifier if applicable
    """
    logger = get_logger('errors')
    
    error_msg = f"{type(error).__name__}: {str(error)}"
    
    if request_id:
        error_msg = f"[{request_id}] {error_msg}"
    
    if context:
        error_msg = f"{error_msg} (Context: {context})"
    
    logger.error(error_msg, exc_info=True)


def log_performance(operation: str, duration: float, details: dict = None):
    """
    Log performance metrics.
    
    Args:
        operation: Operation name
        duration: Operation duration in seconds
        details: Additional performance details
    """
    logger = get_logger('performance')
    
    msg = f"{operation}: {duration:.3f}s"
    
    if details:
        details_str = ", ".join([f"{k}={v}" for k, v in details.items()])
        msg = f"{msg} ({details_str})"
    
    logger.info(msg)


# Initialize logging on module import
if not logging.getLogger().handlers:
    setup_logging()
