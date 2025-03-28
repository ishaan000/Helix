import os
from openai import OpenAI
from dotenv import load_dotenv
from agents.tools import (
    tool_definitions,
    generate_sequence,
    revise_step,
    change_tone,
    add_step,
    generate_recruiting_asset
)
from database.models import SequenceStep, Session, User
import json


load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def chat_with_openai(messages: list, session_id: str) -> dict:
    print(f"\nProcessing chat with session_id: {session_id}")  # Debug log

    # Fetch the user context via the session ID
    session = Session.query.get(session_id)
    if session and session.user:
        user = session.user
        tone = user.preferences.get("tone", "professional") if user.preferences else "professional"
        context_message = {
            "role": "system",
            "content": f"""
    The user is a recruiter named {user.name} at {user.company}.
    They are a {user.title} in the {user.preferences.get('industry', 'N/A')} industry.
    Their preferred tone is {tone}.
    Do NOT ask for this information again unless explicitly requested.
    """
        }
        # Inject into the second position (after the main system prompt, before chat history)
        messages.insert(1, context_message)
        
    # Step 1: Send user + history messages and tool defs
    response = client.chat.completions.create(
        model="gpt-4",
        messages=messages,
        tools=tool_definitions,
        tool_choice="auto"
    )

    reply = response.choices[0].message
    # Step 2: If tool is called, extract name + arguments
    if reply.tool_calls:
        for tool_call in reply.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            
            # Always use the correct session_id from the chat endpoint
            args["session_id"] = session_id
            
            print(f"→ Tool called: {name}")
            print(f"→ Arguments: {json.dumps(args, indent=2)}")

            try:
                if name == "generate_sequence":
                    result = generate_sequence(**args)
                elif name == "revise_step":
                    result = revise_step(**args)
                elif name == "change_tone":
                    result = change_tone(**args)
                elif name == "add_step":
                    result = add_step(**args)
                elif name == "generate_recruiting_asset":
                    result = generate_recruiting_asset(**args)
                
                print(f"Tool execution result: {result}")  # Debug log
            except Exception as e:
                print(f"Error executing tool {name}: {str(e)}")  # Debug log
                continue

        # After tool execution, fetch updated sequence
        print(f"Fetching sequence for session_id: {session_id}")  # Debug log
        steps = SequenceStep.query.filter_by(session_id=session_id).order_by(SequenceStep.step_number).all()
        print(f"Found {len(steps)} steps for session_id: {session_id}")  # Debug log

        if name == "generate_sequence":
            follow_up_prompt = """You just created an outreach sequence using the `generate_sequence` tool.

        Now respond naturally:
        - Mention that the sequence is ready.
        - Offer to tweak the tone, revise a step, or regenerate it.
        - Don't repeat your intro or say hello.
        - Keep it short, friendly, and helpful.
        """
        elif name == "generate_recruiting_asset":
            follow_up_prompt = """You just helped the recruiter using the `generate_recruiting_asset` tool.

        Now respond naturally:
        - Mention that the message is ready.
        - Ask if the user wants to update the tone, fix any sections, or regenerate it.
        - Be proactive and conversational — avoid starting with 'Hi' or repeating your name.
        """
        else:
            follow_up_prompt = f"""You just used the `{name}` tool.

        Respond naturally:
        - Mention what was done (e.g. revised a step, changed tone).
        - Ask if there's anything else the user would like to tweak or explore.
        - Keep it short and friendly.
        """

        # Step 3: Send follow-up prompt to get natural response
        follow_up_response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": follow_up_prompt},
                {"role": "user", "content": "What happened?"}
            ]
        )

        sequence_data = [{"step_number": step.step_number, "content": step.content} for step in steps]
        print(f"Returning sequence data: {sequence_data}")  # Debug log

        return {
            "reply": follow_up_response.choices[0].message.content,
            "sequence": sequence_data
        }

    return {"reply": reply.content}