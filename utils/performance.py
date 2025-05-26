"""
Performance optimization utilities for AI NVCB application.

This module provides comprehensive performance optimization features including
caching, connection pooling, request optimization, memory management,
and performance monitoring.
"""

import os
import time
import asyncio
import hashlib
from typing import Dict, Any, Optional, Callable, Union, List
from datetime import datetime, timedelta
from functools import wraps, lru_cache
from contextlib import asynccontextmanager
import pickle
import json
import psutil
from pathlib import Path

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

try:
    import aioredis
    HAS_AIOREDIS = True
except ImportError:
    HAS_AIOREDIS = False

try:
    from prometheus_client import Counter, Histogram, Gauge
    HAS_PROMETHEUS = True
except ImportError:
    HAS_PROMETHEUS = False

from utils.production_logging import get_production_logger

logger = get_production_logger('performance')


class PerformanceMetrics:
    """Centralized performance metrics collection."""
    
    def __init__(self):
        self.metrics = {}
        self.prometheus_metrics = {}
        
        if HAS_PROMETHEUS:
            self._setup_prometheus_metrics()
    
    def _setup_prometheus_metrics(self):
        """Setup Prometheus metrics."""
        self.prometheus_metrics = {
            'request_duration': Histogram(
                'ai_nvcb_request_duration_seconds',
                'Request duration in seconds',
                ['method', 'endpoint', 'status']
            ),
            'cache_hits': Counter(
                'ai_nvcb_cache_hits_total',
                'Total cache hits',
                ['cache_type', 'key_pattern']
            ),
            'cache_misses': Counter(
                'ai_nvcb_cache_misses_total',
                'Total cache misses',
                ['cache_type', 'key_pattern']
            ),
            'memory_usage': Gauge(
                'ai_nvcb_memory_usage_bytes',
                'Memory usage in bytes',
                ['type']
            ),
            'cpu_usage': Gauge(
                'ai_nvcb_cpu_usage_percent',
                'CPU usage percentage'
            ),
            'active_connections': Gauge(
                'ai_nvcb_active_connections',
                'Number of active connections',
                ['type']
            ),
            'ollama_requests': Counter(
                'ai_nvcb_ollama_requests_total',
                'Total Ollama requests',
                ['model', 'status']
            ),
            'ollama_duration': Histogram(
                'ai_nvcb_ollama_duration_seconds',
                'Ollama request duration in seconds',
                ['model']
            )
        }
    
    def record_request_duration(self, method: str, endpoint: str, status: int, duration: float):
        """Record HTTP request duration."""
        if HAS_PROMETHEUS and 'request_duration' in self.prometheus_metrics:
            self.prometheus_metrics['request_duration'].labels(
                method=method,
                endpoint=endpoint,
                status=str(status)
            ).observe(duration)
        
        # Store in local metrics
        key = f"{method}:{endpoint}"
        if key not in self.metrics:
            self.metrics[key] = []
        self.metrics[key].append({
            'duration': duration,
            'status': status,
            'timestamp': datetime.utcnow()
        })
    
    def record_cache_hit(self, cache_type: str, key_pattern: str):
        """Record cache hit."""
        if HAS_PROMETHEUS and 'cache_hits' in self.prometheus_metrics:
            self.prometheus_metrics['cache_hits'].labels(
                cache_type=cache_type,
                key_pattern=key_pattern
            ).inc()
    
    def record_cache_miss(self, cache_type: str, key_pattern: str):
        """Record cache miss."""
        if HAS_PROMETHEUS and 'cache_misses' in self.prometheus_metrics:
            self.prometheus_metrics['cache_misses'].labels(
                cache_type=cache_type,
                key_pattern=key_pattern
            ).inc()
    
    def update_system_metrics(self):
        """Update system resource metrics."""
        if not HAS_PROMETHEUS:
            return
        
        # Memory metrics
        memory = psutil.virtual_memory()
        if 'memory_usage' in self.prometheus_metrics:
            self.prometheus_metrics['memory_usage'].labels(type='total').set(memory.total)
            self.prometheus_metrics['memory_usage'].labels(type='used').set(memory.used)
            self.prometheus_metrics['memory_usage'].labels(type='available').set(memory.available)
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent()
        if 'cpu_usage' in self.prometheus_metrics:
            self.prometheus_metrics['cpu_usage'].set(cpu_percent)


