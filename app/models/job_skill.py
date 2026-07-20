"""
app/models/job_skill.py

SQLAlchemy model for the `job_skills` junction table.

Represents a many-to-many association: a job posting requires many
skills, and a skill appears across many postings. This table is what
demand-aggregation queries (e.g. "most in-demand skills", "top
missing skills by frequency" — SRS section 7) group and count over,
so its skill_id index matters more here than on any other table.

No extraction logic lives here — this file defines structure only.
"""

from sqlalchemy import ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class JobSkill(db.Model):
    """
    Associates a Job posting with a Skill it requires.

    Table: job_skills
    """

    __tablename__ = "job_skills"
    __table_args__ = (
        # Prevents duplicate rows if extraction runs twice on the
        # same posting.
        UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
        # The most important index on this table: demand-aggregation
        # queries group/count by skill_id across many job rows.
        Index("ix_job_skills_skill_id", "skill_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    job_id: Mapped[int] = mapped_column(
        ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    # --- Relationships ---
    job: Mapped["Job"] = relationship(back_populates="job_skills")
    skill: Mapped["Skill"] = relationship(back_populates="job_skills")

    def __repr__(self) -> str:
        return f"<JobSkill job_id={self.job_id} skill_id={self.skill_id}>"
