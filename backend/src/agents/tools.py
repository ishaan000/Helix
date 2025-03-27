from database.models import SequenceStep, db
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re
from typing import Dict, Any, Optional

from socketio_instance import socketio  # ✅ import safely

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def get_sequence_data(session_id: int):
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
    return [{"step_number": step.step_number, "content": step.content} for step in steps]

def emit_sequence_update(session_id: int):
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
    sequence_data = [{"step_number": s.step_number, "content": s.content} for s in steps]
    socketio.emit("sequence_updated", {"session_id": session_id, "sequence": sequence_data})

def validate_sequence_params(role: str, location: str) -> Optional[str]:
    """Validates the input parameters for sequence generation."""
    if not role or not location:
        return "Missing required parameters: role and location are required"
    if len(role) > 100 or len(location) > 100:
        return "Role and location exceed maximum length limits"
    return None

def generate_sequence(role: str, location: str, session_id: int, step_count: Optional[int] = None) -> str:
    print(f"\nGenerating sequence for role: {role}, location: {location}, session_id: {session_id}")

    validation_error = validate_sequence_params(role, location)
    if validation_error:
        return f"{validation_error}"

    base_prompt = f"""
Generate an outreach sequence for recruiting a {role} based in {location}.
Respond in JSON format as a list like:
[
  {{ "step_number": 1, "content": "..." }},
  ...
]
"""
    if step_count:
        base_prompt = f"Generate a {step_count}-step outreach sequence for a {role} in {location}.\n" + base_prompt

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a recruiting assistant that creates candidate outreach sequences. Generate professional and engaging outreach messages."
                },
                {"role": "user", "content": base_prompt}
            ],
            temperature=0.7
        )

        content = response.choices[0].message.content
        print("\nRaw GPT content:\n", content)

        try:
            steps_json = json.loads(content)
        except json.JSONDecodeError:
            try:
                json_str = re.search(r"\[.*\]", content, re.DOTALL).group()
                steps_json = json.loads(json_str)
                print("\n✅ Extracted JSON steps:\n", steps_json)
            except Exception as e:
                return f"Failed to parse sequence steps: {str(e)}\n\nRaw content:\n{content}"

        for step in steps_json:
            if not isinstance(step, dict) or "step_number" not in step or "content" not in step:
                return "Invalid step structure in generated sequence"

        SequenceStep.query.filter_by(session_id=session_id).delete()
        db.session.commit()

        for step in steps_json:
            db.session.add(SequenceStep(
                session_id=session_id,
                step_number=step["step_number"],
                content=step["content"]
            ))

        db.session.commit()

        emit_sequence_update(session_id)  # ✅ clean emit after save
        return "Outreach sequence generated and saved successfully."

    except Exception as e:
        return f"Error generating sequence: {str(e)}"

    
def revise_step(session_id: int, step_number: int, new_instruction: str) -> str:
    step = SequenceStep.query.filter_by(session_id=session_id, step_number=step_number).first()
    if not step:
        return f"Step {step_number} not found."

    prompt = f"""Rewrite this message to reflect the following instruction:
Instruction: {new_instruction}
Original message: {step.content}
Rewritten message:"""

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{ "role": "user", "content": prompt }],
        temperature=0.7
    )

    step.content = response.choices[0].message.content.strip()
    db.session.commit()
    emit_sequence_update(session_id)
    return f"Step {step_number} revised."


def change_tone(session_id: int, tone: str) -> str:
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
    if not steps:
        return "No steps found for this session."

    for step in steps:
        prompt = f"Rewrite the following message to be more {tone}:\n\n{step.content}"
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.7
        )
        step.content = response.choices[0].message.content.strip()

    db.session.commit()
    emit_sequence_update(session_id)
    return f"All steps updated to have a more {tone} tone."


def add_step(session_id: int, step_content: str, position: Optional[int] = None) -> str:
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()

    if position is None or position > len(steps):
        position = len(steps) + 1

    # Shift later steps down
    for step in reversed(steps):
        if step.step_number >= position:
            step.step_number += 1

    new_step = SequenceStep(session_id=session_id, step_number=position, content=step_content)
    db.session.add(new_step)
    db.session.commit()
    emit_sequence_update(session_id)
    return f"New step added at position {position}."

tool_definitions = [
    {
        "type": "function",
        "function": {
            "name": "generate_sequence",
            "description": "Generates a candidate outreach sequence based on role and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The role being hired for"},
                    "location": {"type": "string", "description": "Where the job is based"},
                    "step_count": {"type": "integer", "description": "Optional. Number of outreach steps to include"},
                    "session_id": {"type": "integer"}
                },
                "required": ["role", "location", "session_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "revise_step",
            "description": "Revises the content of a specific step using an instruction",
            "parameters": {
                "type": "object",
                "properties": {
                    "step_number": {"type": "integer", "description": "Step number to revise"},
                    "new_instruction": {"type": "string", "description": "How to revise this step"},
                    "session_id": {"type": "integer"}
                },
                "required": ["step_number", "new_instruction", "session_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "change_tone",
            "description": "Changes the tone of the entire sequence (e.g. casual, personal, professional)",
            "parameters": {
                "type": "object",
                "properties": {
                    "tone": {"type": "string", "description": "Tone to apply (e.g. personal, bold, casual)"},
                    "session_id": {"type": "integer"}
                },
                "required": ["tone", "session_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "add_step",
            "description": "Adds a new step to the outreach sequence",
            "parameters": {
                "type": "object",
                "properties": {
                    "step_content": {"type": "string", "description": "Content of the new step"},
                    "position": {"type": "integer", "description": "Position to insert the step"},
                    "session_id": {"type": "integer"}
                },
                "required": ["step_content", "session_id"]
            }
        }
    }
]
