# app/agents/testdrive_agent.py
from typing import Dict

from ..agent_helper import create_agent_with_tools, TESTDRIVE_AGENT_TOOLS, invoke_agent
from ..memory import append_conversation_message, get_conversation_history

# System prompt for TestDriveAgent
TESTDRIVE_AGENT_SYSTEM_PROMPT = """You are AutoSherpa's Test Drive Booking Agent, a helpful assistant for scheduling test drives.

Your role:
- Help customers book test drives for their preferred car models
- Check available time slots and confirm bookings
- Be friendly, professional, and efficient

Guidelines:
- When a user wants to book a test drive, first identify the car model they're interested in
- Use get_car_by_id to verify the car model exists
- Use get_available_testdrive_slots to show available time slots
- Use book_testdrive to confirm the booking with user_phone, car_model, and slot
- Always confirm the booking details clearly (car name, date, time)
- If the user doesn't specify a car model, politely ask which model they'd like to test drive
- If no slots are available, offer to notify them when slots open up
- Keep responses concise and suitable for WhatsApp messaging
- Use friendly emojis sparingly (🚗 for cars, 📅 for dates)

Example interactions:
- User: "I want to test drive Nexon"
  → Use get_car_by_id("nexon"), then get_available_testdrive_slots(), then book_testdrive()

- User: "Book test drive"
  → Ask which car model they'd like to test drive

Always confirm bookings clearly and provide all necessary details!"""

_agent_executor = None


def get_agent():
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent_with_tools(
            system_prompt=TESTDRIVE_AGENT_SYSTEM_PROMPT,
            tools=TESTDRIVE_AGENT_TOOLS,
            temperature=0.7,
        )
    return _agent_executor


def _session_id(user_phone: str, context: Dict) -> str:
    return (context or {}).get("session_id") or user_phone or "anonymous"


def handle(user_phone: str, text: str, context: Dict) -> str:
    """
    TestDriveAgent: schedule or ask for more details for test drive booking.
    """
    session_id = _session_id(user_phone, context)
    history = get_conversation_history(session_id, limit=12)
    agent = get_agent()

    input_text = f"User phone: {user_phone}\nUser message: {text}"
    if context:
        input_text += f"\nContext: {context}"

    try:
        reply, latency = invoke_agent(agent, history, input_text)
    except Exception:
        reply = (
            "I'm having trouble confirming the test drive right now. "
            "Could you share the car model and preferred timing once more?"
        )
        latency = 0.0

    reply = reply or "I can help you book a test drive! Which car model would you like to test drive?"

    append_conversation_message(session_id, "user", text)
    append_conversation_message(session_id, "assistant", reply)
    return reply, latency
