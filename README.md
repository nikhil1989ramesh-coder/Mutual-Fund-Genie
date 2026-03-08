# 🏦 MF Genie — HDFC Mutual Fund AI Assistant

A RAG-powered chatbot that answers factual questions about the **top 5 HDFC Mutual Fund schemes** using only official AMC, AMFI, and SEBI sources. Zero hallucinations. Zero financial advice.

---

## 📋 Project Overview

| | |
|---|---|
| **Product scope** | INDMoney |
| **Target AMC** | HDFC Mutual Fund |
| **Objective** | Facts-only, RAG-based FAQ assistant for **retail beginners** (e.g. “What is a mutual fund?”) and **professionals** (e.g. expense ratio, AUM). Uses only official public sources; no investment advice. |

**Corpus (verified public URLs):** ET Money & Groww factsheets for the top 5 schemes (Flexi Cap, ELSS Tax Saver, Mid-Cap Opportunities, Small Cap, Liquid Fund); AMFI NAV/master data; SEBI circulars; AMFI knowledge centre for educational content. See `architecture.md` for the full URL list.

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
| **Deployment** | Vercel |

---

## 🏗️ Architecture Pipeline

### 1. Ingest (Data scrape & process)

Crawl and extract structured scheme data from INDMoney’s HDFC AMC portal for the **top 5 schemes**. Store text chunks and build a **FAISS** index via `build_faiss_db.py` from `vector_store_chunks.json`; optional structured metadata (e.g. `structured_store.csv`).

### 2. Retrieve (Search & context)

User query → embedding with `sentence-transformers/all-MiniLM-L6-v2` → similarity search on the **in-memory** FAISS index (`top_k=6`). Chunks are loaded once at startup (and on scheduler reload); context is capped at 2,400 characters.

### 3. Generate (LLM response)

**Groq** (`llama-3.1-8b-instant`, `max_tokens=280`, 18s timeout) with optional **Gemini 1.5 Flash** fallback. Up to 80 recent answers cached by query. Rules: context-only, top-5 HDFC only, ≤3 sentences, no advice, no PII; every answer ends with *"Last updated from sources: &lt;sources&gt;"*.

### 4. Chat app (Frontend + backend)

- **Frontend:** Next.js 15 — ChatInterface, FAQSection, apiService; scroll-to-results and error banners.
- **Backend:** FastAPI `/api/chat` (POST) and `/api/faq` (GET); CORS enabled. Returns `{ answer, sources }`.

### 5. Scheduler (Data freshness)

APScheduler runs in the FastAPI lifespan; periodically triggers ingest/rebuild and hot-reloads the FAISS index and in-memory chunks.

---

## 📂 Project Structure

```
├── Phase_1_Data_Ingestion/     # Scrapers for ET Money, Groww, SEBI
├── Phase_2_Knowledge_Base/     # Chunking, FAISS build (build_faiss_db.py), vector_store_chunks.json
├── Phase_3_Query_Generation/   # RAG agent (retrieve + Groq/Gemini), in-memory cache
├── Phase-4_Backend_API/        # FastAPI (chat, FAQ), lifespan + scheduler
├── Phase_5_Scheduler/          # APScheduler
├── frontend/                   # Next.js 15 (app/, components/, lib/, API routes)
├── tests/                      # pytest test_api.py (9 API tests)
├── api/                        # Optional Vercel serverless stub
├── architecture.md             # Full architecture and corpus URLs
├── vercel.json
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

---

## 🧪 Testing

| | Command |
|---|--------|
| **Backend** | `python -m pytest tests/ -v` (9 tests) |
| **Frontend** | `cd frontend && npm test` (apiService + ChatInterface) |
| **Integration** | `python Phase_6_Testing_Deliverables/test_suite.py` (if that folder exists) |

---

## 🌐 Deployment (Vercel)

- Connect the repo ([GitHub](https://github.com/nikhil1989ramesh-coder/Mutual-Fund-Genie)); set **Root Directory** to **`frontend`**.
- Optional: `GROQ_API_KEY` (and `GEMINI_API_KEY` for fallback). For full RAG, run the FastAPI backend elsewhere and set `NEXT_PUBLIC_API_URL`.

**Pre-push:** Run `python -m pytest tests/ -v`, `cd frontend && npm test`, and `cd frontend && npm run build`.

---

## 📚 Appendix (from architecture)

**Target audience** — (1) Retail beginners: educational queries (e.g. “What is a mutual fund?”) from AMFI/SEBI corpus. (2) Professionals/support: factual metrics (expense ratio, AUM, exit load).

**Known limitations** — Scraping AMFI/SEBI can be restricted; some educational content is hard-coded or via aggregators. NAV/AUM are as of the last extraction until the scheduler runs again.

---

## ⚖️ Disclaimer

This project is for **educational purposes only**. It is not SEBI-registered and does not provide financial advice. Always consult official AMC documents before investing.

**Created by [Nikhil Ramesh](https://www.linkedin.com/in/nikhil-ramesh-1b526141/)**
