from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import requests, os, time, datetime, json
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("PHONE_NUMBER_ID")


# --- 1️⃣ Verify Webhook (GET) ---
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        if mode == "subscribe" and token == VERIFY_TOKEN:
            print("✅ WEBHOOK VERIFIED")
            return JSONResponse(content=int(challenge))
        else:
            return JSONResponse(content={"error": "Verification failed"}, status_code=403)
    return JSONResponse(content={"error": "Bad request"}, status_code=400)


# --- 2️⃣ Receive Message (POST) ---
@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    print("📩 Incoming data:", json.dumps(data, indent=2))

    if "entry" in data:
        for entry in data["entry"]:
            for change in entry.get("changes", []):
                value = change.get("value", {})
                messages = value.get("messages", [])

                if messages:
                    msg = messages[0]
                    phone_number = msg["from"]
                    text = msg["text"]["body"] if "text" in msg else None
                    timestamp = msg.get("timestamp")  # WhatsApp UNIX timestamp

                    if timestamp:
                        # Convert WhatsApp timestamp to datetime
                        sent_time = datetime.datetime.fromtimestamp(int(timestamp))
                        received_time = datetime.datetime.utcnow()
                        latency = (received_time - sent_time).total_seconds() * 1000  # in ms

                        print(f"⏱ Message Latency: {latency:.2f} ms")
                        print(f"📨 Message received at: {received_time} | Sent at: {sent_time}")

                    if text:
                        start_reply_time = time.time()
                        send_message(phone_number, f"You said: {text}")
                        end_reply_time = time.time()
                        response_latency = (end_reply_time - start_reply_time) * 1000  # ms
                        print(f"⚡ Response Latency: {response_latency:.2f} ms")

    return JSONResponse(content={"status": "received"})


# --- 3️⃣ Send Message via Meta API ---
def send_message(to, message):
    url = f"https://graph.facebook.com/v19.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }

    start_time = time.time()
    response = requests.post(url, headers=headers, json=data)
    end_time = time.time()

    api_call_latency = (end_time - start_time) 
    print(f"🌐 API Call Latency: {api_call_latency:.2f} ms")
    print("📤 Sent message:", response.json())

    return response.json()
