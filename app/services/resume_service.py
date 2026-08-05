"""
app/services/resume_service.py

Business logic for resume upload and retrieval.
"""

import os
import uuid

from flask import current_app

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository
from app.utils.pdf_extractor import extract_text_from_pdf
from app.utils.validators import validate_resume_file


class ResumeService:
    """Encapsulates resume upload/processing/retrieval business logic."""

    @staticmethod
    def upload_resume(user_id: int, file) -> Resume:
        """
        Validates, saves, extracts text from, and persists an
        uploaded resume file.

        Args:
            user_id: The id of the currently authenticated user.
            file: A werkzeug FileStorage object from request.files.

        Returns:
            The newly created Resume.

        Raises:
            ValueError: if the file fails validation, or if no
                extractable text is found (e.g. a scanned/image-only
                PDF with no real text layer).
        """
        validate_resume_file(file)

        upload_folder = current_app.config["UPLOAD_FOLDER"]
        os.makedirs(upload_folder, exist_ok=True)

        original_filename = file.filename
        extension = original_filename.rsplit(".", 1)[-1].lower()
        # Collision-safe name on disk; original filename is preserved
        # separately in the DB (Resume.file_name) for display.
        stored_filename = f"{user_id}_{uuid.uuid4().hex}.{extension}"
        file_path = os.path.join(upload_folder, stored_filename)

        file.save(file_path)

        try:
            raw_text = extract_text_from_pdf(file_path)
        except RuntimeError as e:
            os.remove(file_path)
            raise ValueError(
                "This file could not be read as a valid PDF. Please check the file and try again."
            ) from e

        if not raw_text or not raw_text.strip():
            os.remove(file_path)
            raise ValueError(
                "No readable text could be extracted from this PDF. "
                "It may be a scanned or image-based document."
            )

        return ResumeRepository.create(
            user_id=user_id,
            file_name=original_filename,
            file_path=file_path,
            raw_text=raw_text,
        )

    @staticmethod
    def get_resume_for_user(resume_id: int, user_id: int) -> Resume:
        """
        Fetches a single resume, enforcing ownership.

        Raises:
            ValueError: if no such resume exists for this user.
        """
        resume = ResumeRepository.get_by_id_for_user(resume_id, user_id)
        if not resume:
            raise ValueError("Resume not found.")
        return resume

    @staticmethod
    def list_resumes_for_user(user_id: int) -> list[Resume]:
        """Returns all resumes belonging to the given user."""
        return ResumeRepository.list_by_user(user_id)

    @staticmethod
    def get_latest_resume_for_user(user_id: int) -> Resume:
        """
        Fetches the user's most recently uploaded resume.

        Raises:
            ValueError: if the user has no resumes yet.
        """
        resume = ResumeRepository.get_latest_by_user(user_id)
        if not resume:
            raise ValueError("No resumes found for this user.")
        return resume
