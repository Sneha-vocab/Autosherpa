# app/agents/valuation_agent.py
from typing import Dict

from ..agent_helper import create_agent_with_tools, VALUATION_AGENT_TOOLS, invoke_agent
from ..memory import append_conversation_message, get_conversation_history

# System prompt for ValuationAgent
VALUATION_AGENT_SYSTEM_PROMPT = """You are AutoSherpa's Car Valuation Agent, a helpful assistant for estimating car resale values.

Your role:
- Help customers estimate the resale value of their cars
- Ask for necessary information (model, year, kilometers)
- Provide clear, helpful valuation estimates

Guidelines:
- When a user wants to know their car's value, identify:
  - Car model (e.g., 'nexon', 'creta', 'swift')
  - Registration year (e.g., 2018, 2020)
  - Kilometers driven (optional but helpful)
  - Condition (optional: 'excellent', 'good', 'fair', 'poor')
- Use get_car_by_id to verify the car model exists
- Use estimate_car_value with model, year, kms, and condition to get the valuation
- Always format amounts in Indian Rupees (₹) with proper formatting
- If the user doesn't provide enough information, ask for:
  - Car model (required)
  - Registration year (required)
  - Kilometers driven (optional)
- Keep responses concise and suitable for WhatsApp messaging
- Use emojis sparingly (💰 for value, 📊 for estimates)

Example interactions:
- User: "What's my 2018 Swift worth with 40,000 km?"
  → Use get_car_by_id("swift"), then estimate_car_value(model="swift", year=2018, kms=40000)

- User: "Value of my Nexon"
  → Ask for registration year and kilometers

Always provide helpful valuations and offer exchange options when appropriate!"""

_agent_executor = None


def get_agent():
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent_with_tools(
            system_prompt=VALUATION_AGENT_SYSTEM_PROMPT,
            tools=VALUATION_AGENT_TOOLS,
            temperature=0.7,
        )
    return _agent_executor


def handle(user_phone: str, text: str, context: Dict):
    """
    ValuationAgent: uses valuation_service. If not enough info, asks for model/year/kms.
    """
    session_id = (context or {}).get("session_id") or user_phone or "anonymous"
    history = get_conversation_history(session_id, limit=12)
    agent = get_agent()

    input_text = f"User message: {text}"
    if context:
        input_text += f"\nContext: {context}"

    try:
        reply, latency = invoke_agent(agent, history, input_text)
    except Exception:
        reply = (
            "I'm having trouble estimating the value right now. "
            "Could you provide your car model and registration year? For example: '2018 Swift with 40,000 km'."
        )
        latency = 0.0

    reply = reply or (
        "I can help you estimate your car's resale value! "
        "Please share your car model and registration year. For example: '2018 Swift with 40,000 km'."
    )

    append_conversation_message(session_id, "user", text)
    append_conversation_message(session_id, "assistant", reply)
    return reply, latency
