"""
app/repositories/user_repository.py

Data access layer for the User model.

Why this exists:
    Per the layered architecture (Routes -> Services -> Repositories
    -> Models), all direct database queries against `User` belong
    here, not in the service layer or routes. auth_service.py calls
    into this repository rather than using User.query directly. This
    keeps query logic centralized: if lookup behavior ever needs to
    change (e.g. add eager-loading, caching, or a different ORM),
    only this file changes — services and routes are unaffected.

No password hashing, validation, or session logic lives here — this
file only reads and writes User rows. That logic belongs to
auth_service.py.
"""

from app.extensions import db
from app.models.user import User


class UserRepository:
    """
    Encapsulates all direct database access for the User model.

    Implemented as a class of static methods rather than a module of
    bare functions: it holds no instance state (no per-request or
    per-user data), so instantiation would add nothing — but the
    class grouping keeps call sites readable (UserRepository.get_by_email(...))
    and gives this repository a clear, greppable namespace as more
    repositories are added in later sprints.
    """

    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        """
        Fetches a single user by primary key.

        Args:
            user_id: The user's id.

        Returns:
            The matching User, or None if no such user exists.

        Used by Flask-Login's user_loader callback (Step 6) to
        reload a user from the session cookie's stored id on every
        request.
        """
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email: str) -> User | None:
        """
        Fetches a single user by email address.

        Args:
            email: The email to look up.

        Returns:
            The matching User, or None if no such user exists.

        Used by the auth service both during login (to find the
        account to verify a password against) and during
        registration (to check whether the email is already taken).
        """
        return User.query.filter_by(email=email).first()

    @staticmethod
    def email_exists(email: str) -> bool:
        """
        Checks whether a user with the given email already exists,
        without loading the full row — used purely for a fast
        existence check during registration.

        Args:
            email: The email to check.

        Returns:
            True if a user with this email exists, False otherwise.
        """
        return (
            db.session.query(User.id).filter_by(email=email).first() is not None
        )

    @staticmethod
    def create(name: str, email: str, password_hash: str) -> User:
        """
        Creates and persists a new User row.

        Args:
            name: The user's display name.
            email: The user's email (assumed already validated and
                confirmed unique by the caller — this method does not
                re-check, keeping a single responsibility).
            password_hash: An already-hashed password. This method
                never receives or handles a plaintext password —
                hashing is the auth service's responsibility.

        Returns:
            The newly created and persisted User instance.
        """
        user = User(name=name, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        return user
