from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO
from database.db import db
from database.models import User, Session, Message, SequenceStep
from services.openai_client import chat_with_openai
from flask import request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

socketio = SocketIO(cors_allowed_origins="*")

def create_app(testing=False):
    app = Flask(__name__)
    CORS(app)

    if testing:
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    else:
        app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL", "sqlite:///helix.db")

    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["TESTING"] = testing

    db.init_app(app)
    socketio.init_app(app)

    @app.route("/")
    def index():
        return "Helix backend running!"
    
    @app.route("/chat", methods=["POST"])
    def chat():
        data = request.get_json()
        user_message = data.get("message")
        session_id = data.get("session_id", 1)  # Dummy session for now

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        # Save user message to DB
        user_msg = Message(session_id=session_id, sender="user", content=user_message)
        db.session.add(user_msg)
        db.session.commit()

        # Fetch full chat history
        past_messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()

        messages = [
            {
        "role": "system",
        "content": """
        You are Helix, an AI recruiting assistant.

        Your job is to help users create personalized candidate outreach sequences.

        You have access to the `generate_sequence` tool. Use it only when you have the following information:

        1. Role (e.g., Backend Engineer, UX Designer)
        2. Location — do NOT guess this. If the user doesn’t say where the role is based, ask them before calling the tool.
        3. Tone — try to infer it from the conversation if possible. If it’s unclear, feel free to ask the user. 
        4. Step count — choose an appropriate number of outreach steps unless the user specifies one.

        Be conversational, helpful, and sound like a real assistant — not a bot.
        """
            }
        ]           
        for msg in past_messages:
            role = "user" if msg.sender == "user" else "assistant"
            messages.append({"role": role, "content": msg.content})

        # Send to OpenAI
        try:
            ai_response = chat_with_openai(messages, session_id=session_id)

            # Store AI message
            ai_msg = Message(session_id=session_id, sender="ai", content=ai_response)
            db.session.add(ai_msg)
            db.session.commit()

            return jsonify({"response": ai_response})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        
    @app.route("/sequence/<int:session_id>", methods=["GET"])
    def get_sequence(session_id):
        steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()

        return jsonify([
            {
                "step_number": step.step_number,
                "content": step.content
            }
            for step in steps
        ])

    return app
