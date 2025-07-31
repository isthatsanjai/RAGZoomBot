import os
import time
import logging
import base64
import hashlib
import hmac
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from config import Config
import token_utils
from rag_system import RAGSystem, initialize_rag_system, is_a_meaningful_message
from helper import JWT_generator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

rag_system = RAGSystem()

@app.after_request
def add_security_headers(response):
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'require-corp'
    response.headers['Cross-Origin-Resource-Policy'] = 'cross-origin'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    if app.debug:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    return response


@app.route('/')
def serve_bot_client():
    return render_template('index.html')


@app.route('/api/generate-sdk-signature', methods=['POST'])
def generate_sdk_signature():
    
    data = request.json
    meeting_number = data.get('meetingNumber')
    signature = JWT_generator(meeting_number)

    return jsonify({"signature": signature, "apiKey": Config.ZOOM_SDK_KEY})

@app.route('/api/process-chat', methods=['POST'])
def process_chat_message():
    data = request.json
    message = data.get('message', '')
    
    # Use the new, simpler filter
    if not is_a_meaningful_message(message):
        return jsonify({"reply": None})

    logger.info(f"Processing message: '{message}'")
    # Call the new master method that contains all the logic
    answer = rag_system.generate_response(message)
    
    return jsonify({"reply": answer})
      

if __name__ == '__main__':
    #token_utils.load_tokens_from_file()
    initialize_rag_system()
    app.run(host='0.0.0.0', port=5000, debug=True)
