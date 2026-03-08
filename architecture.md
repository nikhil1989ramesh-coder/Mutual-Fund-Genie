# RAG-based Mutual Fund FAQ Chatbot - Architecture Document

## Project Overview
- **Product Scope:** INDMoney
- **Target AMC:** HDFC Mutual Fund
- **Objective:** Build a facts-only, RAG-based FAQ assistant targeting both **retail beginners** (comparing schemes, asking educational questions like "what is a mutual fund?") and **professionals/support teams** (answering repetitive factual questions). It strictly uses official public sources and avoids investment advice.
- **Corpus (11 Verified, Stable URLs - Tested 200 OK):**
  - **HDFC Flexi Cap Fund:**
    1. `https://www.etmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth/15694` (Detailed Factsheet/Overview)
    2. `https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth` (Key Metrics & Ratios)
  - **HDFC ELSS Tax Saver:**
    3. `https://www.etmoney.com/mutual-funds/hdfc-elss-tax-saver-direct-plan-growth/15698` (Detailed Factsheet/Overview)
  - **HDFC Mid-Cap Opportunities Fund:**
    4. `https://www.etmoney.com/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-plan-growth/15684` (Detailed Factsheet/Overview)
    5. `https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth` (Key Metrics & Ratios)
  - **HDFC Liquid Fund:**
    6. `https://www.etmoney.com/mutual-funds/hdfc-liquid-fund-direct-plan-growth/15682` (Detailed Factsheet/Overview)
    7. `https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth` (Key Metrics & Ratios)
  - **HDFC Small Cap Fund:**
    8. `https://www.etmoney.com/mutual-funds/hdfc-small-cap-fund-direct-plan-growth/15690` (Detailed Factsheet/Overview)
    9. `https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth` (Key Metrics & Ratios)
  - **Official Master Data & Guidelines (Educational Corpus):**
    10. `https://www.amfiindia.com/spages/NAVAll.txt` (Live AMFI Master NAV Document - For Data Freshness)
    11. `https://www.sebi.gov.in/sebiweb/home/HomeAction.do?doListing=yes&sid=3&ssid=13&smid=0` (SEBI Mutual Fund Circulars)
    12. `https://www.amfiindia.com/investor#knowledge-centre` (AMFI: What is a Mutual Fund - Educational Baseline)

---

## 🔒 Key Constraints / Rules of Operation
1. **Public Sources ONLY:** All answers must be strictly derived from verified public sources (AMC, AMFI, SEBI). The chatbot will **not** use internal back-end app screenshots or third-party blogs as sources.
2. **Strict NO PII Policy:** The system will explicitly refuse to accept, store, or process Personally Identifiable Information (PAN, Aadhaar, account numbers, OTPs, emails, or phone numbers).
3. **No Performance Claims:** The chatbot will not compute, predict, or compare mutual fund performance/returns. If asked about performance, it must politely decline and link the user to the official factsheet.
4. **Clarity & Transparency:** Every generated answer is restricted to a maximum of 3 sentences and must include the explicit suffix: *"Last updated from sources: <sources>"*.

---

## 🏗️ Architecture Pipeline

### 1. Ingest Phase (Data Scrape & Process)
**Action:** Crawl and extract structured scheme data from INDMoney's HDFC AMC portal.
- **Source:** `https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund`
- **Data Targets (Top 5 HDFC Schemes):** Extract structured data specifically for:
  - HDFC Flexi Cap Fund (Flexi-cap Equity)
  - HDFC ELSS Tax Saver (ELSS Equity)
  - HDFC Mid-Cap Opportunities Fund (Mid-cap Equity)
  - HDFC Small Cap Fund (Small-cap Equity)
  - HDFC Liquid Fund (Liquid Debt)
- **Extraction Scope:** Pull factual data like Expense Ratio, Exit Load, Minimum SIP, Riskometer, Benchmark, AUM, and NAV for each scheme.
- **Storage:** 
  - Embed the extracted data blocks as text chunks representing each scheme's facts.
  - Store chunks in a **Vector Store** — **FAISS** (`build_faiss_db.py` builds the index from `vector_store_chunks.json`). ChromaDB is not used.
  - Optional: Store structured metadata (e.g. `structured_store.csv`) for reference.

### 2. Retrieve Phase (Search & Context Fetching)
**Action:** Find the most relevant facts based on the user's question.
- **Input:** User sends a query (e.g., "What is the exit load for HDFC Flexi Cap?").
- **Embedding:** Convert the user's query text into a vector embedding using `sentence-transformers/all-MiniLM-L6-v2` (same model as ingestion).
- **Similarity Search:** Search the in-memory FAISS index for the **top-k** most similar chunks (`top_k=6` for faster, smaller prompts).
- **In-Memory Chunks:** Chunk text is loaded once at startup (and on scheduler reload) from `vector_store_chunks.json`; no disk read per request.
- **Context Cap:** Combined context is limited to 2,400 characters to keep prompts small and responses fast.
- **Output:** The top-k chunks (and optional metadata sources) passed to the Generate phase.

