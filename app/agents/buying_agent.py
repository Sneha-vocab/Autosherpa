# app/agents/buying_agent.py
import re
from typing import Dict, Optional
from ..agent_helper import create_agent_with_tools, BUYING_AGENT_TOOLS, invoke_agent
from ..memory import append_conversation_message, get_conversation_history, update_session_state, get_session_state

# System prompt for BuyingAgent
BUYING_AGENT_SYSTEM_PROMPT = """You are AutoSherpa's Buying Agent, a helpful and friendly car buying assistant.

Your role:
- Help customers find cars that match their preferences (brand, budget, type)
- Provide clear, concise information about available cars
- Ask clarifying questions when needed (budget, brand preference, type)
- Be conversational and helpful, not robotic

Guidelines:
- When a user asks about cars, use the search_cars tool to find matching vehicles
- If they mention a specific car model, use get_car_by_id to get detailed information
- Always format prices in Indian Rupees (₹) with proper formatting
- If no cars match, politely ask for clarification on their preferences
- Keep responses concise and friendly, suitable for WhatsApp messaging
- Use emojis sparingly (🚗 for cars, 💰 for prices)

Example interactions:
- User: "Show me cars under 15 lakh"
  → Use search_cars with budget_lt=1500000, then present results clearly

- User: "Tell me about Nexon"
  → Use get_car_by_id("nexon"), then provide key details

Always be helpful and guide users toward finding their perfect car!"""

def _get_session_id(user_phone: str, context: Dict) -> str:
    return (context or {}).get("session_id") or user_phone or "anonymous"

BRAND_KEYWORDS = [
    "tata",
    "hyundai",
    "kia",
    "maruti",
    "suzuki",
    "mahindra",
    "toyota",
    "honda",
    "mg",
    "nissan",
]

_agent_executor = None


def _extract_budget(text: str) -> Optional[int]:
    tx = text.lower().replace(",", "").strip()
    match = re.search(r"(\d+(?:\.\d+)?)\s*(lakh|lakhs|l|k|thousand|crore)?", tx)
    if not match:
        return None
    value = float(match.group(1))
    suffix = match.group(2)
    if suffix in ("lakh", "lakhs", "l"):
        return int(value * 100000)
    if suffix in ("k", "thousand"):
        return int(value * 1000)
    if suffix == "crore":
        return int(value * 10000000)
    if value >= 50000:
        return int(value)
    return None


def _extract_brand(text: str) -> Optional[str]:
    tx = text.lower()
    for brand in BRAND_KEYWORDS:
        if brand in tx:
            return brand
    return None


def get_agent():
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent_with_tools(
            system_prompt=BUYING_AGENT_SYSTEM_PROMPT,
            tools=BUYING_AGENT_TOOLS,
            temperature=0.7,
        )
    return _agent_executor


def handle(user_phone: str, text: str, context: Dict) -> str:
    """
    BuyingAgent: search inventory/questions via LangChain agent.
    """
    session_id = _get_session_id(user_phone, context)
    history = get_conversation_history(session_id, limit=12)
    agent = get_agent()

    state = get_session_state(session_id)
    detected_brand = _extract_brand(text) or state.get("brand")
    detected_budget = _extract_budget(text)
    if not detected_budget and state.get("budget"):
        try:
            detected_budget = int(float(state["budget"]))
        except (ValueError, TypeError):
            detected_budget = None

    if detected_brand:
        update_session_state(session_id, brand=detected_brand)
    if detected_budget:
        update_session_state(session_id, budget=detected_budget)

    input_text = f"User message: {text}"
    enriched_context = dict(context or {})
    if detected_brand:
        enriched_context["known_brand"] = detected_brand
    if detected_budget:
        enriched_context["known_budget"] = detected_budget
    if enriched_context:
        input_text += f"\nContext: {enriched_context}"

    try:
        reply, latency = invoke_agent(agent, history, input_text)
    except Exception:
        reply = (
            "I'm having a little trouble fetching inventory details right now. "
            "Could you tell me your preferred brand, budget, or car type so I can help you better?"
        )
        latency = 0.0

    reply = reply or "I'm here to help you find the perfect car! What are you looking for?"

    append_conversation_message(session_id, "user", text)
    append_conversation_message(session_id, "assistant", reply)
    return reply, latency
