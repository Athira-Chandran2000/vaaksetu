---
title: VaakSetu
emoji: 🌉
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# VaakSetu — AI-Assisted Voice Understanding for the 1092 Helpline

> "Bridge of Words" — Ensuring every citizen is heard, understood, and verified in their own language before action is taken.

**VaakSetu** is an intelligent assistive layer for the Karnataka 1092 helpline. It leverages state-of-the-art multilingual AI to bridge the communication gap between citizens and government services, providing real-time interpretation, sentiment analysis, and verified understanding.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    VaakSetu System                          │
│                                                             │
│  ┌──────────┐   ┌──────────────┐   ┌──────────────────┐   │
│  │ Citizen   │──▶│ ASR          │──▶│ Semantic Engine   │   │
│  │ Voice/Text│   │ (Sarvam AI)  │   │ (Groq Llama 3.3)  │   │
│  └──────────┘   └──────────────┘   └────────┬─────────┘   │
│                                              │              │
│  ┌──────────────────────┐   ┌───────────────▼──────────┐  │
│  │ Sentiment Classifier │   │ Multilingual Verification│  │
│  │ (Lexical + Acoustic) │   │ (Restate → Confirm/Deny) │  │
│  └──────────┬───────────┘   └───────────────┬──────────┘  │
│             │                               │              │
│  ┌──────────▼───────────────────────────────▼──────────┐  │
│  │              Agent Dashboard (React)                 │  │
│  │  Interpretation · Sentiment · Verification · CRM    │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─────────────────────────────────────────────────────┐  │
│  │         Real-Time Data Integration Layer             │  │
│  │  Seva Sindhu · BBMP · BWSSB · Bhoomi · Pension      │  │
│  │  Ration Card · 1092 CRM Live Trends                 │  │
│  └─────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.10+** (Backend)
- **Node.js 18+** (Frontend)
- **Groq API Key**: Get a free key from [console.groq.com](https://console.groq.com/)
- **Sarvam AI API Key**: Get a free key from [sarvam.ai](https://www.sarvam.ai/apis) (for audio processing)

### 1. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
# Activate (Windows)
venv\Scripts\activate
# Activate (macOS/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
# Add your GROQ_API_KEY and SARVAM_API_KEY to backend/.env
```

Run the backend:
```bash
python main.py
```
The API will be available at `http://localhost:8000`.

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```
The dashboard will be available at `http://localhost:3000`.

---

## 📋 Key Features

| Feature | Technology | Description |
|---------|------------|-------------|
| **Multilingual ASR** | Sarvam AI (Saaras v3) | Dynamic auto-detection for Kannada, Hindi, and English audio. |
| **Semantic Interpretation** | Groq (Llama 3.3 70B) | Extracts core issues, categories, and entities in < 500ms. |
| **Dynamic Language Sync** | Groq + Sarvam | Automatically responds in the citizen's own script (ಕನ್ನಡ, हिंदी, English) regardless of UI selection. |
| **Verification Loop** | Groq + Heuristics | AI restates the issue in the detected language to ensure accuracy. |
| **Sentiment Analysis** | Local Heuristics | Real-time urgency and distress detection (zero API cost). |
| **Real-Time Data Feeds** | Mock Integrations | Simulated live data from Seva Sindhu, BBMP, BWSSB, and Bhoomi. |
| **Agent Dashbord** | React + Vite | Premium glassmorphism UI with real-time WebSocket updates. |

---

## 🗂️ Project Structure

```
vaaksetu/
├── backend/
│   ├── main.py               # FastAPI server & WebSocket handlers
│   ├── ai_pipeline.py        # Sarvam + Groq orchestration logic
│   ├── models.py             # Pydantic data schemas
│   ├── sentiment.py          # Multilingual sentiment classifier
│   ├── mock_integrations.py  # Simulated government data APIs
│   └── .env                  # API keys and configuration
│
├── frontend/
│   ├── src/
│   │   ├── components/       # UI Components (Dashboard, Cards, etc.)
│   │   ├── hooks/            # Custom React hooks (WebSockets)
│   │   └── index.css         # Design system (Glassmorphism)
│   └── package.json          # Vite/React configuration
│
└── README.md                 # Project documentation
```

---

## 🛡️ Data & Privacy

- **Data Locality**: VaakSetu is designed to run on-premises for government security.
- **Privacy First**: All mock data is anonymized. No citizen PI leaves the secure environment.
- **Multilingual Excellence**: Native script support ensures no loss of meaning during translation.

---

## 📄 License

Built for AI for Bharat Hackathon 2026. All rights reserved.
