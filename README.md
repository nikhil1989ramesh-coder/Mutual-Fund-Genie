# 🏦 MF Genie — HDFC Mutual Fund AI Assistant

A RAG-powered chatbot that answers factual questions about the **top 5 HDFC Mutual Fund schemes** using only official AMC, AMFI, and SEBI sources. Zero hallucinations. Zero financial advice.

---

## 📋 Project Overview

| | |
|---|---|
| **Product scope** | INDMoney |
| **Target AMC** | HDFC Mutual Fund |
| **Objective** | Facts-only, RAG-based FAQ assistant for **retail beginners** (e.g. “What is a mutual fund?”) and **professionals** (e.g. expense ratio, AUM). Uses only official public sources; no investment advice. |

**Corpus (11 verified, stable URLs — tested 200 OK):**

- **HDFC Flexi Cap Fund**
  1. `https://www.etmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/15694` (Detailed Factsheet/Overview)
  2. `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth` (Key Metrics & Ratios)
- **HDFC ELSS Tax Saver**
  3. `https://www.etmoney.com/mutual-funds/hdfc-elss-tax-saver-direct-plan-growth/15698` (Detailed Factsheet/Overview)
- **HDFC Mid-Cap Opportunities Fund**
  4. `https://www.etmoney.com/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-plan-growth/15684` (Detailed Factsheet/Overview)
  5. `https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth` (Key Metrics & Ratios)
- **HDFC Liquid Fund**
  6. `https://www.etmoney.com/mutual-funds/hdfc-liquid-fund-direct-plan-growth/15682` (Detailed Factsheet/Overview)
  7. `https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth` (Key Metrics & Ratios)
- **HDFC Small Cap Fund**
  8. `https://www.etmoney.com/mutual-funds/hdfc-small-cap-fund-direct-plan-growth/15690` (Detailed Factsheet/Overview)
  9. `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` (Key Metrics & Ratios)
- **Official master data & guidelines (educational corpus)**
  10. `https://www.amfiindia.com/spages/NAVAll.txt` (Live AMFI Master NAV — data freshness)
  11. `https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=13&smid=0` (SEBI Mutual Fund Circulars)
  12. `https://www.amfiindia.com/investor#knowledge-centre` (AMFI: What is a Mutual Fund — educational baseline)

---

## 🔒 Key Constraints / Rules of Operation

1. **Public sources only** — Answers are derived only from verified public sources (AMC, AMFI, SEBI). No internal screenshots or third-party blogs.
2. **No PII** — The system refuses to accept, store, or process PII (PAN, Aadhaar, account numbers, OTPs, emails, phone numbers).
3. **No performance claims** — It does not compute, predict, or compare mutual fund performance/returns; it declines and links to the official factsheet.
4. **Clarity** — Answers are at most 3 sentences and end with *"Last updated from sources: &lt;sources&gt;"*.

---

## 🚀 Key Features

- **Facts-only answering** — Strictly from official HDFC AMC, AMFI, and SEBI factsheets.
- **Strict constraints** — Blocks PII, competitor funds, and investment advice.
- **Fast responses** — Groq **Llama-3.1-8b-instant**, in-memory RAG chunks, smaller prompts, and an in-memory response cache for repeat queries.
- **Optional fallback** — When Groq is rate-limited or unavailable, can use **Gemini 1.5 Flash** if `GEMINI_API_KEY` is set.
- **Next.js UI** — Dark, HDFC-themed, responsive chat with scroll-to-results and clear error handling.
- **Data freshness** — APScheduler for periodic NAV/AUM/expense updates.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **LLM** | Groq — Llama-3.1-8b-instant (optional fallback: Gemini 1.5 Flash) |
| **Vector DB** | FAISS + `sentence-transformers/all-MiniLM-L6-v2` (chunks in memory) |
| **Backend** | FastAPI (Python 3.10+) |
| **Frontend** | Next.js 15 (React 19) |
| **Automation** | APScheduler |
| **Testing** | pytest (backend), Jest + React Testing Library (frontend) |
| **Deployment** | Streamlit Cloud (RAG chat), Vercel (Next.js frontend); see below. |

