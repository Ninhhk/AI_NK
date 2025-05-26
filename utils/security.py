"""
Security configuration and utilities for AI NVCB.

This module provides security features including authentication,
authorization, input validation, and security headers.
"""

import os
import hashlib
import secrets
import jwt
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from functools import wraps
from pathlib import Path
import re

logger = logging.getLogger(__name__)


class SecurityConfig:
    """Security configuration and utilities."""
    
    def __init__(self):
        """Initialize security configuration."""
        self.secret_key = os.environ.get("SECRET_KEY", self._generate_secret_key())
        self.admin_username = os.environ.get("ADMIN_USERNAME", "admin")
        self.admin_password_hash = self._hash_password(
            os.environ.get("ADMIN_PASSWORD", "change_this_password_in_production")
        )
        self.jwt_expiry_hours = int(os.environ.get("JWT_EXPIRY_HOURS", "24"))
        self.max_upload_size = int(os.environ.get("UPLOAD_MAX_SIZE", "10485760"))  # 10MB
        self.allowed_file_types = set(
            os.environ.get("UPLOAD_ALLOWED_EXTENSIONS", ".txt,.pdf,.docx,.doc,.md,.rtf").split(",")
        )
        self.rate_limit_requests = int(os.environ.get("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.environ.get("RATE_LIMIT_WINDOW", "60"))
    
    def _generate_secret_key(self) -> str:
        """Generate a secure secret key."""
        return secrets.token_urlsafe(32)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256 with salt."""
        salt = secrets.token_hex(16)
        password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{password_hash}"
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash."""
        try:
            salt, hash_value = password_hash.split(":")
            expected_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return secrets.compare_digest(hash_value, expected_hash)
        except ValueError:
            return False
    
    def generate_jwt_token(self, user_data: Dict[str, Any]) -> str:
        """Generate a JWT token for user authentication."""
        payload = {
            **user_data,
            "exp": datetime.utcnow() + timedelta(hours=self.jwt_expiry_hours),
            "iat": datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm="HS256")
    
    def verify_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=["HS256"])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid JWT token")
            return None
    
    def authenticate_admin(self, username: str, password: str) -> bool:
        """Authenticate admin user."""
        if username != self.admin_username:
            return False
        return self.verify_password(password, self.admin_password_hash)
    
    def validate_file_upload(self, filename: str, file_size: int, file_content: bytes = None) -> Dict[str, Any]:
        """Validate file upload for security."""
        result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # Check file size
        if file_size > self.max_upload_size:
            result["valid"] = False
            result["errors"].append(f"File size {file_size} exceeds maximum {self.max_upload_size} bytes")
        
        # Check file extension
        file_ext = Path(filename).suffix.lower()
        if file_ext not in self.allowed_file_types:
            result["valid"] = False
            result["errors"].append(f"File type {file_ext} not allowed. Allowed types: {', '.join(self.allowed_file_types)}")
        
        # Check filename for security issues
        if self._has_suspicious_filename(filename):
            result["valid"] = False
            result["errors"].append("Filename contains suspicious characters")
        
        # Basic content validation if provided
        if file_content:
            content_warnings = self._validate_file_content(file_content, file_ext)
            result["warnings"].extend(content_warnings)
        
        return result
    
    def _has_suspicious_filename(self, filename: str) -> bool:
        """Check if filename contains suspicious patterns."""
        suspicious_patterns = [
            r"\.\./",  # Directory traversal
            r"\\",     # Windows path separators
            r"[<>:\"|?*]",  # Invalid filename characters
            r"^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)",  # Windows reserved names
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, filename, re.IGNORECASE):
                return True
        
        return False
    
    def _validate_file_content(self, content: bytes, file_ext: str) -> List[str]:
        """Validate file content for potential security issues."""
        warnings = []
        
        # Check for potentially malicious content
        malicious_patterns = [
            b"<script",
            b"javascript:",
            b"vbscript:",
            b"onload=",
            b"onerror=",
            b"<?php",
            b"<%",
        ]
        
        content_lower = content.lower()
        for pattern in malicious_patterns:
            if pattern in content_lower:
                warnings.append(f"Potentially malicious content detected: {pattern.decode('utf-8', 'ignore')}")
        
        # Check file size vs content length
        if len(content) == 0:
            warnings.append("File appears to be empty")
        elif len(content) < 100 and file_ext in [".pdf", ".docx"]:
            warnings.append("File seems unusually small for its type")
        
        return warnings
    
    def sanitize_input(self, text: str, max_length: int = 10000) -> str:
        """Sanitize user input text."""
        if not isinstance(text, str):
            return ""
        
        # Truncate to maximum length
        text = text[:max_length]
        
        # Remove potential XSS patterns
        xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"on\w+\s*=",
        ]
        
        for pattern in xss_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE | re.DOTALL)
        
        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text).strip()
        
        return text
    
    def get_security_headers(self) -> Dict[str, str]:
        """Get recommended security headers."""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' ws: wss:;"
            ),
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": (
                "camera=(), microphone=(), geolocation=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        }
    
    def log_security_event(self, event_type: str, details: Dict[str, Any], severity: str = "INFO"):
        """Log security-related events."""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "severity": severity,
            "details": details
        }
        
        if severity == "ERROR":
            logger.error(f"Security Event: {event_type}", extra=log_entry)
        elif severity == "WARNING":
            logger.warning(f"Security Event: {event_type}", extra=log_entry)
        else:
            logger.info(f"Security Event: {event_type}", extra=log_entry)


