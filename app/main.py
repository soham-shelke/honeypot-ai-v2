from fastapi import FastAPI
from pydantic import BaseModel
from time import time

from app.inference import predict_labels
from app.extractor import extract_intelligence, merge_intelligence

from app.engagement import generate_engagement_reply

app = FastAPI(json_loads=None, json_dumps=None)
# ---------------- SESSION MEMORY ----------------

sessions = {}
MAX_SESSIONS = 500

def new_session():
    return {
        "start_time": time(),
        "message_count": 0,
        "is_scam": False,
        "intelligence": {
            "phoneNumbers": [],
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "emailAddresses": []
        }
    }

# ---------------- REQUEST MODELS ----------------

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int

class RequestBody(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: list = []
    metadata: dict = {}

def prune_sessions():
    """Prevent memory growth"""
    if len(sessions) > MAX_SESSIONS:
        oldest = list(sessions.keys())[:50]
        for k in oldest:
            sessions.pop(k, None)

# ---------------- HONEYPOT TURN ----------------

@app.post("/honeypot")
def honeypot(req: RequestBody):

    session_id = req.sessionId
    text = req.message.text

    if session_id not in sessions:
        sessions[session_id] = new_session()

    session = sessions[session_id]
    prune_sessions()
    # update counters
    session["message_count"] += 1

    # ML prediction
    preds = predict_labels(text)

    if preds["is_scam"] == 1:
        session["is_scam"] = True

    # Extract intelligence
    intel = extract_intelligence(text)
    session["intelligence"] = merge_intelligence(
        session["intelligence"], intel
    )

    # Honeypot reply (keeps engagement alive)
    reply = generate_engagement_reply(session, preds)

    return {
        "status": "success",
        "reply": reply
    }

# ---------------- FINAL CALLBACK ----------------

@app.post("/final")
def final_output(data: dict):

    session_id = data["sessionId"]

    if session_id not in sessions:
        return {"error": "Session not found"}

    session = sessions[session_id]

    duration = int(time() - session["start_time"])

    final_json = {
        "sessionId": session_id,
        "scamDetected": session["is_scam"],
        "totalMessagesExchanged": session["message_count"],
        "extractedIntelligence": session["intelligence"],
        "engagementMetrics": {
            "engagementDurationSeconds": duration,
            "messageCount": session["message_count"]
        },
        "agentNotes": build_agent_notes(session)
    }

    return final_json



def build_agent_notes(session):
    return (
        "Automated honeypot interaction completed. "
        f"Messages={session['message_count']}, "
        f"ScamDetected={session['is_scam']}."
    )