"""
app/models/learning_roadmap.py

SQLAlchemy model for the `learning_roadmaps` table.

Stores the generated 8-week learning plan, tied to a specific
Analysis rather than directly to a user — so a past roadmap remains
viewable even after the user re-runs analysis and receives a new one.

Modeled as one row per week-per-skill (rather than a single JSON blob
for the whole plan) so the dashboard can query/filter/reorder entries
directly, and so joining with `recommendations` on skill_id to show
resources per week is a simple query rather than a deserialization
step.

No roadmap-generation logic lives here — that belongs to the roadmap
service built in a later sprint. This file defines structure only.
"""

from sqlalchemy import Integer, Text, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class LearningRoadmap(db.Model):
    """
    Represents one week-and-skill entry within a generated learning
    roadmap for a specific analysis run.

    Table: learning_roadmaps
    """

    __tablename__ = "learning_roadmaps"
    __table_args__ = (
        # Roadmaps are always displayed in week order for a specific
        # analysis; this composite index directly supports that
        # access pattern and also covers analysis_id-only lookups
        # (since it's the leading column), so no separate single-
        # column index is needed.
        Index("ix_learning_roadmaps_analysis_week", "analysis_id", "week_number"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    analysis_id: Mapped[int] = mapped_column(
        ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False
    )

    # 1-8, per the fixed 8-week plan format. Range validation belongs
    # to the roadmap-generation service (later sprint), not enforced
    # at the schema level.
    week_number: Mapped[int] = mapped_column(Integer, nullable=False)

    skill_id: Mapped[int] = mapped_column(
        ForeignKey("skills.id", ondelete="CASCADE"), nullable=False
    )

    # Optional elaboration on what to do that week (e.g. specific
    # course + project suggestion). Nullable since skill + week number
    # alone may suffice for a minimal first version of the generator.
    focus_description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # --- Relationships ---
    analysis: Mapped["Analysis"] = relationship(
        back_populates="learning_roadmap_entries"
    )
    skill: Mapped["Skill"] = relationship(back_populates="learning_roadmap_entries")

    def __repr__(self) -> str:
        return (
            f"<LearningRoadmap id={self.id} analysis_id={self.analysis_id} "
            f"week={self.week_number} skill_id={self.skill_id}>"
        )
