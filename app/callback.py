import requests

GUVI_ENDPOINT = "https://hackathon.guvi.in/api/updateHoneyPotFinalResult"


def send_final_result(payload: dict):
    """
    Sends final intelligence to GUVI evaluation server.
    Non-blocking safe call — failures do not break API.
    """

    try:
        print("\n🚀 SENDING FINAL RESULT TO GUVI")
        print(payload)

        response = requests.post(
            GUVI_ENDPOINT,
            json=payload,
            timeout=5
        )

        print("✅ GUVI RESPONSE:", response.status_code, response.text)

    except Exception as e:
        print("❌ GUVI CALLBACK FAILED:", str(e))