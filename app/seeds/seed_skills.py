"""
app/seeds/seed_skills.py

Seeds the `skills` table with an initial curated taxonomy.

This is the master vocabulary that resume-skill extraction and
job-description-skill extraction (both later sprints) match against.
Categories (Programming, Frontend, Backend, Database, Cloud, DevOps,
AI) are represented implicitly via each skill's `category` field,
per the finalized schema — there is no separate categories table.

Idempotent by design: each skill is looked up by its unique `name`
before insertion. Already-present skills are skipped, so this script
is safe to run any number of times without creating duplicates or
raising a unique-constraint error.
"""

import json

from app.extensions import db
from app.models.skill import Skill

# (name, category, aliases) — aliases is a list, stored as a JSON
# string per the Skill model's design (app/models/skill.py). Empty
# list where no common alias exists.
SKILLS_SEED_DATA: list[tuple[str, str, list[str]]] = [
    # --- Programming ---
    ("Python", "Programming", []),
    ("Java", "Programming", []),
    ("C++", "Programming", ["CPP"]),
    ("JavaScript", "Programming", ["JS"]),
    ("TypeScript", "Programming", ["TS"]),
    # --- Frontend ---
    ("React", "Frontend", ["ReactJS"]),
    ("HTML", "Frontend", ["HTML5"]),
    ("CSS", "Frontend", ["CSS3"]),
    ("Angular", "Frontend", []),
    # --- Backend ---
    ("Flask", "Backend", []),
    ("Django", "Backend", []),
    ("Node.js", "Backend", ["NodeJS"]),
    ("Express.js", "Backend", ["ExpressJS"]),
    ("REST API", "Backend", ["RESTful API"]),
    # --- Database ---
    ("SQL", "Database", []),
    ("MySQL", "Database", []),
    ("PostgreSQL", "Database", ["Postgres"]),
    ("MongoDB", "Database", []),
    ("SQLite", "Database", []),
    # --- Cloud ---
    ("AWS", "Cloud", ["Amazon Web Services"]),
    ("Azure", "Cloud", ["Microsoft Azure"]),
    ("Google Cloud Platform", "Cloud", ["GCP"]),
    # --- DevOps ---
    ("Docker", "DevOps", []),
    ("Git", "DevOps", []),
    ("Linux", "DevOps", []),
    ("CI/CD", "DevOps", ["Continuous Integration"]),
    # --- AI ---
    ("Machine Learning", "AI", ["ML"]),
    ("Deep Learning", "AI", ["DL"]),
    ("Natural Language Processing", "AI", ["NLP"]),
    ("TensorFlow", "AI", []),
    ("PyTorch", "AI", []),
    ("Pandas", "AI", []),
    ("NumPy", "AI", []),
    ("Scikit-learn", "AI", ["sklearn"]),
]


def seed_skills() -> None:
    """
    Inserts each skill in SKILLS_SEED_DATA that doesn't already exist
    (matched by name). Commits once at the end.

    Must be called within an active Flask application context (the
    caller — the CLI seed command — is responsible for that).
    """
    inserted_count = 0
    skipped_count = 0

    for name, category, aliases in SKILLS_SEED_DATA:
        existing = Skill.query.filter_by(name=name).first()
        if existing:
            skipped_count += 1
            continue

        skill = Skill(
            name=name,
            category=category,
            aliases=json.dumps(aliases) if aliases else None,
        )
        db.session.add(skill)
        inserted_count += 1

    db.session.commit()
    print(f"[seed_skills] Inserted {inserted_count}, skipped {skipped_count} (already existed).")
