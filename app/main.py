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
SAFE_REPLY = "Could you clarify that again?"

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
# GLOBAL EXCEPTION HANDLER
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
# UNIFIED ENDPOINT
# =====================================================

@app.post("/honeypot")
async def honeypot(
    request: Request,
    _: str = Depends(verify_api_key)
):

    body = await request.json()

    print("\n----- INCOMING REQUEST -----")
    print(body)
    print("----------------------------\n")

    # FINAL CALL (no message field)
    if "message" not in body:

        sid = body.get("sessionId")

        if sid not in sessions:
            return safe_final(sid)

        session = sessions[sid]
        duration = int(time() - session["start_time"])

        response = {
            "sessionId": sid,
            "scamDetected": session["is_scam"],
            "totalMessagesExchanged": session["message_count"],
            "engagementDurationSeconds": duration,
            "extractedIntelligence": session["intelligence"],
            "agentNotes": build_agent_notes(session)
        }

        print("----- FINAL RESPONSE -----")
        print(response)
        print("--------------------------\n")

        return response

    # CONVERSATION TURN
    sid = body["sessionId"]
    text = body["message"]["text"]

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

    response = {
        "status": "success",
        "reply": reply
    }

    print("----- TURN RESPONSE -----")
    print(response)
    print("-------------------------\n")

    return response

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
        "agentNotes": "Safe fallback."
    }

def build_agent_notes(session):
    return (
        f"Conversation completed. Messages={session['message_count']}, "
        f"ScamDetected={session['is_scam']}."
    )