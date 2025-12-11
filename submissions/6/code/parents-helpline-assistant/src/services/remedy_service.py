"""Service for home remedies."""
from sqlalchemy.orm import Session
from src.database.models import HomeRemedy
from src.utils.logger import get_logger
from typing import List, Optional

logger = get_logger(__name__)


class RemedyService:
    """Service for home remedy management."""

    @staticmethod
    def get_remedies_by_condition(
        db: Session,
        condition: str,
        child_age_months: int,
    ) -> List[HomeRemedy]:
        """
        Get approved home remedies for a condition and child age.

        Args:
            db: Database session
            condition: Condition name
            child_age_months: Child's age in months

        Returns:
            List of appropriate home remedies
        """
        return db.query(HomeRemedy).filter(
            HomeRemedy.condition.ilike(f"%{condition}%"),
            HomeRemedy.is_approved == True,
            HomeRemedy.min_age_months <= child_age_months,
            HomeRemedy.max_age_months >= child_age_months,
        ).all()

    @staticmethod
    def get_all_remedies(db: Session) -> List[HomeRemedy]:
        """
        Get all approved home remedies.

        Args:
            db: Database session

        Returns:
            List of all approved remedies
        """
        return db.query(HomeRemedy).filter(
            HomeRemedy.is_approved == True
        ).order_by(HomeRemedy.condition, HomeRemedy.remedy_name).all()

    @staticmethod
    def search_remedies(
        db: Session,
        search_term: str,
        child_age_months: Optional[int] = None,
    ) -> List[HomeRemedy]:
        """
        Search remedies by condition or remedy name.

        Args:
            db: Database session
            search_term: Search term
            child_age_months: Optional age filter

        Returns:
            List of matching remedies
        """
        query = db.query(HomeRemedy).filter(
            HomeRemedy.is_approved == True,
            (HomeRemedy.condition.ilike(f"%{search_term}%")) |
            (HomeRemedy.remedy_name.ilike(f"%{search_term}%"))
        )

        if child_age_months is not None:
            query = query.filter(
                HomeRemedy.min_age_months <= child_age_months,
                HomeRemedy.max_age_months >= child_age_months,
            )

        return query.all()
