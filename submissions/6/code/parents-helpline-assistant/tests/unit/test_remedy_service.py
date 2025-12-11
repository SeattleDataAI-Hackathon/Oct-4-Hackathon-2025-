"""Unit tests for remedy service."""
import pytest
from src.services.remedy_service import RemedyService
from src.database.models import HomeRemedy


class TestRemedyService:
    """Test cases for RemedyService."""

    def test_get_remedies_by_condition(self, db_session, sample_home_remedy_data):
        """Test retrieving remedies by condition."""
        # Add remedy to database
        remedy = HomeRemedy(**sample_home_remedy_data)
        db_session.add(remedy)
        db_session.commit()

        # Get remedies
        remedies = RemedyService.get_remedies_by_condition(
            db=db_session,
            condition="Common Cold",
            child_age_months=12,
        )

        assert len(remedies) >= 1
        assert any(r.remedy_name == sample_home_remedy_data["remedy_name"] for r in remedies)

    def test_get_remedies_age_filter(self, db_session):
        """Test age filtering for remedies."""
        # Add remedy for older babies only
        older_baby_remedy = HomeRemedy(
            condition="Cough",
            remedy_name="Honey for Cough",
            description="Use honey",
            instructions="Give 1 tsp",
            min_age_months=12,
            max_age_months=36,
        )
        db_session.add(older_baby_remedy)
        db_session.commit()

        # Try to get for young baby (should be empty)
        young_remedies = RemedyService.get_remedies_by_condition(
            db=db_session,
            condition="Cough",
            child_age_months=6,  # Too young
        )

        assert len(young_remedies) == 0

        # Get for appropriate age
        appropriate_remedies = RemedyService.get_remedies_by_condition(
            db=db_session,
            condition="Cough",
            child_age_months=18,  # Appropriate age
        )

        assert len(appropriate_remedies) >= 1

    def test_search_remedies(self, db_session, sample_home_remedy_data):
        """Test searching remedies."""
        # Add remedy
        remedy = HomeRemedy(**sample_home_remedy_data)
        db_session.add(remedy)
        db_session.commit()

        # Search by condition
        results = RemedyService.search_remedies(
            db=db_session,
            search_term="cold",
            child_age_months=12,
        )

        assert len(results) >= 1
        assert any("cold" in r.condition.lower() for r in results)
