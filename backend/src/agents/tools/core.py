from database.models import SequenceStep, db, Session
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import re
from typing import Dict, Any, Optional, List
from .web_search import search_professionals, get_professional_details

from socketio_instance import socketio  # import safely
import logging

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
logger = logging.getLogger(__name__)

def get_sequence_data(session_id: str):
    """Retrieve all steps of a sequence for a given session.
    
    This function fetches all sequence steps associated with a specific chat session,
    ordered by their step number.
    
    Args:
        session_id (str): The unique identifier of the chat session
        
    Returns:
        list: A list of dictionaries, where each dictionary contains:
            - step_number (int): The order of the step
            - content (str): The content of the step
            
    Note:
        Returns an empty list if no steps are found for the given session_id
    """
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

def generate_sequence(role: str, location: str, session_id: str, step_count: Optional[int] = None, profile_url: Optional[str] = None) -> str:
    print(f"\nGenerating sequence for role: {role}, location: {location}, session_id: {session_id}, profile_url: {profile_url}")

    validation_error = validate_sequence_params(role, location)
    if validation_error:
        return f"{validation_error}"

    # Get user info from session
    session = Session.query.get(session_id)
    user_name = session.user.name if session and session.user else "the job seeker"
    user_title = session.user.title if session and session.user else "professional"

    # Get professional details if profile_url is provided
    professional_context = ""
    if profile_url:
        try:
            details = get_professional_details(profile_url)
            professional_context = f"""
            Professional Details:
            - Profile: {profile_url}
            - Current Position: {details.get('title', 'N/A')}
            - Background: {details.get('content', 'N/A')}
            
            Use these details to personalize the networking/job application sequence. Reference specific aspects of their company and role that align with the job seeker's skills and interests.
            """
        except Exception as e:
            logger.error(f"Error fetching professional details: {str(e)}")
            professional_context = ""

    base_prompt = f"""
Generate a professional outreach sequence for a job seeker interested in a {role} position based in {location}.
The messages should be written from {user_name}'s perspective as a {user_title}.
Make sure to highlight relevant skills and experience that would make them a good fit for the role.

Follow this structure for each step:
1. Initial Outreach: Introduce yourself, mention how you found them, and express specific interest in their company/team. Highlight 1-2 relevant skills or experiences that make you a good fit. End with a clear call to action (like requesting a brief conversation).

2. Follow-up: If no response, send a brief, friendly follow-up that adds value - perhaps sharing an insight about their industry or a recent company announcement. Reiterate your interest and make it easy to respond.

3. Final Touch: If still no response, send one final message that's concise and direct, emphasizing your continued interest and offering flexibility for a brief conversation.

{professional_context}

Respond in JSON format as a list like:
[
  {{ "step_number": 1, "content": "..." }},
  {{ "step_number": 2, "content": "..." }},
  {{ "step_number": 3, "content": "..." }}
]

Each message should be complete and self-contained. Make sure to:
- Keep messages concise but personal
- Reference specific details about the company/role
- Highlight relevant skills and experiences
- Include clear next steps
- Maintain a professional yet conversational tone
- Avoid generic language
"""
    if step_count:
        base_prompt = f"Generate a {step_count}-step outreach sequence for a job seeker interested in a {role} position in {location}.\n" + base_prompt

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are a job search assistant that creates personalized outreach sequences for networking and job applications. Generate professional and engaging outreach messages that follow a clear structure and reference specific details about the target company and role when available. Each message should be complete and self-contained."
                },
                {"role": "user", "content": base_prompt}
            ],
            temperature=0.7,
            max_tokens=2000  # Ensure we get complete responses
        )

        content = response.choices[0].message.content
        print("\nRaw GPT content:\n", content)

        try:
            # First try direct JSON parsing
            steps_json = json.loads(content)
        except json.JSONDecodeError:
            try:
                # Try to extract JSON array using regex
                json_str = re.search(r"\[.*\]", content, re.DOTALL)
                if not json_str:
                    return f"Could not find JSON array in response. Raw content:\n{content}"
                steps_json = json.loads(json_str.group())
                print("\n✅ Extracted JSON steps:\n", steps_json)
            except Exception as e:
                return f"Failed to parse sequence steps: {str(e)}\n\nRaw content:\n{content}"

        # Validate step structure
        if not isinstance(steps_json, list):
            return f"Expected JSON array, got {type(steps_json)}. Raw content:\n{content}"

        for step in steps_json:
            if not isinstance(step, dict):
                return f"Invalid step type: {type(step)}. Expected dict. Raw content:\n{content}"
            if "step_number" not in step or "content" not in step:
                return f"Missing required fields in step: {step}. Raw content:\n{content}"
            if not isinstance(step["step_number"], int):
                return f"Invalid step_number type: {type(step['step_number'])}. Expected int. Raw content:\n{content}"
            if not isinstance(step["content"], str):
                return f"Invalid content type: {type(step['content'])}. Expected str. Raw content:\n{content}"

        try:
            # Delete existing steps
            SequenceStep.query.filter_by(session_id=session_id).delete()
            db.session.commit()

            # Add new steps
            for step in steps_json:
                new_step = SequenceStep(
                    session_id=session_id,
                    step_number=step["step_number"],
                    content=step["content"].strip()  # Ensure content is stripped
                )
                db.session.add(new_step)
                print(f"Adding step {step['step_number']} for session {session_id}")

            db.session.commit()
            print(f"Successfully saved {len(steps_json)} steps for session {session_id}")

            # Verify the steps were saved
            saved_steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
            print(f"Verified {len(saved_steps)} steps in database for session {session_id}")

            if len(saved_steps) != len(steps_json):
                print(f"Warning: Saved steps count ({len(saved_steps)}) doesn't match generated steps count ({len(steps_json)})")
                db.session.rollback()
                return "Error: Failed to save all steps correctly"

            emit_sequence_update(session_id)
            return "Outreach sequence generated and saved successfully."

        except Exception as e:
            db.session.rollback()
            print(f"Database error while saving sequence: {str(e)}")
            return f"Error saving sequence to database: {str(e)}"

    except Exception as e:
        print(f"Error in generate_sequence: {str(e)}")
        return f"Error generating sequence: {str(e)}"

