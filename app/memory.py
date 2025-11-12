"""
Conversation memory backed by Redis.
"""
from __future__ import annotations

import json
from typing import Dict, List, Optional

import redis
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage

from .config import settings

_redis_client: Optional[redis.Redis] = None

HISTORY_LIMIT = 40


def _get_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client


def _history_key(session_id: str) -> str:
    return f"chat:{session_id}:history"


def _state_key(session_id: str) -> str:
    return f"chat:{session_id}:state"


def get_conversation_history(session_id: str, limit: Optional[int] = None) -> List[BaseMessage]:
    """
    Return the conversation history as LangChain BaseMessage objects.
    """
    history_limit = limit or HISTORY_LIMIT
    try:
        client = _get_client()
        entries = client.lrange(_history_key(session_id), -history_limit, -1)
    except Exception:
        return []

    history: List[BaseMessage] = []
    for raw in entries:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        role = data.get("role")
        content = data.get("content", "")
        if role == "assistant":
            history.append(AIMessage(content=content))
        elif role == "user":
            history.append(HumanMessage(content=content))
    return history


def get_conversation_history_plain(session_id: str, limit: Optional[int] = None) -> List[Dict[str, str]]:
    """
    Return conversation history as list of dictionaries (role/content).
    """
    history_limit = limit or HISTORY_LIMIT
    try:
        client = _get_client()
        entries = client.lrange(_history_key(session_id), -history_limit, -1)
    except Exception:
        return []

    plain: List[Dict[str, str]] = []
    for raw in entries:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        plain.append(
            {
                "role": data.get("role", "assistant"),
                "content": data.get("content", ""),
            }
        )
    return plain


def append_conversation_message(session_id: str, role: str, content: str) -> None:
    """
    Append a message to the conversation history.
    """
    try:
        client = _get_client()
        payload = json.dumps({"role": role, "content": content})
        key = _history_key(session_id)
        client.rpush(key, payload)
        client.ltrim(key, -HISTORY_LIMIT, -1)
    except Exception:
        # Swallow Redis errors to avoid impacting user flows.
        return


def get_session_state(session_id: str) -> Dict[str, str]:
    """
    Retrieve stored session attributes (brand, budget, type, etc.).
    """
    try:
        client = _get_client()
        state = client.hgetall(_state_key(session_id))
    except Exception:
        return {}
    return state or {}


def update_session_state(session_id: str, **kwargs: Optional[str]) -> None:
    """
    Update session state with provided key/value pairs.
    """
    mapping = {k: str(v) for k, v in kwargs.items() if v is not None and v != ""}
    if not mapping:
        return
    try:
        client = _get_client()
        client.hset(_state_key(session_id), mapping=mapping)
    except Exception:
        return


def clear_session(session_id: str) -> None:
    """
    Remove conversation history and state for a session.
    """
    try:
        client = _get_client()
        client.delete(_history_key(session_id))
        client.delete(_state_key(session_id))
    except Exception:
        return

