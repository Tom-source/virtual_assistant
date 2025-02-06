import os
import logging
from flask import Flask, render_template, jsonify
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation, ConversationConfig
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface

# Load environment variables from .env
load_dotenv()

# Set up logging so that INFO messages are printed to the terminal.
logging.basicConfig(level=logging.INFO)

# Create the Flask app.
app = Flask(__name__)

# Retrieve environment variables.
agent_id = os.getenv("AGENT_ID")
api_key = os.getenv("ELEVENLABS_API_KEY")
if not agent_id or not api_key:
    raise ValueError("Please set both AGENT_ID and ELEVENLABS_API_KEY in your .env file.")

logging.info("Environment variables loaded successfully.")

# Initialize the ElevenLabs client.
client = ElevenLabs(api_key=api_key)

# Create the Conversation instance (do not start the session automatically).
conversation = Conversation(
    client,
    agent_id,
    requires_auth=True,  # Authentication is required if an API key is provided.
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=lambda response: logging.info(f"Agent: {response}"),
    callback_agent_response_correction=lambda original, corrected: logging.info(f"Agent: {original} -> {corrected}"),
    callback_user_transcript=lambda transcript: logging.info(f"User: {transcript}")
)

# Endpoint to start the back-end conversation session.
@app.route('/start-session')
def start_session():
    try:
        conversation.start_session()
        return jsonify({"status": "session started"}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"status": "error", "message": str(e)}), 500

# Endpoint to end the back-end conversation session.
@app.route('/end-session')
def end_session():
    try:
        conversation.end_session()
        return jsonify({"status": "session ended"}), 200
    except Exception as e:
        logging.error(e)
        return jsonify({"status": "error", "message": str(e)}), 500

# Serve the front‑end page.
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    logging.info("Starting Flask server on http://127.0.0.1:5000")
    app.run(host="127.0.0.1", port=5000, debug=True)
