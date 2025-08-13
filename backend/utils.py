"""
Utility functions for StockBuddy Backend
"""
import re
import logging
from functools import wraps
from flask import request, jsonify
import time

logger = logging.getLogger(__name__)

def validate_symbol(symbol):
    """Validate stock symbol format"""
    if not symbol or not isinstance(symbol, str):
        return False
    
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Check if symbol contains only alphanumeric characters and is reasonable length
    if not re.match(r'^[A-Z0-9]{1,15}$', symbol):
        return False
    
    return symbol

def validate_numeric(value, field_name, min_value=None, max_value=None):
    """Validate numeric input with optional range checking"""
    try:
        num_value = float(value)
        
        if min_value is not None and num_value < min_value:
            raise ValueError(f"{field_name} must be at least {min_value}")
        
        if max_value is not None and num_value > max_value:
            raise ValueError(f"{field_name} must not exceed {max_value}")
        
        return num_value
    except (ValueError, TypeError) as e:
        raise ValueError(f"Invalid {field_name}: {str(e)}")

def sanitize_input(data):
    """Sanitize input data"""
    if isinstance(data, str):
        # Remove potentially harmful characters
        return re.sub(r'[<>"\']', '', data.strip())
    elif isinstance(data, dict):
        return {k: sanitize_input(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_input(item) for item in data]
    else:
        return data

def rate_limit(max_requests=100, per_seconds=3600):
    """Simple in-memory rate limiting decorator"""
    requests_log = {}
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_id = request.remote_addr
            now = time.time()
            
            # Clean old entries
            requests_log[client_id] = [
                req_time for req_time in requests_log.get(client_id, [])
                if now - req_time < per_seconds
            ]
            
            # Check rate limit
            if len(requests_log.get(client_id, [])) >= max_requests:
                logger.warning(f"Rate limit exceeded for {client_id}")
                return jsonify({'error': 'Rate limit exceeded'}), 429
            
            # Log this request
            if client_id not in requests_log:
                requests_log[client_id] = []
            requests_log[client_id].append(now)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def log_execution_time(f):
    """Decorator to log function execution time"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        execution_time = time.time() - start_time
        logger.info(f"{f.__name__} executed in {execution_time:.3f} seconds")
        return result
    return decorated_function

def safe_divide(numerator, denominator, default=0):
    """Safe division with default value for zero division"""
    try:
        return numerator / denominator if denominator != 0 else default
    except (TypeError, ValueError):
        return default

def format_currency(amount, currency='INR'):
    """Format currency amount"""
    try:
        return f"{currency} {amount:,.2f}"
    except (ValueError, TypeError):
        return f"{currency} 0.00"

def validate_request_data(required_fields=None, optional_fields=None):
    """Decorator to validate request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.get_json() if request.is_json else request.form.to_dict()
            
            if not data:
                return jsonify({'error': 'No data provided'}), 400
            
            # Check required fields
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'error': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            # Sanitize all input data
            data = sanitize_input(data)
            
            # Add sanitized data to kwargs
            kwargs['validated_data'] = data
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

class APICache:
    """Simple in-memory cache for API responses"""
    def __init__(self, default_timeout=300):
        self.cache = {}
        self.default_timeout = default_timeout
    
    def get(self, key):
        if key in self.cache:
            data, timestamp, timeout = self.cache[key]
            if time.time() - timestamp < timeout:
                return data
            else:
                del self.cache[key]
        return None
    
    def set(self, key, value, timeout=None):
        timeout = timeout or self.default_timeout
        self.cache[key] = (value, time.time(), timeout)
    
    def clear(self):
        self.cache.clear()
    
    def size(self):
        return len(self.cache)

# Global cache instance
api_cache = APICache()

def cached_api_call(timeout=300):
    """Decorator for caching API calls"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Create cache key from function name and arguments
            cache_key = f"{f.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            cached_result = api_cache.get(cache_key)
            if cached_result is not None:
                logger.info(f"Cache hit for {f.__name__}")
                return cached_result
            
            # Execute function and cache result
            result = f(*args, **kwargs)
            api_cache.set(cache_key, result, timeout)
            logger.info(f"Cache miss for {f.__name__}, result cached")
            
            return result
        return decorated_function
    return decorator
