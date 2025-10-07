from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import anthropic
import os
import sys
from openai import OpenAI
import base64
from PIL import Image
import pillow_heif
from io import BytesIO

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
from rank_terms import generate_terms

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

app = Flask(__name__)
CORS(app)

# API keys from rank_terms.py
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY", "placeholder")
OPENAI_KEY = os.environ.get("OPENAI_API_KEY", "placeholder")

# Initialize clients
anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
openai_client = OpenAI(api_key=OPENAI_KEY)
print("✓ API clients initialized")

@app.route('/')
def index():
    return render_template('index.html')

def add_emojis_to_terms(terms, anthropic_client):
    """
    Add emojis to a list of terms using a single API call.
    Returns a list of terms with emojis prepended.
    """
    # Format terms as a comma-separated list
    terms_str = ", ".join(terms)

    prompt = f"""For each of these words/phrases, add a single relevant emoji that best represents it.

Words: {terms_str}

Return ONLY a comma-separated list with each word prefixed by its emoji and a space.
Format: "emoji word, emoji word, emoji word"

Example input: "run, think, water"
Example output: "🏃 run, 💭 think, 💧 water"

Be concise. Use the most appropriate single emoji for each term. Output the list on one line."""

    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()

        # Parse the response - split by comma and clean up
        emoji_terms = [term.strip() for term in response_text.split(',')]

        # Fallback: if parsing fails, return terms with default emoji
        if len(emoji_terms) != len(terms):
            return [f"✨ {term}" for term in terms]

        return emoji_terms

    except Exception as e:
        print(f"Error adding emojis: {e}")
        # Fallback: return terms with default emoji
        return [f"✨ {term}" for term in terms]

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json
        context = data.get('context', '')

        if not context:
            return jsonify({'error': 'Context is required'}), 400

        # Generate terms using the rank_terms module (top 50-75 words)
        result = generate_terms(
            context,
            n=75,  # Generate top 75 words
            anthropic_client=anthropic_client,
            openai_client=openai_client
        )

        # Extract just the top 50-75 terms (already ranked by score)
        terms = [item['term'] for item in result['terms'][:75]]

        # Add emojis with a single API call
        print(f"Adding emojis to top {len(terms)} terms...")
        emoji_terms = add_emojis_to_terms(terms, anthropic_client)

        return jsonify({
            'success': True,
            'terms': emoji_terms,
            'context': context
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-sentences', methods=['POST'])
def generate_sentences():
    try:
        data = request.json
        words = data.get('words', [])

        if not words:
            return jsonify({'error': 'Words are required'}), 400

        # Remove emojis from words for cleaner sentence generation
        clean_words = [word.split(' ', 1)[-1] if ' ' in word else word for word in words]
        words_str = ", ".join(clean_words)

        prompt = f"""Create 15-20 different short, simple sentences using ONLY these words IN THIS EXACT ORDER: {words_str}

CRITICAL RULES:
- Use ONLY the words provided - DO NOT add any other content words
- You may ONLY add function words (the, a, an, is, are, was, were, to, at, in, on, etc.)
- You may conjugate verbs as necessary (add -s, -ed, -ing)
- You may add plural markers (-s, -es)
- Keep the exact order of the content words given
- Make the sentences grammatically correct
- Be natural and simple
- Vary the sentence structures and function words used
- Show different ways to express the same idea with the given words

Return ONLY the sentences, one per line. No numbering, no extra text."""

        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=2500,
            messages=[{"role": "user", "content": prompt}]
        )

        response_text = message.content[0].text.strip()
        sentences = [s.strip() for s in response_text.split('\n') if s.strip()]

        # Rank sentences using OpenAI embeddings for semantic similarity
        print(f"Ranking {len(sentences)} sentences by semantic similarity...")
        ranked_sentences = rank_sentences_by_similarity(sentences, clean_words, openai_client)

        # Return only top 5 sentences
        top_sentences = ranked_sentences[:5]
        print(f"Selected top {len(top_sentences)} sentences")

        return jsonify({
            'success': True,
            'sentences': top_sentences
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def rank_sentences_by_similarity(sentences, words, openai_client):
    """
    Rank sentences by semantic similarity to the selected words using OpenAI embeddings.
    """
    import numpy as np
    from sklearn.metrics.pairwise import cosine_similarity

    # Create a reference phrase from the selected words
    reference_phrase = " ".join(words)

    # Embed the reference phrase
    try:
        ref_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=reference_phrase,
            encoding_format="float"
        )
        ref_embedding = np.array(ref_response.data[0].embedding)

        # Embed all sentences
        sent_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=sentences,
            encoding_format="float"
        )
        sent_embeddings = [np.array(item.embedding) for item in sent_response.data]

        # Calculate similarity scores
        scores = []
        for i, sent_emb in enumerate(sent_embeddings):
            similarity = cosine_similarity([ref_embedding], [sent_emb])[0][0]

            # Add direct word match bonus
            sentence_lower = sentences[i].lower()
            word_match_count = sum(1 for word in words if word.lower() in sentence_lower)
            word_match_ratio = word_match_count / len(words) if len(words) > 0 else 0

            # Combined score: 70% semantic + 30% direct match
            combined_score = 0.7 * similarity + 0.3 * word_match_ratio
            scores.append((sentences[i], combined_score, similarity, word_match_ratio))

        # Sort by combined score
        scores.sort(key=lambda x: x[1], reverse=True)

        # Log ranking
        print("\nTop 5 ranked sentences:")
        for i, (sent, combined, semantic, direct) in enumerate(scores[:5], 1):
            print(f"  {i}. [Score:{combined:.3f}] (sem:{semantic:.3f}, dir:{direct:.3f})")
            print(f"     {sent}")

        return [item[0] for item in scores]

    except Exception as e:
        print(f"Error ranking sentences: {e}")
        # Fallback: return original order
        return sentences

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech():
    """
    Convert text to speech using OpenAI TTS API.
    Returns audio file.
    """
    try:
        data = request.json
        text = data.get('text', '')

        if not text:
            return jsonify({'error': 'Text is required'}), 400

        # Use OpenAI TTS
        response = openai_client.audio.speech.create(
            model="tts-1",  # or "tts-1-hd" for higher quality
            voice="alloy",  # options: alloy, echo, fable, onyx, nova, shimmer
            input=text
        )

        # Return audio as base64
        audio_content = response.content
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')

        return jsonify({
            'success': True,
            'audio': audio_base64,
            'format': 'mp3'
        })

    except Exception as e:
        print(f"TTS Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def resize_image_if_needed(image_bytes, max_size_mb=5.0, max_dimension=1568):
    """Resize image if it's too large."""
    size_mb = len(image_bytes) / (1024 * 1024)
    img = Image.open(BytesIO(image_bytes))
    width, height = img.size
    needs_resize = False

    if width > max_dimension or height > max_dimension:
        needs_resize = True
        if width > height:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        else:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
    elif size_mb > max_size_mb:
        needs_resize = True
        new_width = int(width * 0.8)
        new_height = int(height * 0.8)

    if needs_resize:
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    if img.mode not in ('RGB', 'L'):
        img = img.convert('RGB')

    output = BytesIO()
    img.save(output, format='JPEG', quality=85, optimize=True)
    output.seek(0)
    return output.read()

@app.route('/analyze-image', methods=['POST'])
def analyze_image():
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No image file provided'}), 400

        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Read and process image
        image_bytes = file.read()

        # Resize if needed
        image_bytes = resize_image_if_needed(image_bytes)

        # Encode to base64
        image_base64 = base64.standard_b64encode(image_bytes).decode("utf-8")

        # Create prompt for Claude
        prompt = """Describe this image in detail. Focus on:
1. What you see in the image
2. Key objects and subjects
3. The setting and context
4. Any notable features or details

Provide a comprehensive description that could be used to generate relevant vocabulary."""

        # Call Claude API with vision
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ],
                }
            ],
        )

        description = message.content[0].text

        # Log description to backend only
        print(f"\n{'='*60}")
        print(f"IMAGE ANALYSIS:")
        print(f"{'='*60}")
        print(description)
        print(f"{'='*60}\n")

        return jsonify({
            'success': True,
            'description': description
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)