"""
API Authentication Middleware for borctakip application.
Provides Bearer token authentication using API keys.
"""

from typing import Optional, Dict, Callable
from api_key_manager import validate_api_key


def authenticate_api_request(authorization_header: Optional[str]) -> Optional[Dict]:
    """
    Authenticate an API request using the Authorization header.
    
    Args:
        authorization_header: The value of the Authorization header
                             Expected format: "Bearer <api_key>"
    
    Returns:
        Dictionary with user context if authenticated, None otherwise
    """
    if not authorization_header:
        return None
    
    # Check for Bearer token
    parts = authorization_header.split()
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
    
    api_key = parts[1]
    
    # Validate the API key
    key_data = validate_api_key(api_key)
    
    if not key_data:
        return None
    
    # Return user context
    return {
        'user_id': key_data['user_id'],
        'key_id': key_data['id'],
        'key_name': key_data['key_name'],
        'authenticated': True
    }


def require_api_auth(func: Callable) -> Callable:
    """
    Decorator to require API authentication for a function.
    
    Usage:
        @require_api_auth
        def my_protected_function(auth_context, *args, **kwargs):
            user_id = auth_context['user_id']
            # ... function logic
    
    Args:
        func: The function to protect
        
    Returns:
        Wrapped function that requires authentication
    """
    def wrapper(authorization_header: str, *args, **kwargs):
        auth_context = authenticate_api_request(authorization_header)
        
        if not auth_context:
            return {
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key',
                'status': 401
            }
        
        # Call the original function with auth context
        return func(auth_context, *args, **kwargs)
    
    return wrapper


# Example Flask middleware (if using Flask)
class FlaskAPIAuthMiddleware:
    """
    Flask middleware for API authentication.
    
    Usage in Flask:
        from flask import Flask, request
        
        app = Flask(__name__)
        auth_middleware = FlaskAPIAuthMiddleware()
        
        @app.before_request
        def check_auth():
            return auth_middleware.before_request(request)
    """
    
    def __init__(self, excluded_paths=None):
        """
        Initialize the middleware.
        
        Args:
            excluded_paths: List of paths that don't require authentication
        """
        self.excluded_paths = excluded_paths or []
    
    def before_request(self, request):
        """
        Check authentication before each request.
        
        Args:
            request: Flask request object
            
        Returns:
            None if authenticated, error response otherwise
        """
        # Skip authentication for excluded paths
        if request.path in self.excluded_paths:
            return None
        
        # Get authorization header
        auth_header = request.headers.get('Authorization')
        
        # Authenticate
        auth_context = authenticate_api_request(auth_header)
        
        if not auth_context:
            from flask import jsonify
            return jsonify({
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key'
            }), 401
        
        # Store auth context in request for later use
        request.auth_context = auth_context
        return None


# Example FastAPI dependency (if using FastAPI)
def get_api_auth(authorization: Optional[str] = None) -> Dict:
    """
    FastAPI dependency for API authentication.
    
    Usage:
        from fastapi import Depends, Header
        
        @app.get("/protected")
        def protected_endpoint(
            auth: Dict = Depends(
                lambda authorization: get_api_auth(authorization)
            ),
            authorization: str = Header(None)
        ):
            user_id = auth['user_id']
            # ... endpoint logic
    
    Args:
        authorization: Authorization header value
        
    Returns:
        Authentication context dictionary
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_context = authenticate_api_request(authorization)
    
    if not auth_context:
        # Import FastAPI HTTPException only if using FastAPI
        try:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing API key",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except ImportError:
            # If FastAPI is not available, return error dict
            return {
                'error': 'Unauthorized',
                'message': 'Invalid or missing API key',
                'status': 401
            }
    
    return auth_context


# Simple function-based authentication check
def check_api_auth(authorization_header: Optional[str]) -> tuple:
    """
    Simple authentication check that returns status and context.
    
    Args:
        authorization_header: The Authorization header value
        
    Returns:
        Tuple of (is_authenticated: bool, context: Dict or None)
    """
    if not authorization_header:
        return False, None
    
    auth_context = authenticate_api_request(authorization_header)
    
    if auth_context:
        return True, auth_context
    
    return False, None


if __name__ == '__main__':
    # Test the middleware
    print("API Authentication Middleware Test")
    print("=" * 50)
    
    # Test with no header
    result = authenticate_api_request(None)
    print(f"No header: {result}")
    
    # Test with invalid format
    result = authenticate_api_request("InvalidFormat")
    print(f"Invalid format: {result}")
    
    # Test with Bearer but invalid key
    result = authenticate_api_request("Bearer invalid_key_12345")
    print(f"Invalid key: {result}")
    
    print("\nTo test with a real key:")
    print("1. Create an API key using api_key_manager.py")
    print("2. Use: authenticate_api_request('Bearer <your_key>')")
