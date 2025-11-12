"""
Helper functions for creating LangChain agents with Gemini.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
import time
from langchain_core.messages import HumanMessage
from langchain.agents import create_agent
from .config import settings
from .tools import (
    search_cars,
    get_car_by_id,
    book_testdrive,
    get_available_testdrive_slots,
    calculate_emi,
    estimate_car_value,
    list_service_packages,
    get_available_service_slots,
    book_service_appointment,
    faq_lookup,
)


def get_gemini_llm(temperature: float = 0.7):
    """Create a Gemini LLM instance."""
    api_key = settings.GEMINI_API_KEY or settings.LLM_API_KEY
    if not api_key:
        raise ValueError("GEMINI_API_KEY or LLM_API_KEY must be set in environment variables")
    
    return ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=api_key,
        temperature=temperature,
        convert_system_message_to_human=True,
    )


def create_agent_with_tools(
    system_prompt: str,
    tools: list,
    temperature: float = 0.7,
):
    """Create a LangChain agent with specified tools and system prompt."""
    llm = get_gemini_llm(temperature=temperature)

    return create_agent(llm, tools, system_prompt=system_prompt)


def invoke_agent(agent, history, user_text: str) -> tuple[str, float]:
    """Invoke the compiled agent graph with chat history."""
    messages = list(history) + [HumanMessage(content=user_text)]
    start = time.perf_counter()
    result = agent.invoke({"messages": messages})
    latency = time.perf_counter() - start

    if isinstance(result, dict):
        output_messages = result.get("messages")
        if output_messages:
            last = output_messages[-1]
            content = getattr(last, "content", None)
            if isinstance(content, list):
                reply = " ".join(
                    part.get("text", "") if isinstance(part, dict) else str(part)
                    for part in content
                ).strip()
                return reply, latency
            if isinstance(content, str):
                return content, latency
        if "output" in result and result["output"]:
            return result["output"], latency
        return str(result), latency

    content = getattr(result, "content", None)
    if content:
        return content, latency

    return str(result), latency


# Tool sets for different agents
BUYING_AGENT_TOOLS = [search_cars, get_car_by_id, faq_lookup]
TESTDRIVE_AGENT_TOOLS = [get_car_by_id, get_available_testdrive_slots, book_testdrive, faq_lookup]
FINANCE_AGENT_TOOLS = [get_car_by_id, calculate_emi, faq_lookup]
COMPARISON_AGENT_TOOLS = [get_car_by_id, faq_lookup]
VALUATION_AGENT_TOOLS = [get_car_by_id, estimate_car_value, faq_lookup]
SERVICE_AGENT_TOOLS = [
    list_service_packages,
    get_available_service_slots,
    book_service_appointment,
    get_car_by_id,
    faq_lookup,
]
