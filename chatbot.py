"""
chatbot.py
==========
NLP-based chatbot engine for Sunrise College Inquiry Bot.
Uses NLTK for tokenization, stopword removal, and lemmatization.
Matches user input to intents defined in intents.json.
"""

import json
import random
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ─── NLTK Resource Download ─────────────────────────────────────────────────
# Download required NLTK resources (only runs if not already downloaded)
def download_nltk_resources():
    resources = ['punkt', 'stopwords', 'wordnet', 'omw-1.4', 'punkt_tab']
    for resource in resources:
        try:
            nltk.download(resource, quiet=True)
        except Exception as e:
            print(f"Warning: Could not download {resource}: {e}")

download_nltk_resources()

# ─── Initialize NLP Tools ────────────────────────────────────────────────────
lemmatizer = WordNetLemmatizer()

try:
    stop_words = set(stopwords.words('english'))
    # Keep important question words even if they're stopwords
    stop_words -= {'what', 'when', 'where', 'who', 'which', 'how', 'why', 'is', 'are', 'do', 'does', 'can'}
except:
    stop_words = set()


# ─── Load Intents ────────────────────────────────────────────────────────────
def load_intents():
    """Load the intents JSON file from the data directory."""
    # Try multiple paths so it works from different working directories
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'data', 'intents.json'),
        'data/intents.json',
        'intents.json',
    ]
    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    raise FileNotFoundError("intents.json not found. Please check your file structure.")

intents_data = load_intents()


# ─── NLP Helper Functions ─────────────────────────────────────────────────────
def preprocess_text(text: str) -> list:
    """
    Clean and tokenize user input using NLP techniques:
    1. Lowercase
    2. Tokenize
    3. Remove stopwords
    4. Lemmatize each token
    """
    # Step 1: Convert to lowercase
    text = text.lower().strip()

    # Step 2: Tokenize the text into words
    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    # Step 3: Remove stopwords and non-alphabetic tokens
    filtered = [t for t in tokens if t.isalpha() and t not in stop_words]

    # Step 4: Lemmatize — reduce words to their base form
    # e.g., "fees" → "fee", "courses" → "course", "available" → "available"
    lemmatized = [lemmatizer.lemmatize(t) for t in filtered]

    return lemmatized


def calculate_match_score(user_tokens: list, pattern: str) -> float:
    """
    Calculate a similarity score between user input tokens and a pattern string.
    Returns a score between 0.0 and 1.0 based on keyword overlap.
    """
    # Preprocess the pattern as well
    pattern_tokens = preprocess_text(pattern)

    if not pattern_tokens:
        return 0.0

    # Count how many pattern tokens appear in the user input
    matches = sum(1 for token in pattern_tokens if token in user_tokens)

    # Score = matched tokens / total pattern tokens
    score = matches / len(pattern_tokens)
    return score


def extract_keywords(text: str) -> list:
    """Extract the most meaningful keywords from user input."""
    tokens = preprocess_text(text)
    return tokens


# ─── Main Chatbot Response Function ──────────────────────────────────────────
def get_response(user_input: str) -> dict:
    """
    Main function to determine the best intent match and return a bot response.

    Args:
        user_input: Raw text message from the user

    Returns:
        dict with keys: 'response' (str), 'intent' (str), 'confidence' (float)
    """
    if not user_input or not user_input.strip():
        return {
            'response': "Please type a message and I'll do my best to help!",
            'intent': 'empty',
            'confidence': 0.0
        }

    # Preprocess user input
    user_tokens = preprocess_text(user_input)
    user_lower = user_input.lower().strip()

    best_intent = None
    best_score = 0.0
    confidence_threshold = 0.3  # Minimum score to consider a match

    # ── Score each intent ──────────────────────────────────────────────────
    for intent in intents_data['intents']:
        tag = intent['tag']

        # Skip the 'unknown' fallback intent during scoring
        if tag == 'unknown':
            continue

        for pattern in intent.get('patterns', []):
            # Method 1: Exact substring match (high confidence)
            if pattern.lower() in user_lower or user_lower in pattern.lower():
                score = 1.0
            else:
                # Method 2: Token overlap score
                score = calculate_match_score(user_tokens, pattern)

            if score > best_score:
                best_score = score
                best_intent = intent

    # ── Select Response ────────────────────────────────────────────────────
    if best_intent and best_score >= confidence_threshold:
        # Pick a random response from the matched intent
        response = random.choice(best_intent['responses'])
        return {
            'response': response,
            'intent': best_intent['tag'],
            'confidence': round(best_score, 2)
        }
    else:
        # Fallback to the 'unknown' intent
        unknown_intent = next(
            (i for i in intents_data['intents'] if i['tag'] == 'unknown'),
            None
        )
        if unknown_intent:
            response = random.choice(unknown_intent['responses'])
        else:
            response = "I'm not sure how to answer that. Please contact the college directly at info@sunrisecollege.edu.in"

        return {
            'response': response,
            'intent': 'unknown',
            'confidence': 0.0
        }


# ─── Quick Test ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("   Sunrise College Chatbot – NLP Engine Test")
    print("=" * 60)

    test_queries = [
        "Hello",
        "What is the admission process?",
        "What are BCA fees?",
        "Is hostel available?",
        "Tell me about placement packages",
        "When will exams start?",
        "Who is the HOD of Computer Science?",
        "How can I contact the college?",
        "What courses are available?",
        "blah blah xyz unknown"
    ]

    for query in test_queries:
        result = get_response(query)
        print(f"\nQ: {query}")
        print(f"Intent: {result['intent']} | Confidence: {result['confidence']}")
        print(f"A: {result['response'][:100]}...")
        print("-" * 60)