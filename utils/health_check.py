"""
Health check utilities for AI NVCB application.

This module provides health check functionality for monitoring
the application's components and dependencies.
"""

import asyncio
import sqlite3
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

# Optional imports with fallbacks
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from utils.logging_config import get_logger

logger = get_logger('health')


class HealthChecker:
    """Health checker for AI NVCB application components."""
    
    def __init__(self):
        self.checks = {}
        self.last_check = None
        self.check_interval = int(os.getenv('HEALTH_CHECK_INTERVAL', '60'))
        self.timeout = int(os.getenv('HEALTH_CHECK_TIMEOUT', '10'))
    
    async def check_all(self) -> Dict[str, Any]:
        """
        Run all health checks and return results.
        
        Returns:
            Dictionary containing health check results
        """
        results = {
            'timestamp': datetime.utcnow().isoformat(),
            'status': 'healthy',
            'checks': {},
            'summary': {}
        }
        
        # Core application checks
        checks_to_run = [
            ('database', self.check_database),
            ('disk_space', self.check_disk_space),
            ('uploads', self.check_uploads_directory),
        ]
        
        # Optional checks based on available dependencies
        if AIOHTTP_AVAILABLE:
            checks_to_run.extend([
                ('ollama', self.check_ollama),
                ('network', self.check_network_connectivity),
                ('ssl_certificates', self.check_ssl_certificates)
            ])
        
        if REDIS_AVAILABLE:
            checks_to_run.append(('redis', self.check_redis))
        
        if PSUTIL_AVAILABLE:
            checks_to_run.extend([
                ('memory', self.check_memory),
                ('cpu', self.check_cpu_usage)
            ])
        
        healthy_count = 0
        total_count = len(checks_to_run)
        
        for check_name, check_func in checks_to_run:
            try:
                check_result = await check_func()
                results['checks'][check_name] = check_result
                
                if check_result.get('status') == 'healthy':
                    healthy_count += 1
                elif check_result.get('status') == 'warning':
                    if results['status'] == 'healthy':
                        results['status'] = 'warning'
                else:
                    results['status'] = 'unhealthy'
                    
            except Exception as e:
                logger.error(f"Health check {check_name} failed: {e}")
                results['checks'][check_name] = {
                    'status': 'error',
                    'message': str(e),
                    'timestamp': datetime.utcnow().isoformat()
                }
                results['status'] = 'unhealthy'
        
        # Summary
        results['summary'] = {
            'healthy_checks': healthy_count,
            'total_checks': total_count,
            'health_percentage': (healthy_count / total_count) * 100 if total_count > 0 else 0
        }
        
        self.last_check = results
        return results
    
    async def check_database(self) -> Dict[str, Any]:
        """Check database connectivity and basic operations."""
        try:
            db_url = os.getenv('DATABASE_URL', 'sqlite:///./ai_nvcb.db')
            
            if db_url.startswith('sqlite'):
                # SQLite check
                db_path = db_url.replace('sqlite:///', '').replace('sqlite://', '')
                
                if not Path(db_path).exists():
                    return {
                        'status': 'unhealthy',
                        'message': 'Database file does not exist',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                
                # Test connection
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                conn.close()
                
                return {
                    'status': 'healthy',
                    'message': 'Database connection successful',
                    'database_type': 'sqlite',
                    'database_path': db_path,
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                # PostgreSQL or other database
                return {
                    'status': 'warning',
                    'message': 'External database health check not implemented',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Database check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_ollama(self) -> Dict[str, Any]:
        """Check Ollama service availability."""
        if not AIOHTTP_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'aiohttp not available for Ollama check',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            ollama_url = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=self.timeout)) as session:
                async with session.get(f"{ollama_url}/api/tags") as response:
                    if response.status == 200:
                        data = await response.json()
                        models = data.get('models', [])
                        
                        return {
                            'status': 'healthy',
                            'message': 'Ollama service is available',
                            'url': ollama_url,
                            'models_count': len(models),
                            'models': [m.get('name') for m in models],
                            'timestamp': datetime.utcnow().isoformat()
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'message': f'Ollama returned status {response.status}',
                            'url': ollama_url,
                            'timestamp': datetime.utcnow().isoformat()
                        }
                        
        except asyncio.TimeoutError:
            return {
                'status': 'unhealthy',
                'message': 'Ollama service timeout',
                'url': ollama_url,
                'timestamp': datetime.utcnow().isoformat()
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Ollama check failed: {str(e)}',
                'url': ollama_url,
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_redis(self) -> Dict[str, Any]:
        """Check Redis connectivity."""
        if not REDIS_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'redis package not available',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
            
            # Parse Redis URL
            if redis_url.startswith('redis://'):
                r = redis.from_url(redis_url)
                
                # Test connection
                r.ping()
                info = r.info()
                
                return {
                    'status': 'healthy',
                    'message': 'Redis connection successful',
                    'url': redis_url,
                    'version': info.get('redis_version'),
                    'memory_used': info.get('used_memory_human'),
                    'timestamp': datetime.utcnow().isoformat()
                }
            else:
                return {
                    'status': 'warning',
                    'message': 'Redis not configured',
                    'timestamp': datetime.utcnow().isoformat()
                }
                
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Redis check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_disk_space(self) -> Dict[str, Any]:
        """Check available disk space."""
        if not PSUTIL_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'psutil not available for disk space check',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            # Check current directory disk space
            disk_usage = psutil.disk_usage('.')
            
            free_gb = disk_usage.free / (1024**3)
            total_gb = disk_usage.total / (1024**3)
            used_percent = (disk_usage.used / disk_usage.total) * 100
            
            # Determine status based on available space
            if free_gb < 1:  # Less than 1GB free
                status = 'unhealthy'
                message = f'Very low disk space: {free_gb:.1f}GB free'
            elif free_gb < 5:  # Less than 5GB free
                status = 'warning'
                message = f'Low disk space: {free_gb:.1f}GB free'
            else:
                status = 'healthy'
                message = f'Sufficient disk space: {free_gb:.1f}GB free'
            
            return {
                'status': status,
                'message': message,
                'free_gb': round(free_gb, 1),
                'total_gb': round(total_gb, 1),
                'used_percent': round(used_percent, 1),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Disk space check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_memory(self) -> Dict[str, Any]:
        """Check memory usage."""
        if not PSUTIL_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'psutil not available for memory check',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            memory = psutil.virtual_memory()
            
            available_gb = memory.available / (1024**3)
            total_gb = memory.total / (1024**3)
            used_percent = memory.percent
            
            # Determine status based on memory usage
            if used_percent > 90:
                status = 'unhealthy'
                message = f'Very high memory usage: {used_percent:.1f}%'
            elif used_percent > 80:
                status = 'warning'
                message = f'High memory usage: {used_percent:.1f}%'
            else:
                status = 'healthy'
                message = f'Normal memory usage: {used_percent:.1f}%'
            
            return {
                'status': status,
                'message': message,
                'available_gb': round(available_gb, 1),
                'total_gb': round(total_gb, 1),
                'used_percent': round(used_percent, 1),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Memory check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_uploads_directory(self) -> Dict[str, Any]:
        """Check uploads directory status."""
        try:
            upload_dir = Path(os.getenv('UPLOAD_DIR', './uploads'))
            
            # Check if directory exists and is writable
            if not upload_dir.exists():
                upload_dir.mkdir(parents=True, exist_ok=True)
            
            if not upload_dir.is_dir():
                return {
                    'status': 'unhealthy',
                    'message': 'Upload path is not a directory',
                    'path': str(upload_dir),
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            # Check write permissions
            test_file = upload_dir / '.health_check'
            try:
                test_file.write_text('health_check')
                test_file.unlink()
                writable = True
            except:
                writable = False
            
            # Count files
            file_count = len(list(upload_dir.rglob('*'))) if upload_dir.exists() else 0
            
            return {
                'status': 'healthy' if writable else 'unhealthy',
                'message': 'Upload directory is accessible' if writable else 'Upload directory is not writable',
                'path': str(upload_dir),
                'writable': writable,
                'file_count': file_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Upload directory check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_cpu_usage(self) -> Dict[str, Any]:
        """Check CPU usage."""
        if not PSUTIL_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'psutil not available for CPU check',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            # Get CPU usage over a short interval
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
            
            # Determine status based on CPU usage
            if cpu_percent > 90:
                status = 'unhealthy'
                message = f'Very high CPU usage: {cpu_percent:.1f}%'
            elif cpu_percent > 80:
                status = 'warning'
                message = f'High CPU usage: {cpu_percent:.1f}%'
            else:
                status = 'healthy'
                message = f'Normal CPU usage: {cpu_percent:.1f}%'
            
            result = {
                'status': status,
                'message': message,
                'cpu_percent': round(cpu_percent, 1),
                'cpu_count': cpu_count,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            if load_avg:
                result['load_avg'] = {
                    '1min': round(load_avg[0], 2),
                    '5min': round(load_avg[1], 2),
                    '15min': round(load_avg[2], 2)
                }
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'CPU check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity to essential services."""
        if not AIOHTTP_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'aiohttp not available for network check',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            # Test connectivity to external services
            test_urls = [
                'https://www.google.com',
                'https://github.com',
                'https://pypi.org'
            ]
            
            successful_connections = 0
            failed_connections = []
            
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                for url in test_urls:
                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                successful_connections += 1
                            else:
                                failed_connections.append(f"{url}: HTTP {response.status}")
                    except Exception as e:
                        failed_connections.append(f"{url}: {str(e)}")
            
            total_tests = len(test_urls)
            success_rate = (successful_connections / total_tests) * 100
            
            if success_rate == 100:
                status = 'healthy'
                message = 'All network connectivity tests passed'
            elif success_rate >= 66:
                status = 'warning'
                message = f'Some network connectivity issues: {success_rate:.0f}% success'
            else:
                status = 'unhealthy'
                message = f'Network connectivity problems: {success_rate:.0f}% success'
            
            return {
                'status': status,
                'message': message,
                'success_rate': round(success_rate, 1),
                'successful_connections': successful_connections,
                'total_tests': total_tests,
                'failed_connections': failed_connections,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Network connectivity check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def check_ssl_certificates(self) -> Dict[str, Any]:
        """Check SSL certificate status for configured domains."""
        if not AIOHTTP_AVAILABLE:
            return {
                'status': 'warning',
                'message': 'aiohttp not available for SSL check',
                'timestamp': datetime.utcnow().isoformat()
            }
        
        try:
            import ssl
            import socket
            
            # Get configured domains from environment
            domains = os.getenv('SSL_DOMAINS', '').split(',')
            domains = [d.strip() for d in domains if d.strip()]
            
            if not domains:
                return {
                    'status': 'warning',
                    'message': 'No SSL domains configured for monitoring',
                    'timestamp': datetime.utcnow().isoformat()
                }
            
            cert_status = []
            overall_status = 'healthy'
            
            for domain in domains:
                try:
                    context = ssl.create_default_context()
                    with socket.create_connection((domain, 443), timeout=10) as sock:
                        with context.wrap_socket(sock, server_hostname=domain) as ssock:
                            cert = ssock.getpeercert()
                            
                            # Parse expiration date
                            not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                            days_until_expiry = (not_after - datetime.utcnow()).days
                            
                            if days_until_expiry < 7:
                                cert_health = 'unhealthy'
                                overall_status = 'unhealthy'
                            elif days_until_expiry < 30:
                                cert_health = 'warning'
                                if overall_status == 'healthy':
                                    overall_status = 'warning'
                            else:
                                cert_health = 'healthy'
                            
                            cert_status.append({
                                'domain': domain,
                                'status': cert_health,
                                'expires': not_after.isoformat(),
                                'days_until_expiry': days_until_expiry,
                                'issuer': cert.get('issuer', [{}])[0].get('organizationName', 'Unknown')
                            })
                            
                except Exception as e:
                    cert_status.append({
                        'domain': domain,
                        'status': 'error',
                        'error': str(e)
                    })
                    overall_status = 'unhealthy'
            
            return {
                'status': overall_status,
                'message': f'SSL certificate check completed for {len(domains)} domains',
                'certificates': cert_status,
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f'SSL certificate check failed: {str(e)}',
                'timestamp': datetime.utcnow().isoformat()
            }


# Global health checker instance
health_checker = HealthChecker()


async def get_health_status() -> Dict[str, Any]:
    """Get current health status."""
    return await health_checker.check_all()


def get_last_health_check() -> Optional[Dict[str, Any]]:
    """Get last health check results."""
    return health_checker.last_check
