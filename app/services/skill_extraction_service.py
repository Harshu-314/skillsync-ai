"""
app/services/skill_extraction_service.py

Business logic for extracting skills from a resume and persisting
the results.
"""

from app.ai.skill_extractor import extract_skills
from app.models.skill import Skill
from app.repositories.skill_repository import SkillRepository
from app.repositories.resume_skill_repository import ResumeSkillRepository
from app.services.resume_service import ResumeService


class SkillExtractionService:
    """Encapsulates skill-extraction orchestration and persistence."""

    @staticmethod
    def extract_and_save_skills_for_resume(resume_id: int, user_id: int) -> list[Skill]:
        """
        Runs skill extraction against a resume's raw_text and
        replaces its stored skill associations with the result.

        Args:
            resume_id: The resume to process.
            user_id: The currently authenticated user — used to
                enforce ownership via the existing, already
                ownership-checked ResumeService lookup rather than
                duplicating that check here.

        Returns:
            The list of matched Skill objects (may be empty — a
            resume genuinely having no recognized skills is a valid
            outcome, not an error).

        Raises:
            ValueError: if the resume doesn't exist or doesn't belong
                to this user (propagated unchanged from
                ResumeService.get_resume_for_user).
        """
        resume = ResumeService.get_resume_for_user(resume_id, user_id)

        all_skills = SkillRepository.get_all()
        matched_skills = extract_skills(resume.raw_text, all_skills)

        ResumeSkillRepository.replace_for_resume(resume_id, matched_skills)

        return matched_skills

    @staticmethod
    def get_skills_for_resume(resume_id: int, user_id: int) -> list[Skill]:
        """
        Returns the currently stored skill matches for a resume,
        without re-running extraction.

        Args:
            resume_id: The resume to look up.
            user_id: The currently authenticated user — ownership
                enforced via ResumeService, same as above.

        Returns:
            The list of currently associated Skill objects (empty if
            extraction hasn't been run yet, or found nothing).

        Raises:
            ValueError: if the resume doesn't exist or doesn't belong
                to this user.
        """
        # Ownership check only — the resume object itself isn't
        # needed beyond confirming access.
        ResumeService.get_resume_for_user(resume_id, user_id)

        return ResumeSkillRepository.get_skills_for_resume(resume_id)
