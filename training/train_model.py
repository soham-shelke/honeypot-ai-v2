import pandas as pd
import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.multiclass import OneVsRestClassifier
from sklearn.linear_model import LogisticRegression

DATA_PATH = "../dataset/train.csv"

LABELS = [
    "is_scam",
    "asks_payment",
    "impersonation",
    "urgency",
    "reward_scam"
]

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

X = df["text"]
y = df[LABELS]

print("Training TF-IDF...")
vectorizer = TfidfVectorizer(
    max_features=3000,
    ngram_range=(1,2)
)

X_vec = vectorizer.fit_transform(X)

print("Training classifier...")
model = OneVsRestClassifier(
    LogisticRegression(max_iter=1000)
)

model.fit(X_vec, y)

print("Saving models...")
joblib.dump(vectorizer, "../models/vectorizer.joblib")
joblib.dump(model, "../models/classifier.joblib")

print("Training complete.")