from flask import Flask
from flask_cors import CORS
from socketio_instance import socketio
from database.db import db
from database.models import User, Session, Message, SequenceStep
from services.openai_client import chat_with_openai
from flask import request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

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
        session_id = data.get("session_id")

        if not user_message:
            return jsonify({"error": "No message provided"}), 400
        
        if not session_id:
            return jsonify({"error": "No session_id provided"}), 400

        print(f"Processing chat for session_id: {session_id}")  # Debug log

        # Save user message to DB
        user_msg = Message(session_id=session_id, sender="user", content=user_message)
        db.session.add(user_msg)
        db.session.commit()

        # Fetch full chat history for this session
        past_messages = Message.query.filter_by(session_id=session_id).order_by(Message.timestamp).all()

        messages = [
            {
                "role": "system",
                "content": """
                        You are Helix, an AI recruiting assistant that helps users generate and refine personalized candidate outreach sequences.

                        **Rules to Follow:**

                        1. **Tool Usage**: Always use tools for sequence-related tasks. Never write or suggest sequence content directly.
                        - Available tools:
                            - `generate_sequence` (requires role and location)
                            - `revise_step` (requires step number and revision instruction)
                            - `change_tone` (requires tone and session_id)
                            - `add_step` (requires step content and session_id)
                            
                            - `generate_recruiting_asset`: Use this for one-off requests like “write an offer letter,” “thank you note,” or “follow-up email.” This tool handles any recruiting-related task from natural language instructions.

                        2. **Clarify Intent**: If the user’s request is unclear, ask a clarifying question before proceeding.

                        3. **Conversational Responses**: Respond conversationally if the user’s input is vague or unrelated to sequence manipulation.

                        **Tone Guidance**:
                        - Technical roles → professional & direct
                        - Creative roles → casual & expressive
                        - Senior roles → formal & strategic
                        - Startup roles → energetic & conversational
                        - Enterprise roles → formal & structured

                        **Your Role**: Act as a friendly, smart recruiting co-pilot, not a chatbot.

                        **Before Responding**:
                        - Verify that your response complies with all rules above.
                        - Ensure you are using tools appropriately (if required).
                        - Avoid direct content creation or unnecessary tool usage.
                        If not compliant, revise your response before sending it.
"""
            }
        ]           
        for msg in past_messages:
            role = "user" if msg.sender == "user" else "assistant"
            messages.append({"role": role, "content": msg.content})

        # Inject current sequence into context (if any)
        sequence_steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
        if sequence_steps:
            sequence_text = "\n\n".join(
                [f"Step {step.step_number}: {step.content}" for step in sequence_steps]
            )
            messages.append({
                "role": "system",
                "content": f"Here is the current outreach sequence for context:\n\n{sequence_text}"
            })

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
                print(f"Received sequence from OpenAI for session_id: {session_id}")  # Debug log
                SequenceStep.query.filter_by(session_id=session_id).delete()
                db.session.commit()  # Commit the delete first

                for step in ai_sequence:
                    new_step = SequenceStep(
                        session_id=session_id,
                        step_number=step["step_number"],
                        content=step["content"]
                    )
                    db.session.add(new_step)
                db.session.commit()

                # Fetch the saved sequence to ensure it's properly serialized
                saved_sequence = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
                print(f"Retrieved saved sequence for session_id {session_id}: {len(saved_sequence)} steps")  # Debug log
                
                sequence_data = [
                    {
                        "step_number": step.step_number,
                        "content": step.content
                    }
                    for step in saved_sequence
                ]
                # Emit updated sequence over WebSocket
                socketio.emit("sequence_updated", {
                    "session_id": session_id,
                    "sequence": sequence_data
                })
            else:
                sequence_data = []  # Return empty array instead of None

            # Return structured response
            response_data = {
                "response": ai_response_text,
                "sequence": sequence_data
            }
            print(f"Sending response for session_id {session_id}: {response_data}")  # Debug log
            return jsonify(response_data)

        except Exception as e:
            import traceback
            traceback.print_exc()  # print full stack trace to console
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
