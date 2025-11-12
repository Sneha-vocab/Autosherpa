from typing import Any, Dict, Optional

from fastapi import APIRouter, Request, BackgroundTasks, HTTPException, Query

from .router_agent import predict_intent
from .config import settings
from .agents import (
    buying_handle,
    testdrive_handle,
    finance_handle,
    comparison_handle,
    valuation_handle,
    service_handle,
    exception_handler_handle,
)
from .whatsapp_sender import send_whatsapp_text

router = APIRouter()

AGENT_MAP = {
    "book_testdrive": testdrive_handle,
    "buy_car": buying_handle,
    "finance_query": finance_handle,
    "compare_cars": comparison_handle,
    "car_valuation": valuation_handle,
    "service_booking": service_handle,
    "exception_handling": exception_handler_handle,
    "greeting": None,  # Handled separately
}

def _extract_whatsapp_payload(payload: Dict[str, Any]) -> tuple[Optional[str], Optional[str], Dict[str, Any]]:
    """Normalize Meta WhatsApp payloads."""
    if not payload:
        return None, None, {}

    sender = payload.get("from") or payload.get("phone")
    message = payload.get("message")
    if sender and isinstance(message, str) and message.strip():
        return sender, message.strip(), {"source": "direct"}

    entries = payload.get("entry")
    if isinstance(entries, list):
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                metadata = value.get("metadata", {})
                contacts = value.get("contacts", [])
                messages = value.get("messages", [])
                if messages:
                    msg = messages[0]
                    sender_id = msg.get("from")
                    text_body = ""
                    if "text" in msg:
                        text_body = msg["text"].get("body", "")
                    elif "interactive" in msg:
                        interactive = msg["interactive"]
                        if "button_reply" in interactive:
                            text_body = interactive["button_reply"].get("title", "")
                        elif "list_reply" in interactive:
                            text_body = interactive["list_reply"].get("title", "")
                    name = contacts[0].get("profile", {}).get("name") if contacts else None
                    extra = {
                        "source": "whatsapp",
                        "name": name,
                        "metadata": metadata,
                        "raw_message": msg,
                    }
                    return sender_id, (text_body or "").strip(), extra

    return None, None, {}


@router.get("/webhook")
async def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    """
    Meta WhatsApp webhook verification endpoint.
    Meta sends a GET request to verify the webhook URL.
    """
    # For Meta webhook verification
    if hub_mode == "subscribe" and hub_verify_token:
        # You can set a verify token in your .env if needed
        verify_token = getattr(settings, "WEBHOOK_VERIFY_TOKEN", None)
        if verify_token and hub_verify_token == verify_token:
            return int(hub_challenge) if hub_challenge else {"status": "verified"}
        elif not verify_token:
            # If no verify token is set, accept any verification
            return int(hub_challenge) if hub_challenge else {"status": "verified"}
    
    # Default response for GET requests
    return {"status": "ok", "message": "Webhook endpoint is active. Use POST to send messages."}

@router.post("/webhook")
async def receive_webhook(req: Request, background_tasks: BackgroundTasks):
    try:
        payload = await req.json()
    except Exception as e:
        # Handle empty body or invalid JSON
        raise HTTPException(status_code=400, detail="Expected JSON body in request")

    sender, message, extra_context = _extract_whatsapp_payload(payload)
    if not sender or not message:
        # Many WhatsApp webhook callbacks are delivery receipts or read statuses.
        return {
            "status": "ignored",
            "reason": "no_message",
        }

    # 1) Preprocess (trim etc.)
    text = message.strip()

    # 2) Predict intent using LangChain/Gemini router
    intent = predict_intent(text)

    # 3) Route to appropriate agent
    agent_handler = AGENT_MAP.get(intent)
    
    latency = None
    if intent == "greeting":
        reply = "Hi 👋 I'm AutoSherpa — I can help you buy, test drive, or service cars. What would you like to do?"
    elif agent_handler:
        # Route to the appropriate agent
        try:
            result = agent_handler(
                sender,
                text,
                context={"intent": intent, "session_id": sender, "extra": extra_context},
            )
        except Exception as e:
            # If agent fails, route to exception handler
            print(f"Agent error for intent {intent}: {e}")
            result = exception_handler_handle(
                sender,
                text,
                context={"intent": intent, "session_id": sender, "extra": extra_context, "error": str(e)},
            )
        if isinstance(result, tuple):
            reply, latency = result
        else:
            reply = result
    else:
        # Unknown intent - route to exception handler
        result = exception_handler_handle(
            sender,
            text,
            context={"intent": intent, "session_id": sender, "extra": extra_context},
        )
        if isinstance(result, tuple):
            reply, latency = result
        else:
            reply = result

    # 4) send response asynchronously
    background_tasks.add_task(send_whatsapp_text, sender, reply)
    if latency is None:
        latency = getattr(req.state, "process_time", None)
    return {
        "status": "ok",
        "intent": intent,
        "latency_seconds": latency,
        "reply_preview": reply[:100] if reply else "",
    }
