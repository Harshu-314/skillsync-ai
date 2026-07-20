"""
run.py

Development server entry point for SkillSync AI Backend.

Why this file is intentionally thin:
    All real application setup (config loading, extension binding,
    blueprint registration, logging, error handlers) lives in the
    application factory (app/__init__.py::create_app). This file's
    only job is to:
      1. Read which environment to run under (from FLASK_ENV, default
         "development").
      2. Call create_app() with it.
      3. Start Werkzeug's dev server.

    Keeping this file minimal means there is nothing here to test —
    the factory itself is what gets exercised by tests (a later
    sprint), by calling create_app("testing") directly, without ever
    running this script.

Usage:
    python run.py
"""

import os

from app import create_app

# Reads FLASK_ENV from the environment (set via .env / python-dotenv,
# loaded below) — defaults to "development" so running this locally
# with no .env configured still works out of the box.
from dotenv import load_dotenv

load_dotenv()

env_name = os.environ.get("FLASK_ENV", "development")
app = create_app(env_name)

if __name__ == "__main__":
    # debug value is already controlled by the loaded config class
    # (DevelopmentConfig sets DEBUG=True), so it isn't hardcoded here.
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
