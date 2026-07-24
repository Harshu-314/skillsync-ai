"""
app/models/user.py

SQLAlchemy model for the `users` table.

Represents a registered account. Every resume and every analysis run
belongs to exactly one user, which is what makes per-user history
(dashboard requirement, SRS section 7) possible.

No business logic (e.g. password verification) lives here — per
Sprint 0 rules, this model defines structure only. Password hashing/
verification logic will be added in the auth service (Sprint 1),
which will operate ON this model rather than the model containing
that logic itself, keeping persistence and business logic separate.

Sprint 1 addition: inherits from Flask-Login's UserMixin, which
supplies default implementations of is_authenticated, is_active,
is_anonymous, and get_id() — the four things Flask-Login requires
on any object passed to login_user()/logout_user() and checked by
@login_required. No new columns were needed for this; UserMixin's
defaults (always-authenticated, always-active once logged in) are
sufficient for this project's scope, which does not include an
admin-disable-account feature.
"""

from datetime import datetime

from flask_login import UserMixin
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


class User(UserMixin, db.Model):
    """
    Represents a registered SkillSync AI user (student / job seeker).

    Table: users
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    # Unique + indexed: email is both the login identifier and must
    # never collide between two accounts. The unique=True flag creates
    # the database-level unique index automatically — no separate
    # Index() declaration needed.
    email: Mapped[str] = mapped_column(String(150), unique=True, nullable=False)

    # Stores only the HASH, never a plaintext password. Sized 255 to
    # comfortably fit typical Werkzeug PBKDF2 hash output. Hashing
    # itself happens in the auth service (Sprint 1), not here.
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, default=datetime.utcnow
    )

    # --- Relationships ---
    # back_populates (rather than backref) is used throughout this
    # project: it requires declaring the relationship explicitly on
    # both sides, which is more verbose but makes the relationship
    # visible and greppable from either model file — important once
    # there are 9 interrelated tables.
    #
    # cascade="all, delete-orphan": if a user is deleted, their
    # resumes/analyses are deleted too rather than left as orphaned
    # rows with a dangling user_id. Appropriate here since a resume or
    # analysis has no meaning without its owning user.
    resumes: Mapped[list["Resume"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    analyses: Mapped[list["Analysis"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email}>"
