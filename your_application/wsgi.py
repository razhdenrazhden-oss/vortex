"""WSGI compatibility entrypoint for platforms that run `gunicorn your_application.wsgi`.

This module allows Render's default Gunicorn command to boot the FastAPI app
if custom Start Command is not applied.
"""

from a2wsgi import ASGIMiddleware

from app.main import app as asgi_app

# Gunicorn default import target expects `application` in module scope.
application = ASGIMiddleware(asgi_app)