---

## 🏗️ Architecture Pipeline

### 1. Ingest (Data scrape & process)

**Main source:** `https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund`

Crawl and extract structured scheme data from INDMoney’s HDFC AMC portal. This feeds the RAG pipeline used by the **Backend API** for chat/query; the **frontend** shows answers with **citations** and **error handling**. **Data targets (Top 5 HDFC schemes):**

- HDFC Flexi Cap Fund (Flexi-cap Equity)
- HDFC ELSS Tax Saver (ELSS Equity)
- HDFC Mid-Cap Opportunities Fund (Mid-cap Equity)
- HDFC Small Cap Fund (Small-cap Equity)
- HDFC Liquid Fund (Liquid Debt)

Store text chunks and build a **FAISS** index via `build_faiss_db.py` from `vector_store_chunks.json`; optional structured metadata (e.g. `structured_store.csv`).

### 2. Retrieve (Search & context)

User query → embedding with `sentence-transformers/all-MiniLM-L6-v2` → similarity search on the **in-memory** FAISS index (`top_k=6`). Used by the **Backend API** for chat/query; **frontend** displays results with **citations** and **error handling**. Chunks are loaded once at startup (and on scheduler reload); context is capped at 2,400 characters.

### 3. Generate (LLM response)

**Groq** (`llama-3.1-8b-instant`, `max_tokens=280`, 18s timeout) with optional **Gemini 1.5 Flash** fallback. **Backend API** returns `{ answer, sources }`; **frontend chat UI** shows **citations** (Sources) and **error handling** (banners). Up to 80 recent answers cached by query. Rules: context-only, top-5 HDFC only, ≤3 sentences, no advice, no PII; every answer ends with *"Last updated from sources: &lt;sources&gt;"*.

### 4. Chat app (Frontend + backend)

- **Backend API for chat/query:** All chat messages and FAQ requests go to the **Backend API** when `NEXT_PUBLIC_API_URL` is set (e.g. `http://localhost:8000`). FastAPI exposes `/api/chat` (POST) and `/api/faq` (GET); CORS enabled. Returns `{ answer, sources }` for every response.
- **Frontend chat UI with citations and error handling:** Next.js 15 — ChatInterface, FAQSection, apiService. Displays each answer with **citations** (Sources section, clickable links from `sources` and inline URLs). **Error handling:** error banner for server/network failures, server-busy message, validation errors; scroll-to-results after response or error.

### 5. Scheduler (Data freshness)

APScheduler runs in the FastAPI lifespan; periodically triggers ingest/rebuild and hot-reloads the FAISS index and in-memory chunks. **Backend API** chat/query then uses updated data; **frontend** continues to show **citations** and **error handling** for all responses.

---

## 📂 Project Structure

```
├── Phase_1_Data_Ingestion/     # Scrapers for ET Money, Groww, SEBI; extracted_corpus.json
├── Phase_2_Knowledge_Base/     # Chunking, FAISS build (build_faiss_db.py), vector_store_chunks.json
├── Phase_3_Query_Generation/   # RAG agent (retrieve + Groq/Gemini), in-memory cache
├── Phase-4_Backend_API/        # FastAPI (chat, FAQ), lifespan + scheduler
├── Phase_5_Scheduler/          # APScheduler
├── frontend/                   # Next.js 15 (app/, components/, lib/, pages/api/)
├── tests/                      # pytest test_api.py (9 API tests)
├── scripts/                    # test_vercel_frontend.py, test_deployed_backends.py (deployment tests)
├── streamlit_app.py            # Streamlit Cloud entry (RAG chat UI)
├── Procfile                    # Railway: uvicorn start for FastAPI
├── architecture.md             # Full architecture and corpus URLs
├── ACTIVITIES.md               # Step-by-step: local run, Streamlit Cloud, full stack, tests
├── DEPLOY_STREAMLIT.md         # Streamlit deploy guide
└── requirements.txt
```

