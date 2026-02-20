# 🛡️ Agentic Honeypot Scam Detection & Intelligence Extraction API

Submission for **India AI Impact Buildathon — Honeypot Challenge (Round 2)**

---

## 🚀 Overview

This project implements a **low-latency agentic honeypot system** that:

- Detects scam conversations using an internally trained ML model
- Engages scammers strategically
- Extracts actionable intelligence
- Returns structured intelligence JSON for automated evaluation

⚠️ No external AI APIs are used.

All intelligence is generated using a lightweight, reproducible ML pipeline.

---

## 🧠 System Architecture


Incoming Message
↓
TF-IDF Vectorizer
↓
Multi-Label Classifier (Logistic Regression)
↓
Intelligence Extractor (Regex Engine)
↓
Engagement Strategy Engine
↓
Structured Honeypot Response


---

## ⚡ Key Features

✅ Internal ML model (scikit-learn)  
✅ Ultra-low latency (<20ms inference)  
✅ Deterministic intelligence extraction  
✅ Stateful conversation agent  
✅ Evaluation-compliant output format  
✅ Fully reproducible training pipeline  

---

## 📂 Repository Structure


honeypot-ai-v2/
│
├── dataset/ # generated training data
├── training/ # dataset + training scripts
├── models/ # saved ML models
├── app/
│ ├── main.py # FastAPI server
│ ├── inference.py # ML inference
│ ├── extractor.py # intelligence extraction
│ └── engagement.py # agent logic


---

## 🏃 Quick Start

### 1️⃣ Create environment

```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
2️⃣ Generate dataset
cd training
python generate_dataset.py
3️⃣ Train model
python train_model.py
4️⃣ Run API
uvicorn app.main:app --host 0.0.0.0 --port 8000

API Docs:

http://127.0.0.1:8000/docs