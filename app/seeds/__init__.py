"""
app/seeds package.

Orchestrates database seeding via a single entry point:
run_all_seeds(). This is the one place that knows the full list of
seed scripts and the order they must run in — individual scripts
(seed_skills, seed_recommendations, ...) are self-contained and don't
reference each other directly, but some have real data dependencies
(e.g. recommendations reference skills by name), so ordering here
matters.

How to add a new seed script in a future sprint:
    1. Create app/seeds/seed_<something>.py, following the same
       pattern as seed_skills.py / seed_recommendations.py: a single
       function (e.g. seed_something()) that is idempotent (checks
       for existing rows before inserting) and commits once at the
       end.
    2. Import that function below and add a call to it inside
       run_all_seeds(), in the correct dependency position.
    No other file needs to change — the CLI command (app/cli.py)
    calls run_all_seeds() and has no awareness of what's inside it.
"""

from app.seeds.seed_skills import seed_skills
from app.seeds.seed_recommendations import seed_recommendations


def run_all_seeds() -> None:
    """
    Runs every seed script in the correct dependency order.

    Must be called within an active Flask application context (the
    CLI command that invokes this is responsible for that — Flask CLI
    commands run inside an app context automatically).

    Order matters:
        1. seed_skills()          — no dependencies, must run first
        2. seed_recommendations() — depends on skills already existing
    """
    print("[seeds] Starting database seed...")
    seed_skills()
    seed_recommendations()
    print("[seeds] Database seed complete.")