class CacheManager:
    """Advanced caching manager with multiple backends."""
    
    def __init__(self):
        self.local_cache = {}
        self.redis_client = None
        self.redis_async_client = None
        self.config = self._load_config()
        self.metrics = PerformanceMetrics()
        
        if HAS_REDIS and self.config['redis_enabled']:
            self._setup_redis()
        
        if HAS_AIOREDIS and self.config['redis_enabled']:
            self._setup_async_redis()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load cache configuration."""
        return {
            'redis_enabled': os.getenv('REDIS_CACHE_ENABLED', 'false').lower() == 'true',
            'redis_url': os.getenv('REDIS_URL', 'redis://localhost:6379/1'),
            'default_ttl': int(os.getenv('CACHE_DEFAULT_TTL', '3600')),  # 1 hour
            'max_local_cache_size': int(os.getenv('MAX_LOCAL_CACHE_SIZE', '1000')),
            'cache_compression': os.getenv('CACHE_COMPRESSION', 'false').lower() == 'true',
            'cache_prefix': os.getenv('CACHE_PREFIX', 'ai_nvcb:')
        }
    
    def _setup_redis(self):
        """Setup Redis client."""
        try:
            self.redis_client = redis.from_url(self.config['redis_url'])
            self.redis_client.ping()
            logger.info("Redis cache client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize Redis cache: {e}")
            self.redis_client = None
    
    async def _setup_async_redis(self):
        """Setup async Redis client."""
        try:
            self.redis_async_client = aioredis.from_url(self.config['redis_url'])
            await self.redis_async_client.ping()
            logger.info("Async Redis cache client initialized")
        except Exception as e:
            logger.warning(f"Failed to initialize async Redis cache: {e}")
            self.redis_async_client = None
    
    def _get_cache_key(self, key: str) -> str:
        """Generate cache key with prefix."""
        return f"{self.config['cache_prefix']}{key}"
    
    def _serialize_value(self, value: Any) -> bytes:
        """Serialize value for caching."""
        if self.config['cache_compression']:
            import zlib
            return zlib.compress(pickle.dumps(value))
        return pickle.dumps(value)
    
    def _deserialize_value(self, data: bytes) -> Any:
        """Deserialize cached value."""
        if self.config['cache_compression']:
            import zlib
            return pickle.loads(zlib.decompress(data))
        return pickle.loads(data)
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        cache_key = self._get_cache_key(key)
        
        # Try local cache first
        if cache_key in self.local_cache:
            entry = self.local_cache[cache_key]
            if entry['expires'] > datetime.utcnow():
                self.metrics.record_cache_hit('local', 'general')
                return entry['value']
            else:
                del self.local_cache[cache_key]
        
        # Try Redis cache
        if self.redis_client:
            try:
                data = self.redis_client.get(cache_key)
                if data:
                    value = self._deserialize_value(data)
                    self.metrics.record_cache_hit('redis', 'general')
                    return value
            except Exception as e:
                logger.warning(f"Redis cache get error: {e}")
        
        self.metrics.record_cache_miss('local_and_redis', 'general')
        return None
    
    async def aget(self, key: str) -> Optional[Any]:
        """Async get value from cache."""
        cache_key = self._get_cache_key(key)
        
        # Try local cache first
        if cache_key in self.local_cache:
            entry = self.local_cache[cache_key]
            if entry['expires'] > datetime.utcnow():
                self.metrics.record_cache_hit('local', 'general')
                return entry['value']
            else:
                del self.local_cache[cache_key]
        
        # Try async Redis cache
        if self.redis_async_client:
            try:
                data = await self.redis_async_client.get(cache_key)
                if data:
                    value = self._deserialize_value(data)
                    self.metrics.record_cache_hit('redis', 'general')
                    return value
            except Exception as e:
                logger.warning(f"Async Redis cache get error: {e}")
        
        self.metrics.record_cache_miss('local_and_redis', 'general')
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache."""
        cache_key = self._get_cache_key(key)
        ttl = ttl or self.config['default_ttl']
        expires = datetime.utcnow() + timedelta(seconds=ttl)
        
        # Set in local cache
        if len(self.local_cache) >= self.config['max_local_cache_size']:
            # Remove oldest entries
            oldest_key = min(self.local_cache.keys(), 
                           key=lambda k: self.local_cache[k]['created'])
            del self.local_cache[oldest_key]
        
        self.local_cache[cache_key] = {
            'value': value,
            'expires': expires,
            'created': datetime.utcnow()
        }
        
        # Set in Redis cache
        if self.redis_client:
            try:
                serialized_value = self._serialize_value(value)
                self.redis_client.setex(cache_key, ttl, serialized_value)
                return True
            except Exception as e:
                logger.warning(f"Redis cache set error: {e}")
        
        return True
    
    async def aset(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Async set value in cache."""
        cache_key = self._get_cache_key(key)
        ttl = ttl or self.config['default_ttl']
        expires = datetime.utcnow() + timedelta(seconds=ttl)
        
        # Set in local cache
        if len(self.local_cache) >= self.config['max_local_cache_size']:
            # Remove oldest entries
            oldest_key = min(self.local_cache.keys(), 
                           key=lambda k: self.local_cache[k]['created'])
            del self.local_cache[oldest_key]
        
        self.local_cache[cache_key] = {
            'value': value,
            'expires': expires,
            'created': datetime.utcnow()
        }
        
        # Set in async Redis cache
        if self.redis_async_client:
            try:
                serialized_value = self._serialize_value(value)
                await self.redis_async_client.setex(cache_key, ttl, serialized_value)
                return True
            except Exception as e:
                logger.warning(f"Async Redis cache set error: {e}")
        
        return True
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        cache_key = self._get_cache_key(key)
        
        # Delete from local cache
        if cache_key in self.local_cache:
            del self.local_cache[cache_key]
        
        # Delete from Redis cache
        if self.redis_client:
            try:
                self.redis_client.delete(cache_key)
                return True
            except Exception as e:
                logger.warning(f"Redis cache delete error: {e}")
        
        return True
    
    def clear(self, pattern: str = None) -> bool:
        """Clear cache entries."""
        if pattern:
            # Clear by pattern
            pattern_key = self._get_cache_key(pattern)
            
            # Clear from local cache
            keys_to_delete = [k for k in self.local_cache.keys() if pattern_key in k]
            for key in keys_to_delete:
                del self.local_cache[key]
            
            # Clear from Redis cache
            if self.redis_client:
                try:
                    keys = self.redis_client.keys(f"{pattern_key}*")
                    if keys:
                        self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis cache clear error: {e}")
        else:
            # Clear all
            self.local_cache.clear()
            
            if self.redis_client:
                try:
                    keys = self.redis_client.keys(f"{self.config['cache_prefix']}*")
                    if keys:
                        self.redis_client.delete(*keys)
                except Exception as e:
                    logger.warning(f"Redis cache clear all error: {e}")
        
        return True


class ConnectionPool:
    """Connection pool manager for external services."""
    
    def __init__(self):
        self.pools = {}
        self.config = self._load_config()
        self.metrics = PerformanceMetrics()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load connection pool configuration."""
        return {
            'max_connections': int(os.getenv('MAX_CONNECTIONS', '100')),
            'max_keepalive_connections': int(os.getenv('MAX_KEEPALIVE_CONNECTIONS', '20')),
            'keepalive_expiry': int(os.getenv('KEEPALIVE_EXPIRY', '30')),
            'connection_timeout': int(os.getenv('CONNECTION_TIMEOUT', '10')),
            'read_timeout': int(os.getenv('READ_TIMEOUT', '30'))
        }
    
    async def get_http_session(self, name: str = 'default') -> 'aiohttp.ClientSession':
        """Get HTTP session with connection pooling."""
        import aiohttp
        
        if name not in self.pools:
            connector = aiohttp.TCPConnector(
                limit=self.config['max_connections'],
                limit_per_host=self.config['max_keepalive_connections'],
                keepalive_timeout=self.config['keepalive_expiry'],
                enable_cleanup_closed=True
            )
            
            timeout = aiohttp.ClientTimeout(
                total=self.config['connection_timeout'] + self.config['read_timeout'],
                connect=self.config['connection_timeout'],
                sock_read=self.config['read_timeout']
            )
            
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=timeout
            )
            
            self.pools[name] = session
            logger.info(f"Created HTTP connection pool: {name}")
        
        return self.pools[name]
    
    async def close_pools(self):
        """Close all connection pools."""
        for name, pool in self.pools.items():
            try:
                await pool.close()
                logger.info(f"Closed connection pool: {name}")
            except Exception as e:
                logger.warning(f"Error closing connection pool {name}: {e}")
        
        self.pools.clear()


