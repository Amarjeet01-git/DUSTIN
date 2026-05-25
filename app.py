"""
app.py
======
Flask backend server for the Sunrise College AI Chatbot.
Provides REST API endpoint for the chatbot frontend.
Run with: python app.py
"""

from flask import Flask, request, jsonify, render_template, send_from_directory
from chatbot import get_response
import os
import datetime

# ─── Initialize Flask App ─────────────────────────────────────────────────────
app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static'
)

# In-memory chat history storage (per session)
# In production, use a database like SQLite or Redis
chat_history = []


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    """Serve the main chatbot HTML page."""
    return render_template('index.html')


@app.route('/api/chat', methods=['POST'])
def chat():
    """
    POST /api/chat
    Request body: { "message": "user input text" }
    Response:     { "response": "bot reply", "intent": "...", "confidence": 0.9 }
    """
    try:
        # Get JSON data from request
        data = request.get_json()

        if not data or 'message' not in data:
            return jsonify({
                'error': 'Bad request: Missing "message" field',
                'response': 'Sorry, I could not process your request. Please try again.'
            }), 400

        user_message = data['message'].strip()

        if not user_message:
            return jsonify({
                'response': 'Please type something and I\'ll help you!',
                'intent': 'empty',
                'confidence': 0.0
            })

        # Get chatbot response using NLP engine
        result = get_response(user_message)

        # Store in chat history
        timestamp = datetime.datetime.now().strftime('%H:%M')
        chat_history.append({
            'user': user_message,
            'bot': result['response'],
            'intent': result['intent'],
            'time': timestamp
        })

        # Keep only last 50 messages in memory
        if len(chat_history) > 50:
            chat_history.pop(0)

        return jsonify({
            'response': result['response'],
            'intent': result['intent'],
            'confidence': result['confidence'],
            'timestamp': timestamp
        })

    except Exception as e:
        print(f"Error in /api/chat: {e}")
        return jsonify({
            'response': 'I encountered an error. Please try again later.',
            'error': str(e)
        }), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """GET /api/history — Returns the current chat history."""
    return jsonify({'history': chat_history})


@app.route('/api/clear', methods=['POST'])
def clear_history():
    """POST /api/clear — Clears the chat history."""
    global chat_history
    chat_history = []
    return jsonify({'message': 'Chat history cleared successfully.'})


@app.route('/api/status', methods=['GET'])
def status():
    """GET /api/status — Health check endpoint."""
    return jsonify({
        'status': 'running',
        'service': 'Sunrise College Chatbot',
        'version': '1.0.0'
    })


# ─── Run Server ───────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('DEBUG', 'True').lower() == 'true'
    print(f"\n{'=' * 50}")
    print(f"  Sunrise College Chatbot – Flask Server")
    print(f"  Running at: http://127.0.0.1:{port}")
    print(f"{'=' * 50}\n")
    app.run(host='0.0.0.0', port=port, debug=debug)