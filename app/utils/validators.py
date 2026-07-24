"""
app/utils/validators.py

Reusable input validation helpers.

Why this exists:
    Format validation (is this a well-formed email? is this password
    long enough?) is a generic concern, not specific to authentication
    business rules (is this email already taken?). Separating the two
    keeps auth_service.py focused on authentication logic, and makes
    these validators reusable by other features later (e.g. profile
    editing, or any future form) without duplicating regex/length
    checks.

Each function raises ValueError with a client-safe message on
failure, and returns None (implicitly) on success — callers simply
call the function and let a ValueError propagate if input is invalid.
"""

import re

# Simple, intentionally permissive email pattern: local-part@domain.tld
# Full RFC-5322 compliance is unnecessary complexity for this project's
# scope — this catches realistic typos/malformed input without
# rejecting valid addresses on edge cases.
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

MIN_PASSWORD_LENGTH = 8
MIN_NAME_LENGTH = 2
MAX_NAME_LENGTH = 100


def validate_registration_input(name: str, email: str, password: str) -> None:
    """
    Validates registration input, raising ValueError on the first
    problem encountered.

    Args:
        name: Proposed display name.
        email: Proposed email address.
        password: Proposed plaintext password.

    Raises:
        ValueError: with a specific, client-safe message describing
            what's wrong.
    """
    if not name or not name.strip():
        raise ValueError("Name is required.")
    if len(name.strip()) < MIN_NAME_LENGTH or len(name.strip()) > MAX_NAME_LENGTH:
        raise ValueError(
            f"Name must be between {MIN_NAME_LENGTH} and {MAX_NAME_LENGTH} characters."
        )

    validate_email_format(email)

    if not password:
        raise ValueError("Password is required.")
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters long.")


def validate_login_input(email: str, password: str) -> None:
    """
    Validates that login input is present and well-formed enough to
    even attempt authentication. Does NOT check whether the
    credentials are correct — that's authenticate_user()'s job.

    Args:
        email: Supplied email address.
        password: Supplied plaintext password.

    Raises:
        ValueError: if either field is missing/malformed.
    """
    if not email or not email.strip():
        raise ValueError("Email is required.")
    if not password:
        raise ValueError("Password is required.")

    validate_email_format(email)


def validate_email_format(email: str) -> None:
    """
    Validates that a string is a plausible email address shape.

    Args:
        email: The email string to check.

    Raises:
        ValueError: if the email is missing or doesn't match the
            expected pattern.
    """
    if not email or not email.strip():
        raise ValueError("Email is required.")
    if not EMAIL_PATTERN.match(email.strip()):
        raise ValueError("Please provide a valid email address.")
