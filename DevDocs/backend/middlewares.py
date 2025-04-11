"""Middleware functions for the Flask application"""
from flask import request, current_app

def setup_cors_headers(response):
    """Add CORS headers to every response"""
    # Allow requests from any origin
    response.headers['Access-Control-Allow-Origin'] = '*'
    
    # Allow specific HTTP methods
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    
    # Allow specific headers in requests
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    
    # Allow cookies in CORS requests
    # response.headers['Access-Control-Allow-Credentials'] = 'true'
    
    # Cache preflight response for 1 hour (3600 seconds)
    response.headers['Access-Control-Max-Age'] = '3600'
    
    return response

def handle_options_requests():
    """Handler for OPTIONS requests"""
    if request.method == 'OPTIONS':
        # Create response object
        response = current_app.make_default_options_response()
        
        # Add CORS headers
        setup_cors_headers(response)
        
        return response
    
    # Not an OPTIONS request, continue normal processing
    return None
