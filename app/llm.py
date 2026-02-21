import requests
import os

LLM_URL = os.getenv("LLM_ENDPOINT")
LLM_KEY = os.getenv("LLM_KEY")


def generate_llm_reply(message: str):

    # If no LLM configured → skip silently
    if not LLM_URL:
        return None

    try:
        payload = {
            "prompt": f"""
You are a cooperative user talking to customer support.
Respond naturally in ONE short sentence.
Do not mention scams or suspicion.

Message:
{message}
"""
        }

        headers = {}
        if LLM_KEY:
            headers["Authorization"] = f"Bearer {LLM_KEY}"

        response = requests.post(
            LLM_URL,
            json=payload,
            headers=headers,
            timeout=1.5,  # latency protection
        )

        data = response.json()

        # Support common response formats
        if isinstance(data, dict):

            if "text" in data:
                return data["text"]

            if "response" in data:
                return data["response"]

            if "choices" in data:
                return data["choices"][0].get("text")

    except Exception as e:
        print("LLM FAILED:", e)

    return None