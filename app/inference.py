import os
import joblib
BASE_DIR = os.path.dirname(os.path.dirname(__file__))

vectorizer = joblib.load(os.path.join(BASE_DIR, "models/vectorizer.joblib"))
model = joblib.load(os.path.join(BASE_DIR, "models/classifier.joblib"))

LABELS = [
    "is_scam",
    "asks_payment",
    "impersonation",
    "urgency",
    "reward_scam"
]

print("Models loaded successfully.")


def predict_labels(text: str):

    X = vectorizer.transform([text])
    preds = model.predict(X)[0]

    return dict(zip(LABELS, preds))