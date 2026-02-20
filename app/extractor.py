import re

# -------------------------------------------------
# PRECOMPILED REGEX (GENERIC — REQUIRED BY SPEC)
# -------------------------------------------------

PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-\s]?)?[6-9]\d{9}"
)

UPI_REGEX = re.compile(r"\b[\w.-]+@[\w]+\b")
LINK_REGEX = re.compile(r"https?://\S+")
BANK_REGEX = re.compile(r"\b\d{9,18}\b")
EMAIL_REGEX = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")


# -------------------------------------------------
# EXTRACTION
# -------------------------------------------------

def extract_intelligence(text: str):

    phones = PHONE_REGEX.findall(text)
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


# -------------------------------------------------
# SESSION MERGE
# -------------------------------------------------

def merge_intelligence(old, new):
    for key in old.keys():
        old[key] = list(set(old[key] + new[key]))
    return old