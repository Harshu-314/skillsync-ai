"""
app/routes/resume_routes.py

Resume upload and retrieval HTTP endpoints.
"""

from flask import Blueprint, request
from flask_login import login_required, current_user

from app.models.resume import Resume
from app.services.resume_service import ResumeService
from app.utils.api_response import success_response, error_response

resume_bp = Blueprint("resumes", __name__, url_prefix="/api/resumes")


def _serialize_resume(resume: Resume, include_text: bool = True) -> dict:
    """
    Shapes a Resume model into a plain dict for API responses.
    """
    data = {
        "id": resume.id,
        "file_name": resume.file_name,
        "uploaded_at": resume.uploaded_at.isoformat(),
    }
    if include_text:
        data["raw_text"] = resume.raw_text
    return data


@resume_bp.route("/upload", methods=["POST"])
@login_required
def upload_resume():
    """
    Uploads a PDF resume for the current user.

    Expects multipart/form-data with a file field named "resume".
    """
    file = request.files.get("resume")

    try:
        resume = ResumeService.upload_resume(user_id=current_user.id, file=file)
    except ValueError as e:
        return error_response(message=str(e), status_code=400)

    return success_response(
        data=_serialize_resume(resume),
        message="Resume uploaded and processed successfully.",
        status_code=201,
    )


@resume_bp.route("", methods=["GET"])
@login_required
def list_resumes():
    """
    Lists all resumes belonging to the current user, most recent
    first. Excludes raw_text from the list view to keep the payload
    light — full text is available via the detail endpoint.
    """
    resumes = ResumeService.list_resumes_for_user(current_user.id)
    return success_response(
        data=[_serialize_resume(r, include_text=False) for r in resumes]
    )


@resume_bp.route("/latest", methods=["GET"])
@login_required
def get_latest_resume():
    """
    Returns the current user's most recently uploaded resume.
    """
    try:
        resume = ResumeService.get_latest_resume_for_user(current_user.id)
    except ValueError as e:
        return error_response(message=str(e), status_code=404)

    return success_response(data=_serialize_resume(resume))


@resume_bp.route("/<int:resume_id>", methods=["GET"])
@login_required
def get_resume(resume_id: int):
    """
    Returns a single resume's full detail, including raw_text.
    Ownership-checked: a resume belonging to another user returns 404,
    not 403, so as not to reveal that the id exists at all.
    """
    try:
        resume = ResumeService.get_resume_for_user(resume_id, current_user.id)
    except ValueError as e:
        return error_response(message=str(e), status_code=404)

    return success_response(data=_serialize_resume(resume))
