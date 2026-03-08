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
| **Deployment** | Vercel |

---

## 🏗️ Architecture Pipeline

### 1. Ingest (Data scrape & process)

**Main source:** `https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund`

Crawl and extract structured scheme data from INDMoney’s HDFC AMC portal. **Data targets (Top 5 HDFC schemes):**

- HDFC Flexi Cap Fund (Flexi-cap Equity)
- HDFC ELSS Tax Saver (ELSS Equity)
- HDFC Mid-Cap Opportunities Fund (Mid-cap Equity)
- HDFC Small Cap Fund (Small-cap Equity)
- HDFC Liquid Fund (Liquid Debt)

Store text chunks and build a **FAISS** index via `build_faiss_db.py` from `vector_store_chunks.json`; optional structured metadata (e.g. `structured_store.csv`).

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

Or from repo root: `npm run dev` (runs the frontend automatically).

By default the frontend uses **built-in stub API routes** (no backend required). To use the FastAPI backend locally, set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend/.env.local` and run the backend as above.

---

## 🧪 Testing

| | Command |
|---|--------|
| **Backend** | `python -m pytest tests/ -v` (9 tests) |
| **Frontend** | `cd frontend && npm test` (apiService + ChatInterface) |
| **Integration** | `python Phase_6_Testing_Deliverables/test_suite.py` (if that folder exists) |

### Build warnings (npm deprecations)

When you run `npm install` in `frontend/` or when Vercel builds, you may see deprecation warnings for `whatwg-encoding`, `inflight`, or `glob`. These come from **transitive dependencies** (Next.js, Jest, ESLint). They do **not** fail the build. The project uses an `overrides` entry for `glob` in `frontend/package.json` to reduce some warnings; the rest can be ignored until upstream packages update.

---

## 🌐 Deployment (Vercel)

**If production shows "Server error" or API calls 404:** Set **Root Directory** to **`frontend`** in Vercel → Project Settings → General, then redeploy. See **[ROOT_CAUSE_ANALYSIS.md](ROOT_CAUSE_ANALYSIS.md)** for full root cause and fix.

### Recommended: Deploy the Next.js app only (frontend)

The production app is the **Next.js frontend** in `frontend/`. It works without the FastAPI backend (stub API routes return placeholder answers). For full RAG, run the FastAPI backend elsewhere and set `NEXT_PUBLIC_API_URL`.

### Fresh project: delete old + create new (exact values)

Use this when you want to delete the existing Vercel project and deploy from scratch.

**Step 1 — Delete the old project (optional)**

1. Go to [Vercel Dashboard](https://vercel.com/dashboard).
2. Open the project you want to remove (e.g. **mutual-fund-genie**).
3. Open **Settings** (top tab).
4. Scroll to **Danger Zone**.
5. Click **Delete Project** and confirm (enter the project name if asked).

**Step 2 — Create a new project**

1. Click **Add New…** → **Project** (or **Import Project**).
2. **Import Git Repository:** choose **GitHub** and select repository **`nikhil1989ramesh-coder/Mutual-Fund-Genie`**. If it’s missing, adjust GitHub App permissions for Vercel and try again.
3. Click **Import**.

**Step 3 — Configure (values to enter)**

Before deploying, set these. Click **Edit** next to each if the defaults differ.

| Field | Value | Notes |
|-------|--------|--------|
| **Project Name** | `mf-genie` or `mutual-fund-genie` | Any name you prefer. |
| **Root Directory** | `frontend` | **Required.** Edit → enter `frontend` (no slash) → Continue. |
| **Framework Preset** | `Next.js` | Should auto-detect. |
| **Build Command** | `npm run build` | Or leave default. |
| **Output Directory** | *(leave default)* | Next.js sets this. |
| **Install Command** | `npm install` | Or leave default. |
| **Node.js Version** | `20.x` or default | 18.x or 20.x both work. |

**Step 4 — Environment variables (optional)**

- For **frontend-only** deploy: leave empty.
- For **full RAG** later: add `GROQ_API_KEY`, optionally `GEMINI_API_KEY`, and `NEXT_PUBLIC_API_URL` (your FastAPI backend URL) under **Settings → Environment Variables**.

**Step 5 — Deploy**

- Click **Deploy**. Wait for the build (about 1–2 minutes).
- Open the **Visit** / **Production URL** when ready.

**Step 6 — Optional:** **Settings → Domains** to add a custom domain.

---

### Steps to get deployment right

1. **Connect the repo**
   - In [Vercel](https://vercel.com): **Add New Project** → Import [GitHub repo](https://github.com/nikhil1989ramesh-coder/Mutual-Fund-Genie).

2. **Set Root Directory (critical)**
   - **Project Settings** → **General** → **Root Directory** → click **Edit**.
   - Set to **`frontend`** (no leading slash). Save.
   - This makes Vercel use `frontend/` as the project root and `frontend/vercel.json` for config. The repo-root `vercel.json` is **not** used when Root Directory is `frontend`.

3. **Build settings (should auto-detect)**
   - **Framework Preset:** Next.js (auto-detected from `frontend/package.json`).
   - **Build Command:** `npm run build` (or leave default).
   - **Output Directory:** leave default (Next.js sets this).
   - **Install Command:** `npm install` (or leave default).

4. **Environment variables (optional)**
   - **Project Settings** → **Environment Variables**
   - Add `GROQ_API_KEY` (and `GEMINI_API_KEY` for fallback) if you later connect a backend.
   - For frontend-only deploy, you don’t need any env vars.

5. **Deploy**
   - Push to `main` or click **Redeploy** in the Vercel dashboard.

### Pre-push checklist

Run before pushing to avoid deploy failures:

```bash
cd frontend && npm run build
cd frontend && npm test
```

Optional (backend tests): `python -m pytest tests/ -v`

### If deployment still fails

| Error | Fix |
|-------|-----|
| **Function Runtimes must have a valid version** | You are not using Root Directory `frontend`. Set **Root Directory** to **`frontend`** so `frontend/vercel.json` is used (no Python runtime). |
| **Function must contain at least one property** | Same as above: use Root Directory **`frontend`**. |
| **Build fails / No package.json** | Root Directory must be **`frontend`**, not repo root. |
| **404 or wrong routes** | Ensure Root Directory is **`frontend`**; the app is served from the Next.js build in `frontend/`. |
| **Unknown server error** | Ensure **Build Command** is exactly **`npm run build`** (not `npm run`). Redeploy after fixing. If it persists, redeploy from the latest code (API routes and apiService were hardened to return JSON on errors). |

### Optional: deploy from repo root (no Root Directory)

If you do **not** set Root Directory, the repo-root `vercel.json` is used. It is configured to run `cd frontend && npm run build` and use `frontend/.next` as output. Prefer using **Root Directory = frontend** for the most reliable builds.

---

## 📚 Appendix (from architecture)

**Target audience** — (1) Retail beginners: educational queries (e.g. “What is a mutual fund?”) from AMFI/SEBI corpus. (2) Professionals/support: factual metrics (expense ratio, AUM, exit load).

**Known limitations** — Scraping AMFI/SEBI can be restricted; some educational content is hard-coded or via aggregators. NAV/AUM are as of the last extraction until the scheduler runs again.

---

## ⚖️ Disclaimer

This project is for **educational purposes only**. It is not SEBI-registered and does not provide financial advice. Always consult official AMC documents before investing.

**Created by [Nikhil Ramesh](https://www.linkedin.com/in/nikhil-ramesh-1b526141/)**