def get_user_context(session_id: str) -> str:
    session = Session.query.get(session_id)
    if not session or not session.user:
        return ""
    user = session.user
    
    # Extract job seeker preferences
    prefs = user.preferences or {}
    job_types = ", ".join(prefs.get("jobTypes", []) or ["Full-time"])
    target_companies = ", ".join(prefs.get("targetCompanies", []) or [])
    target_locations = ", ".join(prefs.get("targetLocations", []) or [])
    years_experience = prefs.get("yearsExperience", 0)
    skills = ", ".join(prefs.get("skills", []) or [])
    job_level = prefs.get("jobLevel", "")
    
    context = f"""
The messages should be written from {user.name}'s perspective as a {user.title} in the {user.industry} industry.
"""

    if user.company:
        context += f"Their current or previous company is {user.company}.\n"
    
    if years_experience:
        context += f"They have {years_experience} years of experience.\n"
    
    if skills:
        context += f"Their key skills include: {skills}.\n"
    
    if job_level:
        context += f"They are looking for {job_level}-level positions.\n"
    
    if job_types:
        context += f"They are interested in {job_types} roles.\n"
    
    if target_locations:
        context += f"Their preferred locations are: {target_locations}.\n"
    
    if target_companies:
        context += f"Their target companies include: {target_companies}.\n"
    
    return context

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

