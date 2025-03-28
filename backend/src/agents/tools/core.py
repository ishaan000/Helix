from database.models import SequenceStep, db, Session
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re
from typing import Dict, Any, Optional
from .web_search import search_professionals, get_professional_details

from socketio_instance import socketio  # ✅ import safely
import logging

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

def get_sequence_data(session_id: str):
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
    return [{"step_number": step.step_number, "content": step.content} for step in steps]

def emit_sequence_update(session_id: str):
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

def generate_sequence(role: str, location: str, session_id: str, step_count: Optional[int] = None) -> str:
    print(f"\nGenerating sequence for role: {role}, location: {location}, session_id: {session_id}")

    validation_error = validate_sequence_params(role, location)
    if validation_error:
        return f"{validation_error}"

    # Get user info from session
    session = Session.query.get(session_id)
    user_name = session.user.name if session and session.user else "the recruiter"
    company_name = session.user.company if session and session.user else "the company"

    base_prompt = f"""
Generate an outreach sequence for recruiting a {role} based in {location}.
The messages should be written from {user_name}'s perspective at {company_name}.
Make sure to mention {company_name} in the messages to establish credibility.
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
            model="gpt-4",
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

        try:
            # Delete existing steps
            SequenceStep.query.filter_by(session_id=session_id).delete()
            db.session.commit()

            # Add new steps
            for step in steps_json:
                new_step = SequenceStep(
                    session_id=session_id,
                    step_number=step["step_number"],
                    content=step["content"]
                )
                db.session.add(new_step)
                print(f"Adding step {step['step_number']} for session {session_id}")  # Debug log

            db.session.commit()
            print(f"Successfully saved {len(steps_json)} steps for session {session_id}")  # Debug log

            # Verify the steps were saved
            saved_steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
            print(f"Verified {len(saved_steps)} steps in database for session {session_id}")  # Debug log

            emit_sequence_update(session_id)
            return "Outreach sequence generated and saved successfully."

        except Exception as e:
            db.session.rollback()
            print(f"Database error while saving sequence: {str(e)}")  # Debug log
            return f"Error saving sequence to database: {str(e)}"

    except Exception as e:
        print(f"Error in generate_sequence: {str(e)}")  # Debug log
        return f"Error generating sequence: {str(e)}"

def get_user_context(session_id: str) -> str:
    session = Session.query.get(session_id)
    if not session or not session.user:
        return ""
    user = session.user
    return f"""
The messages should be written from {user.name}'s perspective at {user.company} (a {user.preferences.get('companySize', 'N/A')} company).
{user.name} is a {user.title} in the {user.industry} industry.
"""

def revise_step(session_id: str, step_number: int, new_instruction: str) -> str:
    step = SequenceStep.query.filter_by(session_id=session_id, step_number=step_number).first()
    if not step:
        return f"Step {step_number} not found."

    user_context = get_user_context(session_id)
    prompt = f"""Rewrite this message to reflect the following instruction:
{user_context}
Instruction: {new_instruction}
Original message: {step.content}
Rewritten message:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{ "role": "user", "content": prompt }],
        temperature=0.7
    )

    step.content = response.choices[0].message.content.strip()
    db.session.commit()
    emit_sequence_update(session_id)
    return f"Step {step_number} revised."

def change_tone(session_id: str, tone: str) -> str:
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
    if not steps:
        return "No steps found for this session."

    user_context = get_user_context(session_id)
    for step in steps:
        prompt = f"""Rewrite the following message to be more {tone}:
{user_context}
Original message: {step.content}
Rewritten message:"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{ "role": "user", "content": prompt }],
            temperature=0.7
        )
        step.content = response.choices[0].message.content.strip()

    db.session.commit()
    emit_sequence_update(session_id)
    return f"All steps updated to have a more {tone} tone."

def add_step(session_id: str, step_content: str, position: Optional[int] = None) -> str:
    steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()

    if position is None or position > len(steps):
        position = len(steps) + 1

    # Get user context
    user_context = get_user_context(session_id)
    prompt = f"""Create a new message that matches the style and context of the existing sequence:
{user_context}
Original content: {step_content}
New message:"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{ "role": "user", "content": prompt }],
        temperature=0.7
    )

    new_content = response.choices[0].message.content.strip()

    # Shift step numbers at and after the insertion point
    for step in steps:
        if step.step_number >= position:
            step.step_number += 1

    # Add the new step
    new_step = SequenceStep(session_id=session_id, step_number=position, content=new_content)
    db.session.add(new_step)

    # Reorder everything to ensure consistent step numbering
    all_steps = sorted(steps + [new_step], key=lambda s: s.step_number)
    for idx, step in enumerate(all_steps, start=1):
        step.step_number = idx

    db.session.commit()
    emit_sequence_update(session_id)
    return f"New step added at position {position}."

