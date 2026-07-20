"""
app/models/recommendation.py

SQLAlchemy model for the `recommendations` table.

Stores the static, curated skill -> learning-resource mapping that
powers the recommendation engine (SRS section 5). For each skill, one
or more rows here suggest a course, certification, project idea,
piece of documentation, or practice platform.

resource_type is modeled as a plain validated string rather than a
native database enum: SQLite does not meaningfully enforce enum
constraints, so allowed-value validation belongs in the service layer
(built in a later sprint) rather than the schema itself.

No recommendation-selection logic lives here — this file defines
structure only.
"""

from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db

# Allowed values for resource_type. Enforced in the service layer
# (later sprint) rather than as a DB-level CHECK constraint, keeping
# this migration-friendly if the set of types ever needs to grow.
RESOURCE_TYPES = (
    "course",
    "certification",
    "project_idea",
    "documentation",
    "practice_platform",
)


class Recommendation(db.Model):
    """
    Represents one recommended learning resource for a given skill.

    Table: recommendations
    """

    __tablename__ = "recommendations"
    __table_args__ = (
        # Dashboard filters recommendations by type per skill (e.g.
        # "show 2 courses + 1 project idea" rather than 5 of one
        # type), so this composite index supports that access pattern
        # directly, in addition to the plain skill_id FK index below.
        Index("ix_recommendations_skill_type", "skill_id", "resource_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    resource_type: Mapped[str] = mapped_column(String(30), nullable=False)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Nullable: a project_idea recommendation is a text description,
    # not necessarily backed by a URL.
    url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Nullable: not every resource type has a clear "provider" (e.g.
    # a project idea has none).
    provider_name: Mapped[str | None] = mapped_column(String(150), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # --- Relationships ---
    skill: Mapped["Skill"] = relationship(back_populates="recommendations")

    def __repr__(self) -> str:
        return f"<Recommendation id={self.id} skill_id={self.skill_id} type={self.resource_type}>"