class PerformanceOptimizer:
    """Main performance optimization coordinator."""
    
    def __init__(self):
        self.cache_manager = CacheManager()
        self.connection_pool = ConnectionPool()
        self.metrics = PerformanceMetrics()
        self.optimization_rules = self._load_optimization_rules()
    
    def _load_optimization_rules(self) -> Dict[str, Any]:
        """Load performance optimization rules."""
        return {
            'enable_request_caching': os.getenv('ENABLE_REQUEST_CACHING', 'true').lower() == 'true',
            'enable_response_compression': os.getenv('ENABLE_RESPONSE_COMPRESSION', 'true').lower() == 'true',
            'enable_static_file_caching': os.getenv('ENABLE_STATIC_FILE_CACHING', 'true').lower() == 'true',
            'enable_database_query_caching': os.getenv('ENABLE_DB_QUERY_CACHING', 'true').lower() == 'true',
            'max_request_size': int(os.getenv('MAX_REQUEST_SIZE', '10485760')),  # 10MB
            'request_timeout': int(os.getenv('REQUEST_TIMEOUT', '30')),
            'enable_lazy_loading': os.getenv('ENABLE_LAZY_LOADING', 'true').lower() == 'true',
            'enable_preloading': os.getenv('ENABLE_PRELOADING', 'false').lower() == 'true'
        }
    
    def cache(self, key: str = None, ttl: int = None, ignore_args: List[str] = None):
        """Decorator for caching function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                # Generate cache key
                if key:
                    cache_key = key
                else:
                    # Create key from function name and arguments
                    filtered_kwargs = {k: v for k, v in kwargs.items() 
                                     if ignore_args is None or k not in ignore_args}
                    key_data = f"{func.__name__}:{args}:{filtered_kwargs}"
                    cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get from cache
                start_time = time.time()
                cached_result = await self.cache_manager.aget(cache_key)
                
                if cached_result is not None:
                    cache_duration = time.time() - start_time
                    logger.debug(f"Cache hit for {func.__name__}", extra={
                        'cache_key': cache_key,
                        'cache_duration': cache_duration
                    })
                    return cached_result
                
                # Execute function
                result = await func(*args, **kwargs)
                
                # Cache result
                await self.cache_manager.aset(cache_key, result, ttl)
                
                execution_duration = time.time() - start_time
                logger.debug(f"Function executed and cached: {func.__name__}", extra={
                    'cache_key': cache_key,
                    'execution_duration': execution_duration
                })
                
                return result
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                # Generate cache key
                if key:
                    cache_key = key
                else:
                    filtered_kwargs = {k: v for k, v in kwargs.items() 
                                     if ignore_args is None or k not in ignore_args}
                    key_data = f"{func.__name__}:{args}:{filtered_kwargs}"
                    cache_key = hashlib.md5(key_data.encode()).hexdigest()
                
                # Try to get from cache
                start_time = time.time()
                cached_result = self.cache_manager.get(cache_key)
                
                if cached_result is not None:
                    cache_duration = time.time() - start_time
                    logger.debug(f"Cache hit for {func.__name__}", extra={
                        'cache_key': cache_key,
                        'cache_duration': cache_duration
                    })
                    return cached_result
                
                # Execute function
                result = func(*args, **kwargs)
                
                # Cache result
                self.cache_manager.set(cache_key, result, ttl)
                
                execution_duration = time.time() - start_time
                logger.debug(f"Function executed and cached: {func.__name__}", extra={
                    'cache_key': cache_key,
                    'execution_duration': execution_duration
                })
                
                return result
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    def monitor_performance(self, operation_name: str = None):
        """Decorator for monitoring function performance."""
        def decorator(func: Callable) -> Callable:
            op_name = operation_name or func.__name__
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    logger.info(f"Performance: {op_name} completed", extra={
                        'operation': op_name,
                        'duration': duration,
                        'status': 'success'
                    })
                    
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    
                    logger.error(f"Performance: {op_name} failed", extra={
                        'operation': op_name,
                        'duration': duration,
                        'status': 'error',
                        'error': str(e)
                    })
                    raise
            
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time
                    
                    logger.info(f"Performance: {op_name} completed", extra={
                        'operation': op_name,
                        'duration': duration,
                        'status': 'success'
                    })
                    
                    return result
                except Exception as e:
                    duration = time.time() - start_time
                    
                    logger.error(f"Performance: {op_name} failed", extra={
                        'operation': op_name,
                        'duration': duration,
                        'status': 'error',
                        'error': str(e)
                    })
                    raise
            
            return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
        
        return decorator
    
    async def optimize_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Optimize incoming request data."""
        optimized_data = request_data.copy()
        
        # Apply optimization rules
        if self.optimization_rules['enable_request_caching']:
            # Add cache headers if applicable
            optimized_data['cache_control'] = 'max-age=3600'
        
        if self.optimization_rules['enable_response_compression']:
            # Enable compression for large responses
            optimized_data['accept_encoding'] = 'gzip, deflate'
        
        return optimized_data
    
    def get_performance_stats(self) -> Dict[str, Any]:
        """Get current performance statistics."""
        stats = {
            'cache_stats': {
                'local_cache_size': len(self.cache_manager.local_cache),
                'redis_connected': self.cache_manager.redis_client is not None
            },
            'connection_pool_stats': {
                'active_pools': len(self.connection_pool.pools)
            },
            'system_stats': {
                'memory_usage': psutil.virtual_memory()._asdict(),
                'cpu_usage': psutil.cpu_percent(),
                'disk_usage': psutil.disk_usage('.')._asdict()
            }
        }
        
        return stats


# Global performance optimizer instance
performance_optimizer = PerformanceOptimizer()


def cache(key: str = None, ttl: int = None, ignore_args: List[str] = None):
    """Global cache decorator."""
    return performance_optimizer.cache(key=key, ttl=ttl, ignore_args=ignore_args)


def monitor_performance(operation_name: str = None):
    """Global performance monitoring decorator."""
    return performance_optimizer.monitor_performance(operation_name=operation_name)


async def get_optimized_http_session(name: str = 'default'):
    """Get optimized HTTP session."""
    return await performance_optimizer.connection_pool.get_http_session(name)


def get_performance_stats() -> Dict[str, Any]:
    """Get global performance statistics."""
    return performance_optimizer.get_performance_stats()
