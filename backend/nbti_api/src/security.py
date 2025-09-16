"""
Security utilities and configurations for the NBTI API
"""

import os
import logging
from functools import wraps
from datetime import datetime, timedelta
from flask import request, jsonify, current_app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from werkzeug.security import check_password_hash
import re

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100 per hour", "20 per minute"]
)

# Security headers configuration
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Referrer-Policy': 'strict-origin-when-cross-origin',
    'Permissions-Policy': 'geolocation=(), microphone=(), camera=()'
}

def init_security(app):
    """Initialize security configurations for the Flask app."""
    
    # Initialize rate limiter
    limiter.init_app(app)
    
    # Add security headers to all responses
    @app.after_request
    def add_security_headers(response):
        if current_app.config.get('SECURITY_HEADERS_ENABLED', True):
            for header, value in SECURITY_HEADERS.items():
                response.headers[header] = value
        
        # Add CSP header if configured
        csp = current_app.config.get('CONTENT_SECURITY_POLICY')
        if csp:
            response.headers['Content-Security-Policy'] = csp
            
        return response
    
    # Configure logging
    setup_logging(app)
    
    return app

def setup_logging(app):
    """Set up application logging."""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    log_file = app.config.get('LOG_FILE')
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s %(levelname)s %(name)s: %(message)s'
    )
    
    # Configure app logger
    app.logger.setLevel(log_level)
    
    # Add file handler if log file is specified
    if log_file:
        try:
            os.makedirs(os.path.dirname(log_file), exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            app.logger.addHandler(file_handler)
        except Exception as e:
            app.logger.warning(f"Could not set up file logging: {e}")
    
    # Add console handler for development
    if app.config.get('DEBUG'):
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        app.logger.addHandler(console_handler)

def validate_password_strength(password):
    """
    Validate password strength.
    
    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, "Password is strong"

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def sanitize_input(data):
    """Sanitize input data to prevent XSS and injection attacks."""
    if isinstance(data, str):
        # Remove potentially dangerous characters
        data = re.sub(r'[<>"\']', '', data)
        # Limit length
        data = data[:1000]
    elif isinstance(data, dict):
        return {key: sanitize_input(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    
    return data

def require_role(required_roles):
    """
    Decorator to require specific roles for accessing endpoints.
    
    Args:
        required_roles: List of role names or single role name
    """
    if isinstance(required_roles, str):
        required_roles = [required_roles]
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                verify_jwt_in_request()
                current_user_id = get_jwt_identity()
                
                # Import here to avoid circular imports
                from models.user import User
                
                user = User.query.get(int(current_user_id))
                if not user:
                    return jsonify({'error': 'User not found'}), 401
                
                user_roles = [role.name for role in user.roles]
                
                # Check if user has any of the required roles
                if not any(role in user_roles for role in required_roles):
                    current_app.logger.warning(
                        f"User {user.username} attempted to access {request.endpoint} "
                        f"without required roles: {required_roles}"
                    )
                    return jsonify({
                        'error': 'Insufficient permissions',
                        'required_roles': required_roles
                    }), 403
                
                return f(*args, **kwargs)
                
            except Exception as e:
                current_app.logger.error(f"Role verification error: {str(e)}")
                return jsonify({'error': 'Authorization failed'}), 401
        
        return decorated_function
    return decorator

def log_security_event(event_type, user_id=None, details=None):
    """Log security-related events for auditing."""
    try:
        current_user_id = get_jwt_identity() if user_id is None else user_id
    except:
        current_user_id = 'anonymous'
    
    log_entry = {
        'timestamp': datetime.utcnow().isoformat(),
        'event_type': event_type,
        'user_id': current_user_id,
        'ip_address': request.remote_addr,
        'user_agent': request.headers.get('User-Agent', ''),
        'endpoint': request.endpoint,
        'method': request.method,
        'details': details or {}
    }
    
    current_app.logger.info(f"SECURITY_EVENT: {log_entry}")

def check_rate_limit_exceeded():
    """Check if rate limit is exceeded for current request."""
    # This would integrate with your rate limiting solution
    # For now, it's a placeholder
    return False

class SecurityMiddleware:
    """Security middleware for additional request processing."""
    
    def __init__(self, app):
        self.app = app
        self.init_app(app)
    
    def init_app(self, app):
        app.before_request(self.before_request)
        app.after_request(self.after_request)
    
    def before_request(self):
        """Process requests before they reach the endpoint."""
        # Log all requests for security monitoring
        current_app.logger.info(
            f"REQUEST: {request.method} {request.path} from {request.remote_addr}"
        )
        
        # Check for suspicious patterns
        if self.is_suspicious_request():
            log_security_event('suspicious_request', details={
                'path': request.path,
                'method': request.method,
                'headers': dict(request.headers)
            })
        
        # Validate content length
        max_length = current_app.config.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024)
        if request.content_length and request.content_length > max_length:
            return jsonify({'error': 'Request too large'}), 413
    
    def after_request(self, response):
        """Process responses after endpoint execution."""
        # Log response status for monitoring
        if response.status_code >= 400:
            current_app.logger.warning(
                f"ERROR_RESPONSE: {response.status_code} for {request.method} {request.path}"
            )
        
        return response
    
    def is_suspicious_request(self):
        """Check if request shows suspicious patterns."""
        # Check for common attack patterns
        suspicious_patterns = [
            'script', 'javascript:', 'vbscript:', 'onload', 'onerror',
            'union', 'select', 'insert', 'delete', 'drop', 'exec',
            '../', '..\\', '/etc/passwd', 'cmd.exe'
        ]
        
        # Check URL and query parameters
        full_path = request.full_path.lower()
        for pattern in suspicious_patterns:
            if pattern in full_path:
                return True
        
        # Check headers
        user_agent = request.headers.get('User-Agent', '').lower()
        if 'sqlmap' in user_agent or 'nikto' in user_agent:
            return True
        
        return False

# Rate limiting decorators for specific endpoints
def rate_limit_auth(f):
    """Rate limit for authentication endpoints."""
    return limiter.limit("5 per minute")(f)

def rate_limit_api(f):
    """Rate limit for general API endpoints."""
    return limiter.limit("60 per minute")(f)

def rate_limit_upload(f):
    """Rate limit for file upload endpoints."""
    return limiter.limit("10 per minute")(f)

