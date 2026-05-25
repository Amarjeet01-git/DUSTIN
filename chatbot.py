"""
chatbot.py
==========
NLP-based chatbot engine for Galgotias University Inquiry Bot (Dustin).
Uses NLTK for tokenization, stopword removal, and lemmatization.
Matches user input to intents defined in intents.json.
Fixed: Multi-path auto detection for intents.json (Root & Data folder).
"""

import json
import random
import os
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# ─── NLTK Resource Download ─────────────────────────────────────────────────
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


# ─── Load Intents (Smart Multi-Path Check) ───────────────────────────────────
def load_intents():
    base_dir = os.path.dirname(__file__)
    
    # रास्ता 1: सीधे मुख्य (Root) फोल्डर में चेक करें
    filepath = os.path.join(base_dir, 'intents.json')
   
    # रास्ता 2: अगर बाहर नहीं है, तो 'data' फोल्डर के अंदर चेक करें
    if not os.path.exists(filepath):
        filepath = os.path.join(base_dir, 'data', 'intents.json')
        
    # अगर दोनों जगह नहीं मिले, तब एरर दें
    if not os.path.exists(filepath):
        raise FileNotFoundError("intents.json not found. Please check if it is in root or data/ folder.")
  
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

# Initialize Global Intents Data
intents_data = load_intents()


# ─── NLP Helper Functions ─────────────────────────────────────────────────────
def preprocess_text(text: str) -> list:
    """Clean and tokenize user input using NLP techniques."""
    text = text.lower().strip()

    try:
        tokens = word_tokenize(text)
    except Exception:
        tokens = text.split()

    filtered = [t for t in tokens if t.isalpha() and t not in stop_words]
    lemmatized = [lemmatizer.lemmatize(t) for t in filtered]

    return lemmatized


def calculate_match_score(user_tokens: list, pattern: str) -> float:
    """Calculate a similarity score between user input tokens and a pattern string."""
    pattern_tokens = preprocess_text(pattern)

    if not pattern_tokens:
        return 0.0

    matches = sum(1 for token in pattern_tokens if token in user_tokens)
    score = matches / len(pattern_tokens)
    return score


def extract_keywords(text: str) -> list:
    """Extract the most meaningful keywords from user input."""
    tokens = preprocess_text(text)
    return tokens


# ─── Main Chatbot Response Function ──────────────────────────────────────────
def get_response(user_input: str) -> dict:
    """Main function to determine the best intent match and return a bot response."""
    if not user_input or not user_input.strip():
        return {
            'response': "Please type a message and I'll do my best to help!",
            'intent': 'empty',
            'confidence': 0.0
        }

    user_tokens = preprocess_text(user_input)
    user_lower = user_input.lower().strip()

    best_intent = None
    best_score = 0.0
    confidence_threshold = 0.3

    # Score each intent
    for intent in intents_data['intents']:
        tag = intent['tag']

        if tag == 'unknown':
            continue

        for pattern in intent.get('patterns', []):
            if pattern.lower() in user_lower or user_lower in pattern.lower():
                score = 1.0
            else:
                score = calculate_match_score(user_tokens, pattern)

            if score > best_score:
                best_score = score
                best_intent = intent

    # Select Response
    if best_intent and best_score >= confidence_threshold:
        response = random.choice(best_intent['responses'])
        return {
            'response': response,
            'intent': best_intent['tag'],
            'confidence': round(best_score, 2)
        }
    else:
        unknown_intent = next(
            (i for i in intents_data['intents'] if i['tag'] == 'unknown'),
            None
        )
        if unknown_intent:
            response = random.choice(unknown_intent['responses'])
        else:
            response = "I'm not sure how to answer that. Please contact Galgotias University directly at info@galgotiasuniversity.edu.in"

        return {
            'response': response,
            'intent': 'unknown',
            'confidence': 0.0
        }


if __name__ == '__main__':
    print("=" * 60)
    print("   Galgotias University Chatbot – NLP Engine Test")
    print("=" * 60)
    
    test_queries = ["Hello", "What is the admission process?"]
    for query in test_queries:
        result = get_response(query)
        print(f"\nQ: {query}\nA: {result['response'][:100]}...")