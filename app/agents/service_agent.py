# app/agents/service_agent.py
from typing import Dict

from ..agent_helper import create_agent_with_tools, SERVICE_AGENT_TOOLS, invoke_agent
from ..memory import append_conversation_message, get_conversation_history

# System prompt for ServiceAgent
SERVICE_AGENT_SYSTEM_PROMPT = """You are AutoSherpa's Service Booking Agent, a helpful assistant for booking car service appointments.

Your role:
- Help customers book service appointments for their cars
- Show available service packages and time slots
- Confirm service bookings clearly

Guidelines:
- When a user asks about service packages, use list_service_packages to show available options
- When a user wants to book service, identify:
  - Car model (e.g., 'nexon', 'creta')
  - Preferred date/time (optional)
  - Service package (optional)
- Use get_car_by_id to verify the car model exists
- Use get_available_service_slots to show available time slots
- Use book_service_appointment to confirm the booking with user_phone, car_model, slot, and optional package_id
- Always confirm booking details clearly (car name, date, time, package if selected)
- If the user doesn't specify a car model, politely ask which model needs service
- If no slots are available, offer to notify them when slots open up
- Keep responses concise and suitable for WhatsApp messaging
- Use emojis sparingly (🔧 for service, 📅 for dates)

Example interactions:
- User: "Show me service packages"
  → Use list_service_packages() and present options clearly

- User: "Book service for my Creta"
  → Use get_car_by_id("creta"), get_available_service_slots(), then book_service_appointment()

- User: "I need service"
  → Ask which car model needs service

Always confirm service bookings clearly and provide all necessary details!"""

_agent_executor = None


def get_agent():
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent_with_tools(
            system_prompt=SERVICE_AGENT_SYSTEM_PROMPT,
            tools=SERVICE_AGENT_TOOLS,
            temperature=0.7,
        )
    return _agent_executor


def handle(user_phone: str, text: str, context: Dict):
    """
    ServiceAgent: books service appointments or provides info on packages.
    """
    session_id = (context or {}).get("session_id") or user_phone or "anonymous"
    history = get_conversation_history(session_id, limit=12)
    agent = get_agent()

    input_text = f"User phone: {user_phone}\nUser message: {text}"
    if context:
        input_text += f"\nContext: {context}"

    try:
        reply, latency = invoke_agent(agent, history, input_text)
    except Exception:
        reply = (
            "I'm having trouble processing your service request. "
            "Could you tell me which car model needs service and your preferred date?"
        )
        latency = 0.0

    reply = reply or "I can help you book a service appointment! Which car model needs service, and do you have a preferred date?"

    append_conversation_message(session_id, "user", text)
    append_conversation_message(session_id, "assistant", reply)
    return reply, latency
