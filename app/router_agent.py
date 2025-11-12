"""
Router Agent: Uses LangChain with Gemini to extract intent from user messages.
No keyword matching - purely LLM-based intent classification.
"""
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from .config import settings

# Available intents
AVAILABLE_INTENTS = [
    "buy_car",
    "book_testdrive",
    "finance_query",
    "compare_cars",
    "car_valuation",
    "service_booking",
    "greeting",
    "exception_handling",
]

ROUTER_SYSTEM_PROMPT = """You are AutoSherpa's Intent Router. Your job is to classify user messages into one of these intents:

Available Intents:
1. "buy_car" - User wants to search, browse, or get information about buying cars
2. "book_testdrive" - User wants to book or schedule a test drive
3. "finance_query" - User asks about EMI, loans, financing, down payment, interest rates
4. "compare_cars" - User wants to compare two or more car models
5. "car_valuation" - User wants to know resale value, sell their car, or exchange value
6. "service_booking" - User wants to book service, maintenance, or asks about service packages
7. "greeting" - User says hi, hello, hey, or similar greetings
8. "exception_handling" - User message is unclear, unrelated to cars, or needs special handling

Guidelines:
- Analyze the user's message carefully
- Return ONLY the intent name (one word, no explanation)
- If the message is unclear or doesn't fit any category, return "exception_handling"
- Be accurate - the correct routing depends on your classification
- Consider context: "show me cars" = buy_car, "test drive nexon" = book_testdrive, "emi for 10 lakh" = finance_query

Examples:
- "I want to buy a car" → buy_car
- "Show me available cars" → buy_car
- "Book test drive for Creta" → book_testdrive
- "What's the EMI for Nexon?" → finance_query
- "Compare Creta and Seltos" → compare_cars
- "What's my car worth?" → car_valuation
- "Book service for my car" → service_booking
- "Hi there" → greeting
- "What's the weather?" → exception_handling
- "I don't understand" → exception_handling

Return only the intent name, nothing else."""

# Lazy initialization
_router_llm = None
_router_prompt = None

def get_router_llm():
    """Get or create the router LLM."""
    global _router_llm
    if _router_llm is None:
        api_key = settings.GEMINI_API_KEY or settings.LLM_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY or LLM_API_KEY must be set in environment variables")
        
        _router_llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=api_key,
            temperature=0.3,  # Lower temperature for more consistent classification
            convert_system_message_to_human=True,
        )
    return _router_llm

def get_router_prompt():
    """Get or create the router prompt."""
    global _router_prompt
    if _router_prompt is None:
        _router_prompt = ChatPromptTemplate.from_messages([
            ("system", ROUTER_SYSTEM_PROMPT),
            ("human", "User message: {message}\n\nClassify this message into one of the available intents. Return only the intent name."),
        ])
    return _router_prompt

def predict_intent(text: str) -> str:
    """
    Predict intent from user message using LangChain with Gemini.
    Returns one of the available intents.
    """
    if not text or not text.strip():
        return "exception_handling"
    
    try:
        llm = get_router_llm()
        prompt = get_router_prompt()
        
        # Invoke the LLM
        chain = prompt | llm
        response = chain.invoke({"message": text.strip()})
        
        # Extract intent from response
        intent = response.content.strip().lower()
        
        # Validate intent
        if intent in AVAILABLE_INTENTS:
            return intent
        
        # If response contains an intent name, extract it
        for valid_intent in AVAILABLE_INTENTS:
            if valid_intent in intent:
                return valid_intent
        
        # Fallback to exception_handling if unclear
        return "exception_handling"
        
    except Exception as e:
        # On error, fallback to exception_handling
        print(f"Router error: {e}")
        return "exception_handling"
