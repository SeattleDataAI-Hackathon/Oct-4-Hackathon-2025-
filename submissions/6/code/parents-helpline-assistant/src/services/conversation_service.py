"""Service for managing conversations and messages."""
from sqlalchemy.orm import Session
from src.database.models import Conversation, Message
from src.utils.logger import get_logger
from typing import List, Optional, Dict
from datetime import datetime

logger = get_logger(__name__)


class ConversationService:
    """Service for conversation and message management."""

    @staticmethod
    def create_conversation(
        db: Session,
        session_id: int,
        title: str = "New Conversation",
        child_age_months: Optional[int] = None,
        child_name: Optional[str] = None,
    ) -> Conversation:
        """
        Create a new conversation.

        Args:
            db: Database session
            session_id: Session ID
            title: Conversation title
            child_age_months: Child's age in months (0-36)
            child_name: Child's name for personalized conversation title

        Returns:
            Created conversation
        """
        try:
            # Format title as "ChildName-DateTime" if name is provided
            if child_name:
                timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
                title = f"{child_name}-{timestamp}"

            conversation = Conversation(
                session_id=session_id,
                title=title,
                child_age_months=child_age_months,
                child_name=child_name,
                status="active",
            )
            db.add(conversation)
            db.commit()
            db.refresh(conversation)

            logger.info(f"Conversation created: ID={conversation.id}, Title={title}")
            return conversation

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            db.rollback()
            raise

    @staticmethod
    def add_message(
        db: Session,
        conversation_id: int,
        role: str,
        content: str,
        metadata: Optional[Dict] = None,
    ) -> Message:
        """
        Add a message to a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata (response time, tokens, etc.)

        Returns:
            Created message
        """
        try:
            message = Message(
                conversation_id=conversation_id,
                role=role,
                content=content,
                message_metadata=metadata,
            )
            db.add(message)
            db.commit()
            db.refresh(message)

            logger.info(f"Message added to conversation {conversation_id}: role={role}")
            return message

        except Exception as e:
            logger.error(f"Error adding message: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_conversation_history(
        db: Session,
        conversation_id: int,
        limit: Optional[int] = None,
    ) -> List[Dict[str, str]]:
        """
        Get conversation history in format suitable for AI.

        Args:
            db: Database session
            conversation_id: Conversation ID
            limit: Maximum number of messages to retrieve

        Returns:
            List of messages in format [{"role": "...", "content": "..."}]
        """
        query = db.query(Message).filter(
            Message.conversation_id == conversation_id
        ).order_by(Message.timestamp)

        if limit:
            query = query.limit(limit)

        messages = query.all()

        return [
            {"role": msg.role, "content": msg.content}
            for msg in messages
            if msg.role in ["user", "assistant"]  # Exclude system messages
        ]

    @staticmethod
    def get_conversations_by_session(
        db: Session,
        session_id: int,
    ) -> List[Conversation]:
        """
        Get all conversations for a session.

        Args:
            db: Database session
            session_id: Session ID

        Returns:
            List of conversations
        """
        return db.query(Conversation).filter(
            Conversation.session_id == session_id
        ).order_by(Conversation.created_at.desc()).all()

    @staticmethod
    def get_conversation_by_id(
        db: Session,
        conversation_id: int,
    ) -> Optional[Conversation]:
        """
        Get a conversation by ID.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            Conversation if found, None otherwise
        """
        return db.query(Conversation).filter(
            Conversation.id == conversation_id
        ).first()

    @staticmethod
    def update_conversation_title(
        db: Session,
        conversation_id: int,
        title: str,
    ) -> Optional[Conversation]:
        """
        Update conversation title.

        Args:
            db: Database session
            conversation_id: Conversation ID
            title: New title

        Returns:
            Updated conversation
        """
        try:
            conversation = db.query(Conversation).filter(
                Conversation.id == conversation_id
            ).first()

            if not conversation:
                return None

            conversation.title = title
            db.commit()
            db.refresh(conversation)

            logger.info(f"Conversation {conversation_id} title updated")
            return conversation

        except Exception as e:
            logger.error(f"Error updating conversation title: {e}")
            db.rollback()
            raise
