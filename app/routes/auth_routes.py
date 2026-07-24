"""
app/routes/auth_routes.py

Authentication HTTP endpoints.

Why this exists:
    The HTTP layer for registration, login, logout, and a protected
    "current user" endpoint. Per the layered architecture, routes
    only parse requests and shape responses — all business logic
    (validation rules, hashing, uniqueness checks) lives in
    AuthService and app.utils.validators, which this file calls into
    but never duplicates.

Endpoints:
    POST /api/auth/register  — create a new account
    POST /api/auth/login     — authenticate and start a session
    POST /api/auth/logout    — end the current session (protected)
    GET  /api/auth/me        — return the current user's info (protected)
"""

from flask import Blueprint, request
from flask_login import login_user, logout_user, login_required, current_user

from app.models.user import User
from app.services.auth_service import AuthService
from app.utils.api_response import success_response, error_response
from app.utils.validators import validate_login_input

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


def _serialize_user(user: User) -> dict:
    """
    Shapes a User model into a plain dict safe to return in an API
    response. Deliberately excludes password_hash.
    """
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
    }


@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Registers a new user account.

    Expected JSON body:
        { "name": "...", "email": "...", "password": "..." }

    Does NOT start a session — the client is expected to call
    /login separately afterward.
    """
    data = request.get_json(silent=True) or {}
    name = data.get("name", "")
    email = data.get("email", "")
    password = data.get("password", "")

    try:
        user = AuthService.register_user(name=name, email=email, password=password)
    except ValueError as e:
        return error_response(message=str(e), status_code=400)

    return success_response(
        data=_serialize_user(user),
        message="Account created successfully.",
        status_code=201,
    )


@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Authenticates a user and starts a Flask-Login session.

    Expected JSON body:
        { "email": "...", "password": "..." }
    """
    data = request.get_json(silent=True) or {}
    email = data.get("email", "")
    password = data.get("password", "")

    try:
        validate_login_input(email, password)
        user = AuthService.authenticate_user(email=email, password=password)
    except ValueError as e:
        return error_response(message=str(e), status_code=401)

    login_user(user)

    return success_response(
        data=_serialize_user(user),
        message="Logged in successfully.",
    )


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    """
    Ends the current user's session.

    Requires an active session (@login_required) — logging out
    someone who isn't logged in doesn't make sense, so this correctly
    returns a 401 (handled by Flask-Login's unauthorized handler) if
    called with no active session.
    """
    logout_user()
    return success_response(message="Logged out successfully.")


@auth_bp.route("/me", methods=["GET"])
@login_required
def me():
    """
    Returns the currently authenticated user's info. Demonstrates a
    protected route — any future route needing per-user data follows
    this same @login_required + current_user pattern.
    """
    return success_response(data=_serialize_user(current_user))
