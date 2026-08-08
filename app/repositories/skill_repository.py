"""
app/repositories/skill_repository.py

Data access layer for the Skill model.
"""

from app.extensions import db
from app.models.skill import Skill


class SkillRepository:
    """Encapsulates all direct database access for the Skill model."""

    @staticmethod
    def get_all() -> list[Skill]:
        """
        Returns the full skill taxonomy, ordered by category then
        name for stable, predictable output — used both to build the
        extractor's matcher vocabulary and to serve GET /api/skills.
        """
        return Skill.query.order_by(Skill.category, Skill.name).all()

    @staticmethod
    def get_by_id(skill_id: int) -> Skill | None:
        """Fetches a single skill by primary key."""
        return db.session.get(Skill, skill_id)
