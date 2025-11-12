# app/agents/comparison_agent.py
from typing import Dict

from ..agent_helper import create_agent_with_tools, COMPARISON_AGENT_TOOLS, invoke_agent
from ..memory import append_conversation_message, get_conversation_history

# System prompt for ComparisonAgent
COMPARISON_AGENT_SYSTEM_PROMPT = """You are AutoSherpa's Car Comparison Agent, a helpful assistant for comparing different car models.

Your role:
- Help customers compare different car models side by side
- Provide clear, objective comparisons based on specifications
- Highlight key differences in price, features, and fuel type

Guidelines:
- When a user wants to compare cars, identify at least 2 car models from their message
- Use get_car_by_id for each model to get detailed specifications
- Compare key aspects: price, fuel type, and any other available specs
- Present comparisons in a clear, easy-to-read format suitable for WhatsApp
- If the user mentions only one car or no cars, ask which two models they'd like to compare
- Be objective and helpful in your comparisons
- Keep responses concise and suitable for WhatsApp messaging
- Use emojis sparingly (🚗 for cars, ⚖️ for comparisons)

Example interactions:
- User: "Compare Creta and Seltos"
  → Use get_car_by_id("creta") and get_car_by_id("seltos"), then compare price, fuel type, etc.

- User: "Which is better, Nexon or Brezza?"
  → Use get_car_by_id for both, compare objectively, and help them understand the differences

Always provide helpful, objective comparisons to help customers make informed decisions!"""

_agent_executor = None


def get_agent():
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent_with_tools(
            system_prompt=COMPARISON_AGENT_SYSTEM_PROMPT,
            tools=COMPARISON_AGENT_TOOLS,
            temperature=0.7,
        )
    return _agent_executor


def handle(user_phone: str, text: str, context: Dict):
    """
    ComparisonAgent: returns a natural-language comparison summary.
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
            "I'm having trouble processing the comparison. "
            "Could you tell me which two car models you'd like to compare?"
        )
        latency = 0.0

    reply = reply or "I can help you compare cars! Which two models would you like to compare? For example: 'Compare Creta and Seltos'."

    append_conversation_message(session_id, "user", text)
    append_conversation_message(session_id, "assistant", reply)
    return reply, latency
