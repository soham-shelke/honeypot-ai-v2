import random
import csv

OUTPUT = "../dataset/train.csv"

scam_templates = [
    ("Your SBI account blocked. Pay Rs {amt} via {upi} now",1,1,1,1,0),
    ("KYC expired update immediately at {link}",1,0,1,1,0),
    ("You won lottery of Rs {amt}! claim now",1,0,0,1,1),
    ("Electricity bill pending pay using {upi}",1,1,0,1,0),
    ("I am from bank support verify account urgently",1,0,1,1,0),
    ("Crypto investment doubles money fast",1,1,0,0,1),
    ("Refund approved share bank account {bank}",1,1,0,0,0),
]

legit_templates = [
    "Meeting tomorrow at college",
    "Please send notes",
    "Lunch at 2pm?",
    "Project submission extended",
    "Happy birthday!",
    "Assignment deadline updated"
]

def generate_scam():
    text, *labels = random.choice(scam_templates)

    text = text.format(
        amt=random.choice([1000,2500,5000]),
        upi=random.choice(["raj@okaxis","help@ybl"]),
        link="http://verify-now.co",
        bank="123456789012"
    )

    return [text] + labels

def generate_legit():
    return [random.choice(legit_templates),0,0,0,0,0]

def main():
    header = [
        "text",
        "is_scam",
        "asks_payment",
        "impersonation",
        "urgency",
        "reward_scam"
    ]

    rows = []

    for _ in range(800):
        rows.append(generate_scam())

    for _ in range(600):
        rows.append(generate_legit())

    random.shuffle(rows)

    with open(OUTPUT,"w",newline="",encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

    print("Dataset ready.")

if __name__ == "__main__":
    main()