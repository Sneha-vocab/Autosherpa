# app/agents/finance_agent.py
from typing import Dict

from ..agent_helper import create_agent_with_tools, FINANCE_AGENT_TOOLS, invoke_agent
from ..memory import append_conversation_message, get_conversation_history

# System prompt for FinanceAgent
FINANCE_AGENT_SYSTEM_PROMPT = """You are AutoSherpa's Finance Agent, a helpful assistant for car loan and EMI calculations.

Your role:
- Calculate EMI (Equated Monthly Installment) for car loans
- Help customers understand financing options
- Provide clear, accurate financial information

Guidelines:
- When a user asks about EMI, identify the car model or loan amount
- If they mention a car model, use get_car_by_id to get the car price
- Use calculate_emi with principal (car price or loan amount), annual_rate_percent (default 8.5%), and months (default 60)
- Always format amounts in Indian Rupees (₹) with proper formatting
- Explain the EMI calculation clearly (principal, interest rate, tenure)
- If the user doesn't provide enough information, ask for:
  - Car model OR loan amount
  - Loan tenure (optional, default is 60 months/5 years)
- Keep responses concise and suitable for WhatsApp messaging
- Use emojis sparingly (💰 for money, 📊 for calculations)

Example interactions:
- User: "What's the EMI for Nexon?"
  → Use get_car_by_id("nexon") to get price, then calculate_emi(principal=price)

- User: "EMI for 10 lakh for 3 years"
  → Use calculate_emi(principal=1000000, months=36)

- User: "EMI for 15 lakh at 9% for 4 years"
  → Use calculate_emi(principal=1500000, annual_rate_percent=9.0, months=48)

Always provide clear EMI breakdowns and offer to connect them with finance experts if needed!"""

_agent_executor = None


def get_agent():
    """Get or create the agent executor."""
    global _agent_executor
    if _agent_executor is None:
        _agent_executor = create_agent_with_tools(
            system_prompt=FINANCE_AGENT_SYSTEM_PROMPT,
            tools=FINANCE_AGENT_TOOLS,
            temperature=0.7,
        )
    return _agent_executor


def _session_id(user_phone: str, context: Dict) -> str:
    return (context or {}).get("session_id") or user_phone or "anonymous"


def handle(user_phone: str, text: str, context: Dict) -> str:
    """
    FinanceAgent: calculate EMI or ask clarifying questions.
    """
    session_id = _session_id(user_phone, context)
    history = get_conversation_history(session_id, limit=12)
    agent = get_agent()

    input_text = f"User message: {text}"
    if context:
        input_text += f"\nContext: {context}"

    try:
        reply, latency = invoke_agent(agent, history, input_text)
    except Exception:
        reply = (
            "I'm having trouble calculating the EMI right now. "
            "Could you share the car model or loan amount, the tenure, and (optionally) the interest rate?"
        )
        latency = 0.0

    reply = reply or "I can help you calculate EMI! Please share the car model or loan amount, and I'll calculate the monthly installment for you."

    append_conversation_message(session_id, "user", text)
    append_conversation_message(session_id, "assistant", reply)
    return reply, latency
