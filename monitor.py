#!/usr/bin/env python3
"""
AI NVCB Monitoring Script

This script monitors the health and performance of the AI NVCB application
and can send alerts or notifications when issues are detected.
"""

import asyncio
import aiohttp
import json
import time
import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from utils.health_check import get_health_status
from utils.logging_config import get_logger

logger = get_logger('monitoring')


class MonitoringConfig:
    """Configuration for monitoring."""
    
    def __init__(self):
        self.backend_url = os.getenv('BACKEND_URL', 'http://localhost:8000')
        self.frontend_url = os.getenv('FRONTEND_URL', 'http://localhost:8501')
        self.check_interval = int(os.getenv('MONITOR_CHECK_INTERVAL', '60'))
        self.alert_threshold = int(os.getenv('MONITOR_ALERT_THRESHOLD', '3'))
        self.email_enabled = os.getenv('MONITOR_EMAIL_ENABLED', 'false').lower() == 'true'
        self.webhook_url = os.getenv('WEBHOOK_URL', '')
        
        # Email configuration
        self.smtp_host = os.getenv('EMAIL_SMTP_HOST', '')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', '587'))
        self.email_username = os.getenv('EMAIL_USERNAME', '')
        self.email_password = os.getenv('EMAIL_PASSWORD', '')
        self.email_from = os.getenv('EMAIL_FROM', 'ai-nvcb@localhost')
        self.email_to = os.getenv('MONITOR_EMAIL_TO', '').split(',')


class ApplicationMonitor:
    """Monitor for AI NVCB application."""
    
    def __init__(self, config: MonitoringConfig):
        self.config = config
        self.failure_counts = {}
        self.last_alert_times = {}
        self.monitoring_start_time = datetime.utcnow()
        
    async def monitor_forever(self):
        """Run monitoring loop forever."""
        logger.info("Starting AI NVCB monitoring...")
        
        while True:
            try:
                await self.run_checks()
                await asyncio.sleep(self.config.check_interval)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                await asyncio.sleep(self.config.check_interval)
    
    async def run_checks(self):
        """Run all monitoring checks."""
        checks = [
            ('backend_health', self.check_backend_health),
            ('frontend_availability', self.check_frontend_availability),
            ('api_endpoints', self.check_api_endpoints),
            ('system_resources', self.check_system_resources)
        ]
        
        for check_name, check_func in checks:
            try:
                result = await check_func()
                await self.process_check_result(check_name, result)
            except Exception as e:
                logger.error(f"Check {check_name} failed: {e}")
                await self.process_check_result(check_name, {
                    'status': 'error',
                    'message': str(e)
                })
    
    async def check_backend_health(self) -> Dict[str, Any]:
        """Check backend health."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.config.backend_url}/api/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            'status': 'healthy',
                            'message': 'Backend is responding',
                            'response_time': response.headers.get('x-response-time', 'unknown'),
                            'data': data
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'message': f'Backend returned status {response.status}'
                        }
        except asyncio.TimeoutError:
            return {
                'status': 'unhealthy',
                'message': 'Backend timeout'
            }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Backend connection failed: {str(e)}'
            }
    
    async def check_frontend_availability(self) -> Dict[str, Any]:
        """Check frontend availability."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(self.config.frontend_url) as response:
                    if response.status == 200:
                        return {
                            'status': 'healthy',
                            'message': 'Frontend is accessible'
                        }
                    else:
                        return {
                            'status': 'unhealthy',
                            'message': f'Frontend returned status {response.status}'
                        }
        except Exception as e:
            return {
                'status': 'unhealthy',
                'message': f'Frontend connection failed: {str(e)}'
            }
    
    async def check_api_endpoints(self) -> Dict[str, Any]:
        """Check critical API endpoints."""
        endpoints = [
            '/api/health/detailed',
            '/api/ollama/models',
            '/docs'
        ]
        
        healthy_endpoints = 0
        total_endpoints = len(endpoints)
        endpoint_results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
            for endpoint in endpoints:
                try:
                    async with session.get(f"{self.config.backend_url}{endpoint}") as response:
                        if response.status in [200, 503]:  # 503 is OK for some health checks
                            healthy_endpoints += 1
                            endpoint_results[endpoint] = 'healthy'
                        else:
                            endpoint_results[endpoint] = f'status_{response.status}'
                except Exception as e:
                    endpoint_results[endpoint] = f'error_{str(e)[:50]}'
        
        health_percentage = (healthy_endpoints / total_endpoints) * 100
        
        if health_percentage >= 80:
            status = 'healthy'
        elif health_percentage >= 50:
            status = 'warning'
        else:
            status = 'unhealthy'
        
        return {
            'status': status,
            'message': f'{healthy_endpoints}/{total_endpoints} endpoints healthy',
            'health_percentage': health_percentage,
            'endpoints': endpoint_results
        }
    
    async def check_system_resources(self) -> Dict[str, Any]:
        """Check system resources through health API."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                async with session.get(f"{self.config.backend_url}/api/health/detailed") as response:
                    if response.status == 200:
                        data = await response.json()
                        checks = data.get('checks', {})
                        
                        # Analyze resource checks
                        disk_check = checks.get('disk_space', {})
                        memory_check = checks.get('memory', {})
                        
                        issues = []
                        if disk_check.get('status') != 'healthy':
                            issues.append(f"Disk: {disk_check.get('message', 'unknown issue')}")
                        if memory_check.get('status') != 'healthy':
                            issues.append(f"Memory: {memory_check.get('message', 'unknown issue')}")
                        
                        if not issues:
                            return {
                                'status': 'healthy',
                                'message': 'System resources are normal'
                            }
                        else:
                            return {
                                'status': 'warning',
                                'message': f'Resource issues: {"; ".join(issues)}'
                            }
                    else:
                        return {
                            'status': 'warning',
                            'message': 'Could not check system resources'
                        }
        except Exception as e:
            return {
                'status': 'warning',
                'message': f'Resource check failed: {str(e)}'
            }
    
    async def process_check_result(self, check_name: str, result: Dict[str, Any]):
        """Process the result of a check and handle alerts."""
        status = result.get('status', 'unknown')
        message = result.get('message', 'No message')
        
        # Log the result
        if status == 'healthy':
            logger.info(f"{check_name}: {message}")
            # Reset failure count on success
            self.failure_counts[check_name] = 0
        elif status == 'warning':
            logger.warning(f"{check_name}: {message}")
        else:
            logger.error(f"{check_name}: {message}")
            
            # Increment failure count
            self.failure_counts[check_name] = self.failure_counts.get(check_name, 0) + 1
            
            # Check if we need to send an alert
            if self.failure_counts[check_name] >= self.config.alert_threshold:
                await self.send_alert(check_name, result)
    
    async def send_alert(self, check_name: str, result: Dict[str, Any]):
        """Send alert for failed check."""
        # Check if we've sent an alert recently
        last_alert = self.last_alert_times.get(check_name)
        if last_alert and (datetime.utcnow() - last_alert) < timedelta(minutes=30):
            return  # Don't spam alerts
        
        self.last_alert_times[check_name] = datetime.utcnow()
        
        alert_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'check_name': check_name,
            'status': result.get('status'),
            'message': result.get('message'),
            'failure_count': self.failure_counts[check_name],
            'monitoring_duration': str(datetime.utcnow() - self.monitoring_start_time)
        }
        
        logger.critical(f"ALERT: {check_name} has failed {self.failure_counts[check_name]} times")
        
        # Send email alert
        if self.config.email_enabled and self.config.email_to:
            await self.send_email_alert(alert_data)
        
        # Send webhook alert
        if self.config.webhook_url:
            await self.send_webhook_alert(alert_data)
    
    async def send_email_alert(self, alert_data: Dict[str, Any]):
        """Send email alert."""
        try:
            subject = f"AI NVCB Alert: {alert_data['check_name']} Failed"
            
            body = f"""
