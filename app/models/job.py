"""
app/models/job.py

SQLAlchemy model for the `jobs` table.

Represents a single job posting collected from whichever provider is
currently active (Apify, CSV import, or a future API), per the
provider-abstraction design finalized in the architecture review.
This table is the "industry demand" side of the skill gap analysis —
independent of any individual user.

No ingestion/provider logic lives here — that belongs to the Job
Collection Service and its providers, built in a later sprint. This
file defines structure only.
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Job(db.Model):
    """
    Represents a single job posting.

    Table: jobs
    """

    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Nullable: not every ingestion source reliably provides a company
    # name (e.g. a partial CSV import), and rejecting a whole posting
    # just because this one field is missing would be too strict.
    company: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Full posting text — this is what job-skill extraction (later
    # sprint) runs against, so it must always be present; a posting
    # with no description text contributes nothing to demand analysis.
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Identifies which provider produced this row, e.g. "apify_indeed"
    # or "csv_import" — matches the Job Collection Service's provider
    # abstraction. Indexed for source-based filtering/debugging.
    source: Mapped[str] = mapped_column(String(50), nullable=False, index=True)

    # Link back to the original posting, when the source provides one.
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # When this row was ingested. Indexed because demand-aggregation
    # queries filter/sort on recency (e.g. "postings from the last
    # 30 days") constantly.
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow, index=True
    )

    # --- Relationships ---
    job_skills: Mapped[list["JobSkill"]] = relationship(
        back_populates="job", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Job id={self.id} title={self.title} source={self.source}>"
