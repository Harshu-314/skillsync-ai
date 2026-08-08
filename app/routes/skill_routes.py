"""
app/routes/skill_routes.py

Skill extraction and taxonomy HTTP endpoints.
"""

import json

from flask import Blueprint
from flask_login import login_required, current_user

from app.models.skill import Skill
from app.repositories.skill_repository import SkillRepository
from app.services.skill_extraction_service import SkillExtractionService
from app.utils.api_response import success_response, error_response

skill_bp = Blueprint("skills", __name__, url_prefix="/api")


def _serialize_skill(skill: Skill) -> dict:
    """
    Shapes a Skill model into a plain dict for API responses.
    Aliases are parsed from their stored JSON-string form into a
    real list, so API consumers never have to parse JSON-within-JSON.
    """
    try:
        aliases = json.loads(skill.aliases) if skill.aliases else []
    except (json.JSONDecodeError, TypeError):
        aliases = []

    return {
        "id": skill.id,
        "name": skill.name,
        "category": skill.category,
        "aliases": aliases,
        "description": skill.description,
    }


@skill_bp.route("/resumes/<int:resume_id>/skills/extract", methods=["POST"])
@login_required
def extract_resume_skills(resume_id: int):
    """
    Runs skill extraction against the given resume's raw_text and
    replaces its stored skill associations with the result.
    Ownership-checked: a resume belonging to another user returns 404.
    Idempotent: safe to call repeatedly on the same resume.
    """
    try:
        skills = SkillExtractionService.extract_and_save_skills_for_resume(
            resume_id=resume_id, user_id=current_user.id
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=404)

    return success_response(
        data=[_serialize_skill(s) for s in skills],
        message=f"Extracted {len(skills)} skill(s) from resume.",
    )


@skill_bp.route("/resumes/<int:resume_id>/skills", methods=["GET"])
@login_required
def get_resume_skills(resume_id: int):
    """
    Returns the currently stored skill matches for a resume, without
    re-running extraction. Ownership-checked, same as above.
    """
    try:
        skills = SkillExtractionService.get_skills_for_resume(
            resume_id=resume_id, user_id=current_user.id
        )
    except ValueError as e:
        return error_response(message=str(e), status_code=404)

    return success_response(data=[_serialize_skill(s) for s in skills])


@skill_bp.route("/skills", methods=["GET"])
@login_required
def list_all_skills():
    """
    Returns the complete skill taxonomy. Not resume-scoped — useful
    for future frontend development (e.g. populating a skills
    reference page) and later sprints (e.g. recommendation browsing).
    """
    skills = SkillRepository.get_all()
    return success_response(data=[_serialize_skill(s) for s in skills])
