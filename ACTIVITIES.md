# Detailed Steps to Perform Activities

This document gives **step-by-step instructions** for running the MF Genie app locally (Streamlit or full stack) and deploying the backend on **Streamlit Cloud**.

---

## Command Prompt (Windows) — Copy-paste command sequence

If you use **Command Prompt** on Windows, you can run the commands below in order. Replace the path in **Step 1** with your actual project folder if different.

**Activity 1 — Run Streamlit locally**

```cmd
cd /d "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant"
python -m venv .venv
call .venv\Scripts\activate.bat
pip install -r requirements.txt
python Phase_1_Data_Ingestion\scraper.py
python Phase_2_Knowledge_Base\processor.py
python Phase_2_Knowledge_Base\build_faiss_db.py
streamlit run streamlit_app.py
```

*(Before running Streamlit, create a `.env` file in the project root with `GROQ_API_KEY=your_key` and optionally `GEMINI_API_KEY=your_key`. Stop Streamlit with Ctrl+C.)*

**Activity 3 — Run full stack (backend + frontend)**  
*Terminal 1 (backend):*

```cmd
cd /d "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant"
call .venv\Scripts\activate.bat
python Phase-4_Backend_API\main.py
```

*Terminal 2 (frontend):*

```cmd
cd /d "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant\frontend"
npm install
npm run dev
```

