
# Augmentative and Alternative Communication Tool

A FastAPI web application that generates detailed descriptions of images using Claude's vision capabilities.

An AI-powered Augmentative and Alternative Communication (AAC) tool that helps users generate contextual vocabulary and sentences from images.

Slides link: https://docs.google.com/presentation/d/1YGiIkGLCvR31djQOlJv5BNP7Qfjj2e1R3gXzgQje9W4/edit?usp=sharing

Github Profile: https://github.com/meetapandit/Oct-4-Hackathon-2025-

## Features

- 📸 **Image Upload & Analysis**: Upload images via drag-and-drop, browse, or camera capture
- 🔄 **HEIC Support**: Automatically converts HEIC images to JPEG
- 📏 **Smart Resizing**: Optimizes large images (max 5MB, 1568px)
- 🎨 **Multiple Formats**: Supports JPEG, PNG, WebP, GIF, and HEIC
- 🤖 **AI-Powered Word Generation**: Uses semantic ranking to generate 50-75 contextually relevant words with emojis
- 💬 **Sentence Prediction**: Generates top 5 sentences based on selected words
- 🔊 **Text-to-Speech**: Speaks generated sentences using OpenAI TTS with browser fallback
- ⚡ **Real-time Processing**: Fast analysis with loading indicators

## Project Structure

```
Oct-4-Hackathon-2025-/
├── app.py                   # Main Flask application
├── templates/
│   └── index.html          # Web UI with three-column layout
├── src/
│   ├── __init__.py         # Package initialization
│   └── rank_terms.py       # Semantic ranking using OpenAI embeddings
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore rules
└── README.md              # This file
```

## Setup

### 1. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure Environment Variables

Set the following environment variables:

```bash
export ANTHROPIC_API_KEY=your_anthropic_api_key_here
export OPENAI_API_KEY=your_openai_api_key_here
```

### 4. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5001`

## Usage

### Image Upload (Column 1)
1. Upload an image by:
   - Dragging and dropping into the upload area
   - Clicking "Browse" to select a file
   - Clicking "Camera" to take a photo
2. Click "Analyze Image" to process the image
3. The AI analyzes the image context (logged in backend)

### Word Generation (Column 2)
1. After image analysis, top 50-75 contextually relevant words appear with emojis
2. Click words to select them (they turn teal)
3. Click individual words again or click "Deselect All" to remove selections
4. Click "Generate Sentences" when ready

### Sentence Predictions (Column 3)
1. Top 5 sentences are generated based on selected words
2. Click the speaker icon (🔊) next to any sentence to hear it spoken
3. Uses OpenAI TTS for high-quality voice output

## API Endpoints

### `GET /`
Returns the web UI for the AAC tool

---

### `POST /analyze-image`
Analyzes an uploaded image and returns a description for context.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: `image` (image file)

**Response:**
```json
{
  "success": true,
  "description": "Detailed image description for context...",
  "model": "claude-sonnet-4-5-20250929"
}
```

---

### `POST /generate`
Generates top 50-75 contextually relevant words using semantic ranking.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "context": "Image description or context text"
}
```

**Response:**
```json
{
  "success": true,
  "terms": ["🏃 run", "💧 water", "🌳 tree", "..."],
  "count": 75
}
```

**How it works:**
- Uses OpenAI embeddings (text-embedding-3-small) for semantic similarity
- Combines three signals with weighted scoring:
  - 50% semantic similarity (embedding match)
  - 30% direct match (word appears in context)
  - 20% action margin (general relevance)
- Returns top 50-75 ranked words with relevant emojis

---

### `POST /generate-sentences`
Generates top 5 sentences based on selected words.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "context": "Image description",
  "words": ["water", "drink", "thirsty"]
}
```

**Response:**
```json
{
  "success": true,
  "sentences": [
    "I want to drink water",
    "I am thirsty",
    "Can I have some water",
    "I need a drink",
    "Please give me water"
  ]
}
```

**How it works:**
- Generates 15-20 candidate sentences using Claude
- Ranks sentences using OpenAI embeddings for semantic similarity
- Returns only top 5 most relevant sentences

---

### `POST /text-to-speech`
Converts text to speech audio using OpenAI TTS.

**Request:**
- Method: `POST`
- Content-Type: `application/json`
- Body:
```json
{
  "text": "I want to drink water"
}
```

**Response:**
```json
{
  "success": true,
  "audio": "base64_encoded_mp3_audio_data"
}
```

**How it works:**
- Uses OpenAI TTS model (tts-1) with "alloy" voice
- Returns MP3 audio encoded as base64
- Frontend falls back to browser Web Speech API if needed

---

## Technologies Used

