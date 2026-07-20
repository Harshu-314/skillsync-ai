"""
app/utils package.

Groups shared, cross-cutting helpers used across the application:
    - api_response.py: standardized success/error JSON response builders
    - error_handlers.py: centralized exception-to-JSON-response mapping
    - logger.py: application-wide logging configuration

Nothing business-specific lives in this package — only generic
infrastructure helpers reused by routes/services in every sprint.
"""
