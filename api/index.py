import os
import sys
import django
from django.core.wsgi import get_wsgi_application
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'proj1.settings')
django.setup()

# Import the WSGI application
application = get_wsgi_application()

def handler(request, context):
    """
    Vercel serverless function handler for Django application.
    """
    from django.core.handlers.wsgi import WSGIHandler
    from django.http import HttpResponse

    # Create a WSGI environ from the Vercel request
    environ = {
        'REQUEST_METHOD': request.method,
        'SCRIPT_NAME': '',
        'PATH_INFO': request.path,
        'QUERY_STRING': request.query_string or '',
        'CONTENT_TYPE': request.headers.get('content-type', ''),
        'CONTENT_LENGTH': request.headers.get('content-length', '0'),
        'SERVER_NAME': 'vercel.app',
        'SERVER_PORT': '443',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': request.body or b'',
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': False,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }

    # Add headers to environ
    for key, value in request.headers.items():
        key = key.upper().replace('-', '_')
        if key not in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            environ[f'HTTP_{key}'] = value

    # Handle the request
    handler = WSGIHandler()
    response = handler(environ, lambda status, headers: None)

    # Convert Django response to Vercel response format
    status_code = int(response.status_code)
    headers = dict(response.headers)

    return {
        'statusCode': status_code,
        'headers': headers,
        'body': response.content.decode('utf-8') if isinstance(response.content, bytes) else response.content,
    }