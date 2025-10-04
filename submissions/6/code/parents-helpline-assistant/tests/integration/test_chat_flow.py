"""Integration tests for complete chat flow."""
import pytest
from src.services import ConversationService, SymptomService, AuthService
from src.agents import HealthAssistant


class TestChatFlow:
    """Integration tests for full conversation workflow."""

    def test_complete_conversation_flow(self, db_session):
        """Test complete workflow from session creation to conversation."""
        # Create session
        session, token = AuthService.create_session(db=db_session, role="parent")
        assert session is not None

        # Create conversation
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
            title="Baby Fever Consultation",
            child_age_months=10,
        )
        assert conversation is not None

        # Add user message
        user_msg = ConversationService.add_message(
            db=db_session,
            conversation_id=conversation.id,
            role="user",
            content="My baby has a fever of 101°F",
        )
        assert user_msg is not None

        # Add symptom
        symptom = SymptomService.add_symptom(
            db=db_session,
            conversation_id=conversation.id,
            symptom_name="Fever",
            severity="moderate",
            duration="1 day",
            additional_details="101°F temperature",
        )
        assert symptom is not None

        # Verify symptom
        verified_symptom = SymptomService.verify_symptom(
            db=db_session,
            symptom_id=symptom.id,
        )
        assert verified_symptom.parent_verified is True

        # Get conversation history
        history = ConversationService.get_conversation_history(
            db=db_session,
            conversation_id=conversation.id,
        )
        assert len(history) >= 1

        # Get all conversations for session
        conversations = ConversationService.get_conversations_by_session(
            db=db_session,
            session_id=session.id,
        )
        assert len(conversations) >= 1
        assert conversations[0].id == conversation.id

    def test_multiple_symptoms_tracking(self, db_session):
        """Test tracking multiple symptoms in one conversation."""
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
            child_age_months=8,
        )

        # Add multiple symptoms
        symptoms_data = [
            {"symptom_name": "Fever", "severity": "moderate"},
            {"symptom_name": "Cough", "severity": "mild"},
            {"symptom_name": "Runny nose", "severity": "mild"},
        ]

        for symptom_data in symptoms_data:
            SymptomService.add_symptom(
                db=db_session,
                conversation_id=conversation.id,
                **symptom_data,
            )

        # Get all symptoms
        symptoms = SymptomService.get_symptoms_by_conversation(
            db=db_session,
            conversation_id=conversation.id,
        )

        assert len(symptoms) == 3
        symptom_names = [s.symptom_name for s in symptoms]
        assert "Fever" in symptom_names
        assert "Cough" in symptom_names
        assert "Runny nose" in symptom_names

    def test_conversation_persistence(self, db_session):
        """Test that conversations persist across 'sessions'."""
        # Create first session
        session1, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session1.id,
        )

        # Add messages
        for i in range(5):
            ConversationService.add_message(
                db=db_session,
                conversation_id=conversation.id,
                role="user" if i % 2 == 0 else "assistant",
                content=f"Message {i}",
            )

        # "Simulate" new session by retrieving conversation
        retrieved_conversation = ConversationService.get_conversation_by_id(
            db=db_session,
            conversation_id=conversation.id,
        )

        assert retrieved_conversation is not None
        assert retrieved_conversation.id == conversation.id

        # Get messages
        history = ConversationService.get_conversation_history(
            db=db_session,
            conversation_id=conversation.id,
        )

        assert len(history) == 5