*(Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend\.env.local` so the frontend uses the backend.)*

**Activity 4 — Run tests**

```cmd
cd /d "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant"
call .venv\Scripts\activate.bat
python -m pytest tests\ -v
cd frontend
npm test
```

---

## Prerequisites

Before starting, ensure you have:

| Requirement | How to check |
|-------------|--------------|
| **Python 3.10+** | `python --version` or `py -3 --version` (Windows) |
| **Node.js 18+** (only for Next.js frontend) | `node --version` |
| **Git** | `git --version` |
| **Groq API key** | Get from [console.groq.com](https://console.groq.com) |
| **Gemini API key** (optional) | Get from [aistudio.google.com](https://aistudio.google.com) |

---

## Activity 1: Run the Streamlit App Locally

The Streamlit app is a chat UI that uses the same RAG backend (Phase 3) as the FastAPI API. It shows **citations** (Sources) and **error handling**.

### Step 1.1 — Open the project folder

- Open **Command Prompt** (Win+R → type `cmd` → Enter) or any terminal.
- Go to the project root (where `streamlit_app.py` and `requirements.txt` are).

  **Command Prompt (Windows):**

  ```cmd
  cd /d "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant"
  ```

  *(Use `cd /d` if the project is on a different drive; replace the path with your actual project path.)*

  **PowerShell:**

  ```powershell
  cd "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant"
  ```

  **Mac/Linux:**

  ```bash
  cd /path/to/Build\ RAG\ Chat\ bot\ for\ Mutual\ fund\ assistant
  ```

### Step 1.2 — Create and activate a virtual environment (recommended)

**Command Prompt (Windows):**

```cmd
python -m venv .venv
call .venv\Scripts\activate.bat
```

**PowerShell (Windows):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Mac/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` in the prompt.

### Step 1.3 — Install Python dependencies

From the **project root** (with venv activated in Command Prompt):

**Command Prompt / PowerShell / Bash:**

```cmd
pip install -r requirements.txt
```

This installs FastAPI, Streamlit, sentence-transformers, FAISS, and the rest. The first run may take a few minutes (e.g. downloading PyTorch and the embedding model).

### Step 1.4 — Build the knowledge base (one-time)

The RAG agent needs two files in `Phase_2_Knowledge_Base/`:

- `faiss_index.bin` — FAISS vector index  
- `vector_store_chunks.json` — Text chunks

Run these three commands from the **project root** (one per line in Command Prompt):

**Command Prompt (Windows):**

```cmd
python Phase_1_Data_Ingestion\scraper.py
python Phase_2_Knowledge_Base\processor.py
python Phase_2_Knowledge_Base\build_faiss_db.py
```

**PowerShell / Bash (forward slashes work too):**

```bash
python Phase_1_Data_Ingestion/scraper.py
python Phase_2_Knowledge_Base/processor.py
python Phase_2_Knowledge_Base/build_faiss_db.py
```

- **Scraper:** Fetches data from INDMoney/HDFC sources.  
- **Processor:** Produces chunks and writes `vector_store_chunks.json`.  
- **Build FAISS:** Builds `faiss_index.bin` from that JSON.

If these files already exist, you can skip this step or re-run to refresh data.

### Step 1.5 — Set environment variables (API keys)

Create or edit a `.env` file in the **project root** (same folder as `streamlit_app.py`):

```env
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```

- `GROQ_API_KEY` is **required** for the LLM.  
- `GEMINI_API_KEY` is **optional** (used if Groq fails).

Do not commit `.env` to Git (it should be in `.gitignore`).

### Step 1.6 — Run the Streamlit app

From the **project root** (venv activated):

**Command Prompt / PowerShell / Bash:**

```cmd
streamlit run streamlit_app.py
```

- The app starts at **http://localhost:8501**.  
- Your browser may open automatically; if not, open that URL.  
- Type a question (e.g. “What is the exit load for HDFC Flexi Cap?”) or click a suggested question.  
- Answers show with a **Sources** expander (citations). Errors show in a red banner.

### Step 1.7 — Stop the app

In the terminal, press **Ctrl+C** to stop Streamlit.

---

## Activity 2: Deploy the Backend on Streamlit Cloud

Streamlit Cloud hosts your app and gives you a public URL. Follow these steps exactly.

### Step 2.1 — Push your code to GitHub

1. Ensure your project is a Git repo and pushed to GitHub (e.g. `nikhil1989ramesh-coder/Mutual-Fund-Genie`).
2. Ensure the branch you want to deploy (e.g. `main`) has:
   - `streamlit_app.py` at the **repo root**
   - `requirements.txt` at the repo root (with `streamlit` in it)

### Step 2.2 — Sign in to Streamlit Cloud

1. Open **[share.streamlit.io](https://share.streamlit.io)** in your browser.  
2. Click **Sign in** and sign in with **GitHub**.  
3. Authorize the Streamlit Cloud app to access your GitHub account if asked.

### Step 2.3 — Create a new app

1. Click **New app**.  
2. You may be asked to **authorize your GitHub account** or **install the Streamlit Cloud GitHub App** for your user/org. Complete that if prompted.  
3. In **Create a new app**:
   - **Repository:** Select your repo (e.g. `nikhil1989ramesh-coder/Mutual-Fund-Genie`).  
   - **Branch:** `main` (or the branch you use).  
   - **Main file path:** Type `streamlit_app.py` (must be the path from repo root).  
   - **App URL:** Optional; leave default to get a URL like `https://your-app-name.streamlit.app`.  
4. Leave **Advanced settings** collapsed for now (we’ll use it only if you add a “run before app” step).

### Step 2.4 — Add secrets (API keys)

Streamlit Cloud does not use your local `.env`. You must add secrets in the dashboard.

1. After creating the app (or open an existing app), go to **Settings** (gear icon or **Manage app** → **Settings**).  
2. Open **Secrets**.  
3. Add key-value pairs. You can use **TOML** or the simple editor:

   **Option A — TOML format:**

   ```toml
   GROQ_API_KEY = "your_groq_api_key_here"
   GEMINI_API_KEY = "your_gemini_api_key_here"
   ```

   **Option B — Simple form:**  
   Add two secrets:  
   - Name: `GROQ_API_KEY`, Value: your Groq API key  
   - Name: `GEMINI_API_KEY`, Value: your Gemini API key (optional)

4. **Save**. Streamlit Cloud will expose these as environment variables to your app.

### Step 2.5 — Provide the knowledge base (FAISS + chunks)

The RAG agent needs `Phase_2_Knowledge_Base/faiss_index.bin` and `Phase_2_Knowledge_Base/vector_store_chunks.json`. They are in `.gitignore` by default. Choose one of these:

**Option A — Commit the files (simplest)**

1. Locally, run the pipeline once (Activity 1, Step 1.4) so the two files exist.  
2. Temporarily allow them to be committed (e.g. force-add or remove from `.gitignore` for these two files only).  
3. Commit and push.

   **Command Prompt (Windows):**

   ```cmd
   git add Phase_2_Knowledge_Base\faiss_index.bin Phase_2_Knowledge_Base\vector_store_chunks.json
   git commit -m "Add FAISS index and chunks for Streamlit Cloud"
   git push origin main
   ```

   **Bash / PowerShell:**

   ```bash
   git add Phase_2_Knowledge_Base/faiss_index.bin Phase_2_Knowledge_Base/vector_store_chunks.json
   git commit -m "Add FAISS index and chunks for Streamlit Cloud"
   git push origin main
   ```

4. Streamlit Cloud will then have the files on the next deploy.

**Option B — Build on deploy (advanced)**

1. In Streamlit Cloud: **Settings** → **Advanced settings**.  
2. Under **Run before your app starts**, add a command that builds the knowledge base, for example:

   ```bash
   python Phase_1_Data_Ingestion/scraper.py && python Phase_2_Knowledge_Base/processor.py && python Phase_2_Knowledge_Base/build_faiss_db.py
   ```

3. Ensure `requirements.txt` includes everything needed (scraper, processor, build_faiss_db).  
4. The first deploy will be slower; subsequent deploys may still re-run this unless you use caching.

### Step 2.6 — Deploy

1. Click **Deploy** (or **Redeploy** if the app already exists).  
2. Wait for the build to finish. The log will show `pip install -r requirements.txt` and then starting the app.  
3. When it says **Your app is live**, open the app URL (e.g. `https://your-app-name.streamlit.app`).

### Step 2.7 — Verify

1. Open the app URL.  
2. Ask a question (e.g. “What is a mutual fund?”).  
3. Confirm you get an answer with a **Sources** section.  
4. If you see an error (e.g. missing index or API key), check **Secrets** and that the knowledge base files are present (Option A or B above).

---

## Activity 3: Run the Full Stack Locally (FastAPI + Next.js)

Use this when you want the **Next.js frontend** talking to the **FastAPI backend** on your machine.

### Step 3.1 — Build the knowledge base (if not done)

Same as Activity 1, Step 1.4.

**Command Prompt (Windows):**

```cmd
python Phase_1_Data_Ingestion\scraper.py
python Phase_2_Knowledge_Base\processor.py
python Phase_2_Knowledge_Base\build_faiss_db.py
```

**Bash / PowerShell:**

```bash
python Phase_1_Data_Ingestion/scraper.py
python Phase_2_Knowledge_Base/processor.py
python Phase_2_Knowledge_Base/build_faiss_db.py
```

### Step 3.2 — Start the FastAPI backend

From the **project root** (venv activated).

**Command Prompt (Windows):**

```cmd
python Phase-4_Backend_API\main.py
```

**Bash / PowerShell:**

```bash
python Phase-4_Backend_API/main.py
```

- Backend runs at **http://localhost:8000**.  
- API docs: **http://localhost:8000/docs**.  
- Keep this terminal open.

### Step 3.3 — Configure the frontend to use the backend

1. In the `frontend` folder, create or edit **`frontend\.env.local`** (Windows) or `frontend/.env.local`.  
2. Add this line (no quotes around the value):

   ```env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Save the file.

### Step 3.4 — Install frontend dependencies and run the frontend

**Option A — From repo root (if you have root `package.json`):**

```cmd
npm run dev
```

**Option B — From frontend folder:**

**Command Prompt (Windows):**

```cmd
cd frontend
npm install
npm run dev
```

**Bash / PowerShell:**

```bash
cd frontend
npm install
npm run dev
```

- Frontend runs at **http://localhost:3000**.  
- Open it in the browser; chat messages will go to the FastAPI backend. Answers will show **citations** and **error handling** in the UI.

### Step 3.5 — Stop servers

- In the backend terminal: **Ctrl+C**.  
- In the frontend terminal: **Ctrl+C**.

---

## Activity 4: Run Tests

### Backend (pytest)

From the **project root** with venv activated.

**Command Prompt (Windows):**

```cmd
python -m pytest tests\ -v
```

**Bash / PowerShell:**

```bash
python -m pytest tests/ -v
```

You should see 9 tests pass.

### Frontend (Jest)

**Command Prompt (Windows):**

```cmd
cd frontend
npm test
```

**Bash / PowerShell:**

```bash
cd frontend
npm test
```

Or from repo root: `cd frontend && npm test`.  
You should see the apiService and ChatInterface tests pass.

---

## Quick Reference

**Command Prompt (Windows) — from project root with venv activated:**

| Goal | Command |
|------|---------|
| Go to project folder | `cd /d "C:\Users\Nikhil Ramesh\Desktop\Build RAG Chat bot for Mutual fund assistant"` |
| Activate venv | `call .venv\Scripts\activate.bat` |
| Install Python deps | `pip install -r requirements.txt` |
| Build knowledge base | `python Phase_1_Data_Ingestion\scraper.py` then `processor.py` then `build_faiss_db.py` |
| Run Streamlit | `streamlit run streamlit_app.py` |
| Run FastAPI backend | `python Phase-4_Backend_API\main.py` |
| Run Next.js frontend | `cd frontend` then `npm install` then `npm run dev` |
| Backend tests | `python -m pytest tests\ -v` |
| Frontend tests | `cd frontend` then `npm test` |

**All environments:**

| Goal | Command / Action |
|------|-------------------|
| Deploy on Streamlit Cloud | Share.streamlit.io → New app → Main file `streamlit_app.py` → add Secrets → provide KB → Deploy |
| Point frontend to backend | Set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `frontend\.env.local` |

---

*For more on Streamlit-only deployment, see [DEPLOY_STREAMLIT.md](DEPLOY_STREAMLIT.md).*
