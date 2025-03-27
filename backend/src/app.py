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
                "content": """You are Helix, an AI recruiting assistant.

                Your job is to help users create personalized candidate outreach sequences.

                You have access to the `generate_sequence` tool. Use it when you have the following information:
                1. Role (e.g., Backend Engineer, UX Designer)
                2. Location — do NOT guess this. If the user doesn't say where the role is based, ask them before calling the tool.

                The tone will be automatically determined based on the role and context:
                - For technical roles, use a more professional and direct tone
                - For creative roles, you can be more conversational
                - For senior positions, maintain a more formal tone
                - For startup roles, you can be more casual and enthusiastic
                - For enterprise roles, keep it formal and structured

                Be conversational, helpful, and sound like a real assistant — not a bot."""
            }
        ]           
        for msg in past_messages:
            role = "user" if msg.sender == "user" else "assistant"
            messages.append({"role": role, "content": msg.content})

        # Send to OpenAI
        try:
            ai_result = chat_with_openai(messages, session_id=session_id)

            ai_response_text = ai_result["reply"]
            ai_sequence = ai_result.get("sequence")

            # Store AI message in DB
            ai_msg = Message(session_id=session_id, sender="ai", content=ai_response_text)
            db.session.add(ai_msg)
            db.session.commit()

            # If a sequence was generated, save it
            if ai_sequence:
                SequenceStep.query.filter_by(session_id=session_id).delete()
                for step in ai_sequence:
                    new_step = SequenceStep(
                        session_id=session_id,
                        step_number=step["step_number"],
                        content=step["content"]
                    )
                    db.session.add(new_step)
                db.session.commit()

            # Return structured response
            return jsonify({
                "response": ai_response_text,
                "sequence": ai_sequence
            })

        except Exception as e:
            import traceback
            traceback.print_exc()  # 🔍 print full stack trace to console
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
