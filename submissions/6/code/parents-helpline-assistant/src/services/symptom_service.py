"""Service for managing symptoms."""
from sqlalchemy.orm import Session
from src.database.models import Symptom
from src.utils.logger import get_logger
from typing import List, Optional

logger = get_logger(__name__)


class SymptomService:
    """Service for symptom management."""

    @staticmethod
    def add_symptom(
        db: Session,
        conversation_id: int,
        symptom_name: str,
        severity: Optional[str] = None,
        duration: Optional[str] = None,
        additional_details: Optional[str] = None,
        parent_verified: bool = False,
    ) -> Symptom:
        """
        Add a symptom to a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            symptom_name: Name/description of symptom
            severity: Severity level (mild, moderate, severe)
            duration: Duration description
            additional_details: Additional context
            parent_verified: Whether parent has verified this symptom

        Returns:
            Created symptom
        """
        try:
            symptom = Symptom(
                conversation_id=conversation_id,
                symptom_name=symptom_name,
                severity=severity,
                duration=duration,
                additional_details=additional_details,
                parent_verified=parent_verified,
            )
            db.add(symptom)
            db.commit()
            db.refresh(symptom)

            logger.info(f"Symptom added to conversation {conversation_id}: {symptom_name}")
            return symptom

        except Exception as e:
            logger.error(f"Error adding symptom: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_symptoms_by_conversation(
        db: Session,
        conversation_id: int,
    ) -> List[Symptom]:
        """
        Get all symptoms for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            List of symptoms
        """
        return db.query(Symptom).filter(
            Symptom.conversation_id == conversation_id
        ).order_by(Symptom.timestamp).all()

    @staticmethod
    def verify_symptom(
        db: Session,
        symptom_id: int,
    ) -> Optional[Symptom]:
        """
        Mark a symptom as parent-verified.

        Args:
            db: Database session
            symptom_id: Symptom ID

        Returns:
            Updated symptom
        """
        try:
            symptom = db.query(Symptom).filter(Symptom.id == symptom_id).first()

            if not symptom:
                return None

            symptom.parent_verified = True
            db.commit()
            db.refresh(symptom)

            logger.info(f"Symptom {symptom_id} verified by parent")
            return symptom

        except Exception as e:
            logger.error(f"Error verifying symptom: {e}")
            db.rollback()
            raise
