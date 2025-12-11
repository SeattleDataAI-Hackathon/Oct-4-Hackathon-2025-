"""Unit tests for conversation service."""
import pytest
from src.services.conversation_service import ConversationService
from src.services.auth_service import AuthService


class TestConversationService:
    """Test cases for ConversationService."""

    def test_create_conversation(self, db_session, sample_conversation_data):
        """Test conversation creation."""
        # Create a session first
        session, _ = AuthService.create_session(db=db_session)

        # Create conversation
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
            title=sample_conversation_data["title"],
            child_age_months=sample_conversation_data["child_age_months"],
        )

        assert conversation is not None
        assert conversation.title == sample_conversation_data["title"]
        assert conversation.child_age_months == sample_conversation_data["child_age_months"]
        assert conversation.status == "active"

    def test_add_message(self, db_session):
        """Test adding a message to conversation."""
        # Create session and conversation
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
        )

        # Add message
        message = ConversationService.add_message(
            db=db_session,
            conversation_id=conversation.id,
            role="user",
            content="My baby has a fever",
        )

        assert message is not None
        assert message.role == "user"
        assert message.content == "My baby has a fever"

    def test_get_conversation_history(self, db_session):
        """Test retrieving conversation history."""
        # Create session and conversation
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
        )

        # Add messages
        ConversationService.add_message(
            db=db_session,
            conversation_id=conversation.id,
            role="user",
            content="Hello",
        )
        ConversationService.add_message(
            db=db_session,
            conversation_id=conversation.id,
            role="assistant",
            content="Hi! How can I help?",
        )

        # Get history
        history = ConversationService.get_conversation_history(
            db=db_session,
            conversation_id=conversation.id,
        )

        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"

    def test_update_conversation_title(self, db_session):
        """Test updating conversation title."""
        # Create session and conversation
        session, _ = AuthService.create_session(db=db_session)
        conversation = ConversationService.create_conversation(
            db=db_session,
            session_id=session.id,
            title="Old Title",
        )

        # Update title
        updated = ConversationService.update_conversation_title(
            db=db_session,
            conversation_id=conversation.id,
            title="New Title",
        )

        assert updated is not None
        assert updated.title == "New Title"
