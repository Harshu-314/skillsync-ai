"""
app/models/resume.py

SQLAlchemy model for the `resumes` table.

Represents a single uploaded resume file belonging to a user. Stores
the extracted raw text alongside file metadata, so downstream steps
(skill extraction, re-analysis) work directly against this row rather
than re-reading and re-parsing the PDF from disk each time.

No parsing/extraction logic lives here — that belongs to the resume
service and AI modules built in later sprints. This file defines
structure and relationships only.
"""

from datetime import datetime

from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class Resume(db.Model):
    """
    Represents one uploaded resume and its extracted text.

    Table: resumes
    """

    __tablename__ = "resumes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    # ForeignKey with ondelete="CASCADE" so that, at the database
    # level too (not just via SQLAlchemy's ORM-level cascade on the
    # User side), deleting a user cleans up their resumes. Having it
    # at both levels keeps the DB consistent even if a row is deleted
    # through a raw query that bypasses the ORM.
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)

    # Path where the actual PDF is stored on disk (or, later, object
    # storage) — kept separate from raw_text so the original file
    # remains available (e.g. for the user to re-download) even
    # though analysis only ever needs raw_text.
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)

    # Full extracted text content of the PDF. TEXT (not VARCHAR) since
    # resume length is unbounded and unpredictable.
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)

    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # --- Relationships ---
    user: Mapped["User"] = relationship(back_populates="resumes")

    resume_skills: Mapped[list["ResumeSkill"]] = relationship(
        back_populates="resume", cascade="all, delete-orphan"
    )

    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="resume", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Resume id={self.id} file_name={self.file_name} user_id={self.user_id}>"