- **Flask**: Web framework with CORS support
- **Anthropic Claude API**: Image analysis and text generation (claude-sonnet-4-5-20250929)
- **OpenAI API**: Embeddings (text-embedding-3-small) and TTS (tts-1)
- **Pillow**: Image processing and optimization
- **pillow-heif**: HEIC format support
- **spaCy**: NLP processing for vocabulary generation
- **scikit-learn**: Cosine similarity for semantic ranking

## Semantic Ranking Algorithm

The tool uses a sophisticated ranking system to ensure contextually relevant words and sentences:

1. **Word Ranking** (src/rank_terms.py):
   - Generates vocabulary using spaCy NLP
   - Computes OpenAI embeddings for semantic understanding
   - Scores terms with weighted signals:
     - Direct match: Check if term appears in context (30% weight)
     - Semantic similarity: Cosine similarity of embeddings (50% weight)
     - Action margin: General relevance scoring (20% weight)
   - Returns top 50-75 ranked terms

2. **Sentence Ranking**:
   - Generates diverse sentences using Claude
   - Embeds sentences and selected words
   - Ranks by semantic similarity to selected words
   - Returns top 5 most relevant sentences

## Testing

The project includes comprehensive unit and integration tests to ensure reliability and correctness.

### Test Structure

```
tests/
├── __init__.py           # Test package initialization
├── test_rank_terms.py    # Unit tests for semantic ranking
└── test_app.py           # Unit tests for API connections and Flask endpoints
```

### Running Tests

Install test dependencies:
```bash
pip install pytest pytest-cov
```

Run all tests:
```bash
python -m pytest tests/ -v
```

Run tests with coverage:
```bash
python -m pytest tests/ --cov=src --cov=app --cov-report=html
```

Run specific test file:
```bash
python -m pytest tests/test_rank_terms.py -v
python -m pytest tests/test_app.py -v
```

### Test Coverage

**Unit Tests (tests/test_rank_terms.py):**
- `test_embed_text_success` - Validates OpenAI embedding generation
- `test_embed_text_empty_input` - Tests empty input handling
- `test_embed_text_api_failure` - Tests API failure fallback
- `test_direct_match_exact` - Tests direct word matching in context
- `test_semantic_similarity` - Tests semantic similarity calculation
- `test_score_terms_weighted_combination` - Validates 50/30/20 weighted scoring
- `test_score_terms_sorted_descending` - Ensures correct ranking order

**Unit Tests (tests/test_app.py):**

*API Connection Tests:*
- `test_openai_client_initialization` - Tests OpenAI client setup
- `test_anthropic_client_initialization` - Tests Anthropic client setup
- `test_openai_embedding_call_structure` - Validates embedding API parameters

*Semantic Scoring Tests:*
- `test_cosine_similarity_identical_vectors` - Tests similarity = 1.0 for identical vectors
- `test_cosine_similarity_orthogonal_vectors` - Tests similarity = 0.0 for orthogonal vectors
- `test_cosine_similarity_opposite_vectors` - Tests similarity = -1.0 for opposite vectors
- `test_weighted_score_calculation` - Tests weighted scoring formula (50% semantic + 30% direct + 20% action)
- `test_normalization_preserves_ranking` - Validates normalization maintains ranking order

*Integration Tests:*
- `test_index_route` - Tests homepage loads correctly
- `test_generate_endpoint_success` - Tests word generation flow end-to-end
- `test_generate_endpoint_missing_context` - Tests error handling for missing data
- `test_generate_sentences_endpoint` - Tests sentence generation pipeline
- `test_text_to_speech_endpoint` - Tests TTS audio generation
- `test_analyze_image_endpoint` - Tests image analysis with Claude Vision

### Test Features

- **Mocking**: Uses `unittest.mock` to avoid actual API calls during testing
- **Isolation**: Each test is independent and doesn't affect others
- **Coverage**: Tests cover core functionality, error handling, and edge cases
- **Fast**: Tests run quickly without making real API calls

## Future Enhancements

### AI & Intelligence
- **Context History**: Remember previous interactions to provide better word suggestions
- **Learning System**: Adapt to user's vocabulary preferences over time

### Technical Improvements
- **Offline Mode**: Cache common words and sentences for offline use
- **Response Time Optimization**: Reduce latency with caching and parallel processing
- **Mobile App**: Native iOS and Android applications
- **Database Integration**: Store user preferences, history, and custom vocabulary
- **Real-time Collaboration**: Multiple users working together on the same session

### Integration
- **Smart Home Integration**: Connect with Alexa, Google Home, etc.
- **Calendar/Reminder Integration**: Context-aware suggestions based on scheduled events
- **Social Media Sharing**: Direct sharing to social platforms

## License

MIT License
