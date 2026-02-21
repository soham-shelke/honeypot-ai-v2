import re

# -------------------------------------------------
# REGEX DEFINITIONS
# -------------------------------------------------

# Phone numbers (supports +91, spaces, dashes)
PHONE_REGEX = re.compile(
    r"(?:\+?\d{1,3}[-\s]?)?[6-9]\d{9}"
)

UPI_REGEX = re.compile(r"\b[\w.-]+@[\w]+\b")
LINK_REGEX = re.compile(r"https?://\S+")

# Bank accounts: long digit sequences ONLY
BANK_REGEX = re.compile(r"\b\d{9,18}\b")

EMAIL_REGEX = re.compile(r"\b[\w\.-]+@[\w\.-]+\.\w+\b")


# -------------------------------------------------
# EXTRACTION
# -------------------------------------------------

def extract_intelligence(text: str):

    # -------- phones ----------
    phones = PHONE_REGEX.findall(text)

    # last 10 digits of phones
    phone_core_numbers = {
        re.sub(r"\D", "", p)[-10:]
        for p in phones
    }

    # -------- bank accounts ----------
    raw_banks = BANK_REGEX.findall(text)

    banks = []

    for b in raw_banks:
        # compare using last 10 digits
        if b[-10:] not in phone_core_numbers:
            banks.append(b)

    upi = UPI_REGEX.findall(text)
    links = LINK_REGEX.findall(text)
    emails = EMAIL_REGEX.findall(text)

    return {
        "phoneNumbers": list(set(phones)),
        "bankAccounts": list(set(banks)),
        "upiIds": list(set(upi)),
        "phishingLinks": list(set(links)),
        "emailAddresses": list(set(emails)),
    }

# -------------------------------------------------
# MERGE SESSION DATA
# -------------------------------------------------

def merge_intelligence(old, new):
    for key in old.keys():
        old[key] = list(set(old[key] + new[key]))
    return old