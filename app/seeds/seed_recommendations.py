"""
app/seeds/seed_recommendations.py

Seeds the `recommendations` table with an initial curated set of
learning resources for a subset of common skills, covering all five
resource_type values defined in app/models/recommendation.py
(RESOURCE_TYPES): course, certification, project_idea, documentation,
practice_platform.

There is no separate "recommendation types" table in the finalized
schema — resource_type is a validated string column, and this seed
data is what makes those type values concrete rather than abstract.

Idempotent by design: recommendations have no single unique column
(a skill can legitimately have multiple resources of the same type),
so uniqueness is checked on the combination of
(skill_id, resource_type, title) before inserting. Running this
script repeatedly will not create duplicate rows.

Depends on seed_skills() having already run — recommendations are
looked up by skill name and skipped with a warning if the skill
doesn't exist yet, rather than failing the whole batch.
"""

from app.extensions import db
from app.models.skill import Skill
from app.models.recommendation import Recommendation

# (skill_name, resource_type, title, url, provider_name)
# url/provider_name are None where not applicable (e.g. project ideas).
RECOMMENDATIONS_SEED_DATA: list[tuple[str, str, str, str | None, str | None]] = [
    # --- Python ---
    ("Python", "course", "Python for Everybody", "https://www.coursera.org/specializations/python", "Coursera"),
    ("Python", "certification", "PCEP – Certified Entry-Level Python Programmer", "https://pythoninstitute.org/pcep", "Python Institute"),
    ("Python", "project_idea", "Build a command-line expense tracker", None, None),
    ("Python", "documentation", "Official Python Documentation", "https://docs.python.org/3/", "python.org"),
    ("Python", "practice_platform", "Python Practice Track", "https://www.hackerrank.com/domains/python", "HackerRank"),

    # --- React ---
    ("React", "course", "React – The Complete Guide", "https://www.udemy.com/course/react-the-complete-guide-incl-redux/", "Udemy"),
    ("React", "project_idea", "Build a personal portfolio site with React", None, None),
    ("React", "documentation", "Official React Documentation", "https://react.dev/", "react.dev"),
    ("React", "practice_platform", "Frontend Mentor React Challenges", "https://www.frontendmentor.io/", "Frontend Mentor"),

    # --- SQL ---
    ("SQL", "course", "SQL for Data Science", "https://www.coursera.org/learn/sql-for-data-science", "Coursera"),
    ("SQL", "practice_platform", "SQL Practice Problems", "https://www.hackerrank.com/domains/sql", "HackerRank"),
    ("SQL", "documentation", "PostgreSQL Documentation", "https://www.postgresql.org/docs/", "PostgreSQL"),

    # --- Docker ---
    ("Docker", "course", "Docker for the Absolute Beginner", "https://www.udemy.com/course/learn-docker/", "Udemy"),
    ("Docker", "certification", "Docker Certified Associate (DCA)", "https://www.docker.com/certification/", "Docker Inc."),
    ("Docker", "project_idea", "Containerize a Flask app with Docker", None, None),
    ("Docker", "documentation", "Official Docker Documentation", "https://docs.docker.com/", "Docker Inc."),

    # --- AWS ---
    ("AWS", "course", "AWS Certified Cloud Practitioner Prep", "https://www.coursera.org/learn/aws-cloud-practitioner-essentials", "Coursera"),
    ("AWS", "certification", "AWS Certified Cloud Practitioner", "https://aws.amazon.com/certification/certified-cloud-practitioner/", "AWS"),
    ("AWS", "documentation", "AWS Documentation", "https://docs.aws.amazon.com/", "AWS"),

    # --- Machine Learning ---
    ("Machine Learning", "course", "Machine Learning Specialization", "https://www.coursera.org/specializations/machine-learning-introduction", "Coursera / DeepLearning.AI"),
    ("Machine Learning", "project_idea", "Build a spam email classifier", None, None),
    ("Machine Learning", "documentation", "Scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html", "scikit-learn"),
    ("Machine Learning", "practice_platform", "Kaggle Competitions", "https://www.kaggle.com/competitions", "Kaggle"),

    # --- Git ---
    ("Git", "course", "Git & GitHub Crash Course", "https://www.freecodecamp.org/news/git-and-github-crash-course/", "freeCodeCamp"),
    ("Git", "documentation", "Official Git Documentation", "https://git-scm.com/doc", "git-scm.com"),
    ("Git", "practice_platform", "Learn Git Branching", "https://learngitbranching.js.org/", "Learn Git Branching"),
]


def seed_recommendations() -> None:
    """
    Inserts each recommendation in RECOMMENDATIONS_SEED_DATA that
    doesn't already exist for its (skill, resource_type, title)
    combination. Skips entries whose referenced skill isn't found
    (e.g. seed_skills() hasn't run yet), logging a warning rather than
    failing the whole batch. Commits once at the end.

    Must be called within an active Flask application context.
    """
    inserted_count = 0
    skipped_existing = 0
    skipped_missing_skill = 0

    for skill_name, resource_type, title, url, provider_name in RECOMMENDATIONS_SEED_DATA:
        skill = Skill.query.filter_by(name=skill_name).first()
        if not skill:
            print(f"[seed_recommendations] WARNING: skill '{skill_name}' not found — "
                  f"run seed_skills() first. Skipping '{title}'.")
            skipped_missing_skill += 1
            continue

        existing = Recommendation.query.filter_by(
            skill_id=skill.id, resource_type=resource_type, title=title
        ).first()
        if existing:
            skipped_existing += 1
            continue

        recommendation = Recommendation(
            skill_id=skill.id,
            resource_type=resource_type,
            title=title,
            url=url,
            provider_name=provider_name,
        )
        db.session.add(recommendation)
        inserted_count += 1

    db.session.commit()
    print(
        f"[seed_recommendations] Inserted {inserted_count}, "
        f"skipped {skipped_existing} (already existed), "
        f"skipped {skipped_missing_skill} (missing skill)."
    )
