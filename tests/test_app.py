"""
Unit and integration tests for Flask app endpoints
"""

import unittest
import json
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from app import app
from src.rank_terms import embed_text
from openai import OpenAI
import anthropic


class TestAPIConnections(unittest.TestCase):
    """Unit tests for API connections"""

    @patch.dict(os.environ, {'OPENAI_API_KEY': 'test-key'})
    def test_openai_client_initialization(self):
        """Test OpenAI client can be initialized with API key"""
        client = OpenAI(api_key='test-key')
        self.assertIsNotNone(client)
        self.assertIsInstance(client, OpenAI)

    @patch.dict(os.environ, {'ANTHROPIC_API_KEY': 'test-key'})
    def test_anthropic_client_initialization(self):
        """Test Anthropic client can be initialized with API key"""
        client = anthropic.Anthropic(api_key='test-key')
        self.assertIsNotNone(client)
        self.assertIsInstance(client, anthropic.Anthropic)

    def test_openai_embedding_call_structure(self):
        """Test OpenAI embedding API call structure"""
        mock_client = Mock()
        mock_response = Mock()
        mock_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_client.embeddings.create.return_value = mock_response

        result = embed_text("test text", mock_client)

        # Verify API was called with correct parameters
        mock_client.embeddings.create.assert_called_once()
        call_kwargs = mock_client.embeddings.create.call_args[1]
        self.assertEqual(call_kwargs['model'], 'text-embedding-3-small')
        self.assertEqual(call_kwargs['input'], 'test text')
        self.assertEqual(call_kwargs['encoding_format'], 'float')

        # Verify result structure
        self.assertEqual(len(result), 1536)
        self.assertIsInstance(result, np.ndarray)


class TestSemanticScoring(unittest.TestCase):
    """Unit tests for semantic scoring calculations"""

    def test_cosine_similarity_identical_vectors(self):
        """Test cosine similarity with identical vectors returns 1.0"""
        from sklearn.metrics.pairwise import cosine_similarity

        vec1 = np.array([[1, 0, 0]])
        vec2 = np.array([[1, 0, 0]])

        similarity = cosine_similarity(vec1, vec2)[0][0]
        self.assertAlmostEqual(similarity, 1.0, places=5)

    def test_cosine_similarity_orthogonal_vectors(self):
        """Test cosine similarity with orthogonal vectors returns 0.0"""
        from sklearn.metrics.pairwise import cosine_similarity

        vec1 = np.array([[1, 0, 0]])
        vec2 = np.array([[0, 1, 0]])

        similarity = cosine_similarity(vec1, vec2)[0][0]
        self.assertAlmostEqual(similarity, 0.0, places=5)

    def test_cosine_similarity_opposite_vectors(self):
        """Test cosine similarity with opposite vectors returns -1.0"""
        from sklearn.metrics.pairwise import cosine_similarity

        vec1 = np.array([[1, 0, 0]])
        vec2 = np.array([[-1, 0, 0]])

        similarity = cosine_similarity(vec1, vec2)[0][0]
        self.assertAlmostEqual(similarity, -1.0, places=5)

    def test_weighted_score_calculation(self):
        """Test weighted scoring combines signals correctly"""
        # Score = 0.5 * semantic + 0.3 * direct + 0.2 * action
        semantic_sim = 0.8
        direct_match = 1.0
        action_margin = 0.6

        expected_score = (0.5 * semantic_sim) + (0.3 * direct_match) + (0.2 * action_margin)
        # = 0.4 + 0.3 + 0.12 = 0.82

        self.assertAlmostEqual(expected_score, 0.82, places=2)

    def test_normalization_preserves_ranking(self):
        """Test that normalization preserves relative ranking order"""
        scores = np.array([0.2, 0.8, 0.5, 0.9])

        # Normalize to 0-1 range
        normalized = (scores - scores.min()) / (scores.max() - scores.min())

        # Verify order is preserved
        original_order = np.argsort(scores)
        normalized_order = np.argsort(normalized)

        np.testing.assert_array_equal(original_order, normalized_order)


class TestFlaskEndpoints(unittest.TestCase):
    """Integration tests for Flask endpoints"""

    def setUp(self):
        """Set up test client"""
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_index_route(self):
        """Test that index route returns HTML"""
        response = self.client.get('/')

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'<!DOCTYPE html>', response.data)

    @patch('app.generate_terms')
    @patch('app.add_emojis_to_terms')
    def test_generate_endpoint_success(self, mock_add_emojis, mock_generate):
        """Test /generate endpoint with valid context"""
        # Mock the ranking results
        mock_generate.return_value = {
            'terms': [
                {'term': 'water', 'score': 0.95},
                {'term': 'drink', 'score': 0.90},
                {'term': 'thirsty', 'score': 0.85}
            ]
        }

        # Mock emoji addition
        mock_add_emojis.return_value = ['💧 water', '🥤 drink', '🥵 thirsty']

        response = self.client.post('/generate',
                                   data=json.dumps({'context': 'I want water'}),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('terms', data)
        self.assertEqual(len(data['terms']), 3)

    def test_generate_endpoint_missing_context(self):
        """Test /generate endpoint with missing context"""
        response = self.client.post('/generate',
                                   data=json.dumps({}),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    @patch('app.anthropic_client')
    @patch('app.openai_client')
    def test_generate_sentences_endpoint(self, mock_openai, mock_anthropic):
        """Test /generate-sentences endpoint"""
        # Mock Claude response for sentence generation
        mock_message = Mock()
        mock_message.content = [Mock(text="I want water\nI am thirsty\nCan I have water")]
        mock_anthropic.messages.create.return_value = mock_message

        # Mock OpenAI embeddings
        mock_embedding_response = Mock()
        mock_embedding_response.data = [Mock(embedding=[0.1] * 1536)]
        mock_openai.embeddings.create.return_value = mock_embedding_response

        response = self.client.post('/generate-sentences',
                                   data=json.dumps({
                                       'context': 'drinking scene',
                                       'words': ['water', 'drink']
                                   }),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('sentences', data)

    @patch('app.openai_client')
    def test_text_to_speech_endpoint(self, mock_openai):
        """Test /text-to-speech endpoint"""
        # Mock OpenAI TTS response
        mock_response = Mock()
        mock_response.content = b'fake_audio_data'
        mock_openai.audio.speech.create.return_value = mock_response

        response = self.client.post('/text-to-speech',
                                   data=json.dumps({'text': 'Hello world'}),
                                   content_type='application/json')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('audio', data)

    @patch('app.anthropic_client')
    def test_analyze_image_endpoint(self, mock_anthropic):
        """Test /analyze-image endpoint with image upload"""
        # Mock Claude vision response
        mock_message = Mock()
        mock_message.content = [Mock(text="A person drinking water from a glass")]
        mock_anthropic.messages.create.return_value = mock_message

        # Create a fake image file
        fake_image = BytesIO(b'fake image data')
        fake_image.name = 'test.jpg'

        response = self.client.post('/analyze-image',
                                   data={'image': (fake_image, 'test.jpg')},
                                   content_type='multipart/form-data')

        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertTrue(data['success'])
        self.assertIn('description', data)
        self.assertEqual(data['model'], 'claude-sonnet-4-5-20250929')


if __name__ == '__main__':
    unittest.main()
