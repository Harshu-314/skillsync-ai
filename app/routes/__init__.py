"""
app/routes package.

Purpose:
    Centralizes blueprint registration behind a single function,
    register_blueprints(app), called once from the application
    factory (app/__init__.py).

Why this exists:
    As each sprint introduces a new set of endpoints (auth, resume
    upload, job collection, dashboard, etc.), each will live in its
    own <name>_routes.py file defining its own Blueprint. Rather than
    the factory importing and registering each one individually
    (and growing a long, repetitive list over time), it calls this
    one function — which is the only place that needs to know the
    full list of blueprints in the application.
"""

from flask import Flask

from app.routes.health_routes import health_bp


def register_blueprints(app: Flask) -> None:
    """
    Registers all application blueprints on the given Flask app.

    Args:
        app: The Flask application instance being configured.

    Note:
        Future sprints add their blueprint import above and their
        app.register_blueprint(...) call below — this function is
        the single point of change for wiring in new route modules.
    """
    app.register_blueprint(health_bp)
