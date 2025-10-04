"""Unit tests for symptom service."""
import pytest
from src.services.symptom_service import SymptomService
from src.services.conversation_service import ConversationService
from src.services.auth_service import AuthService


class TestSymptomService:
    """Test cases for SymptomService."""

    def test_add_symptom(self, db_session, sample_symptom_data):
        """Test adding a symptom."""
        # Create session and conversation
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
        )

        # Add symptom
        symptom = SymptomService.add_symptom(
            db=db_session,
            conversation_id=conversation.id,
            **sample_symptom_data,
        )

        assert symptom is not None
        assert symptom.symptom_name == sample_symptom_data["symptom_name"]
        assert symptom.severity == sample_symptom_data["severity"]
        assert symptom.duration == sample_symptom_data["duration"]

    def test_verify_symptom(self, db_session, sample_symptom_data):
        """Test verifying a symptom."""
        # Create session and conversation
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
        )

        # Add symptom
        symptom = SymptomService.add_symptom(
            db=db_session,
            conversation_id=conversation.id,
            **sample_symptom_data,
        )

        assert symptom.parent_verified is False

        # Verify symptom
        verified = SymptomService.verify_symptom(
            db=db_session,
            symptom_id=symptom.id,
        )

        assert verified is not None
        assert verified.parent_verified is True

    def test_get_symptoms_by_conversation(self, db_session, sample_symptom_data):
        """Test retrieving symptoms for a conversation."""
        # Create session and conversation
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
        )

        # Add multiple symptoms
        SymptomService.add_symptom(
            db=db_session,
            conversation_id=conversation.id,
            symptom_name="Fever",
            severity="moderate",
        )
        SymptomService.add_symptom(
            db=db_session,
            conversation_id=conversation.id,
            symptom_name="Cough",
            severity="mild",
        )

        # Get symptoms
        symptoms = SymptomService.get_symptoms_by_conversation(
            db=db_session,
            conversation_id=conversation.id,
        )

        assert len(symptoms) == 2
        assert symptoms[0].symptom_name == "Fever"
        assert symptoms[1].symptom_name == "Cough"