def generate_recruiting_asset(task: str, session_id: str):
    user_context = get_user_context(session_id)
    prompt = f"""
You're a recruiting assistant. Based on the following instruction, generate a fully formatted message (email, letter, follow-up, etc).
{user_context}
Task: {task}

Format the result as if it will be sent to a candidate or hiring manager.
"""

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{ "role": "user", "content": prompt }],
        temperature=0.7
    )

    content = response.choices[0].message.content.strip()

    # Store it as a single step
    SequenceStep.query.filter_by(session_id=session_id).delete()
    db.session.add(SequenceStep(session_id=session_id, step_number=1, content=content))
    db.session.commit()
    emit_sequence_update(session_id)

    return "Recruiting asset generated successfully."

def search_and_analyze_professionals(session_id: str, query: str, location: Optional[str] = None) -> str:
    """
    Search for professionals and generate a summary of findings.
    
    Args:
        session_id (str): The current session ID
        query (str): The search query (e.g., "top designers", "founding engineers")
        location (Optional[str]): Location to search in
    
    Returns:
        str: A formatted response with search results and analysis
    """
    try:
        logger.info(f"Starting search for query: {query}, location: {location}")
        # Get search results
        results = search_professionals(query, location)
        logger.info(f"Search results: {results}")
        
        if not results or not results.get("professionals"):
            logger.warning("No professionals found in results")
            return "I couldn't find any professionals matching your search criteria."
        
        # Format the response
        response = f"I found {len(results['professionals'])} professionals matching your search for '{query}'"
        if location:
            response += f" in {location}"
        response += ":\n\n"
        
        for i, prof in enumerate(results["professionals"], 1):
            if isinstance(prof, dict):
                response += f"{i}. {prof.get('name', 'Unknown')}\n"
                response += f"   Source: {prof.get('source', 'Unknown')}\n"
                response += f"   {prof.get('snippet', 'No description available')}\n\n"
            else:
                logger.warning(f"Invalid professional data format: {prof}")
        
        # Store the search results in the session for later use
        session = Session.query.get(session_id)
        if session:
            session.search_results = json.dumps(results)
            db.session.commit()
            logger.info("Successfully stored search results in session")
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search_and_analyze_professionals: {str(e)}", exc_info=True)
        return f"An error occurred while searching: {str(e)}"

def generate_personalized_outreach(profile_url: str, session_id: str) -> str:
    """
    Generate a personalized outreach message based on a professional's profile.
    
    Args:
        profile_url (str): URL of the professional's profile
        session_id (str): The current session ID
    
    Returns:
        str: A personalized outreach message
    """
    try:
        # Get professional details
        details = get_professional_details(profile_url)
        
        # Get user context
        session = Session.query.get(session_id)
        user_name = session.user.name if session and session.user else "the recruiter"
        company_name = session.user.company if session and session.user else "the company"
        
        # Generate personalized message using OpenAI
        prompt = f"""
        Generate a personalized outreach message for a professional based on their profile:
        Profile URL: {profile_url}
        Profile Content: {details['content']}
        
        The message should be from {user_name} at {company_name} and should:
        1. Reference specific details from their profile
        2. Show genuine interest in their work
        3. Be concise but personal
        4. Include a clear value proposition
        
        Format the message in a professional but conversational tone.
        """
        
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert recruiter crafting personalized outreach messages."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
        
    except Exception as e:
        return f"An error occurred while generating the outreach message: {str(e)}"

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
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"}
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
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"}
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
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"}
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
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"}
                },
                "required": ["step_content", "session_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_recruiting_asset",
            "description": "Creates a single recruiting-related message (offer letter, thank you note, follow-up, etc) from a task description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Instruction like 'Write a thank you email to Sarah after the interview'"},
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"}
                },
                "required": ["task", "session_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_and_analyze_professionals",
            "description": "Searches for professionals based on role and location, and provides a detailed analysis",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"},
                    "query": {"type": "string", "description": "The search query (e.g., 'top designers', 'founding engineers')"},
                    "location": {"type": "string", "description": "Optional. Location to search in (e.g., 'San Francisco')"}
                },
                "required": ["session_id", "query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_personalized_outreach",
            "description": "Generates a personalized outreach message for a specific professional based on their profile",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"},
                    "profile_url": {"type": "string", "description": "The URL of the professional's profile"}
                },
                "required": ["session_id", "profile_url"]
            }
        }
    }
] 