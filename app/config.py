"""
config.py

Defines application configuration using class-based settings.

Why class-based config:
    Flask supports loading configuration from a Python object via
    `app.config.from_object(config_class)`. Using classes (instead of
    scattering constants across files) lets us:
      - Keep all tunable settings in one place.
      - Share common defaults via inheritance.
      - Swap environments (development / testing / production) with a
        single string, without touching any other file.

No business logic lives here — only configuration values, all sourced
from environment variables with sane local-dev defaults.
"""

import os
from datetime import timedelta

# Base directory of the project (one level above this file's parent,
# i.e. the project root, since this file lives in app/config.py)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


class Config:
    """
    Base configuration shared by all environments.

    Environment-specific classes below override only what differs.
    Values are read from environment variables where they represent
    secrets or deployment-specific settings, with safe local defaults
    so the app still runs out-of-the-box for local development.
    """

    # --- Flask core ---
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "dev-secret-key-change-in-env-file")

    # --- SQLAlchemy ---
    # Disabling event system we don't use; saves memory and avoids a
    # deprecation warning SQLAlchemy raises if left unset.
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False

    # Default DB path; overridden per-environment below via subclasses
    # or via the DATABASE_URL environment variable if set.
    SQLALCHEMY_DATABASE_URI: str = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'skillsync.db')}"
    )

    # --- CORS ---
    # Comma-separated list in .env, split into a list here.
    # Example .env value: CORS_ORIGINS=http://localhost:3000
    CORS_ORIGINS: list[str] = os.environ.get(
        "CORS_ORIGINS", "http://localhost:3000"
    ).split(",")

    # --- Logging ---
    LOG_DIR: str = os.path.join(BASE_DIR, "logs")
    LOG_FILE: str = os.path.join(LOG_DIR, "skillsync.log")
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")

    # --- File Upload (values only — enforcement logic comes in the
    # Resume Upload sprint; defined now so they're not hardcoded later) ---
    MAX_CONTENT_LENGTH: int = 5 * 1024 * 1024  # 5 MB, per SRS section 10
    ALLOWED_RESUME_EXTENSIONS: set[str] = {"pdf"}

    # Where uploaded resume PDFs are saved on disk. Built from BASE_DIR
    # (not a relative path) so it resolves consistently regardless of
    # the working directory `python run.py` happens to be launched
    # from. Local disk storage only — no cloud storage (S3 etc.), per
    # the project's stated "no cloud infrastructure" scope constraint.
    UPLOAD_FOLDER: str = os.path.join(BASE_DIR, "uploads", "resumes")

    # --- Session / misc ---
    PERMANENT_SESSION_LIFETIME = timedelta(hours=12)


class DevelopmentConfig(Config):
    """Local development settings: debug on, verbose logging."""

    DEBUG: bool = True
    LOG_LEVEL: str = "DEBUG"


class TestingConfig(Config):
    """
    Used by the automated test suite (introduced in a later sprint).
    Uses an in-memory SQLite database so tests never touch real data
    and each test run starts fresh.
    """

    TESTING: bool = True
    DEBUG: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"


class ProductionConfig(Config):
    """
    Production settings: debug off, secret key MUST come from the
    environment (no fallback) — enforced in __init__.py at app-creation
    time, not here, so importing this module never raises by itself.
    """

    DEBUG: bool = False


# Maps a simple string key (used by the app factory / FLASK_ENV) to the
# actual config class. Keeps __init__.py from importing class names
# directly and having to know they exist.
config_by_name: dict[str, type[Config]] = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}
