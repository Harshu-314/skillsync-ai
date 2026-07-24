"""
app/auth_setup.py

Configures Flask-Login for this application: binds the LoginManager
to the app, registers the user_loader callback, and overrides the
default unauthorized-request behavior.

Why this is its own file rather than living in extensions.py or
app/__init__.py:
    - extensions.py cannot import the User model or UserRepository
      without creating a circular import (models import `db` FROM
      extensions.py), so the user_loader callback — which needs both
      — cannot be defined there.
    - app/__init__.py is meant to stay pure orchestration (per its own
      docstring), delegating each concern to a small dedicated
      function. This file is that delegate for Flask-Login, following
      the same register_*(app) pattern as register_blueprints,
      register_error_handlers, and register_cli_commands.

Why the unauthorized handler is overridden:
    Flask-Login's default behavior when @login_required blocks an
    unauthenticated request is to redirect (302) to a configured
    login *page* — a reasonable default for a server-rendered HTML
    app, but wrong for a JSON API. Without this override, a React
    frontend would receive a redirect instead of a JSON 401 it can
    actually handle.
"""

from flask import Flask

from app.extensions import login_manager
from app.repositories.user_repository import UserRepository
from app.utils.api_response import error_response


def register_login_manager(app: Flask) -> None:
    """
    Binds Flask-Login to the given app and configures its callbacks.

    Args:
        app: The Flask application instance being configured.
    """
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str):
        """
        Reloads a User from the id stored in the session cookie.
        Called automatically by Flask-Login on every request to a
        route protected by @login_required (and whenever current_user
        is accessed).

        Args:
            user_id: The id Flask-Login stored in the session,
                always passed in as a string (via User.get_id(),
                supplied by UserMixin).

        Returns:
            The matching User, or None if no such user exists
            (e.g. the account was deleted after the session was
            created) — Flask-Login treats None as "not logged in".
        """
        return UserRepository.get_by_id(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        """
        Overrides Flask-Login's default redirect-to-login-page
        behavior. Returns a standard JSON 401 instead, consistent
        with every other error response in this API.
        """
        return error_response(
            message="Authentication required. Please log in.",
            status_code=401,
        )
