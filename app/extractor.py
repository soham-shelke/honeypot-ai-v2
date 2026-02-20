import re

# ---------------- PRECOMPILED REGEX ----------------

PHONE_REGEX = re.compile(
    r"(?:\+91[\-\s]?|0091[\-\s]?|91[\-\s]?)?[6-9]\d{9}\b"
)

UPI_REGEX = re.compile(r"\b[\w.-]+@[\w]+\b")
LINK_REGEX = re.compile(r"https?://\S+")
BANK_REGEX = re.compile(r"\b\d{9,18}\b")
EMAIL_REGEX = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")


# ---------------- NORMALIZATION ----------------

def normalize_phone(number: str):
    """Convert phone numbers to 10-digit Indian format"""
    digits = re.sub(r"\D", "", number)

    if digits.startswith("0091"):
        digits = digits[4:]
    elif digits.startswith("91") and len(digits) == 12:
        digits = digits[2:]

    return digits


# ---------------- EXTRACTION ----------------

def extract_intelligence(text: str):

    phones = PHONE_REGEX.findall(text)
    phones = [normalize_phone(p) for p in phones]

    upi = UPI_REGEX.findall(text)
    links = LINK_REGEX.findall(text)
    banks = BANK_REGEX.findall(text)
    emails = EMAIL_REGEX.findall(text)

    return {
        "phoneNumbers": list(set(phones)),
        "bankAccounts": list(set(banks)),
        "upiIds": list(set(upi)),
        "phishingLinks": list(set(links)),
        "emailAddresses": list(set(emails)),
    }


# ---------------- MERGE SESSION DATA ----------------

def merge_intelligence(old, new):
    """Merge session intelligence uniquely"""

    for key in old.keys():
        old[key] = list(set(old[key] + new[key]))

    return old