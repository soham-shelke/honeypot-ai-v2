import requests
import os

LLM_URL = os.getenv("LLM_ENDPOINT")
LLM_KEY = os.getenv("LLM_KEY")


def generate_llm_reply(message: str):

    payload = {
        "prompt": f"""
You are a cautious but cooperative user speaking to customer support.
Keep responses short (1 sentence).
Do NOT reveal suspicion.
Ask clarifying questions naturally.

Message:
{message}
"""
    }

    r = requests.post(
        LLM_URL,
        json=payload,
        headers={"Authorization": f"Bearer {LLM_KEY}"},
        timeout=2.0  # HARD latency cap
    )

    return r.json()["text"]