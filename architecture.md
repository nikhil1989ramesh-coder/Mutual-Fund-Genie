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

### 5. Header Visual Polish
- **[MODIFY] Logo**: Position the `🏦` and `🧞` emojis vertically within the gradient box.
- **[MODIFY] Typography**: Ensure font weights and colors match the reference image (bold white title, muted subtitle).

### 6. Section & Content Polish
- **[MODIFY] Header**: Remove `🧞` from the logo.
- **[MODIFY] Icons**: Use `📈` for Schemes, `🏢` for About, `🎓` for Basics, and `💡` for Suggested.
- **[MODIFY] ChatInterface**: Rephrase welcome instructions as requested.
- **[MODIFY] Alignment**: Refine Laptop (1024px-1365px) grid and margins for visual balance.
- **[MODIFY] Live Badge**: Add `@keyframes` for a blinking green dot (`.status-dot`).

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
  - Store chunks in a **Vector Store** (e.g., ChromaDB, FAISS) for similarity search.
  - Optional: Store structured metadata (like exact numerical fees or categories) in an **Optional Structured Store** (e.g., SQLite or Pandas DataFrame/Dicts) for direct filtering.

### 2. Retrieve Phase (Search & Context Fetching)
**Action:** Find the most relevant facts based on the user's question.
- **Input:** User sends a query (e.g., "What is the exit load for HDFC Flexi Cap?").
- **Embedding:** Convert the user's query text into a vector embedding using the same model used during ingestion.
- **Similarity Search:** Search the Vector Store to find the `top-k` most contextually similar data chunks.
- **Optional Filtering:** (If using a structured store) filter chunks by scheme name or category before similarity search to ensure maximum accuracy.
- **Output:** The `top-k` chunks representing the factual context.

### 3. Generate Phase (LLM Response Creation)
**Action:** Formulate the final answer using strictly the retrieved context via the Groq API.
- **Provider & Model:** Utilize **Groq** as the Large Language Model engine for ultra-fast generation.
- **Input:** `User Query` + `top-k Retrieved Chunks` sent to the Groq LLM.
- **Prompt Constraints (Strict Execution):**
  - **Context-Only Answering:** The Chatbot MUST NOT answer any question from its own pre-trained knowledge. It must strictly use *only* the information retrieved from the embeddings. If the answer is not in the embeddings, it must state it does not know.
  - **Scope Limitation (Top 5 Only):** If a user asks about any mutual fund scheme, bank, or AMC *other* than the predefined Top 5 HDFC schemes (Flexi Cap, ELSS, Mid-Cap, Small Cap, Liquid), the LLM must strictly refuse to answer and state: `"I only have access to information regarding the top 5 HDFC mutual fund schemes."`
  - **Persona Adaptability:** The system prompt must instruct the LLM to provide simple, clear answers for beginners (e.g., explaining "what is a mutual fund?" using the AMFI educational corpus) while maintaining precision for professionals asking about expense ratios or AUM.
  - **Factual & Concise:** Ensure the response is factual and ≤ 3 sentences.
  - **No Investment Advice:** Refuse any subjective, predictive, or advice-seeking queries (e.g., "Should I buy?", "Is this a good fund?") and trigger a polite refusal message with an educational link (W1 constraint).
  - **PII Refusal (Out of Scope):** The chatbot must strictly refuse to answer or process any questions asking for or providing Personal Identifiable Information (PAN, Aadhaar, account numbers, etc.), stating it is out of scope.
- **Output Assembly:** LLM generates the final constrained answer. 
- **Citation formatting:** The system appends the exact source URL metadata to the generated text, ending with: *"Last updated from sources: <date>"*.

### 4. Chat App (Frontend to Backend Integration)
**Action:** The user interface layer connecting to the RAG pipeline.
- **Frontend Interaction:** The user interface (web app, Streamlit, etc.) captures user messages and displays responses.
- **Backend Flow (API):** 
  -## Phase 4 — Visual Polish (Header)
- [x] Refine header logo with stacked emojis (Bank + Genie).
- [x] Ensure "LIVE" badge and subtitle alignment match reference image.

## Phase 5 — Content & Alignment Refinement
- [x] Remove Genie logo from header (keep Bank).
- [x] Add specific icons for each section (Schemes, About, Basics, Suggested).
- [x] Update welcome instructions with exact rephrased wording.
- [/] Fix laptop viewport alignment for section accuracy.
- [ ] Add blinking green dot to "Live" badge.
nd **Generate** steps.
- **Response delivery:** The backend returns the constructed answer, complete with strict citations/sources, back to the frontend to be displayed.

### 5. Scheduler (Data Freshness Optimization)
**Action:** Keep facts up to date against INDMoney/HDFC source changes.
- **Execution:** Implement a scheduled cron job or background task (e.g., Celery, APScheduler, or a simple recurring Python script).
- **Update Cycle:** The scheduler periodically triggers the **Ingest** script.
- **Impact:** Ensures the Chat App always retrieves and generates answers using the most current NAVs, AUMs, or fee structures without manual intervention.

---

## 📚 Appendix

### A. Target Audience & Personas
- **Retail Beginners:** Everyday users comparing mutual fund schemes. The chatbot is designed to handle educational baseline queries like *"What is a mutual fund?"* by retrieving explicit, non-jargon definitions directly from the injected AMFI/SEBI corpus.
- **Professionals & Support Teams:** Content/support staff answering repetitive MF questions. The chatbot handles strict factual inquiries based on the scraped metrics like Expense Ratios, AUM, and Exit Loads to maintain accuracy at scale.

### B. Known Limitations & Constraints
- **Bot Protection & 404s:** Direct scraping against official AMFI and SEBI knowledge-center URLs is heavily restricted and error-prone. Critical educational data must sometimes be strictly hard-coded or queried via aggregators.
- **Real-Time NAV Variations:** The NAV and AUM metrics reflected by the Chatbot are strictly based on the extraction timestamp. Intraday fluctuations are not reflected until the Phase 5 Scheduler triggers a new sync.
