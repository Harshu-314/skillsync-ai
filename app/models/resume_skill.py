"""
app/models/resume_skill.py

SQLAlchemy model for the `resume_skills` junction table.

Represents a many-to-many association: a resume has many skills, and
a skill can appear in many resumes. This table is what skill
extraction (a later sprint) populates after running spaCy-based
matching against the `skills` taxonomy on a resume's raw text.

No extraction logic lives here — this file defines structure only.
"""

from sqlalchemy import Float, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class ResumeSkill(db.Model):
    """
    Associates a Resume with a Skill found within it.

    Table: resume_skills
    """

    __tablename__ = "resume_skills"
    __table_args__ = (
        # Prevents the same skill being recorded twice for the same
        # resume (e.g. extraction re-run, or matched via both a
        # canonical name and an alias).
        UniqueConstraint("resume_id", "skill_id", name="uq_resume_skill"),
        # Supports "which resumes have skill X" lookups in addition to
        # the composite index above (which is resume_id-first).
        Index("ix_resume_skills_skill_id", "skill_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    # Confidence/similarity score from the extraction step, when
    # meaningful (e.g. semantic match rather than exact keyword hit).
    # Nullable since not every extraction method produces one.
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # --- Relationships ---
    resume: Mapped["Resume"] = relationship(back_populates="resume_skills")
    skill: Mapped["Skill"] = relationship(back_populates="resume_skills")

    def __repr__(self) -> str:
        return f"<ResumeSkill resume_id={self.resume_id} skill_id={self.skill_id}>"
