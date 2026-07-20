"""
app/models/skill.py

SQLAlchemy model for the `skills` table.

The single source of truth for every skill the system recognizes.
Both resume-skill extraction and job-description-skill extraction
match against this table, ensuring the two sides of the gap analysis
(student skills vs. industry skills) are always compared using the
same controlled vocabulary rather than free-form, inconsistent
strings.

Replaces the earlier skills_v1.json approach from the v1 SRS — moving
the taxonomy into the database allows it to grow without a code
deploy and lets other tables reference it via a proper foreign key.

No extraction/matching logic lives here — this file defines structure
only. Alias resolution and NLP matching belong to the AI module built
in a later sprint.
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Skill(db.Model):
    """
    Represents a single recognized skill in the master taxonomy.

    Table: skills
    """

    __tablename__ = "skills"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Canonical name, e.g. "Python", "React", "Machine Learning".
    # Unique because this is a controlled vocabulary — every other
    # table references a skill by this row's id, never by a raw
    # string, so duplicates here would silently fragment matching.
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    # Groups skills for dashboard views (e.g. "Skill Categories",
    # category-filtered "Most In-Demand Skills"). Indexed since it's
    # queried/grouped-by frequently, but not unique — many skills
    # share a category.
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Alternate names/abbreviations stored as a JSON array string,
    # e.g. '["ML", "Machine-Learning"]'. Nullable: many skills have no
    # common alias. Parsed and used by extraction logic (later
    # sprint), not queried directly at the SQL level.
    aliases: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Optional longer-form description; not required for matching
    # logic, purely informational (e.g. for a future admin view).
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # --- Relationships ---
    # A skill can appear in many resumes, many job postings, have
    # many recommended resources, and be the focus of many roadmap
    # entries — all one-to-many from this side.
    resume_skills: Mapped[list["ResumeSkill"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )
    job_skills: Mapped[list["JobSkill"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )
    learning_roadmap_entries: Mapped[list["LearningRoadmap"]] = relationship(
        back_populates="skill", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Skill id={self.id} name={self.name} category={self.category}>"
