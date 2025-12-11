"""Service for diagnosis and recommendations."""
from sqlalchemy.orm import Session
from src.database.models import Diagnosis, Recommendation
from src.utils.logger import get_logger
from typing import List, Optional, Dict

logger = get_logger(__name__)


class DiagnosisService:
    """Service for diagnosis and recommendation management."""

    @staticmethod
    def create_diagnosis(
        db: Session,
        conversation_id: int,
        condition: str,
        confidence_score: Optional[float] = None,
        data_sources: Optional[Dict] = None,
        reasoning: Optional[str] = None,
        requires_urgent_care: bool = False,
    ) -> Diagnosis:
        """
        Create a diagnosis for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID
            condition: Diagnosed condition name
            confidence_score: Confidence level (0.0-1.0)
            data_sources: Sources used for diagnosis (CDC, WebMD, etc.)
            reasoning: Explanation of diagnosis
            requires_urgent_care: Whether urgent care is needed

        Returns:
            Created diagnosis
        """
        try:
            diagnosis = Diagnosis(
                conversation_id=conversation_id,
                condition=condition,
                confidence_score=confidence_score,
                data_sources=data_sources,
                reasoning=reasoning,
                requires_urgent_care=requires_urgent_care,
            )
            db.add(diagnosis)
            db.commit()
            db.refresh(diagnosis)

            logger.info(f"Diagnosis created for conversation {conversation_id}: {condition}")
            return diagnosis

        except Exception as e:
            logger.error(f"Error creating diagnosis: {e}")
            db.rollback()
            raise

    @staticmethod
    def add_recommendation(
        db: Session,
        diagnosis_id: int,
        recommendation_type: str,
        description: str,
        priority: int = 2,
        safety_notes: Optional[str] = None,
    ) -> Recommendation:
        """
        Add a recommendation to a diagnosis.

        Args:
            db: Database session
            diagnosis_id: Diagnosis ID
            recommendation_type: Type (monitoring, medication, home_remedy, escalation)
            description: Recommendation description
            priority: Priority level (1=high, 2=medium, 3=low)
            safety_notes: Safety information

        Returns:
            Created recommendation
        """
        try:
            recommendation = Recommendation(
                diagnosis_id=diagnosis_id,
                recommendation_type=recommendation_type,
                description=description,
                priority=priority,
                safety_notes=safety_notes,
            )
            db.add(recommendation)
            db.commit()
            db.refresh(recommendation)

            logger.info(f"Recommendation added to diagnosis {diagnosis_id}: {recommendation_type}")
            return recommendation

        except Exception as e:
            logger.error(f"Error adding recommendation: {e}")
            db.rollback()
            raise

    @staticmethod
    def get_diagnoses_by_conversation(
        db: Session,
        conversation_id: int,
    ) -> List[Diagnosis]:
        """
        Get all diagnoses for a conversation.

        Args:
            db: Database session
            conversation_id: Conversation ID

        Returns:
            List of diagnoses
        """
        return db.query(Diagnosis).filter(
            Diagnosis.conversation_id == conversation_id
        ).order_by(Diagnosis.timestamp).all()

    @staticmethod
    def get_recommendations_by_diagnosis(
        db: Session,
        diagnosis_id: int,
    ) -> List[Recommendation]:
        """
        Get all recommendations for a diagnosis.

        Args:
            db: Database session
            diagnosis_id: Diagnosis ID

        Returns:
            List of recommendations ordered by priority
        """
        return db.query(Recommendation).filter(
            Recommendation.diagnosis_id == diagnosis_id
        ).order_by(Recommendation.priority).all()
