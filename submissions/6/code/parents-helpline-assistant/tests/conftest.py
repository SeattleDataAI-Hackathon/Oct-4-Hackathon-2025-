"""Pytest configuration and fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.database.connection import Base
from src.database.models import *  # noqa
import os

# Use in-memory SQLite for tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """Create a test database engine."""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """Create a test database session."""
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "test_parent",
        "email": "parent@test.com",
        "password": "SecurePass123!",
    }


@pytest.fixture
def sample_conversation_data():
    """Sample conversation data for testing."""
    return {
        "title": "Test Conversation",
        "child_age_months": 12,
    }


@pytest.fixture
def sample_symptom_data():
    """Sample symptom data for testing."""
    return {
        "symptom_name": "Fever",
        "severity": "moderate",
        "duration": "2 days",
        "additional_details": "Temperature around 101°F",
    }


@pytest.fixture
def sample_home_remedy_data():
    """Sample home remedy data for testing."""
    return {
        "condition": "Common Cold",
        "remedy_name": "Test Humidifier Use",
        "description": "Use a cool-mist humidifier",
        "instructions": "Place in baby's room",
        "safety_notes": "Clean daily",
        "min_age_months": 0,
        "max_age_months": 36,
    }
