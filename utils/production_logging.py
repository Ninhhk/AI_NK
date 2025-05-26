"""
Production logging configuration for AI NVCB application.

This module provides enhanced logging configuration for production deployments
including structured logging, metrics collection, monitoring integration,
and advanced log processing capabilities.
"""

import os
import json
import logging
import logging.handlers
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
import asyncio
import aiofiles
from dataclasses import dataclass, asdict
import traceback

try:
    import elasticsearch
    HAS_ELASTICSEARCH = True
except ImportError:
    HAS_ELASTICSEARCH = False

try:
    import prometheus_client
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False


@dataclass
class LogEntry:
    """Structured log entry for JSON logging."""
    timestamp: str
    level: str
    logger: str
    message: str
    module: str
    function: str
    line: int
    request_id: Optional[str] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    trace_id: Optional[str] = None
    span_id: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None
    exception: Optional[Dict[str, Any]] = None


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        # Extract exception information
        exception_info = None
        if record.exc_info:
            exception_info = {
                'type': record.exc_info[0].__name__ if record.exc_info[0] else None,
                'message': str(record.exc_info[1]) if record.exc_info[1] else None,
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Create log entry
        log_entry = LogEntry(
            timestamp=datetime.utcnow().isoformat() + 'Z',
            level=record.levelname,
            logger=record.name,
            message=record.getMessage(),
            module=record.module,
            function=record.funcName,
            line=record.lineno,
            request_id=getattr(record, 'request_id', None),
            user_id=getattr(record, 'user_id', None),
            session_id=getattr(record, 'session_id', None),
            trace_id=getattr(record, 'trace_id', None),
            span_id=getattr(record, 'span_id', None),
            extra=getattr(record, 'extra', None),
            exception=exception_info
        )
        
        # Convert to JSON
        return json.dumps(asdict(log_entry), default=str, ensure_ascii=False)


class ElasticsearchHandler(logging.Handler):
    """Custom handler for sending logs to Elasticsearch."""
    
    def __init__(self, elasticsearch_url: str, index_prefix: str = "ai-nvcb-logs"):
        super().__init__()
        self.elasticsearch_url = elasticsearch_url
        self.index_prefix = index_prefix
        self.es_client = None
        
        if HAS_ELASTICSEARCH:
            try:
                self.es_client = elasticsearch.Elasticsearch([elasticsearch_url])
            except Exception as e:
                print(f"Failed to initialize Elasticsearch client: {e}")
    
    def emit(self, record: logging.LogRecord) -> None:
        """Send log record to Elasticsearch."""
        if not self.es_client:
            return
        
        try:
            # Format log record
            formatted_record = json.loads(self.format(record))
            
            # Create index name with date
            index_name = f"{self.index_prefix}-{datetime.utcnow().strftime('%Y.%m.%d')}"
            
            # Send to Elasticsearch
            self.es_client.index(
                index=index_name,
                body=formatted_record
            )
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Failed to send log to Elasticsearch: {e}")


class PrometheusLoggingHandler(logging.Handler):
    """Handler for collecting logging metrics with Prometheus."""
    
    def __init__(self):
        super().__init__()
        self.log_counter = None
        self.error_counter = None
        
        if HAS_PROMETHEUS:
            self.log_counter = prometheus_client.Counter(
                'ai_nvcb_log_messages_total',
                'Total log messages',
                ['level', 'logger']
            )
            self.error_counter = prometheus_client.Counter(
                'ai_nvcb_errors_total',
                'Total errors',
                ['error_type', 'module']
            )
    
    def emit(self, record: logging.LogRecord) -> None:
        """Update Prometheus metrics."""
        if not self.log_counter:
            return
        
        try:
            # Count log messages
            self.log_counter.labels(
                level=record.levelname,
                logger=record.name
            ).inc()
            
            # Count errors
            if record.levelname in ['ERROR', 'CRITICAL'] and record.exc_info:
                error_type = record.exc_info[0].__name__ if record.exc_info[0] else 'Unknown'
                self.error_counter.labels(
                    error_type=error_type,
                    module=record.module
                ).inc()
        except Exception:
            # Don't let metrics collection break logging
            pass


class ProductionLoggingManager:
    """Manager for production logging configuration."""
    
    def __init__(self):
        self.config = self._load_config()
        self.handlers = {}
        self.log_aggregator = LogAggregator()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load logging configuration from environment."""
        return {
            'log_level': os.getenv('LOG_LEVEL', 'INFO'),
            'log_format': os.getenv('LOG_FORMAT', 'json'),
            'log_file': os.getenv('LOG_FILE', 'logs/ai_nvcb.log'),
            'log_rotation_size': int(os.getenv('LOG_ROTATION_SIZE', '50000000')),  # 50MB
            'log_backup_count': int(os.getenv('LOG_BACKUP_COUNT', '10')),
            'log_compression': os.getenv('LOG_COMPRESSION', 'gzip'),
            'enable_console_logging': os.getenv('ENABLE_CONSOLE_LOGGING', 'true').lower() == 'true',
            'enable_file_logging': os.getenv('ENABLE_FILE_LOGGING', 'true').lower() == 'true',
            'enable_elasticsearch': os.getenv('ENABLE_ELASTICSEARCH_LOGGING', 'false').lower() == 'true',
            'enable_prometheus': os.getenv('ENABLE_PROMETHEUS_LOGGING', 'false').lower() == 'true',
            'elasticsearch_url': os.getenv('ELASTICSEARCH_URL', 'http://localhost:9200'),
            'log_index_prefix': os.getenv('LOG_INDEX_PREFIX', 'ai-nvcb-logs'),
            'sensitive_fields': os.getenv('SENSITIVE_LOG_FIELDS', 'password,token,key,secret').split(','),
            'log_sampling_rate': float(os.getenv('LOG_SAMPLING_RATE', '1.0')),
            'async_logging': os.getenv('ASYNC_LOGGING', 'false').lower() == 'true'
        }
    
    def setup_production_logging(self) -> None:
        """Setup comprehensive production logging."""
        # Create logs directory
        log_dir = Path(self.config['log_file']).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        
        # Configure formatters
        formatters = self._create_formatters()
        
        # Configure handlers
        handlers = self._create_handlers(formatters)
        
        # Configure loggers
        self._configure_loggers(handlers)
        
        # Setup log aggregation
        if self.config['async_logging']:
            asyncio.create_task(self.log_aggregator.start())
        
        # Log startup message
        logger = logging.getLogger('ai_nvcb.production')
        logger.info("Production logging initialized", extra={
            'config': self._sanitize_config(self.config)
        })
    
    def _create_formatters(self) -> Dict[str, logging.Formatter]:
        """Create logging formatters."""
        formatters = {}
        
        if self.config['log_format'] == 'json':
            formatters['json'] = JSONFormatter()
            formatters['console'] = JSONFormatter()
        else:
            detailed_format = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(module)s:%(funcName)s:%(lineno)d - %(message)s'
            )
            formatters['detailed'] = logging.Formatter(
                detailed_format,
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            formatters['console'] = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
        
        return formatters
    
    def _create_handlers(self, formatters: Dict[str, logging.Formatter]) -> Dict[str, logging.Handler]:
        """Create logging handlers."""
        handlers = {}
        
        # Console handler
        if self.config['enable_console_logging']:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self.config['log_level'])
            console_handler.setFormatter(formatters['console'])
            handlers['console'] = console_handler
        
        # File handler with rotation
        if self.config['enable_file_logging']:
            file_handler = logging.handlers.RotatingFileHandler(
                filename=self.config['log_file'],
                maxBytes=self.config['log_rotation_size'],
                backupCount=self.config['log_backup_count'],
                encoding='utf-8'
            )
            file_handler.setLevel(self.config['log_level'])
            
            # Use JSON formatter for file logging
            formatter_key = 'json' if self.config['log_format'] == 'json' else 'detailed'
            file_handler.setFormatter(formatters[formatter_key])
            handlers['file'] = file_handler
        
        # Elasticsearch handler
        if self.config['enable_elasticsearch'] and HAS_ELASTICSEARCH:
            es_handler = ElasticsearchHandler(
                self.config['elasticsearch_url'],
                self.config['log_index_prefix']
            )
            es_handler.setLevel(self.config['log_level'])
            es_handler.setFormatter(formatters['json'])
            handlers['elasticsearch'] = es_handler
        
        # Prometheus metrics handler
        if self.config['enable_prometheus'] and HAS_PROMETHEUS:
            prometheus_handler = PrometheusLoggingHandler()
            prometheus_handler.setLevel('WARNING')  # Only collect error metrics
            handlers['prometheus'] = prometheus_handler
        
        return handlers
    
    def _configure_loggers(self, handlers: Dict[str, logging.Handler]) -> None:
        """Configure application loggers."""
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(self.config['log_level'])
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Add handlers
        for handler in handlers.values():
            root_logger.addHandler(handler)
        
        # Configure specific loggers
        logger_configs = {
            'ai_nvcb': self.config['log_level'],
            'backend': self.config['log_level'],
            'frontend': self.config['log_level'],
            'utils': self.config['log_level'],
            'uvicorn': 'INFO',
            'fastapi': 'INFO',
            'sqlalchemy': 'WARNING',
            'aiohttp': 'INFO'
        }
        
        for logger_name, level in logger_configs.items():
            logger = logging.getLogger(logger_name)
            logger.setLevel(level)
            logger.propagate = True
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Remove sensitive information from config for logging."""
        sanitized = config.copy()
        
        # Remove sensitive fields
        sensitive_keys = ['elasticsearch_url', 'password', 'token', 'secret']
        for key in sensitive_keys:
            if key in sanitized:
                sanitized[key] = '[REDACTED]'
        
        return sanitized
    
    def get_enhanced_logger(self, name: str) -> 'EnhancedLogger':
        """Get an enhanced logger with additional functionality."""
        return EnhancedLogger(name, self.config)


class EnhancedLogger:
    """Enhanced logger with additional production features."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        self.logger = logging.getLogger(f"ai_nvcb.{name}")
        self.config = config
        self.request_context = {}
    
    def set_request_context(self, request_id: str = None, user_id: str = None, 
                          session_id: str = None, trace_id: str = None, span_id: str = None):
        """Set request context for correlation."""
        self.request_context = {
            'request_id': request_id,
            'user_id': user_id,
            'session_id': session_id,
            'trace_id': trace_id,
            'span_id': span_id
        }
    
    def _add_context(self, extra: Dict[str, Any] = None) -> Dict[str, Any]:
        """Add request context to log entry."""
        context = self.request_context.copy()
        if extra:
            context.update(extra)
        return context
    
    def debug(self, message: str, extra: Dict[str, Any] = None):
        """Log debug message with context."""
        self.logger.debug(message, extra=self._add_context(extra))
    
    def info(self, message: str, extra: Dict[str, Any] = None):
        """Log info message with context."""
        self.logger.info(message, extra=self._add_context(extra))
    
    def warning(self, message: str, extra: Dict[str, Any] = None):
        """Log warning message with context."""
        self.logger.warning(message, extra=self._add_context(extra))
    
    def error(self, message: str, exc_info: bool = True, extra: Dict[str, Any] = None):
        """Log error message with context and exception info."""
        self.logger.error(message, exc_info=exc_info, extra=self._add_context(extra))
    
    def critical(self, message: str, exc_info: bool = True, extra: Dict[str, Any] = None):
        """Log critical message with context and exception info."""
        self.logger.critical(message, exc_info=exc_info, extra=self._add_context(extra))
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics."""
        extra = {'operation': operation, 'duration': duration}
        if details:
            extra.update(details)
        
        self.info(f"Performance: {operation} completed in {duration:.3f}s", extra=extra)
    
    def log_security_event(self, event_type: str, severity: str, details: Dict[str, Any] = None):
        """Log security-related events."""
        extra = {
            'event_type': event_type,
            'severity': severity,
            'security_event': True
        }
        if details:
            extra.update(details)
        
        if severity in ['high', 'critical']:
            self.error(f"Security Event: {event_type}", extra=extra)
        else:
            self.warning(f"Security Event: {event_type}", extra=extra)


class LogAggregator:
    """Asynchronous log aggregation for high-volume logging."""
    
    def __init__(self, buffer_size: int = 1000, flush_interval: int = 5):
        self.buffer_size = buffer_size
        self.flush_interval = flush_interval
        self.log_buffer = []
        self.running = False
    
    async def start(self):
        """Start the log aggregation service."""
        self.running = True
        while self.running:
            await asyncio.sleep(self.flush_interval)
            await self.flush_logs()
    
    async def flush_logs(self):
        """Flush buffered logs to storage."""
        if not self.log_buffer:
            return
        
        # Process buffered logs
        logs_to_process = self.log_buffer.copy()
        self.log_buffer.clear()
        
        # Here you would implement batch processing to external systems
        # For example, bulk insert to Elasticsearch, send to log aggregation service, etc.
        pass
    
    def stop(self):
        """Stop the log aggregation service."""
        self.running = False


# Global production logging manager
production_logging_manager = ProductionLoggingManager()


def setup_production_logging():
    """Setup production logging configuration."""
    production_logging_manager.setup_production_logging()


def get_production_logger(name: str) -> EnhancedLogger:
    """Get a production-ready enhanced logger."""
    return production_logging_manager.get_enhanced_logger(name)


# Initialize production logging
if os.getenv('ENVIRONMENT', 'development').lower() == 'production':
    setup_production_logging()
