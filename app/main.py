from fastapi import FastAPI, Request, Header, HTTPException, Depends, Response
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException as FastAPIHTTPException
from pydantic import BaseModel
from time import time
import traceback
import os
from typing import Union

from app.inference import predict_labels
from app.extractor import extract_intelligence, merge_intelligence
from app.engagement import generate_engagement_reply

# =====================================================
# CONFIG
# =====================================================

API_KEY = os.getenv("HONEYPOT_API_KEY", "test123")
SAFE_REPLY = "Could you explain that again? I want to follow correctly."

app = FastAPI()

# =====================================================
# AUTH
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

    if isinstance(exc, FastAPIHTTPException):
        raise exc

    traceback.print_exc()

    return JSONResponse(
        status_code=200,
        content={"status": "success", "reply": SAFE_REPLY},
    )


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health():
    return {"status": "ok"}


@app.head("/health")
def health_head():
    return Response(status_code=200)


@app.get("/")
def root():
    return {"message": "Honeypot running"}


# =====================================================
# SESSION STORE
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
    if len(sessions) > MAX_SESSIONS:
        for k in list(sessions.keys())[:50]:
            sessions.pop(k, None)


# =====================================================
# MODELS
# =====================================================

class Message(BaseModel):
    sender: str
    text: str
    timestamp: Union[int, str]  # SPEC FIX


class RequestBody(BaseModel):
    sessionId: str
    message: Message
    conversationHistory: list = []
    metadata: dict = {}


# =====================================================
# HONEYPOT TURN
# =====================================================

@app.post("/honeypot")
def honeypot(req: RequestBody, _: str = Depends(verify_api_key)):

    sid = req.sessionId
    text = req.message.text

    if sid not in sessions:
        sessions[sid] = new_session()

    session = sessions[sid]
    prune_sessions()

    session["message_count"] += 1

    preds = predict_labels(text)

    if preds["is_scam"] == 1:
        session["is_scam"] = True

    intel = extract_intelligence(text)
    session["intelligence"] = merge_intelligence(
        session["intelligence"], intel
    )

    reply = generate_engagement_reply(session, preds)

    return {"status": "success", "reply": reply}


# =====================================================
# FINAL OUTPUT (SPEC EXACT FORMAT)
# =====================================================

@app.post("/final")
def final_output(data: dict, _: str = Depends(verify_api_key)):

    try:
        sid = data["sessionId"]

        if sid not in sessions:
            return safe_final(sid)

        session = sessions[sid]
        duration = int(time() - session["start_time"])

        return {
            "sessionId": sid,
            "scamDetected": session["is_scam"],
            "totalMessagesExchanged": session["message_count"],
            "engagementDurationSeconds": duration,
            "extractedIntelligence": session["intelligence"],
            "agentNotes": build_agent_notes(session)
        }

    except Exception:
        traceback.print_exc()
        return safe_final(data.get("sessionId", "unknown"))


# =====================================================
# SAFE FALLBACK
# =====================================================

def safe_final(sid):
    return {
        "sessionId": sid,
        "scamDetected": False,
        "totalMessagesExchanged": 0,
        "engagementDurationSeconds": 0,
        "extractedIntelligence": {
            "phoneNumbers": [],
            "bankAccounts": [],
            "upiIds": [],
            "phishingLinks": [],
            "emailAddresses": []
        },
        "agentNotes": "Recovered safely from error."
    }


def build_agent_notes(session):
    return (
        f"Conversation completed. Messages={session['message_count']}, "
        f"ScamDetected={session['is_scam']}."
    )