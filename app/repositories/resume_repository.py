"""
app/repositories/resume_repository.py

Data access layer for the Resume model.
"""

from app.extensions import db
from app.models.resume import Resume


class ResumeRepository:
    """Encapsulates all direct database access for the Resume model."""

    @staticmethod
    def create(user_id: int, file_name: str, file_path: str, raw_text: str) -> Resume:
        """
        Creates and persists a new Resume row.
        """
        resume = Resume(
            user_id=user_id,
            file_name=file_name,
            file_path=file_path,
            raw_text=raw_text,
        )
        db.session.add(resume)
        db.session.commit()
        return resume

    @staticmethod
    def get_by_id_for_user(resume_id: int, user_id: int) -> Resume | None:
        """
        Fetches a resume by id, scoped to a specific owner. Returns
        None if the resume doesn't exist OR belongs to a different
        user — callers should treat both cases identically (404),
        never revealing that a resume with that id exists but isn't
        theirs.
        """
        return Resume.query.filter_by(id=resume_id, user_id=user_id).first()

    @staticmethod
    def list_by_user(user_id: int) -> list[Resume]:
        """
        Returns all resumes belonging to a user, most recent first.
        """
        return (
            Resume.query.filter_by(user_id=user_id)
            .order_by(Resume.uploaded_at.desc())
            .all()
        )

    @staticmethod
    def get_latest_by_user(user_id: int) -> Resume | None:
        """
        Returns the most recently uploaded resume for a user, or None
        if they have no resumes yet.
        """
        return (
            Resume.query.filter_by(user_id=user_id)
            .order_by(Resume.uploaded_at.desc())
            .first()
        )