---

## ⚙️ Setup & Installation

**Prerequisites:** Python 3.10+, Node.js 18+, [Groq API key](https://console.groq.com).

```bash
pip install -r requirements.txt
cd frontend && npm install
```

Create a `.env` in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

Optional (fallback when Groq is rate-limited):

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

---

## ⚡ Performance & Response Speed

- **In-memory chunks** — No disk read per query; FAISS + chunks loaded at startup and on scheduler reload.
- **Smaller retrieval** — `top_k=6`, 2,400-character context cap.
- **Response cache** — Up to 80 recent answers by query text.
- **Groq** — `max_tokens=280`, 18s timeout; optional Gemini fallback.

---

## 🏃 Running Locally

**One-time: build knowledge base**

```bash
python Phase_1_Data_Ingestion/scraper.py
python Phase_2_Knowledge_Base/processor.py
python Phase_2_Knowledge_Base/build_faiss_db.py
```

**Backend** (FastAPI + scheduler): `http://localhost:8000`

```bash
python Phase-4_Backend_API/main.py
```

**Frontend:** `http://localhost:3000`

```bash
cd frontend && npm run dev
```

Or from repo root: `npm run dev` (runs the frontend automatically).

By default the frontend uses **built-in stub API routes** (no backend required). To use the FastAPI backend locally, set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` and run the backend as above.

---

## 🧪 Testing

| | Command |
|---|--------|
| **Backend** | `python -m pytest tests/ -v` (9 tests) |
| **Frontend** | `cd frontend && npm test` (apiService + ChatInterface) |

### Build warnings (npm deprecations)

When you run `npm install` in `frontend/`, you may see deprecation warnings for `whatwg-encoding`, `inflight`, or `glob`. These come from **transitive dependencies** (Next.js, Jest, ESLint). They do **not** fail the build. The project uses an `overrides` entry for `glob` in `frontend/package.json` to reduce some warnings; the rest can be ignored until upstream packages update.

---

## 🌐 Deployment

**Live deployments (integrated):**

| App | URL |
|-----|-----|
| **Backend (RAG chat)** | [https://nikhil-ramesh-ai-mfgenie.streamlit.app](https://nikhil-ramesh-ai-mfgenie.streamlit.app) — full RAG Q&A with citations |
| **Frontend (Next.js)** | [https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app](https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app) — chat UI (stub API or set `NEXT_PUBLIC_API_URL` for FastAPI) |

- **Streamlit:** Main file `streamlit_app.py`, branch `main`; see **[DEPLOY_STREAMLIT.md](DEPLOY_STREAMLIT.md)**. For detailed steps (local, Streamlit Cloud, full stack, tests) see **[ACTIVITIES.md](ACTIVITIES.md)**.
- **Vercel:** Root Directory = `frontend`; optional env `NEXT_PUBLIC_API_URL` for a FastAPI backend (e.g. Railway). Push to `main` triggers redeploy.
- **Railway (FastAPI backend):** See **[DEPLOY_RAILWAY.md](DEPLOY_RAILWAY.md)** for step-by-step deployment and Vercel integration.

**Test deployed frontend/backend:**

```bash
python scripts/test_vercel_frontend.py
python scripts/test_deployed_backends.py
```

---

## 📚 Appendix (from architecture)

**Target audience** — (1) Retail beginners: educational queries (e.g. “What is a mutual fund?”) from AMFI/SEBI corpus. (2) Professionals/support: factual metrics (expense ratio, AUM, exit load).

**Known limitations** — Scraping AMFI/SEBI can be restricted; some educational content is hard-coded or via aggregators. NAV/AUM are as of the last extraction until the scheduler runs again.

---

## ⚖️ Disclaimer

This project is for **educational purposes only**. It is not SEBI-registered and does not provide financial advice. Always consult official AMC documents before investing.

**Created by [Nikhil Ramesh](https://www.linkedin.com/in/nikhil-ramesh-1b526141/)**
