import random

# ---------------- HUMAN-LIKE RESPONSE POOLS ----------------

EARLY_STAGE = [
    "I'm not fully understanding yet. Could you guide me step by step?",
    "I'm new to this process. Please explain what I should do first.",
    "Okay, I want to resolve this. What should I do now?"
]

ASK_UPI = [
    "I want to complete the payment. Can you confirm the UPI ID?",
    "Before paying, please share the UPI details again.",
    "Can you send the UPI ID so I can transfer correctly?"
]

ASK_BANK = [
    "Could you provide the bank account number for the transfer?",
    "I may use bank transfer instead — can you share account details?",
]

ASK_LINK = [
    "Please send the official link where I should complete this.",
    "Where exactly should I update the details? Share the link please.",
]

ASK_PHONE = [
    "If something goes wrong, which number should I contact?",
    "Can I have a contact number in case payment fails?",
]

IMP_VERIFICATION = [
    "Can you confirm your employee ID for verification?",
    "Which department are you calling from exactly?",
]

REWARD_PROBE = [
    "Is any processing fee required before receiving the reward?",
    "Do I need to pay anything to claim this prize?",
]

FALLBACK = [
    "Okay, please explain the next step clearly.",
    "I'm following. What should I do after that?",
    "Alright, continue please."
]


def pick(options):
    """Deterministic-safe random choice"""
    return random.choice(options)


def generate_engagement_reply(session, preds):

    intel = session["intelligence"]
    msg_count = session["message_count"]

    # -------- EARLY CONVERSATION --------
    if msg_count < 3:
        return pick(EARLY_STAGE)

    # -------- INTELLIGENCE TARGETING --------
    if preds["asks_payment"] and not intel["upiIds"]:
        return pick(ASK_UPI)

    if preds["asks_payment"] and not intel["bankAccounts"]:
        return pick(ASK_BANK)

    if preds["urgency"] and not intel["phishingLinks"]:
        return pick(ASK_LINK)

    if not intel["phoneNumbers"]:
        return pick(ASK_PHONE)

    if preds["impersonation"]:
        return pick(IMP_VERIFICATION)

    if preds["reward_scam"]:
        return pick(REWARD_PROBE)

    return pick(FALLBACK)