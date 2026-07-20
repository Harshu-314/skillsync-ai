"""
app/utils/error_handlers.py

Centralized error handling.

Why this exists:
    By default, Flask returns HTML error pages for things like a 404
    (unknown route) or an unhandled exception (500). Since this is a
    JSON API consumed by a React frontend, every error — expected or
    not — should come back as JSON in the same shape the rest of the
    API uses (see api_response.py). Registering handlers here, once,
    means no individual route ever needs its own try/except for these
    generic cases; only truly business-specific errors (added in
    later sprints) need per-route handling.

Handlers registered:
    - 400 Bad Request
    - 404 Not Found
    - 405 Method Not Allowed
    - 500 Internal Server Error
    - Exception (catch-all safety net for anything unhandled)

Each handler logs the error (so it's traceable in logs/skillsync.log)
before returning the standardized error response.
"""

from flask import Flask
from werkzeug.exceptions import HTTPException

from app.utils.api_response import error_response


def register_error_handlers(app: Flask) -> None:
    """
    Attaches centralized error handlers to the given Flask app.

    Args:
        app: The Flask application instance being configured.
    """

    @app.errorhandler(400)
    def handle_bad_request(error: HTTPException):
        app.logger.warning(f"Bad request: {error}")
        return error_response(
            message="The request was malformed or missing required data.",
            status_code=400,
        )

    @app.errorhandler(404)
    def handle_not_found(error: HTTPException):
        app.logger.warning(f"Not found: {error}")
        return error_response(
            message="The requested resource was not found.",
            status_code=404,
        )

    @app.errorhandler(405)
    def handle_method_not_allowed(error: HTTPException):
        app.logger.warning(f"Method not allowed: {error}")
        return error_response(
            message="This HTTP method is not allowed for the requested endpoint.",
            status_code=405,
        )

    @app.errorhandler(500)
    def handle_internal_server_error(error: HTTPException):
        app.logger.error(f"Internal server error: {error}")
        return error_response(
            message="An unexpected server error occurred.",
            status_code=500,
        )

    @app.errorhandler(Exception)
    def handle_uncaught_exception(error: Exception):
        # Safety net for anything not already covered above (e.g. a
        # bug in a service function raising a plain ValueError).
        # Without this, such errors would surface as Flask's default
        # HTML 500 page instead of our JSON error shape.
        app.logger.exception(f"Unhandled exception: {error}")
        return error_response(
            message="An unexpected error occurred. Please try again later.",
            status_code=500,
        )