### 3. Generate Phase (LLM Response Creation)
**Action:** Formulate the final answer using strictly the retrieved context.
- **Primary Provider:** **Groq** — model `llama-3.1-8b-instant`; `max_tokens=280`, timeout 18s.
- **Optional Fallback:** If Groq returns 429 (rate limit) or a connection error after retries, the system can call **Gemini 1.5 Flash** when `GEMINI_API_KEY` is set.
- **Response Cache:** Up to 80 recent (answer, sources) pairs are cached by normalized query text; repeat queries return immediately without calling the LLM.
- **Input:** `User Query` + capped retrieved context sent to the LLM.
- **Prompt Constraints (Strict Execution):**
  - **Context-Only Answering:** The Chatbot MUST NOT answer from its own knowledge; use *only* the retrieved context. If the answer is not in the context, state it does not know.
  - **Scope Limitation (Top 5 Only):** Refuse questions about schemes/AMCs other than the Top 5 HDFC schemes; state: `"I only have access to information regarding the top 5 HDFC mutual fund schemes."`
  - **Persona Adaptability:** Simple, clear answers for beginners; precise metrics for professionals.
  - **Factual & Concise:** Response ≤ 3 sentences; no investment advice; no PII.
- **Citation:** Every answer ends with *"Last updated from sources: <sources>"*.

### 4. Chat App (Frontend to Backend Integration)
**Action:** The user interface layer connecting to the RAG pipeline.
- **Frontend:** Next.js 15 app (React 19) — `ChatInterface`, `FAQSection`, `apiService`; dark HDFC-themed UI, responsive layout, scroll-to-results after each response, and clear error banners for server-busy or network failures.
- **Backend API (Phase-4_Backend_API):** FastAPI exposes `/api/chat` (POST) and `/api/faq` (GET). Each request runs the full **Retrieve** and **Generate** pipeline (or returns a cached response). CORS enabled for the frontend.
- **Response delivery:** The backend returns `{ answer, sources }`; the frontend displays the answer with source links and citations.

### 5. Scheduler (Data Freshness Optimization)
**Action:** Keep facts up to date against INDMoney/HDFC source changes.
- **Execution:** APScheduler (Phase_5_Scheduler) runs as part of the FastAPI app lifespan.
- **Update Cycle:** The scheduler periodically triggers the ingest/rebuild pipeline; on completion it calls a reload callback to hot-reload the FAISS index and in-memory chunks.
- **Impact:** The Chat App uses the latest NAVs, AUMs, and fee structures without manual intervention.

---

## ✅ UI & Content Checklist (Implemented)

- [x] Header: Bank logo only; "LIVE" badge with blinking green dot (`.status-dot`).
- [x] Section icons: 📈 Schemes, 🏢 About, 🎓 Basics, 💡 Suggested.
- [x] Welcome instructions and scroll-to-results behavior.
- [x] Laptop/tablet/mobile responsive grid and alignment.

---

## 🧪 Testing

- **Backend:** `tests/test_api.py` — pytest; 9 tests covering `/api/chat` (valid, empty, whitespace, missing field, internal error), `/api/faq` (list + fallback), and `/docs` / `/openapi.json`.
- **Frontend:** Jest (apiService + ChatInterface) — 9 tests covering success/error paths, server-busy banner, and network failure handling.

---

## 📚 Appendix

### A. Target Audience & Personas
- **Retail Beginners:** Everyday users comparing mutual fund schemes. The chatbot is designed to handle educational baseline queries like *"What is a mutual fund?"* by retrieving explicit, non-jargon definitions directly from the injected AMFI/SEBI corpus.
- **Professionals & Support Teams:** Content/support staff answering repetitive MF questions. The chatbot handles strict factual inquiries based on the scraped metrics like Expense Ratios, AUM, and Exit Loads to maintain accuracy at scale.

### B. Known Limitations & Constraints
- **Bot Protection & 404s:** Direct scraping against official AMFI and SEBI knowledge-center URLs is heavily restricted and error-prone. Critical educational data must sometimes be strictly hard-coded or queried via aggregators.
- **Real-Time NAV Variations:** The NAV and AUM metrics reflected by the Chatbot are strictly based on the extraction timestamp. Intraday fluctuations are not reflected until the Phase 5 Scheduler triggers a new sync.
