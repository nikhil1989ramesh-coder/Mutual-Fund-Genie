# 🏦 MF Genie — HDFC Mutual Fund AI Assistant

A RAG-powered chatbot that answers factual questions about the **top 5 HDFC Mutual Fund schemes** using only official AMC, AMFI, and SEBI sources. Zero hallucinations. Zero financial advice.

---

## 🚀 Key Features

- **Facts-Only Answering** — strictly uses official HDFC AMC, AMFI, and SEBI factsheets
- **Strict Constraints** — blocks PII (PAN, Aadhaar, Account Numbers), competitor funds, and investment advice
- **Ultra-Fast** — powered by **Groq (Llama-3.3-70b-versatile)** for sub-second responses
- **Premium Next.js UI** — dark-themed, HDFC-branded, glassomorphism design with animated chat
- **Automated Data Freshness** — APScheduler pipeline for daily NAV/AUM/Expense Ratio updates

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq — Llama-3.3-70b-versatile |
| **Vector DB** | FAISS + `sentence-transformers/all-MiniLM-L6-v2` |
| **Backend** | FastAPI (Python 3.10+) |
| **Frontend** | **Next.js 16 (React 19)** |
| **Automation** | APScheduler |
| **Deployment** | Vercel |

---

## 📂 Project Structure

```
├── Phase_1_Data_Ingestion/     # Scrapers for ET Money, Groww, SEBI
├── Phase_2_Knowledge_Base/     # Chunking, processing, FAISS build
├── Phase_3_Query_Generation/   # RAG agent + persona management
├── Phase-4_Backend_API/        # FastAPI endpoints (chat, FAQ)
│   └── test_api.py             # pytest API test suite
├── Phase_5_Scheduler/          # APScheduler for daily data refresh
├── Phase-6_Testing_Deliverables/ # Integration test suite
├── frontend/                   # Next.js 16 Application
│   └── src/
│       ├── app/                # Next.js App Router
│       │   ├── layout.js       # Root layout + SEO metadata
│       │   ├── page.js         # Main page (orchestrates components)
│       │   └── globals.css     # HDFC-branded design system
│       ├── components/
│       │   ├── ChatInterface.js # Chat UI with message bubbles
│       │   └── FAQSection.js   # Dynamic FAQ sidebar
│       └── lib/
│           └── apiService.js   # API client for backend communication
├── api/
│   └── index.py                # Vercel entry point for FastAPI
├── vercel.json                 # Vercel build & routing config
└── requirements.txt
```

---

## ⚙️ Setup & Installation

### 1. Prerequisites
- Python 3.10+
- Node.js 18+
- A **Groq API Key** from [console.groq.com](https://console.groq.com)

### 2. Python Environment
```bash
pip install -r requirements.txt
```

### 3. Frontend Dependencies
```bash
cd frontend
npm install
```

### 4. Environment Variables
Create a `.env` file in the root:
```env
GROQ_API_KEY=your_groq_api_key_here
```

---

## 🏃 Running Locally

### Step 1: Initialize the Knowledge Base (one-time)
```bash
python Phase_1_Data_Ingestion/scraper.py
python Phase_2_Knowledge_Base/processor.py
python Phase_2_Knowledge_Base/build_faiss_db.py
```

### Step 2: Start the Backend (FastAPI + Scheduler)
```bash
python Phase-4_Backend_API/main.py
```
API will be available at `http://localhost:8000`.

### Step 3: Start the Next.js Frontend
```bash
cd frontend
npm run dev
```
Frontend will be available at **`http://localhost:3000`**.

---

## 🧪 Testing

### Backend API Tests (pytest)
```bash
python -m pytest Phase-4_Backend_API/test_api.py -v
```

### Integration / Constraint Tests
```bash
python Phase-6_Testing_Deliverables/test_suite.py
```

---

## 🌐 Deployment (Vercel)

> **Note**: Do not deploy until explicitly instructed.

This repo is configured for **Vercel** deployment from the `main` branch of:
[`https://github.com/nikhil1989ramesh-coder/Mutual-Fund-Genie`](https://github.com/nikhil1989ramesh-coder/Mutual-Fund-Genie)

Before deploying, add these environment variables in Vercel's dashboard:
- `GROQ_API_KEY` — your Groq API key

---

## ⚖️ Disclaimer

This project is for **educational purposes only**. It is NOT SEBI-registered and does not provide financial advice. Always consult official AMC documents before investing.

**Created by [Nikhil Ramesh](https://www.linkedin.com/in/nikhil-ramesh-1b526141/)**
