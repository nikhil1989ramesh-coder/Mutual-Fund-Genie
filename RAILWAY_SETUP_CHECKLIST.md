# Railway project setup checklist

Use this in your Railway project:  
**https://railway.com/project/5a9eda67-2c49-408e-b67f-24534aba68be**

Copy the variable **values** from your local `.env` (do not commit `.env` to git).

---

## 1. Connect the repo (if not already)

- In the project, click **New** → **GitHub Repo** (or **Add service** → **GitHub Repo**).
- Select: **Build RAG Chat bot for Mutual fund assistant**.
- Branch: **main**.

---

## 2. Service settings

Click the **service** that was created from the repo.

| Setting | Value |
|--------|--------|
| **Root Directory** | Leave **empty** |
| **Build Command** | Leave default (repo’s `railway.json` uses: `python Phase_2_Knowledge_Base/build_faiss_db.py`). If build fails, set to: `pip install -r requirements.txt && python Phase_2_Knowledge_Base/build_faiss_db.py` |
| **Start Command** | Leave default (from `railway.json`: `uvicorn Phase-4_Backend_API.main:app --host 0.0.0.0 --port $PORT`) |

---

## 3. Variables (from your `.env`)

In the service → **Variables** tab:

| Variable name | Where to get the value |
|---------------|-------------------------|
| `GROQ_API_KEY` | Copy from your local `.env` (line 1) |
| `GEMINI_API_KEY` | Copy from your local `.env` (line 2) |

Paste each value into Railway and save. Railway will redeploy after you add variables.

---

## 4. Public URL

- In the service go to **Settings** → **Networking** (or **Public Networking**).
- Click **Generate Domain** (or **Add domain**).
- Copy the URL (e.g. `https://xxxx.up.railway.app`) — **no trailing slash**.

Use this URL as `NEXT_PUBLIC_API_URL` in Vercel so the frontend talks to this backend.

---

## 5. After deploy

- Open `https://your-railway-domain.up.railway.app/docs` to confirm the API is up.
- In Vercel: **Settings** → **Environment Variables** → set `NEXT_PUBLIC_API_URL` = your Railway URL → **Redeploy** the frontend.
