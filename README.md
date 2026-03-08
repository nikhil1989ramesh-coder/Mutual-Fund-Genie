# 🏦 MF Genie — HDFC Mutual Fund AI Assistant

A RAG-powered chatbot that answers factual questions about the **top 5 HDFC Mutual Fund schemes** using only official AMC, AMFI, and SEBI sources. Zero hallucinations. Zero financial advice.

---

## 🚀 Key Features

- **Facts-Only Answering** — strictly uses official HDFC AMC, AMFI, and SEBI factsheets
- **Strict Constraints** — blocks PII (PAN, Aadhaar, Account Numbers), competitor funds, and investment advice
- **Fast Responses** — Groq **Llama-3.1-8b-instant**, in-memory RAG chunks, smaller prompts, and an in-memory response cache for repeat queries
- **Optional Fallback** — when Groq is rate-limited or unavailable, can use **Gemini 1.5 Flash** if `GEMINI_API_KEY` is set
- **Premium Next.js UI** — dark-themed, HDFC-branded, responsive chat with scroll-to-results and clear error handling
- **Automated Data Freshness** — APScheduler pipeline for periodic NAV/AUM/Expense Ratio updates

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Groq — Llama-3.1-8b-instant (optional fallback: Gemini 1.5 Flash) |
| **Vector DB** | FAISS + `sentence-transformers/all-MiniLM-L6-v2` (chunks loaded in memory) |
| **Backend** | FastAPI (Python 3.10+) |
| **Frontend** | Next.js 15 (React 19) |
| **Automation** | APScheduler |
| **Testing** | pytest (backend), Jest + React Testing Library (frontend) |
| **Deployment** | Vercel |

---

## 📂 Project Structure

```
├── Phase_1_Data_Ingestion/     # Scrapers for ET Money, Groww, SEBI
├── Phase_2_Knowledge_Base/     # Chunking, processing, FAISS build (build_faiss_db.py), vector_store_chunks.json
├── Phase_3_Query_Generation/   # RAG agent (retrieve + Groq/Gemini), in-memory cache
├── Phase-4_Backend_API/        # FastAPI endpoints (chat, FAQ), lifespan + scheduler
├── Phase_5_Scheduler/          # APScheduler for periodic data refresh
├── frontend/                   # Next.js 15 Application
│   ├── src/
│   │   ├── app/                # App Router (layout.js, page.js, globals.css)
│   │   ├── components/         # ChatInterface.js, FAQSection.js
│   │   └── lib/                # apiService.js, apiService.test.js
│   ├── jest.config.cjs        # Jest + jsdom for unit tests
│   └── package.json
├── tests/                      # pytest test_api.py (9 API tests)
├── api/                        # Vercel serverless entry (optional)
├── vercel.json
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
Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Optional (for fallback when Groq is rate-limited or unavailable):

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ⚡ Performance & Response Speed

- **In-memory chunks:** FAISS metadata and `vector_store_chunks.json` are loaded once at startup (and on scheduler reload); no disk read per query.
- **Smaller retrieval:** `top_k=6` chunks and a 2,400-character context cap keep prompts small so the LLM responds faster.
- **Response cache:** Up to 80 recent answers are cached by query text; repeat or near-identical questions return instantly.
- **Groq settings:** `max_tokens=280`, timeout 18s; optional Gemini 1.5 Flash fallback after retries on 429 or connection errors.

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
python -m pytest tests/ -v
```
Runs all 9 API tests (chat, FAQ, validation, docs).

### Frontend Tests (Jest)
```bash
cd frontend
npm test
```
Runs apiService and ChatInterface failure-mode tests.

### Integration / Constraint Tests (optional)
If `Phase_6_Testing_Deliverables` exists:
```bash
python Phase_6_Testing_Deliverables/test_suite.py
```

---

## 🌐 Deployment (Vercel)

> **Note**: Deploy only when instructed.

This repo is ready to push to GitHub and deploy on Vercel after you run the checks below.

### Pre-push checklist (run locally)
1. **Backend tests**: `python -m pytest tests/ -v` → all 9 tests pass  
2. **Frontend tests**: `cd frontend && npm test` → all 9 tests pass  
3. **Frontend build**: `cd frontend && npm run build` → build succeeds  

### Vercel setup
- Connect the repo from [GitHub](https://github.com/nikhil1989ramesh-coder/Mutual-Fund-Genie) (or your fork).
- Set **Root Directory** to `frontend` so Next.js builds and serves the app.
- Add environment variable: `GROQ_API_KEY` (for any serverless API that calls Groq).
- Optional: if you use the serverless `api/` for health/echo, leave `api/` not in `.vercelignore`; for full RAG you run the FastAPI backend elsewhere and point the frontend `NEXT_PUBLIC_API_URL` to it.

---

## ⚖️ Disclaimer

This project is for **educational purposes only**. It is NOT SEBI-registered and does not provide financial advice. Always consult official AMC documents before investing.

**Created by [Nikhil Ramesh](https://www.linkedin.com/in/nikhil-ramesh-1b526141/)**