AI NVCB Monitoring Alert

Check: {alert_data['check_name']}
Status: {alert_data['status']}
Message: {alert_data['message']}
Failure Count: {alert_data['failure_count']}
Timestamp: {alert_data['timestamp']}
Monitoring Duration: {alert_data['monitoring_duration']}

Please investigate the issue as soon as possible.
            """.strip()
            
            msg = MIMEMultipart()
            msg['From'] = self.config.email_from
            msg['To'] = ', '.join(self.config.email_to)
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.config.smtp_host, self.config.smtp_port)
            server.starttls()
            server.login(self.config.email_username, self.config.email_password)
            text = msg.as_string()
            server.sendmail(self.config.email_from, self.config.email_to, text)
            server.quit()
            
            logger.info(f"Email alert sent for {alert_data['check_name']}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def send_webhook_alert(self, alert_data: Dict[str, Any]):
        """Send webhook alert."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.config.webhook_url,
                    json=alert_data,
                    headers={'Content-Type': 'application/json'}
                ) as response:
                    if response.status == 200:
                        logger.info(f"Webhook alert sent for {alert_data['check_name']}")
                    else:
                        logger.error(f"Webhook alert failed with status {response.status}")
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AI NVCB Application Monitor")
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Check interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--backend-url',
        type=str,
        default='http://localhost:8000',
        help='Backend URL to monitor'
    )
    parser.add_argument(
        '--frontend-url',
        type=str,
        default='http://localhost:8501',
        help='Frontend URL to monitor'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run checks once and exit'
    )
    return parser.parse_args()


async def main():
    """Main function."""
    args = parse_args()
    
    # Override config with command line arguments
    config = MonitoringConfig()
    config.backend_url = args.backend_url
    config.frontend_url = args.frontend_url
    config.check_interval = args.interval
    
    monitor = ApplicationMonitor(config)
    
    if args.once:
        logger.info("Running monitoring checks once...")
        await monitor.run_checks()
        logger.info("Monitoring checks completed")
    else:
        await monitor.monitor_forever()


if __name__ == '__main__':
    asyncio.run(main())
