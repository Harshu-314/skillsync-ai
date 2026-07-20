"""
app/models/analysis.py

SQLAlchemy model for the `analyses` table.

Represents a single run of skill-gap analysis, tying a specific
resume snapshot to its results at that point in time. Multiple
analysis rows can (and should) exist for the same resume, since
re-running analysis later against a shifted job market can produce a
different result — this table's history is what the dashboard's
"Resume Analysis History" section reads from.

No scoring/comparison logic lives here — that belongs to the gap
analysis service built in a later sprint. This file defines structure
only.
"""

from datetime import datetime

from sqlalchemy import Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Analysis(db.Model):
    """
    Represents one skill-gap analysis run for a user's resume.

    Table: analyses
    """

    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # Indexed: "get all analyses for this user" is the core query
    # behind the dashboard's history view.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Indexed: supports viewing how results changed across re-runs of
    # the same resume over time.
    resume_id: Mapped[int] = mapped_column(
        ForeignKey("resumes.id", ondelete="CASCADE"), nullable=False, index=True
    )

    # Core skill-match result from the gap analysis service
    # (Sentence-Transformer + cosine similarity comparison).
    match_percentage: Mapped[float] = mapped_column(Float, nullable=False)

    # Weighted composite score per the finalized formula:
    # 60% skill match + 20% resume quality + 10% projects + 10% experience.
    resume_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Stored directly rather than recomputed from junction tables on
    # every history-list render — cheap to store, avoids an extra
    # join+count purely to display a summary list.
    matched_skills_count: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_skills_count: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="analyses")
    resume: Mapped["Resume"] = relationship(back_populates="analyses")

    learning_roadmap_entries: Mapped[list["LearningRoadmap"]] = relationship(
        back_populates="analysis", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return (
            f"<Analysis id={self.id} user_id={self.user_id} "
            f"resume_id={self.resume_id} match={self.match_percentage}>"
        )
