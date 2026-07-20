"""
app/models package.

Aggregates all model imports in one place. This matters for
Flask-Migrate/Alembic: it detects tables by inspecting whichever
model classes have been imported into Python's memory at the time
`flask db migrate` runs. Importing every model here, and importing
this package once from the app factory's context, guarantees Alembic
sees the full schema — not just whichever model happened to be
imported by whatever route ran first.

Models are added here one at a time as each is built and approved.
"""

from app.models.user import User
from app.models.resume import Resume
from app.models.skill import Skill
from app.models.job import Job
from app.models.resume_skill import ResumeSkill
from app.models.job_skill import JobSkill
from app.models.recommendation import Recommendation
from app.models.analysis import Analysis
from app.models.learning_roadmap import LearningRoadmap

__all__ = [
    "User",
    "Resume",
    "Skill",
    "Job",
    "ResumeSkill",
    "JobSkill",
    "Recommendation",
    "Analysis",
    "LearningRoadmap",
]
