import os, requests
from .config import settings

def send_whatsapp_text(to_phone: str, message: str):
    token = settings.WHATSAPP_TOKEN
    phone_id = settings.WHATSAPP_PHONE_ID
    if not token or not phone_id:
        # Fallback to log mode
        print(f"[WHATSAPP MOCK] to={to_phone} message={message}")
        return {"mock": True, "message": message}

    url = f"https://graph.facebook.com/{settings.META_API_VERSION}/{phone_id}/messages"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message}
    }
    try:
        r = requests.post(url, json=payload, headers=headers, timeout=8)
        r.raise_for_status()
        data = r.json()
        print(f"[WHATSAPP SENT] to={to_phone} id={data.get('messages', [{}])[0].get('id') if isinstance(data, dict) else 'unknown'}")
        return data
    except requests.HTTPError as exc:
        content = None
        try:
            content = r.json()
        except Exception:
            content = r.text
        print(f"[WHATSAPP ERROR] status={r.status_code} body={content}")
        raise
    except Exception as exc:
        print(f"[WHATSAPP ERROR] unexpected={exc}")
        raise
