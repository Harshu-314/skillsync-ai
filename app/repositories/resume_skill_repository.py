"""
app/repositories/resume_skill_repository.py

Data access layer for the resume_skills junction table.
"""

from app.extensions import db
from app.models.resume_skill import ResumeSkill
from app.models.skill import Skill


class ResumeSkillRepository:
    """Encapsulates all direct database access for ResumeSkill associations."""

    @staticmethod
    def replace_for_resume(
        resume_id: int, skills: list[Skill], confidence_score: float = 1.0
    ) -> list[ResumeSkill]:
        """
        Replaces all skill associations for a resume with a fresh
        set, atomically.

        Deletes any existing resume_skills rows for this resume, then
        inserts one row per given skill, all within a single
        transaction — so a re-run of extraction never leaves stale
        associations, and a failure partway through leaves the
        original data untouched rather than half-updated.

        Args:
            resume_id: The resume being updated.
            skills: The full set of Skill objects to associate. Each
                gets confidence_score applied uniformly, since
                PhraseMatcher's exact matches carry no per-match
                confidence variance (unlike a future fuzzier method).
            confidence_score: Applied to every new row. Defaults to
                1.0 (certain match), appropriate for exact
                phrase-matching.

        Returns:
            The newly created ResumeSkill rows.

        Raises:
            Exception: any database error is re-raised after rollback,
                so the caller (and ultimately the global error
                handlers from Sprint 0) see the original failure
                rather than a silently swallowed one.
        """
        try:
            ResumeSkill.query.filter_by(resume_id=resume_id).delete()

            new_associations = [
                ResumeSkill(
                    resume_id=resume_id,
                    skill_id=skill.id,
                    confidence_score=confidence_score,
                )
                for skill in skills
            ]
            db.session.add_all(new_associations)
            db.session.commit()
            return new_associations
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def get_skills_for_resume(resume_id: int) -> list[Skill]:
        """
        Returns the full Skill objects currently associated with a
        resume (via the resume_skills junction), not just ids —
        callers get complete, ready-to-use skill data without a
        second lookup.
        """
        return (
            Skill.query.join(ResumeSkill, ResumeSkill.skill_id == Skill.id)
            .filter(ResumeSkill.resume_id == resume_id)
            .order_by(Skill.category, Skill.name)
            .all()
        )
