"""
extensions.py

Instantiates Flask extensions at module scope, WITHOUT binding them to
an application instance.

Why this file exists (the circular-import problem it solves):
    - Model files (app/models/*.py) need to import `db` to define
      columns and relationships.
    - The application factory (app/__init__.py) needs those model
      classes to exist before Flask-Migrate can detect them.
    - If `db = SQLAlchemy()` were created *inside* the factory
      function, models importing it at module load time would fail,
      because the factory hasn't run yet when Python first imports
      the models package.

The standard fix: create extension instances here, unbound. Models
import `db` from this module directly. The factory function then
calls `db.init_app(app)` (and similarly for migrate/cors) to bind
each extension to the specific app instance being created.

No configuration values live here — those come from config.py and are
applied only when `.init_app(app)` runs inside the factory.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager

# SQLAlchemy instance — imported by every model file as `from app.extensions import db`
db = SQLAlchemy()

# Flask-Migrate instance — wraps Alembic; bound to both `app` and `db`
# inside the factory, since it needs to know about both to generate
# and apply migrations against our models.
migrate = Migrate()

# CORS instance — allows the React frontend (running on a different
# port/origin during development) to call this API. Actual allowed
# origins are supplied via config (CORS_ORIGINS) when init_app runs.
cors = CORS()

# Flask-Login instance — manages session-based authentication state
# (login_user(), logout_user(), @login_required, current_user).
# Its user-loader callback and unauthorized-request handler are
# registered in the factory (app/__init__.py), not here, since both
# need the User model and UserRepository, which this module cannot
# import without creating a circular import (models import `db` from
# this file).
login_manager = LoginManager()
