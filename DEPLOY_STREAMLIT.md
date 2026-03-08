# Deploy Backend (RAG) on Streamlit Cloud

The Streamlit app (`streamlit_app.py`) runs the same RAG backend used by the FastAPI API: it uses the **Backend API** logic (Phase 3 RAG agent) and shows **citations** (Sources) and **error handling** in the UI.

**For detailed step-by-step instructions** (including prerequisites, virtual env, building the knowledge base, and Streamlit Cloud deploy), see **[ACTIVITIES.md](ACTIVITIES.md)**.

## Run locally

From the **repo root**:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Open http://localhost:8501. Ensure `.env` has `GROQ_API_KEY` (and optionally `GEMINI_API_KEY`). The RAG agent expects `Phase_2_Knowledge_Base/faiss_index.bin` and `Phase_2_Knowledge_Base/vector_store_chunks.json` to exist (run the data pipeline once if needed).

## Deploy on Streamlit Cloud

1. **Connect repo**
   - Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
   - **New app** → connect your GitHub repo (e.g. `nikhil1989ramesh-coder/Mutual-Fund-Genie`).

2. **App settings**
   - **Main file path:** `streamlit_app.py`
   - **Branch:** `main` (or your default branch).
   - Leave **Working directory** empty (app runs from repo root).

3. **Secrets**
   - In the app’s **Settings → Secrets**, add:
     - `GROQ_API_KEY` = your Groq API key
     - `GEMINI_API_KEY` = your Gemini API key (optional fallback)
   - Streamlit Cloud injects these as env vars; the app and RAG agent read them via `python-dotenv` / `os.environ`.

4. **Knowledge base (FAISS + chunks)**
   - The RAG agent needs:
     - `Phase_2_Knowledge_Base/faiss_index.bin`
     - `Phase_2_Knowledge_Base/vector_store_chunks.json`
   - These are in `.gitignore` by default. Choose one:
     - **Option A:** Run the data pipeline locally, then commit these two files so the repo has them (Streamlit Cloud will use them).
     - **Option B:** Add a build step (e.g. a script run in **Advanced settings → Run before app**) that runs your ingest + FAISS build so the files are created at deploy time (slower first deploy).

5. **Deploy**
   - Click **Deploy**. After the build, your app URL will be live. Use the chat to ask HDFC Mutual Fund questions; answers will show with **Sources** and error messages if something fails.

## Notes

- The app uses the same Phase 3 RAG agent as the FastAPI backend; no scheduler runs in the Streamlit app (no periodic ingest).
- For a one-time refresh of the knowledge base, run the pipeline locally and push the updated `faiss_index.bin` and `vector_store_chunks.json`, or run the build script in the Cloud “Run before app” step.
