"""Authentication service for user management."""
from sqlalchemy.orm import Session
from src.database.models import User, Session as DBSession
from src.utils.security import hash_password, verify_password, create_access_token
from src.utils.logger import get_logger
import secrets
from datetime import datetime
from typing import Optional, Tuple

logger = get_logger(__name__)


class AuthService:
    """Service for authentication and user management."""

    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        full_name: str = None,
        username: str = None,
        role: str = "parent",
        verification_token: str = None,
        email_verified: bool = False
    ) -> Optional[User]:
        """
        Create a new user.

        Args:
            db: Database session
            email: Email address
            password: Plain text password
            full_name: User's full name
            username: Username (optional, will use email if not provided)
            role: User role

        Returns:
            Created user or None if email exists
        """
        try:
            # Use email as username if not provided
            if not username:
                username = email.split('@')[0]

            # Check if user exists
            existing = db.query(User).filter(User.email == email).first()

            if existing:
                logger.warning(f"User creation failed: email already exists")
                return None

            # Create user
            user = User(
                username=username,
                email=email,
                password_hash=hash_password(password),
                full_name=full_name,
                role=role,
                email_verified=email_verified,
                verification_token=verification_token,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            logger.info(f"User created successfully: {email}")
            return user

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            db.rollback()
            return None

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
        """
        Authenticate a user by email.

        Args:
            db: Database session
            email: Email address
            password: Plain text password

        Returns:
            User if authenticated, None otherwise
        """
        user = db.query(User).filter(User.email == email).first()

        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Authentication failed for user: {email}")
            return None

        logger.info(f"User authenticated successfully: {email}")
        return user

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: Email address

        Returns:
            User if found, None otherwise
        """
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def create_session(
        db: Session,
        user_id: Optional[int] = None,
        role: str = "parent",
    ) -> Tuple[DBSession, str]:
        """
        Create a new session (authenticated or anonymous).

        Args:
            db: Database session
            user_id: User ID (None for anonymous)
            role: User role (parent, healthcare_professional)

        Returns:
            Tuple of (Session, access_token)
        """
        try:
            # Generate session token
            session_token = secrets.token_urlsafe(32)

            # Create session
            session = DBSession(
                user_id=user_id,
                session_token=session_token,
                is_authenticated=user_id is not None,
                role=role,
            )
            db.add(session)
            db.commit()
            db.refresh(session)

            # Create access token
            token_data = {
                "session_id": session.id,
                "session_token": session_token,
                "role": role,
            }
            access_token = create_access_token(token_data)

            logger.info(f"Session created: {'authenticated' if user_id else 'anonymous'}")
            return session, access_token

        except Exception as e:
            logger.error(f"Error creating session: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_session_by_token(db: Session, session_token: str) -> Optional[DBSession]:
        """
        Get session by token.

        Args:
            db: Database session
            session_token: Session token

        Returns:
            Session if found and valid, None otherwise
        """
        session = db.query(DBSession).filter(
            DBSession.session_token == session_token
        ).first()

        if session:
            # Update last activity
            session.last_activity = datetime.utcnow()
            db.commit()

        return session
