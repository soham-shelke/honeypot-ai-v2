import random
from app.llm import generate_llm_reply

# -------------------------------------------------
# RESPONSE POOLS
# -------------------------------------------------

OPENING = [
    "That sounds serious. What should I do first?",
    "I want to resolve this properly. Please guide me step by step.",
    "Okay, I understand. What should I do now?"
]

PAYMENT_PROBES = [
    "Where exactly should I send the payment?",
    "Can you confirm the payment details again?",
]

CONTACT_PROBES = [
    "If something goes wrong, how can I contact you directly?",
    "Is there a support number I should keep?"
]

LINK_PROBES = [
    "Can you send the verification link again?",
    "Where should I complete this process?"
]

GENERIC = [
    "I'm listening — what comes next?",
    "Alright, please continue.",
    "Okay, I am following."
]


# -------------------------------------------------
# SAFE ENGAGEMENT FUNCTION
# -------------------------------------------------

def generate_engagement_reply(session, preds, text):

    turn = session["message_count"]
    intel = session["intelligence"]

    # ---- early turns (fast deterministic) ----
    if turn <= 2:
        return random.choice(OPENING)

    # ---- selective LLM usage ----
    if turn >= 4 and turn % 4 == 0:
        llm_reply = generate_llm_reply(text)
        if isinstance(llm_reply, str) and llm_reply.strip():
            return llm_reply

    # ---- intelligence probing ----
    if not intel["phoneNumbers"]:
        return random.choice(CONTACT_PROBES)

    if not intel["phishingLinks"]:
        return random.choice(LINK_PROBES)

    if preds.get("asks_payment"):
        return random.choice(PAYMENT_PROBES)

    # ---- ALWAYS SAFE FALLBACK ----
    return random.choice(GENERIC)