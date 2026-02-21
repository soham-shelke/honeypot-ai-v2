import random
from app.llm import generate_llm_reply
# -------------------------------------------------
# RESPONSE POOLS (GENERIC — NOT SCENARIO BASED)
# -------------------------------------------------

OPENING_RESPONSES = [
    "I'm not sure I understand yet. Could you explain what happened?",
    "That sounds serious. What should I do first?",
    "I want to resolve this properly. Please guide me step by step."
]

PAYMENT_PROBES = [
    "Before I proceed, can you confirm the payment details again?",
    "Where exactly should I send the payment?",
    "I want to make sure I transfer correctly — can you share the account or UPI once more?"
]

CONTACT_PROBES = [
    "If something goes wrong, how can I contact you directly?",
    "Is there a support number I should keep in case this fails?",
]

LINK_PROBES = [
    "Can you send the official link again so I open the correct page?",
    "Where should I complete the verification? Please share the link."
]

VERIFICATION_PROBES = [
    "Can you confirm your department or employee ID for verification?",
    "Just to be safe, which team are you calling from?"
]

GENERIC_CONTINUE = [
    "Okay, I'm following. What should I do next?",
    "Alright, please continue.",
    "I'm listening — what comes next?"
]


# -------------------------------------------------
# MAIN ENGAGEMENT LOGIC
# -------------------------------------------------

def generate_engagement_reply(session, preds, text):

    turn = session["message_count"]

    # ---- FAST PATH (no LLM) ----
    if turn <= 3:
        return random.choice(OPENING_RESPONSES)

    # ---- USE LLM ONLY SOMETIMES ----
    if turn % 3 == 0:
        try:
            return generate_llm_reply(text)
        except Exception:
            pass  # fallback safely

    # ---- normal probing ----
    if preds.get("asks_payment"):
        return random.choice(PAYMENT_PROBES)

    if not session["intelligence"]["phoneNumbers"]:
        return random.choice(CONTACT_PROBES)

    return random.choice(GENERIC_CONTINUE)