def generate_networking_asset(task: str, session_id: str):
    user_context = get_user_context(session_id)
    prompt = f"""
You're a job search assistant. Based on the following instruction, generate a fully formatted message (email, letter, follow-up, etc).
{user_context}
Task: {task}

Format the result as if it will be sent to a potential employer, hiring manager, or networking contact.
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

    return "Networking asset generated successfully."

def search_and_analyze_professionals(
    session_id: str,
    query: str,
    location: Optional[str] = None,
    years_experience: Optional[int] = None,
    skills: Optional[List[str]] = None,
    current_company: Optional[str] = None
) -> str:
    """
    Search for potential employers and networking contacts based on role and location.
    
    Args:
        session_id (str): The session ID
        query (str): Search query (e.g., "hiring managers", "engineering directors")
        location (Optional[str]): Location to search in
        years_experience (Optional[int]): Minimum years of experience
        skills (Optional[List[str]]): List of relevant skills
        current_company (Optional[str]): Target company name
    
    Returns:
        str: Formatted results with professional profiles
    """
    try:
        # Get user context for personalization
        user_context = get_user_context(session_id)
        
        # Search for professionals
        results = search_professionals(
            query=query,
            location=location,
            years_experience=years_experience,
            skills=skills,
            current_company=current_company
        )
        
        if not results["professionals"]:
            return f"I couldn't find any professionals matching your criteria for '{query}' in {location or 'any location'}. Would you like to try different search criteria?"
        
        # Format the results
        response = f"I found {results['total_found']} potential contacts matching your search for '{query}'"
        if location:
            response += f" in {location}"
        response += ":\n\n"
        
        for i, prof in enumerate(results["professionals"], 1):
            response += f"{i}. {prof['name']}\n"
            
            # Add current position if available
            if prof.get("current_position"):
                response += f"Current: {prof['current_position']}\n"
            
            # Add experience if available
            if "years_experience" in prof:
                response += f"Experience: {prof['years_experience']}+ years\n"
            
            # Add matched skills if available
            if "matched_skills" in prof and prof["matched_skills"]:
                response += f"Skills: {', '.join(prof['matched_skills'])}\n"
            
            # Add profile link
            response += f"Profile: {prof['link']}\n\n"
        
        response += "\nWould you like to:\n"
        response += "1. Generate a personalized outreach sequence for any of these professionals (I'll use their profile details to create a tailored message)\n"
        response += "2. Get more details about specific professionals\n"
        response += "3. Refine the search with different criteria"
        
        return response
        
    except Exception as e:
        logger.error(f"Error in search_and_analyze_professionals: {str(e)}", exc_info=True)
        return f"An error occurred while searching for professionals: {str(e)}"

def generate_personalized_outreach(profile_url: str, session_id: str) -> str:
    """
    Generate a personalized outreach message for a specific professional based on their profile.
    
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
        user_name = session.user.name if session and session.user else "the job seeker"
        user_title = session.user.title if session and session.user else "professional"
        
        # Generate personalized message using OpenAI
        prompt = f"""
        Generate a personalized outreach message for a professional based on their profile:
        Profile URL: {profile_url}
        Profile Content: {details['content']}
        
        The message should be from {user_name} as a {user_title} and should:
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
            "description": "Generates a job application or networking outreach sequence based on role and location, optionally personalized for a specific professional",
            "parameters": {
                "type": "object",
                "properties": {
                    "role": {"type": "string", "description": "The role you're interested in"},
                    "location": {"type": "string", "description": "Where the job is based"},
                    "step_count": {"type": "integer", "description": "Optional. Number of outreach steps to include"},
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"},
                    "profile_url": {"type": "string", "description": "Optional. URL of the professional's profile to personalize the sequence"}
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
            "name": "generate_networking_asset",
            "description": "Creates a single job search-related message (application email, thank you note, follow-up, etc) from a task description",
            "parameters": {
                "type": "object",
                "properties": {
                    "task": {"type": "string", "description": "Instruction like 'Write a thank you email after the interview with Google'"},
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
            "description": "Searches for potential employers and networking contacts based on role and location",
            "parameters": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "The session ID as a string UUID"},
                    "query": {"type": "string", "description": "The search query (e.g., 'hiring managers', 'engineering directors')"},
                    "location": {"type": "string", "description": "Optional. Location to search in (e.g., 'San Francisco')"},
                    "years_experience": {"type": "integer", "description": "Optional. Minimum years of experience"},
                    "skills": {"type": "array", "items": {"type": "string"}, "description": "Optional. List of relevant skills"},
                    "current_company": {"type": "string", "description": "Optional. Target company name"}
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