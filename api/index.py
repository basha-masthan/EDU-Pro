import os
import sys

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj1.settings')

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import django
from django.core.wsgi import get_wsgi_application
from django.conf import settings

django.setup()

# Import the WSGI application
application = get_wsgi_application()

def handler(event, context):
    """
    Vercel serverless function handler for Django application.
    """
    try:
        from django.core.handlers.wsgi import WSGIHandler
        from io import BytesIO

        # Extract request data from Vercel event
        method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_string = event.get('queryStringParameters', {})
        headers = event.get('headers', {})
        body = event.get('body', '')

        # Build query string
        query_str = '&'.join([f"{k}={v}" for k, v in query_string.items()]) if query_string else ''

        # Create WSGI environ
        environ = {
            'REQUEST_METHOD': method,
            'SCRIPT_NAME': '',
            'PATH_INFO': path,
            'QUERY_STRING': query_str,
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body) if body else 0),
            'SERVER_NAME': headers.get('host', 'vercel.app'),
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': BytesIO(body.encode('utf-8') if isinstance(body, str) else body or b''),
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }

        # Add headers to environ
        for key, value in headers.items():
            key = key.upper().replace('-', '_')
            if key not in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                environ[f'HTTP_{key}'] = value

        # Handle the request
        handler = WSGIHandler()
        response_data = {}

        def start_response(status, response_headers, exc_info=None):
            response_data['statusCode'] = int(status.split()[0])
            response_data['headers'] = {k: v for k, v in response_headers}

        # Get response
        response_body = handler(environ, start_response)

        # Convert response body
        if hasattr(response_body, '__iter__'):
            response_body = b''.join(response_body)

        response_data['body'] = response_body.decode('utf-8') if isinstance(response_body, bytes) else str(response_body)

        return response_data

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        # Return error response with full traceback
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}", "traceback": "{error_details}"}}'
        }