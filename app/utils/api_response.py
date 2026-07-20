"""
app/utils/api_response.py

Standardized API response builders.

Why this exists:
    Without a shared convention, different routes/developers tend to
    shape JSON responses differently (some return {"error": "..."},
    others {"message": "..."}, etc.), which makes the frontend's error
    handling brittle. This module defines exactly two functions —
    success_response() and error_response() — used by EVERY route and
    by the centralized error handlers, so the shape is identical
    everywhere:

    Success shape:
        {
            "success": true,
            "data": <payload>,
            "message": "..."
        }

    Error shape:
        {
            "success": false,
            "message": "...",
            "errors": <optional details>
        }

    Both are paired with an appropriate HTTP status code, returned as
    a (dict, status_code) tuple — Flask accepts this directly from a
    route function.
"""

from typing import Any


def success_response(
    data: Any = None, message: str = "Request successful", status_code: int = 200
) -> tuple[dict, int]:
    """
    Builds a standardized success response.

    Args:
        data: The payload to return (dict, list, primitive, or None).
        message: Human-readable success message.
        status_code: HTTP status code, defaults to 200.

    Returns:
        Tuple of (response_dict, status_code), directly returnable
        from a Flask route.
    """
    return (
        {
            "success": True,
            "data": data,
            "message": message,
        },
        status_code,
    )


def error_response(
    message: str = "An error occurred",
    errors: Any = None,
    status_code: int = 400,
) -> tuple[dict, int]:
    """
    Builds a standardized error response.

    Args:
        message: Human-readable summary of what went wrong.
        errors: Optional additional detail — e.g. field-level
            validation errors, or None if not applicable.
        status_code: HTTP status code, defaults to 400.

    Returns:
        Tuple of (response_dict, status_code), directly returnable
        from a Flask route or an error handler.
    """
    return (
        {
            "success": False,
            "message": message,
            "errors": errors,
        },
        status_code,
    )
