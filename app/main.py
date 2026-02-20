from fastapi import FastAPI, Request, Header, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from pydantic import BaseModel
from time import time
import traceback
import os

from app.inference import predict_labels
from app.extractor import extract_intelligence, merge_intelligence
from app.engagement import generate_engagement_reply

# =====================================================
# CONFIG
# =====================================================

API_KEY = os.getenv("HONEYPOT_API_KEY", "test123")
SAFE_REPLY = "I want to proceed correctly. Could you explain once more?"

app = FastAPI(json_loads=None, json_dumps=None)

# =====================================================
# AUTHENTICATION
# =====================================================

def verify_api_key(
    x_api_key: str | None = Header(default=None, alias="x-api-key")
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")


# =====================================================
# GLOBAL CRASH PROTECTION
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    # Allow authentication + HTTP errors normally
    if isinstance(exc, FastAPIHTTPException):
        raise exc

    print("⚠️ Exception caught:")
    traceback.print_exc()

    return JSONResponse(
        status_code=200,
        content={
            "status": "success",
            "reply": SAFE_REPLY
        },
    )


# =====================================================
# HEALTH ENDPOINTS (Render + UptimeRobot)
# =====================================================

@app.get("/health")
def health_get():
    return {
        "status": "ok",
        "service": "honeypot-ai",
        "modelLoaded": True
    }


@app.head("/health")
def health_head():
    return Response(status_code=200)


@app.get("/")
def root():
    return {"message": "Honeypot AI API running"}


# =====================================================
# SESSION MEMORY
# =====================================================

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


def prune_sessions():
    """Prevent memory growth"""
    if len(sessions) > MAX_SESSIONS:
        oldest = list(sessions.keys())[:50]
        for k in oldest:
            sessions.pop(k, None)


# =====================================================
# REQUEST MODELS
# =====================================================

class Message(BaseModel):
    sender: str
    text: str
    timestamp: int


class RequestBody(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: list = []
    metadata: dict = {}


# =====================================================
# HONEYPOT TURN ENDPOINT
# =====================================================

@app.post("/honeypot")
def honeypot(
    req: RequestBody,
    _: str = Depends(verify_api_key)
):

    session_id = req.sessionId
    text = req.message.text

    if session_id not in sessions:
        sessions[session_id] = new_session()

    session = sessions[session_id]
    prune_sessions()

    # update message count
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

    # Engagement reply
    reply = generate_engagement_reply(session, preds)

    return {
        "status": "success",
        "reply": reply
    }


# =====================================================
# FINAL CALLBACK ENDPOINT
# =====================================================

@app.post("/final")
def final_output(
    data: dict,
    _: str = Depends(verify_api_key)
):

    try:
        session_id = data["sessionId"]

        if session_id not in sessions:
            return safe_empty_final(session_id)

        session = sessions[session_id]
        duration = int(time() - session["start_time"])

        return {
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

    except Exception:
        traceback.print_exc()
        return safe_empty_final(data.get("sessionId", "unknown"))


# =====================================================
# SAFE FALLBACK FINAL RESPONSE
# =====================================================

def safe_empty_final(session_id: str):
    return {
        "sessionId": session_id,
        "scamDetected": False,
        "totalMessagesExchanged": 0,
        "extractedIntelligence": {
            "phoneNumbers": [],
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "emailAddresses": []
        },
        "engagementMetrics": {
            "engagementDurationSeconds": 0,
            "messageCount": 0
        },
        "agentNotes": "Safe fallback response."
    }


def build_agent_notes(session):
    return (
        "Automated honeypot interaction completed. "
        f"Messages={session['message_count']}, "
        f"ScamDetected={session['is_scam']}."
    )