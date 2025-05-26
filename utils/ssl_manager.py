"""
SSL/TLS certificate management for AI NVCB application.

This module provides comprehensive SSL certificate management including
certificate generation, validation, renewal, and monitoring for production
deployments.
"""

import os
import ssl
import socket
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import tempfile
import shutil
import asyncio

try:
    from cryptography import x509
    from cryptography.x509.oid import NameOID, ExtensionOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

try:
    import certbot.main
    HAS_CERTBOT = True
except ImportError:
    HAS_CERTBOT = False

from utils.production_logging import get_production_logger

logger = get_production_logger('ssl')


class SSLCertificateManager:
    """Comprehensive SSL certificate management."""
    
    def __init__(self):
        self.config = self._load_config()
        self.cert_directory = Path(self.config['cert_directory'])
        self.cert_directory.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load SSL configuration from environment."""
        return {
            'cert_directory': os.getenv('SSL_CERT_DIRECTORY', './ssl'),
            'key_size': int(os.getenv('SSL_KEY_SIZE', '2048')),
            'cert_validity_days': int(os.getenv('SSL_CERT_VALIDITY_DAYS', '365')),
            'auto_renewal_enabled': os.getenv('SSL_AUTO_RENEWAL', 'true').lower() == 'true',
            'renewal_threshold_days': int(os.getenv('SSL_RENEWAL_THRESHOLD_DAYS', '30')),
            'acme_email': os.getenv('ACME_EMAIL', ''),
            'acme_server': os.getenv('ACME_SERVER', 'https://acme-v02.api.letsencrypt.org/directory'),
            'domains': [d.strip() for d in os.getenv('SSL_DOMAINS', '').split(',') if d.strip()],
            'enable_hsts': os.getenv('ENABLE_HSTS', 'true').lower() == 'true',
            'hsts_max_age': int(os.getenv('HSTS_MAX_AGE', '31536000')),  # 1 year
            'enable_ocsp_stapling': os.getenv('ENABLE_OCSP_STAPLING', 'true').lower() == 'true',
            'cipher_suites': os.getenv('SSL_CIPHER_SUITES', 'ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS'),
            'protocols': os.getenv('SSL_PROTOCOLS', 'TLSv1.2,TLSv1.3').split(',')
        }
    
    def generate_self_signed_certificate(self, domain: str, organization: str = 'AI NVCB') -> Tuple[str, str]:
        """
        Generate a self-signed certificate for development/testing.
        
        Args:
            domain: Domain name for the certificate
            organization: Organization name
            
        Returns:
            Tuple of (certificate_path, private_key_path)
        """
        if not HAS_CRYPTOGRAPHY:
            raise RuntimeError("Cryptography library not available for certificate generation")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=self.config['key_size']
        )
        
        # Generate certificate
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, "US"),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "State"),
            x509.NameAttribute(NameOID.LOCALITY_NAME, "City"),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, domain),
        ])
        
        certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.utcnow()
        ).not_valid_after(
            datetime.utcnow() + timedelta(days=self.config['cert_validity_days'])
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName(domain),
            ]),
            critical=False,
        ).sign(private_key, hashes.SHA256())
        
        # Save certificate and key
        cert_path = self.cert_directory / f"{domain}.crt"
        key_path = self.cert_directory / f"{domain}.key"
        
        # Write certificate
        with open(cert_path, "wb") as f:
            f.write(certificate.public_bytes(serialization.Encoding.PEM))
        
        # Write private key
        with open(key_path, "wb") as f:
            f.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
        
        # Set proper permissions
        os.chmod(cert_path, 0o644)
        os.chmod(key_path, 0o600)
        
        logger.info(f"Generated self-signed certificate for {domain}", extra={
            'domain': domain,
            'cert_path': str(cert_path),
            'key_path': str(key_path),
            'validity_days': self.config['cert_validity_days']
        })
        
        return str(cert_path), str(key_path)
    
    def request_letsencrypt_certificate(self, domains: List[str], email: str = None) -> bool:
        """
        Request Let's Encrypt certificate using Certbot.
        
        Args:
            domains: List of domain names
            email: Email for registration
            
        Returns:
            True if successful, False otherwise
        """
        if not HAS_CERTBOT:
            logger.error("Certbot not available for Let's Encrypt certificates")
            return False
        
        if not domains:
            logger.error("No domains specified for certificate request")
            return False
        
        email = email or self.config['acme_email']
        if not email:
            logger.error("No email specified for Let's Encrypt registration")
            return False
        
        try:
            # Prepare certbot arguments
            certbot_args = [
                'certonly',
                '--standalone',
                '--non-interactive',
                '--agree-tos',
                '--email', email,
                '--cert-path', str(self.cert_directory),
                '--key-path', str(self.cert_directory),
                '--server', self.config['acme_server']
            ]
            
            # Add domains
            for domain in domains:
                certbot_args.extend(['-d', domain])
            
            # Run certbot
            result = certbot.main.main(certbot_args)
            
            if result == 0:
                logger.info("Let's Encrypt certificate obtained successfully", extra={
                    'domains': domains,
                    'email': email
                })
                return True
            else:
                logger.error(f"Certbot failed with exit code: {result}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to request Let's Encrypt certificate: {e}")
            return False
    
    def validate_certificate(self, cert_path: str, key_path: str = None) -> Dict[str, Any]:
        """
        Validate SSL certificate.
        
        Args:
            cert_path: Path to certificate file
            key_path: Path to private key file (optional)
            
        Returns:
            Validation results
        """
        results = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'details': {}
        }
        
        try:
            # Load certificate
            with open(cert_path, 'rb') as f:
                cert_data = f.read()
            
            if HAS_CRYPTOGRAPHY:
                cert = x509.load_pem_x509_certificate(cert_data)
                
                # Check expiration
                now = datetime.utcnow()
                not_after = cert.not_valid_after
                not_before = cert.not_valid_before
                
                if now < not_before:
                    results['errors'].append(f"Certificate not yet valid (valid from {not_before})")
                elif now > not_after:
                    results['errors'].append(f"Certificate expired on {not_after}")
                else:
                    days_until_expiry = (not_after - now).days
                    if days_until_expiry < self.config['renewal_threshold_days']:
                        results['warnings'].append(f"Certificate expires in {days_until_expiry} days")
                
                # Extract certificate details
                results['details'] = {
                    'subject': cert.subject.rfc4514_string(),
                    'issuer': cert.issuer.rfc4514_string(),
                    'serial_number': str(cert.serial_number),
                    'not_before': not_before.isoformat(),
                    'not_after': not_after.isoformat(),
                    'days_until_expiry': (not_after - now).days,
                    'signature_algorithm': cert.signature_algorithm_oid._name
                }
                
                # Check key usage
                try:
                    key_usage = cert.extensions.get_extension_for_oid(ExtensionOID.KEY_USAGE).value
                    results['details']['key_usage'] = {
                        'digital_signature': key_usage.digital_signature,
                        'key_encipherment': key_usage.key_encipherment,
                        'key_agreement': key_usage.key_agreement
                    }
                except x509.ExtensionNotFound:
                    pass
                
                # Check subject alternative names
                try:
                    san = cert.extensions.get_extension_for_oid(ExtensionOID.SUBJECT_ALTERNATIVE_NAME).value
                    results['details']['subject_alt_names'] = [name.value for name in san]
                except x509.ExtensionNotFound:
                    pass
            
            # Validate private key if provided
            if key_path and os.path.exists(key_path):
                try:
                    with open(key_path, 'rb') as f:
                        key_data = f.read()
                    
                    if HAS_CRYPTOGRAPHY:
                        private_key = serialization.load_pem_private_key(key_data, password=None)
                        
                        # Verify key matches certificate
                        cert_public_key = cert.public_key()
                        private_public_key = private_key.public_key()
                        
                        # Compare public key numbers
                        if hasattr(cert_public_key, 'public_numbers') and hasattr(private_public_key, 'public_numbers'):
                            if cert_public_key.public_numbers() != private_public_key.public_numbers():
                                results['errors'].append("Private key does not match certificate")
                        
                        results['details']['key_size'] = private_key.key_size if hasattr(private_key, 'key_size') else 'Unknown'
                        
                except Exception as e:
                    results['errors'].append(f"Private key validation failed: {e}")
            
            # Set overall validity
            results['valid'] = len(results['errors']) == 0
            
        except Exception as e:
            results['errors'].append(f"Certificate validation failed: {e}")
        
        return results
    
    def check_certificate_expiry(self, domain: str, port: int = 443) -> Dict[str, Any]:
        """
        Check certificate expiry for a domain.
        
        Args:
            domain: Domain name to check
            port: Port number (default 443)
            
        Returns:
            Certificate expiry information
        """
        result = {
            'domain': domain,
            'port': port,
            'valid': False,
            'error': None,
            'expires': None,
            'days_until_expiry': None,
            'issuer': None
        }
        
        try:
            # Connect to domain and get certificate
            context = ssl.create_default_context()
            with socket.create_connection((domain, port), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Parse expiration date
                    not_after = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                    days_until_expiry = (not_after - datetime.utcnow()).days
                    
                    result.update({
                        'valid': True,
                        'expires': not_after.isoformat(),
                        'days_until_expiry': days_until_expiry,
                        'issuer': cert.get('issuer', [{}])[0].get('organizationName', 'Unknown'),
                        'subject': dict(x[0] for x in cert.get('subject', [])),
                        'version': cert.get('version', 'Unknown'),
                        'serial_number': cert.get('serialNumber', 'Unknown')
                    })
                    
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    async def monitor_certificates(self) -> List[Dict[str, Any]]:
        """
        Monitor all configured certificates.
        
        Returns:
            List of certificate status reports
        """
        results = []
        
        # Check configured domains
        for domain in self.config['domains']:
            if domain:
                cert_info = self.check_certificate_expiry(domain)
                results.append(cert_info)
                
                # Log warnings for expiring certificates
                if cert_info['valid'] and cert_info['days_until_expiry'] is not None:
                    if cert_info['days_until_expiry'] < 7:
                        logger.error(f"Certificate for {domain} expires in {cert_info['days_until_expiry']} days", extra={
                            'domain': domain,
                            'days_until_expiry': cert_info['days_until_expiry'],
                            'expires': cert_info['expires']
                        })
                    elif cert_info['days_until_expiry'] < self.config['renewal_threshold_days']:
                        logger.warning(f"Certificate for {domain} expires in {cert_info['days_until_expiry']} days", extra={
                            'domain': domain,
                            'days_until_expiry': cert_info['days_until_expiry'],
                            'expires': cert_info['expires']
                        })
        
        # Check local certificate files
        for cert_file in self.cert_directory.glob('*.crt'):
            domain = cert_file.stem
            key_file = self.cert_directory / f"{domain}.key"
            
            validation = self.validate_certificate(str(cert_file), str(key_file) if key_file.exists() else None)
            
            result = {
                'domain': domain,
                'type': 'local_file',
                'cert_path': str(cert_file),
                'key_path': str(key_file) if key_file.exists() else None,
                'valid': validation['valid'],
                'errors': validation['errors'],
                'warnings': validation['warnings'],
                'details': validation['details']
            }
            
            results.append(result)
        
        return results
    
    def renew_certificates(self) -> Dict[str, Any]:
        """
        Renew certificates that are approaching expiry.
        
        Returns:
            Renewal results
        """
        results = {
            'renewed': [],
            'failed': [],
            'skipped': []
        }
        
        if not self.config['auto_renewal_enabled']:
            logger.info("Auto-renewal is disabled")
            return results
        
        # Check which certificates need renewal
        for domain in self.config['domains']:
            if not domain:
                continue
                
            cert_info = self.check_certificate_expiry(domain)
            
            if not cert_info['valid']:
                logger.warning(f"Cannot check certificate for {domain}: {cert_info.get('error', 'Unknown error')}")
                continue
            
            days_until_expiry = cert_info.get('days_until_expiry')
            if days_until_expiry is None or days_until_expiry > self.config['renewal_threshold_days']:
                results['skipped'].append({
                    'domain': domain,
                    'reason': f"Certificate valid for {days_until_expiry} more days"
                })
                continue
            
            # Attempt renewal
            logger.info(f"Attempting to renew certificate for {domain} (expires in {days_until_expiry} days)")
            
            if HAS_CERTBOT and self.config['acme_email']:
                # Use Let's Encrypt renewal
                try:
                    renewal_success = self.request_letsencrypt_certificate([domain], self.config['acme_email'])
                    if renewal_success:
                        results['renewed'].append({
                            'domain': domain,
                            'method': 'letsencrypt',
                            'renewed_at': datetime.utcnow().isoformat()
                        })
                        logger.info(f"Successfully renewed certificate for {domain}")
                    else:
                        results['failed'].append({
                            'domain': domain,
                            'error': 'Let\'s Encrypt renewal failed'
                        })
                        logger.error(f"Failed to renew certificate for {domain}")
                except Exception as e:
                    results['failed'].append({
                        'domain': domain,
                        'error': str(e)
                    })
                    logger.error(f"Certificate renewal failed for {domain}: {e}")
            else:
                # Generate new self-signed certificate
                try:
                    self.generate_self_signed_certificate(domain)
                    results['renewed'].append({
                        'domain': domain,
                        'method': 'self_signed',
                        'renewed_at': datetime.utcnow().isoformat()
                    })
                    logger.info(f"Generated new self-signed certificate for {domain}")
                except Exception as e:
                    results['failed'].append({
                        'domain': domain,
                        'error': str(e)
                    })
                    logger.error(f"Failed to generate self-signed certificate for {domain}: {e}")
        
        return results
    
    def get_ssl_context(self, cert_path: str, key_path: str) -> ssl.SSLContext:
        """
        Create SSL context with security best practices.
        
        Args:
            cert_path: Path to certificate file
            key_path: Path to private key file
            
        Returns:
            Configured SSL context
        """
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Load certificate and key
        context.load_cert_chain(cert_path, key_path)
        
        # Configure security settings
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Set cipher suites
        context.set_ciphers(self.config['cipher_suites'])
        
        # Enable OCSP stapling if configured
        if self.config['enable_ocsp_stapling']:
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
        
        return context
    
    def get_security_headers(self) -> Dict[str, str]:
        """
        Get recommended security headers for HTTPS.
        
        Returns:
            Dictionary of security headers
        """
        headers = {}
        
        # HSTS header
        if self.config['enable_hsts']:
            hsts_value = f"max-age={self.config['hsts_max_age']}"
            if self.config.get('hsts_include_subdomains', True):
                hsts_value += "; includeSubDomains"
            if self.config.get('hsts_preload', False):
                hsts_value += "; preload"
            headers['Strict-Transport-Security'] = hsts_value
        
        # Additional security headers
        headers.update({
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': 'DENY',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        })
        
        return headers


# Global SSL certificate manager
ssl_manager = SSLCertificateManager()


def get_ssl_manager() -> SSLCertificateManager:
    """Get the global SSL certificate manager."""
    return ssl_manager


async def monitor_ssl_certificates() -> List[Dict[str, Any]]:
    """Monitor SSL certificates."""
    return await ssl_manager.monitor_certificates()


def renew_ssl_certificates() -> Dict[str, Any]:
    """Renew SSL certificates."""
    return ssl_manager.renew_certificates()
