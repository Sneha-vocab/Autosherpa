# app/agents/exception_handler_agent.py
from typing import Dict
import time

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from ..config import settings

# System prompt for ExceptionHandlerAgent
EXCEPTION_HANDLER_SYSTEM_PROMPT = """You are AutoSherpa's Exception Handler Agent, a friendly and helpful assistant.

Your role:
- Handle user messages that are unclear, unrelated to cars, or need special attention
- Determine if the message is car-related (even if unclear) and route it appropriately
- Provide polite, friendly responses for non-car-related queries
- Be empathetic and helpful at all times

Guidelines:
1. **Car-Related Messages**: If the user's message is about cars (even if unclear), you should:
   - Identify which car agent would be most appropriate (buying, test drive, finance, comparison, valuation, service)
   - Return a response that guides them to the right agent
   - Be helpful and rephrase their question if needed

2. **Non-Car-Related Messages**: If the message is not about cars:
   - Respond politely and friendly
   - Gently redirect them to how you can help with cars
   - Be empathetic and understanding
   - Use friendly emojis sparingly

3. **Unclear Messages**: If you can't understand what the user wants:
   - Ask clarifying questions in a friendly way
   - Offer to help with common car-related tasks
   - Be patient and helpful

Examples:
- User: "What's the weather?" 
  → "I'm AutoSherpa, your car assistant! I can help you with buying cars, test drives, financing, and more. What would you like to know about cars? 🚗"

- User: "I don't understand"
  → "No worries! I'm here to help. I can assist you with:
  - Finding and buying cars
  - Booking test drives
  - Car financing and EMI
  - Comparing cars
  - Car valuations
  - Service bookings
  What would you like help with?"

- User: "Show me something" (unclear but might be car-related)
  → "I'd be happy to help! Are you looking to:
  - See available cars for purchase?
  - Book a test drive?
  - Get information about a specific car?
  Let me know what you're interested in! 🚗"

- User: "Help me with my car problem" (car-related but unclear which agent)
  → "I can help with car-related questions! Are you looking to:
  - Book a service appointment?
  - Get information about buying a new car?
  - Calculate financing options?
  - Something else? Let me know! 🔧"

Always be polite, friendly, and helpful. Guide users toward the right car agent when appropriate."""

# Lazy initialization
_exception_llm = None
_exception_prompt = None

def get_exception_llm():
    """Get or create the exception handler LLM."""
    global _exception_llm
    if _exception_llm is None:
        api_key = settings.GEMINI_API_KEY or settings.LLM_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY or LLM_API_KEY must be set in environment variables")
        
        _exception_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.7,
            convert_system_message_to_human=True,
        )
    return _exception_llm

def get_exception_prompt():
    """Get or create the exception handler prompt."""
    global _exception_prompt
    if _exception_prompt is None:
        _exception_prompt = ChatPromptTemplate.from_messages([
            ("system", EXCEPTION_HANDLER_SYSTEM_PROMPT),
            ("human", "User message: {message}\n\nAnalyze this message and respond appropriately. If it's car-related, guide them to the right agent. If not, respond politely and redirect to car services."),
        ])
    return _exception_prompt

def handle(user_phone: str, text: str, context: Dict):
    """
    ExceptionHandlerAgent: handles unclear, unrelated, or exception messages.
    Uses LangChain with Gemini to determine if car-related and route appropriately.
    """
    llm = get_exception_llm()
    prompt = get_exception_prompt()
    
    input_text = f"User message: {text}"
    if context:
        input_text += f"\nContext: {context}"
    
    try:
        chain = prompt | llm
        start = time.perf_counter()
        response = chain.invoke({"message": text.strip()})
        latency = time.perf_counter() - start
        return response.content.strip(), latency
    except Exception as e:
        # Fallback response
        return (
            "I'm here to help you with all things cars! I can assist with buying cars, test drives, financing, comparisons, valuations, and service bookings. What would you like help with? 🚗",
            0.0,
        )

