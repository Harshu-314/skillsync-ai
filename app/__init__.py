"""
app/__init__.py

Application Factory for SkillSync AI Backend.

Why a factory function instead of a module-level `app = Flask(...)`:
    - Enables creating multiple app instances with different config
      (development, testing, production) — critical once the test
      suite exists, since tests need a fresh app + in-memory DB per
      run rather than reusing a shared global instance.
    - Avoids import-time side effects: nothing runs (no DB connection,
      no blueprint registration) until create_app() is explicitly
      called, which keeps this module safe to import from anywhere
      (e.g. Alembic's env.py, test fixtures) without triggering a
      full app boot as a side effect.

This function is intentionally just orchestration — it delegates each
concern (extensions, blueprints, error handlers, logging) to a small
dedicated function/module, so this file stays readable as the project
grows across sprints.
"""

from flask import Flask

from app.config import config_by_name
from app.extensions import db, migrate, cors
from app.auth_setup import register_login_manager
from app.utils.logger import configure_logging
from app.utils.error_handlers import register_error_handlers
from app.routes import register_blueprints
from app.cli import register_cli_commands


def create_app(env_name: str = "development") -> Flask:
    """
    Application factory.

    Args:
        env_name: Which config to load — one of "development",
            "testing", "production". Matches keys in
            config_by_name (app/config.py). Defaults to
            "development" for local runs via `python run.py`.

    Returns:
        A fully configured Flask application instance, ready to run
        or be handed to a WSGI server.
    """
    app = Flask(__name__)

    # 1. Load configuration for the requested environment.
    app.config.from_object(config_by_name[env_name])

    # 2. Bind extensions (created, unbound, in extensions.py) to this
    #    specific app instance.
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, origins=app.config["CORS_ORIGINS"])

    # 2b. Bind Flask-Login and register its user_loader + unauthorized
    #     handler. Kept as its own step (and own file, auth_setup.py)
    #     since it needs the User model / UserRepository, which
    #     extensions.py itself cannot import without a circular import.
    register_login_manager(app)

    # 3. Configure logging before anything else runs, so subsequent
    #    steps (and every route/service from later sprints) can log.
    configure_logging(app)

    # 4. Register all blueprints (currently just health check;
    #    each future sprint adds its blueprint in app/routes/).
    register_blueprints(app)

    # 5. Register centralized error handlers so every route returns
    #    errors in the same standardized JSON shape.
    register_error_handlers(app)

    # 6. Register custom CLI commands (currently: `flask seed run`).
    #    Future sprints add more commands in app/cli.py without this
    #    factory needing any further changes.
    register_cli_commands(app)

    app.logger.info(f"SkillSync AI Backend created with '{env_name}' config.")

    return app
