# Scripts

## test_vercel_frontend.py

Tests the **Vercel-deployed Next.js frontend** only: home page, `/api/faq`, and `POST /api/chat`.

Vercel project: [mutual-fund-genie](https://vercel.com/nikhil1989ramesh-5219s-projects/mutual-fund-genie)

### Run (from repo root)

```bash
# Default URL: https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app
python scripts/test_vercel_frontend.py

# Custom URL (e.g. custom domain or different deployment)
python scripts/test_vercel_frontend.py --url https://your-app.vercel.app

# Or set env
set VERCEL_URL=https://your-app.vercel.app
python scripts/test_vercel_frontend.py
```

### If you get HTTP 401

Vercel [Deployment Protection](https://vercel.com/docs/security/deployment-protection) may be enabled. Either:

- In **Project → Settings → Deployment Protection**, allow public access for Production, or  
- Use `--url` with a deployment URL that is publicly accessible (e.g. a preview URL or custom domain without protection).

### Requirements

- Python 3.7+
- `requests`: `pip install requests`

---

## test_deployed_backends.py

Tests your **deployed** Streamlit app, Vercel frontend, and (optionally) FastAPI backend after deployment.

### Run (from repo root)

```bash
# Use default URLs (Streamlit + Vercel project mutual-fund-genie)
python scripts/test_deployed_backends.py

# Override URLs
python scripts/test_deployed_backends.py --streamlit-url https://nikhil-ramesh-ai-mfgenie.streamlit.app --vercel-url https://your-vercel-app.vercel.app

# Include FastAPI backend (e.g. Railway)
set BACKEND_API_URL=https://your-app.up.railway.app
python scripts/test_deployed_backends.py
```

### Default URLs

- **Streamlit:** https://nikhil-ramesh-ai-mfgenie.streamlit.app  
- **Vercel:** https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app  

If your Vercel production URL is different (e.g. custom domain or different project name), pass `--vercel-url YOUR_URL`.

### If Vercel returns 401

Vercel [Deployment Protection](https://vercel.com/docs/security/deployment-protection) may be enabled. Either:

- Turn off protection for Production in **Project → Settings → Deployment Protection**, or  
- Use `--vercel-url` with a public deployment URL that isn’t protected.

### Requirements

- Python 3.7+
- `requests`: `pip install requests`

### Exit code

- `0` — all checked URLs passed  
- `1` — at least one check failed (see script output)
