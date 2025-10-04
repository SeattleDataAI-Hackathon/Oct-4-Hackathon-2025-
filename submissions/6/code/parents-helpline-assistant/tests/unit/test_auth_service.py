"""Unit tests for authentication service."""
import pytest
from src.services.auth_service import AuthService
from src.database.models import User


class TestAuthService:
    """Test cases for AuthService."""

    def test_create_user_success(self, db_session, sample_user_data):
        """Test successful user creation."""
        user = AuthService.create_user(
            db=db_session,
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
        )

        assert user is not None
        assert user.username == sample_user_data["username"]
        assert user.email == sample_user_data["email"]
        assert user.password_hash != sample_user_data["password"]  # Should be hashed

    def test_create_user_duplicate_username(self, db_session, sample_user_data):
        """Test user creation with duplicate username."""
        # Create first user
        AuthService.create_user(
            db=db_session,
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
        )

        # Try to create second user with same username
        duplicate_user = AuthService.create_user(
            db=db_session,
            username=sample_user_data["username"],
            email="different@test.com",
            password=sample_user_data["password"],
        )

        assert duplicate_user is None

    def test_authenticate_user_success(self, db_session, sample_user_data):
        """Test successful authentication."""
        # Create user
        AuthService.create_user(
            db=db_session,
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
        )

        # Authenticate
        user = AuthService.authenticate_user(
            db=db_session,
            username=sample_user_data["username"],
            password=sample_user_data["password"],
        )

        assert user is not None
        assert user.username == sample_user_data["username"]

    def test_authenticate_user_wrong_password(self, db_session, sample_user_data):
        """Test authentication with wrong password."""
        # Create user
        AuthService.create_user(
            db=db_session,
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
        )

        # Try to authenticate with wrong password
        user = AuthService.authenticate_user(
            db=db_session,
            username=sample_user_data["username"],
            password="WrongPassword123!",
        )

        assert user is None

    def test_create_anonymous_session(self, db_session):
        """Test creating anonymous session."""
        session, token = AuthService.create_session(
            db=db_session,
            user_id=None,
            role="parent",
        )

        assert session is not None
        assert session.is_authenticated is False
        assert session.user_id is None
        assert token is not None

    def test_create_authenticated_session(self, db_session, sample_user_data):
        """Test creating authenticated session."""
        # Create user
        user = AuthService.create_user(
            db=db_session,
            username=sample_user_data["username"],
            email=sample_user_data["email"],
            password=sample_user_data["password"],
        )

        # Create session
        session, token = AuthService.create_session(
            db=db_session,
            user_id=user.id,
            role="parent",
        )

        assert session is not None
        assert session.is_authenticated is True
        assert session.user_id == user.id
        assert token is not None
