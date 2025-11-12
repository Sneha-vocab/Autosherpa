"""
Chat API for testing agents.
"""
from fastapi import APIRouter, HTTPException, Request
from .router_agent import predict_intent
from .agents import (
    buying_handle,
    testdrive_handle,
    finance_handle,
    comparison_handle,
    valuation_handle,
    service_handle,
    exception_handler_handle,
)
from .memory import get_conversation_history_plain

router = APIRouter()

AGENT_MAP = {
    "book_testdrive": testdrive_handle,
    "buy_car": buying_handle,
    "finance_query": finance_handle,
    "compare_cars": comparison_handle,
    "car_valuation": valuation_handle,
    "service_booking": service_handle,
    "exception_handling": exception_handler_handle,
    "greeting": None,
}

@router.get("/api/chat")
async def chat_get(request: Request, message: str = None):
    """
    GET endpoint for chat testing.
    Usage: /api/chat?message=I want to buy a car
    """
    if not message:
        return {
            "status": "ok",
            "message": "Send a message using ?message=your_message",
            "example": "/api/chat?message=I want to buy a car"
        }
    
    sender = "test_user"
    text = message.strip()
    
    # Predict intent
    intent = predict_intent(text)
    
    # Route to appropriate agent
    agent_handler = AGENT_MAP.get(intent)
    
    latency = None
    if intent == "greeting":
        reply = "Hi 👋 I'm AutoSherpa — I can help you buy, test drive, or service cars. What would you like to do?"
    elif agent_handler:
        try:
            result = agent_handler(sender, text, context={"intent": intent, "session_id": sender})
        except Exception as e:
            print(f"Agent error for intent {intent}: {e}")
            result = exception_handler_handle(sender, text, context={"intent": intent, "session_id": sender, "error": str(e)})
        if isinstance(result, tuple):
            reply, latency = result
        else:
            reply = result
    else:
        result = exception_handler_handle(sender, text, context={"intent": intent, "session_id": sender})
        if isinstance(result, tuple):
            reply, latency = result
        else:
            reply = result

    if latency is None and request is not None:
        latency = getattr(request.state, "process_time", None)
    
    return {
        "status": "ok",
        "intent": intent,
        "message": text,
        "reply": reply,
        "history": get_conversation_history_plain(sender),
        "latency_seconds": latency,
    }

@router.post("/api/chat")
async def chat_post(req: Request):
    """
    POST endpoint for chat testing.
    Body: {"message": "I want to buy a car", "from": "optional_user_id"}
    """
    try:
        payload = await req.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Expected JSON body")
    
    sender = payload.get("from") or "test_user"
    message = payload.get("message") or ""
    
    if not message:
        raise HTTPException(status_code=400, detail="Missing 'message' field in request body")
    
    text = message.strip()
    
    # Predict intent
    intent = predict_intent(text)
    
    # Route to appropriate agent
    agent_handler = AGENT_MAP.get(intent)
    
    latency = None
    if intent == "greeting":
        reply = "Hi 👋 I'm AutoSherpa — I can help you buy, test drive, or service cars. What would you like to do?"
    elif agent_handler:
        try:
            result = agent_handler(sender, text, context={"intent": intent, "session_id": sender})
        except Exception as e:
            print(f"Agent error for intent {intent}: {e}")
            result = exception_handler_handle(sender, text, context={"intent": intent, "session_id": sender, "error": str(e)})
        if isinstance(result, tuple):
            reply, latency = result
        else:
            reply = result
    else:
        result = exception_handler_handle(sender, text, context={"intent": intent, "session_id": sender})
        if isinstance(result, tuple):
            reply, latency = result
        else:
            reply = result

    if latency is None:
        latency = getattr(req.state, "process_time", None)
    
    return {
        "status": "ok",
        "intent": intent,
        "message": text,
        "reply": reply,
        "history": get_conversation_history_plain(sender),
        "latency_seconds": latency,
    }
