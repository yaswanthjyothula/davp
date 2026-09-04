"""
Vercel Serverless Entry Point for Formula 1 Historical Analytics & Cinematic Experience.
Wraps the Flask + Plotly Dash WSGI server.
"""

import os
import sys

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import server

class VercelWSGIHandler:
    """
    WSGI wrapper ensuring original PATH_INFO is preserved
    when Vercel rewrites or proxies requests.
    """
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app

    def __call__(self, environ, start_response):
        matched_path = environ.get('HTTP_X_MATCHED_PATH') or environ.get('HTTP_X_NOW_ROUTE_MATCHES')
        if matched_path:
            current_path = environ.get('PATH_INFO', '')
            if not current_path.startswith('/dashboard') and not current_path.startswith('/_dash'):
                environ['PATH_INFO'] = matched_path
        return self.wsgi_app(environ, start_response)

# Vercel entrypoint looks for 'app' or 'application'
app = VercelWSGIHandler(server)
application = app

if __name__ == '__main__':
    from app import app as dash_app
    dash_app.run(host='0.0.0.0', port=3000, debug=False)
