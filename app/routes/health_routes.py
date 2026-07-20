"""
app/routes/health_routes.py

Health check endpoint.

Purpose:
    GET /api/health — a simple, dependency-free endpoint used to
    confirm the backend is running and reachable. This is standard
    practice for any deployed API (used by uptime monitors, load
    balancers, or just a developer sanity-checking the server is up)
    and, for this project, doubles as proof that Sprint 0's entire
    wiring — factory, config, extensions, logging, blueprint
    registration, and the standardized response format — works
    together correctly.

    Deliberately contains NO business logic and touches no database
    table, per the Sprint 0 scope (no business logic yet).
"""

from flask import Blueprint

from app.utils.api_response import success_response

# Blueprint name "health" and url_prefix "/api" combine with the route
# below to produce the final path: /api/health
health_bp = Blueprint("health", __name__, url_prefix="/api")


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Returns basic service status information.

    Response:
        {
            "success": true,
            "data": {
                "status": "healthy",
                "project": "SkillSync AI Backend",
                "version": "1.0.0"
            },
            "message": "Request successful"
        }
    """
    data = {
        "status": "healthy",
        "project": "SkillSync AI Backend",
        "version": "1.0.0",
    }
    return success_response(data=data)
