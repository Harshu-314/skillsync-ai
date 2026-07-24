"""
app/services/auth_service.py

Business logic for user registration and authentication.

Why this exists:
    Per the layered architecture (Routes -> Services -> Repositories
    -> Models), routes must not contain business logic and
    repositories must not contain business rules or hashing. This
    service is the one place that:
      - Validates registration input (via app.utils.validators).
      - Enforces email uniqueness.
      - Hashes passwords before they ever reach the repository/DB.
      - Verifies a login attempt's password against the stored hash.

Routes call AuthService.register_user(...) / authenticate_user(...)
and are responsible only for translating the outcome (a User on
success, a raised ValueError on failure) into an HTTP response via
api_response.py.
"""

from werkzeug.security import generate_password_hash, check_password_hash

from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.utils.validators import validate_registration_input


class AuthService:
    """
    Encapsulates authentication business logic. Stateless — all
    methods are static, operating only on their arguments and the
    repository layer.
    """

    @staticmethod
    def register_user(name: str, email: str, password: str) -> User:
        """
        Validates input, enforces email uniqueness, hashes the
        password, and creates a new user.

        Args:
            name: Display name.
            email: Email address (used as the login identifier).
            password: Plaintext password — hashed here, never stored
                or logged in plaintext form.

        Returns:
            The newly created User.

        Raises:
            ValueError: if input fails validation, or if the email
                is already registered. The message is safe to surface
                directly to the client via error_response().
        """
        validate_registration_input(name, email, password)

        if UserRepository.email_exists(email):
            raise ValueError("An account with this email already exists.")

        password_hash = generate_password_hash(password)
        return UserRepository.create(name=name, email=email, password_hash=password_hash)

    @staticmethod
    def authenticate_user(email: str, password: str) -> User:
        """
        Verifies login credentials.

        Args:
            email: Email address supplied at login.
            password: Plaintext password supplied at login.

        Returns:
            The authenticated User.

        Raises:
            ValueError: if no user matches the email, or the password
                is incorrect. Deliberately uses the SAME message for
                both cases ("Invalid email or password") rather than
                distinguishing "no such user" from "wrong password" —
                revealing which one occurred would let an attacker
                enumerate which emails are registered.
        """
        user = UserRepository.get_by_email(email)

        if not user or not check_password_hash(user.password_hash, password):
            raise ValueError("Invalid email or password.")

        return user
