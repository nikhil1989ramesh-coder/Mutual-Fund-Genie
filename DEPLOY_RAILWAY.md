# Deploy FastAPI Backend on Railway

Step-by-step guide to deploy the **Phase-4 FastAPI backend** (RAG chat API) on [Railway](https://railway.app) so your Vercel frontend can use it.

---

## What’s in the repo for Railway

- **Procfile** — `web: uvicorn Phase-4_Backend_API.main:app --host 0.0.0.0 --port $PORT`
- **railway.json** — Build: run `build_faiss_db.py` to create the FAISS index; Start: run the FastAPI app with uvicorn. Railway uses this so the index is built at deploy time (no need to commit `faiss_index.bin`).

---

## Prerequisites

- This repo pushed to **GitHub**
- [Railway account](https://railway.app) (sign in with GitHub)
- **GROQ API key** from [Groq Console](https://console.groq.com)  
  Optional: **GEMINI_API_KEY** for fallback when Groq is rate-limited

---

## Step 1: Create a new project on Railway

1. Go to [railway.app](https://railway.app) and sign in with **GitHub**.
2. Click **New Project**.
3. Choose **Deploy from GitHub repo**.
4. Select the repository: **Build RAG Chat bot for Mutual fund assistant** (or your repo name).
5. Railway will create a project and add a new **service** from that repo.

---

## Step 2: Configure the service (root and build)

1. Click the new **service** (the one linked to your repo).
2. Open the **Settings** tab.
3. **Root Directory:** leave **empty** (deploy from repo root). All folders (`Phase_2_Knowledge_Base`, `Phase_3_Query_Generation`, `Phase-4_Backend_API`, etc.) must be at the root.
4. **Build:**
   - Railway will use **railway.json** from the repo:
     - Installs dependencies (Nixpacks runs `pip install -r requirements.txt` for Python).
     - Runs **Build command:** `python Phase_2_Knowledge_Base/build_faiss_db.py` to generate `faiss_index.bin` and `faiss_metadata.json` from `vector_store_chunks.json`.
   - If the build step doesn’t run or fails, in **Settings → Build** set **Build Command** to:
     ```bash
     pip install -r requirements.txt && python Phase_2_Knowledge_Base/build_faiss_db.py
     ```
5. **Start:** Railway uses **railway.json** so the start command is:
   ```bash
   uvicorn Phase-4_Backend_API.main:app --host 0.0.0.0 --port $PORT
   ```
   If you don’t use railway.json, set this in **Settings → Deploy** as **Start Command**. Railway sets `PORT` automatically.

---

## Step 3: Add environment variables

1. In the service, open the **Variables** tab (or **Settings → Variables**).
2. Add:

| Name            | Value                     | Required |
|-----------------|---------------------------|----------|
| `GROQ_API_KEY`  | Your Groq API key         | Yes      |
| `GEMINI_API_KEY`| Your Gemini API key      | No (fallback) |

3. Save. Railway will redeploy when you change variables (if auto-deploy is on).

---

## Step 4: Deploy and get the URL

1. If this is the first deploy, Railway will build and deploy automatically after you connect the repo and set variables.
2. **Build** can take several minutes (PyTorch, sentence-transformers, FAISS, and running `build_faiss_db.py`).
3. When the deploy succeeds, open the **Settings** tab and find **Public Networking** (or **Generate Domain**). Generate a **public URL** for the service.
4. Copy the URL, e.g. `https://your-app-name.up.railway.app` — use it **without** a trailing slash as your backend base URL.

---

## Step 5: Point Vercel frontend to Railway

1. In [Vercel Dashboard](https://vercel.com/dashboard) → your **frontend** project → **Settings** → **Environment Variables**.
2. Add or update:
   - **Name:** `NEXT_PUBLIC_API_URL`
   - **Value:** `https://your-app-name.up.railway.app` (your Railway URL, no trailing slash)
   - **Environments:** Production (and Preview if you want).
3. **Redeploy** the frontend (Deployments → ⋮ → Redeploy).

Your Next.js app will then call the FastAPI backend on Railway for chat and FAQs.

---

## Step 6: Verify

1. **Backend:** Open `https://your-railway-url.up.railway.app/docs` — FastAPI Swagger UI should load. Try `POST /api/chat` with body `{"message": "What is a mutual fund?"}`.
2. **Frontend:** Open your Vercel app URL and send a chat message; you should get an answer with sources.

---

## Troubleshooting

| Issue | What to do |
|-------|------------|
| Build fails: “No module named …” | Set **Build Command** to `pip install -r requirements.txt && python Phase_2_Knowledge_Base/build_faiss_db.py`. |
| Build fails: “vector_store_chunks.json not found” | Ensure repo root is used (Root Directory empty) and `Phase_2_Knowledge_Base/vector_store_chunks.json` is committed. |
| App crashes at startup: “Error loading Vector Database” | Build must run `build_faiss_db.py` so `faiss_index.bin` and `faiss_metadata.json` exist in `Phase_2_Knowledge_Base/`. Check build logs. |
| 502 / app not responding | Ensure **Start Command** is `uvicorn Phase-4_Backend_API.main:app --host 0.0.0.0 --port $PORT` and that `$PORT` is used (Railway sets it). |
| CORS errors from Vercel | Backend allows all origins; if you change that later, add your Vercel domain (e.g. `https://your-app.vercel.app`). |

---

## Summary

| Step | Action |
|------|--------|
| 1 | Railway → New Project → Deploy from GitHub repo → select this repo |
| 2 | Service Settings: Root Directory empty; build/start from **railway.json** (or set Build + Start commands as above) |
| 3 | Variables: add `GROQ_API_KEY`, optional `GEMINI_API_KEY` |
| 4 | Generate public URL; copy it (no trailing slash) |
| 5 | Vercel → Settings → Environment Variables → `NEXT_PUBLIC_API_URL` = Railway URL → Redeploy |
| 6 | Test `/docs` and the Vercel chat UI |

Your FastAPI backend runs on Railway; the Vercel frontend uses it for full RAG answers with citations.
