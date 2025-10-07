"""
Unit tests for semantic ranking functionality in rank_terms.py
"""

import unittest
import numpy as np
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.rank_terms import embed_text, compute_signals, score_terms


class TestEmbedText(unittest.TestCase):
    """Test the embedding function"""

    def setUp(self):
        """Set up mock OpenAI client"""
        self.mock_client = Mock()

    def test_embed_text_success(self):
        """Test successful text embedding"""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        self.mock_client.embeddings.create.return_value = mock_response

        result = embed_text("test text", self.mock_client)

        self.assertEqual(len(result), 1536)
        self.assertIsInstance(result, np.ndarray)
        self.mock_client.embeddings.create.assert_called_once()

    def test_embed_text_empty_input(self):
        """Test embedding with empty input returns zero vector"""
        result = embed_text("", self.mock_client)

        self.assertEqual(len(result), 1536)
        self.assertTrue(np.all(result == 0))

    def test_embed_text_api_failure(self):
        """Test that API failure returns zero vector"""
        self.mock_client.embeddings.create.side_effect = Exception("API Error")

        result = embed_text("test", self.mock_client)

        self.assertEqual(len(result), 1536)
        self.assertTrue(np.all(result == 0))


class TestComputeSignals(unittest.TestCase):
    """Test the signal computation for term ranking"""

    def setUp(self):
        """Set up test data"""
        self.mock_client = Mock()

        # Create mock embeddings
        self.term_vectors = {
            "water": np.array([0.8, 0.2, 0.1] + [0.0] * 1533),
            "drink": np.array([0.7, 0.3, 0.2] + [0.0] * 1533),
            "run": np.array([0.1, 0.1, 0.9] + [0.0] * 1533)
        }

        self.context_vector = np.array([0.75, 0.25, 0.15] + [0.0] * 1533)
        self.context = "I want to drink water"

    def test_direct_match_exact(self):
        """Test direct match bonus for exact word match"""
        terms = ["water", "drink", "run"]

        signals = compute_signals(
            terms,
            self.term_vectors,
            self.context_vector,
            self.mock_client,
            self.context
        )

        # "water" and "drink" appear in context, "run" does not
        self.assertEqual(signals["water"]["direct_match"], 1.0)
        self.assertEqual(signals["drink"]["direct_match"], 1.0)
        self.assertEqual(signals["run"]["direct_match"], 0.0)

    def test_semantic_similarity(self):
        """Test semantic similarity calculation"""
        terms = ["water"]

        signals = compute_signals(
            terms,
            self.term_vectors,
            self.context_vector,
            self.mock_client,
            self.context
        )

        # Should have positive similarity since vectors are aligned
        self.assertGreater(signals["water"]["semantic_sim"], 0.5)
        self.assertLessEqual(signals["water"]["semantic_sim"], 1.0)


class TestScoreTerms(unittest.TestCase):
    """Test the final scoring and ranking of terms"""

    def test_score_terms_weighted_combination(self):
        """Test that scoring combines signals with correct weights"""
        signals = {
            "water": {
                "semantic_sim": 0.9,
                "direct_match": 1.0,
                "action_margin": 0.7
            },
            "run": {
                "semantic_sim": 0.3,
                "direct_match": 0.0,
                "action_margin": 0.8
            }
        }

        scored = score_terms(signals)

        # Verify structure
        self.assertEqual(len(scored), 2)
        self.assertIn("term", scored[0])
        self.assertIn("score", scored[0])

        # "water" should score higher due to direct match and high semantic similarity
        # Score = 0.5 * 0.9 + 0.3 * 1.0 + 0.2 * 0.7 = 0.45 + 0.3 + 0.14 = 0.89
        # "run" = 0.5 * 0.3 + 0.3 * 0.0 + 0.2 * 0.8 = 0.15 + 0.0 + 0.16 = 0.31

        water_score = next(item["score"] for item in scored if item["term"] == "water")
        run_score = next(item["score"] for item in scored if item["term"] == "run")

        self.assertGreater(water_score, run_score)
        self.assertGreater(water_score, 0.8)
        self.assertLess(run_score, 0.4)

    def test_score_terms_sorted_descending(self):
        """Test that results are sorted by score (highest first)"""
        signals = {
            "low": {"semantic_sim": 0.2, "direct_match": 0.0, "action_margin": 0.3},
            "high": {"semantic_sim": 0.9, "direct_match": 1.0, "action_margin": 0.8},
            "medium": {"semantic_sim": 0.5, "direct_match": 0.5, "action_margin": 0.5}
        }

        scored = score_terms(signals)

        # Verify descending order
        self.assertEqual(scored[0]["term"], "high")
        self.assertEqual(scored[1]["term"], "medium")
        self.assertEqual(scored[2]["term"], "low")

        # Verify scores are in descending order
        scores = [item["score"] for item in scored]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == '__main__':
    unittest.main()
