"""
WSGI entry point for Axis Colleges AI Chatbot
Production-ready WSGI configuration for deployment
"""

import os
from advanced_ai_app import app

# Configure application for production
app.config['DEBUG'] = False
app.config['TESTING'] = False

# Security headers for production
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# WSGI application
application = app

if __name__ == "__main__":
    application.run()