class RateLimiter:
    """Simple rate limiting implementation."""
    
    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """Initialize rate limiter."""
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}  # {client_id: [(timestamp, count), ...]}
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if client is allowed to make a request."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        # Clean old entries
        if client_id in self.requests:
            self.requests[client_id] = [
                (timestamp, count) for timestamp, count in self.requests[client_id]
                if timestamp > cutoff
            ]
        else:
            self.requests[client_id] = []
        
        # Count requests in current window
        total_requests = sum(count for _, count in self.requests[client_id])
        
        if total_requests >= self.max_requests:
            return False
        
        # Add current request
        self.requests[client_id].append((now, 1))
        return True
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.window_seconds)
        
        if client_id not in self.requests:
            return self.max_requests
        
        # Count current requests
        current_requests = sum(
            count for timestamp, count in self.requests[client_id]
            if timestamp > cutoff
        )
        
        return max(0, self.max_requests - current_requests)


# Decorator for admin authentication
def require_admin_auth(security_config: SecurityConfig):
    """Decorator to require admin authentication."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # This is a placeholder - in a real FastAPI app, you'd check the request headers
            # For now, we'll assume authentication is handled at the route level
            return func(*args, **kwargs)
        return wrapper
    return decorator


# Global security instance
security = SecurityConfig()
rate_limiter = RateLimiter(
    max_requests=security.rate_limit_requests,
    window_seconds=security.rate_limit_window
)


def create_security_config_file():
    """Create a security configuration file with recommendations."""
    config_content = """# AI NVCB Security Configuration
# 
# This file contains security-related settings and recommendations

# =============================================================================
# AUTHENTICATION & AUTHORIZATION
# =============================================================================

# Admin credentials (CHANGE THESE IN PRODUCTION!)
ADMIN_USERNAME=admin
ADMIN_PASSWORD=change_this_password_in_production

# JWT settings
SECRET_KEY=change_this_secret_key_in_production
JWT_EXPIRY_HOURS=24

# =============================================================================
# FILE UPLOAD SECURITY
# =============================================================================

# Maximum file size (bytes)
UPLOAD_MAX_SIZE=10485760  # 10MB

# Allowed file extensions
UPLOAD_ALLOWED_EXTENSIONS=.txt,.pdf,.docx,.doc,.md,.rtf

# Upload directory (should be outside web root)
UPLOAD_DIR=./uploads

# =============================================================================
# RATE LIMITING
# =============================================================================

# Rate limiting settings
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# =============================================================================
# CORS SETTINGS
# =============================================================================

# Allowed origins (comma-separated)
CORS_ORIGINS=http://localhost:8501,http://localhost:3000

# Allow credentials
CORS_ALLOW_CREDENTIALS=true

# =============================================================================
# SSL/TLS SETTINGS (PRODUCTION)
# =============================================================================

# SSL certificate files
SSL_CERTFILE=
SSL_KEYFILE=

# Force HTTPS redirect
FORCE_HTTPS=false

# =============================================================================
# SECURITY HEADERS
# =============================================================================

# Enable security headers
ENABLE_SECURITY_HEADERS=true

# Content Security Policy
CSP_ENABLED=true

# =============================================================================
# LOGGING & MONITORING
# =============================================================================

# Security event logging
SECURITY_LOG_LEVEL=INFO
SECURITY_LOG_FILE=logs/security.log

# Failed login attempt threshold
MAX_FAILED_LOGINS=5
LOGIN_LOCKOUT_MINUTES=15

# =============================================================================
# BACKUP SECURITY
# =============================================================================

# Backup encryption
BACKUP_ENCRYPTION_ENABLED=false
BACKUP_ENCRYPTION_KEY=

# =============================================================================
# DEVELOPMENT SETTINGS (DISABLE IN PRODUCTION)
# =============================================================================

# Debug mode (NEVER enable in production)
DEBUG=false

# Skip security checks (NEVER enable in production)
SKIP_SECURITY_CHECKS=false

# Mock authentication (NEVER enable in production)
MOCK_AUTH=false
"""
    
    config_path = Path("security.env.example")
    config_path.write_text(config_content)
    
    print(f"✅ Security configuration template created: {config_path}")
    print("⚠️  IMPORTANT: Review and customize the settings before deployment!")
    print("🔒 Change default passwords and secret keys in production!")


def main():
    """Main function for security utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security utilities for AI NVCB")
    parser.add_argument("--action", choices=["create-config", "validate-upload", "test-auth"], 
                       default="create-config", help="Action to perform")
    parser.add_argument("--file", help="File to validate (for validate-upload)")
    parser.add_argument("--username", help="Username (for test-auth)")
    parser.add_argument("--password", help="Password (for test-auth)")
    
    args = parser.parse_args()
    
    if args.action == "create-config":
        create_security_config_file()
        
    elif args.action == "validate-upload":
        if not args.file:
            print("❌ File path required for validation")
            return 1
        
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return 1
        
        file_content = file_path.read_bytes()
        result = security.validate_file_upload(
            file_path.name, 
            len(file_content), 
            file_content
        )
        
        print(f"Validation result for {file_path.name}:")
        print(f"  Valid: {result['valid']}")
        if result['errors']:
            print("  Errors:")
            for error in result['errors']:
                print(f"    - {error}")
        if result['warnings']:
            print("  Warnings:")
            for warning in result['warnings']:
                print(f"    - {warning}")
                
    elif args.action == "test-auth":
        if not args.username or not args.password:
            print("❌ Username and password required for auth test")
            return 1
        
        is_valid = security.authenticate_admin(args.username, args.password)
        print(f"Authentication result: {'✅ Valid' if is_valid else '❌ Invalid'}")
    
    return 0


if __name__ == "__main__":
    exit(main())
