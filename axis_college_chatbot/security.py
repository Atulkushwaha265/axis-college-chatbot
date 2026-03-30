"""
Security utilities for Axis Colleges AI Chatbot
Contains input validation, XSS prevention, SQL injection protection, and other security functions
"""

import re
import html
import hashlib
import secrets
from functools import wraps
from flask import request, session, abort, jsonify
import bleach
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logger = logging.getLogger(__name__)

class SecurityValidator:
    """Security validation class for input sanitization and validation"""
    
    # XSS protection using bleach
    ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'ul', 'ol', 'li']
    ALLOWED_ATTRIBUTES = {'*': ['class']}
    ALLOWED_STYLES = []
    
    @staticmethod
    def sanitize_input(input_string):
        """Sanitize input to prevent XSS attacks"""
        if not input_string:
            return ""
        
        # Convert to string if not already
        if not isinstance(input_string, str):
            input_string = str(input_string)
        
        # HTML escape
        sanitized = html.escape(input_string)
        
        # Additional bleach sanitization
        sanitized = bleach.clean(
            sanitized,
            tags=SecurityValidator.ALLOWED_TAGS,
            attributes=SecurityValidator.ALLOWED_ATTRIBUTES,
            styles=SecurityValidator.ALLOWED_STYLES,
            strip=True
        )
        
        return sanitized.strip()
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        if not email:
            return False
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(email_pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate phone number format"""
        if not phone:
            return False
        
        phone_pattern = r'^[\d\s\-\+\(\)]{10,20}$'
        return re.match(phone_pattern, phone) is not None
    
    @staticmethod
    def validate_name(name):
        """Validate name format"""
        if not name:
            return False
        
        name_pattern = r'^[a-zA-Z\s\.\-]{2,50}$'
        return re.match(name_pattern, name) is not None
    
    @staticmethod
    def detect_sql_injection(input_string):
        """Detect potential SQL injection attempts"""
        if not input_string:
            return False
        
        dangerous_patterns = [
            r'(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION|SCRIPT)\b)',
            r'(--|;|\/\*|\*\/|xp_|sp_)',
            r'(\bOR\b.*=.*\bOR\b)',
            r'(\bAND\b.*=.*\bAND\b)',
            r'(\bWHERE\b.*\bOR\b)',
            r'(<script|</script|javascript:|vbscript:|onload=|onerror=)'
        ]
        
        input_upper = input_string.upper()
        for pattern in dangerous_patterns:
            if re.search(pattern, input_upper, re.IGNORECASE):
                logger.warning(f"Potential SQL injection detected: {input_string}")
                return True
        
        return False
    
    @staticmethod
    def detect_xss(input_string):
        """Detect potential XSS attempts"""
        if not input_string:
            return False
        
        xss_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'vbscript:',
            r'onload=',
            r'onerror=',
            r'onclick=',
            r'onmouseover=',
            r'<iframe[^>]*>',
            r'<object[^>]*>',
            r'<embed[^>]*>'
        ]
        
        for pattern in xss_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                logger.warning(f"Potential XSS detected: {input_string}")
                return True
        
        return False
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if len(password) > 128:
            return False, "Password must be less than 128 characters"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is valid"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename to prevent directory traversal"""
        if not filename:
            return ""
        
        # Remove path separators and dangerous characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        filename = re.sub(r'\.\.', '', filename)
        filename = filename.strip('. ')
        
        # Limit filename length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename

class RateLimiter:
    """Simple rate limiter implementation"""
    
    def __init__(self):
        self.requests = {}
    
    def is_allowed(self, key, limit, period):
        """Check if request is allowed based on rate limit"""
        import time
        
        now = time.time()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Remove old requests outside the period
        self.requests[key] = [req_time for req_time in self.requests[key] if now - req_time < period]
        
        # Check if under limit
        if len(self.requests[key]) < limit:
            self.requests[key].append(now)
            return True
        
        return False

# Global rate limiter instance
rate_limiter = RateLimiter()

def rate_limit(limit, period):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Use IP address as key
            key = request.remote_addr
            
            if not rate_limiter.is_allowed(key, limit, period):
                return jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Please try again later.'
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_csrf_token():
    """Validate CSRF token for state-changing requests"""
    if request.method in ['POST', 'PUT', 'DELETE']:
        token = session.pop('_csrf_token', None)
        if not token or token != request.form.get('_csrf_token'):
            abort(403)

def generate_csrf_token():
    """Generate CSRF token"""
    if '_csrf_token' not in session:
        session['_csrf_token'] = secrets.token_hex(16)
    return session['_csrf_token']

def require_https():
    """Decorator to require HTTPS in production"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_secure and not app.debug:
                return redirect(request.url.replace('http://', 'https://'), code=301)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json_input(required_fields=None, optional_fields=None):
    """Decorator to validate JSON input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({'error': 'Content-Type must be application/json'}), 400
            
            data = request.get_json()
            if not data:
                return jsonify({'error': 'Invalid JSON data'}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            # Validate and sanitize input fields
            sanitized_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Check for security issues
                    if SecurityValidator.detect_sql_injection(value):
                        logger.warning(f"SQL injection attempt detected in field {key}: {value}")
                        return jsonify({'error': 'Invalid input detected'}), 400
                    
                    if SecurityValidator.detect_xss(value):
                        logger.warning(f"XSS attempt detected in field {key}: {value}")
                        return jsonify({'error': 'Invalid input detected'}), 400
                    
                    # Sanitize the input
                    sanitized_data[key] = SecurityValidator.sanitize_input(value)
                else:
                    sanitized_data[key] = value
            
            # Replace request data with sanitized data
            request._cached_json = (sanitized_data, True)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_form_input(validation_rules=None):
    """Decorator to validate form input"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if validation_rules:
                for field_name, rules in validation_rules.items():
                    field_value = request.form.get(field_name, '').strip()
                    
                    # Required field validation
                    if rules.get('required', False) and not field_value:
                        return jsonify({
                            'error': f'{field_name} is required'
                        }), 400
                    
                    # Type validation
                    if field_value:
                        field_type = rules.get('type', 'string')
                        
                        if field_type == 'email' and not SecurityValidator.validate_email(field_value):
                            return jsonify({
                                'error': f'Invalid {field_name} format'
                            }), 400
                        
                        elif field_type == 'phone' and not SecurityValidator.validate_phone(field_value):
                            return jsonify({
                                'error': f'Invalid {field_name} format'
                            }), 400
                        
                        elif field_type == 'name' and not SecurityValidator.validate_name(field_value):
                            return jsonify({
                                'error': f'Invalid {field_name} format'
                            }), 400
                        
                        elif field_type == 'password':
                            is_valid, message = SecurityValidator.validate_password(field_value)
                            if not is_valid:
                                return jsonify({'error': message}), 400
                        
                        # Length validation
                        min_length = rules.get('min_length')
                        if min_length and len(field_value) < min_length:
                            return jsonify({
                                'error': f'{field_name} must be at least {min_length} characters'
                            }), 400
                        
                        max_length = rules.get('max_length')
                        if max_length and len(field_value) > max_length:
                            return jsonify({
                                'error': f'{field_name} must be less than {max_length} characters'
                            }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def secure_headers(response):
    """Add security headers to response"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    
    if not request.is_secure:
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    
    # Content Security Policy
    csp = (
        "default-src 'self'; "
        "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; "
        "img-src 'self' data: https:; "
        "font-src 'self' https://cdnjs.cloudflare.com; "
        "connect-src 'self'; "
        "frame-ancestors 'none';"
    )
    response.headers['Content-Security-Policy'] = csp
    
    return response

def log_security_event(event_type, details, severity='INFO'):
    """Log security events"""
    log_message = f"SECURITY_EVENT: {event_type} - {details}"
    
    if severity == 'CRITICAL':
        logger.critical(log_message)
    elif severity == 'WARNING':
        logger.warning(log_message)
    else:
        logger.info(log_message)

def generate_secure_token(length=32):
    """Generate a cryptographically secure token"""
    return secrets.token_hex(length)

def hash_password(password):
    """Hash password using werkzeug"""
    return generate_password_hash(password)

def verify_password(hashed_password, password):
    """Verify password against hash"""
    return check_password_hash(hashed_password, password)

def create_session_token():
    """Create secure session token"""
    return secrets.token_urlsafe(32)

def validate_session():
    """Validate session integrity"""
    if 'user_id' not in session:
        return False
    
    # Check session age
    if 'session_created' in session:
        import time
        session_age = time.time() - session['session_created']
        if session_age > 86400:  # 24 hours
            session.clear()
            return False
    
    return True

class SecurityHeaders:
    """Security headers middleware"""
    
    def __init__(self, app):
        self.app = app
        self.app.after_request(self.add_security_headers)
    
    def add_security_headers(self, response):
        """Add security headers to all responses"""
        return secure_headers(response)

# Input validation schemas
VALIDATION_SCHEMAS = {
    'course': {
        'name': {'required': True, 'type': 'string', 'min_length': 2, 'max_length': 100},
        'duration': {'required': True, 'type': 'string', 'min_length': 1, 'max_length': 50},
        'fees': {'required': True, 'type': 'number', 'min_value': 0},
        'eligibility': {'required': False, 'type': 'string', 'max_length': 500},
        'description': {'required': False, 'type': 'string', 'max_length': 1000}
    },
    'faq': {
        'question': {'required': True, 'type': 'string', 'min_length': 5, 'max_length': 500},
        'answer': {'required': True, 'type': 'string', 'min_length': 5, 'max_length': 1000},
        'category': {'required': True, 'type': 'string', 'max_length': 50}
    },
    'login': {
        'username': {'required': True, 'type': 'string', 'min_length': 3, 'max_length': 20},
        'password': {'required': True, 'type': 'password'}
    },
    'contact': {
        'name': {'required': True, 'type': 'name'},
        'email': {'required': True, 'type': 'email'},
        'phone': {'required': False, 'type': 'phone'},
        'message': {'required': True, 'type': 'string', 'min_length': 10, 'max_length': 1000}
    }
}
