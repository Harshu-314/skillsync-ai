"""Initial schema — all 9 core tables

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-07-19

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # --- users (no FK dependencies) ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=150), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("email", name="uq_users_email"),
    )

    # --- skills (no FK dependencies) ---
    op.create_table(
        "skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("aliases", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("name", name="uq_skills_name"),
    )
    op.create_index("ix_skills_category", "skills", ["category"])

    # --- jobs (no FK dependencies) ---
    op.create_table(
        "jobs",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("company", sa.String(length=255), nullable=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("source", sa.String(length=50), nullable=False),
        sa.Column("source_url", sa.String(length=500), nullable=True),
        sa.Column("fetched_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_jobs_source", "jobs", ["source"])
    op.create_index("ix_jobs_fetched_at", "jobs", ["fetched_at"])

    # --- resumes (depends on users) ---
    op.create_table(
        "resumes",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("file_path", sa.String(length=500), nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.Column("uploaded_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_resumes_user_id", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_resumes_user_id", "resumes", ["user_id"])

    # --- resume_skills (depends on resumes, skills) ---
    op.create_table(
        "resume_skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(
            ["resume_id"], ["resumes.id"], name="fk_resume_skills_resume_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], name="fk_resume_skills_skill_id", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("resume_id", "skill_id", name="uq_resume_skill"),
    )
    op.create_index("ix_resume_skills_skill_id", "resume_skills", ["skill_id"])

    # --- job_skills (depends on jobs, skills) ---
    op.create_table(
        "job_skills",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("job_id", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["job_id"], ["jobs.id"], name="fk_job_skills_job_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], name="fk_job_skills_skill_id", ondelete="CASCADE"
        ),
        sa.UniqueConstraint("job_id", "skill_id", name="uq_job_skill"),
    )
    op.create_index("ix_job_skills_skill_id", "job_skills", ["skill_id"])

    # --- recommendations (depends on skills) ---
    op.create_table(
        "recommendations",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("resource_type", sa.String(length=30), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=True),
        sa.Column("provider_name", sa.String(length=150), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], name="fk_recommendations_skill_id", ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_recommendations_skill_type", "recommendations", ["skill_id", "resource_type"]
    )

    # --- analyses (depends on users, resumes) ---
    op.create_table(
        "analyses",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("resume_id", sa.Integer(), nullable=False),
        sa.Column("match_percentage", sa.Float(), nullable=False),
        sa.Column("resume_score", sa.Float(), nullable=False),
        sa.Column("matched_skills_count", sa.Integer(), nullable=False),
        sa.Column("missing_skills_count", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_analyses_user_id", ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["resume_id"], ["resumes.id"], name="fk_analyses_resume_id", ondelete="CASCADE"
        ),
    )
    op.create_index("ix_analyses_user_id", "analyses", ["user_id"])
    op.create_index("ix_analyses_resume_id", "analyses", ["resume_id"])

    # --- learning_roadmaps (depends on analyses, skills) ---
    op.create_table(
        "learning_roadmaps",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("analysis_id", sa.Integer(), nullable=False),
        sa.Column("week_number", sa.Integer(), nullable=False),
        sa.Column("skill_id", sa.Integer(), nullable=False),
        sa.Column("focus_description", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["analysis_id"],
            ["analyses.id"],
            name="fk_learning_roadmaps_analysis_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["skill_id"], ["skills.id"], name="fk_learning_roadmaps_skill_id", ondelete="CASCADE"
        ),
    )
    op.create_index(
        "ix_learning_roadmaps_analysis_week", "learning_roadmaps", ["analysis_id", "week_number"]
    )


def downgrade():
    # Reverse order: children before parents, so no FK ever points at
    # an already-dropped table.
    op.drop_index("ix_learning_roadmaps_analysis_week", table_name="learning_roadmaps")
    op.drop_table("learning_roadmaps")

    op.drop_index("ix_analyses_resume_id", table_name="analyses")
    op.drop_index("ix_analyses_user_id", table_name="analyses")
    op.drop_table("analyses")

    op.drop_index("ix_recommendations_skill_type", table_name="recommendations")
    op.drop_table("recommendations")

    op.drop_index("ix_job_skills_skill_id", table_name="job_skills")
    op.drop_table("job_skills")

    op.drop_index("ix_resume_skills_skill_id", table_name="resume_skills")
    op.drop_table("resume_skills")

    op.drop_index("ix_resumes_user_id", table_name="resumes")
    op.drop_table("resumes")

    op.drop_index("ix_jobs_fetched_at", table_name="jobs")
    op.drop_index("ix_jobs_source", table_name="jobs")
    op.drop_table("jobs")

    op.drop_index("ix_skills_category", table_name="skills")
    op.drop_table("skills")

    op.drop_table("users")
