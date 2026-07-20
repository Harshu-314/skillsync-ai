"""
app/cli.py

Registers custom Flask CLI commands.

Why a separate file:
    Keeps CLI command definitions out of the application factory
    (app/__init__.py), which stays focused on orchestrating setup
    steps rather than defining command bodies. As more CLI commands
    are added in future sprints (e.g. a `flask seed reset` to wipe
    reference data, or admin utilities), they belong here, grouped
    logically, without the factory growing unbounded.

Commands defined:
    flask seed run   — runs all seed scripts via run_all_seeds()
                        (app/seeds/__init__.py). Safe to run multiple
                        times: every individual seed script is
                        idempotent, so re-running this command updates
                        nothing that already exists rather than
                        duplicating it.
"""

import click
from flask import Flask

from app.seeds import run_all_seeds


def register_cli_commands(app: Flask) -> None:
    """
    Registers all custom CLI command groups on the given Flask app.

    Args:
        app: The Flask application instance being configured.
    """

    @app.cli.group("seed")
    def seed_group():
        """Commands for seeding reference/lookup data into the database."""
        pass

    @seed_group.command("run")
    def seed_run():
        """
        Runs all seed scripts (skills, recommendations, ...) in
        dependency order. Idempotent — safe to run repeatedly.

        Usage:
            flask seed run
        """
        run_all_seeds()
        click.echo("Seeding finished successfully.")
