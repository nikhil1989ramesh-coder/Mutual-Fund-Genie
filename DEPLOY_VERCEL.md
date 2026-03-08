# Deploy to Vercel (mutual-fund-genie)

## 1. Connect your GitHub repo to the mutual-fund-genie project

1. Open **[mutual-fund-genie on Vercel](https://vercel.com/nikhil1989ramesh-5219s-projects/mutual-fund-genie)**.
2. Go to **Settings → Git**.
3. If not connected: **Connect Git Repository** → choose **GitHub** → select `nikhil1989ramesh-coder/Mutual-Fund-Genie`.
4. Set **Root Directory** to **`frontend`** (required so Vercel builds the Next.js app).
5. Leave **Framework Preset** as **Next.js** (auto-detected).
6. **Save**.

## 2. (Optional) Environment variables

- For **stub deployment** (no RAG backend): no env vars needed. The app uses built-in `/api/chat` and `/api/faq` stubs.
- For **full RAG**: add `NEXT_PUBLIC_API_URL` = your FastAPI backend URL (e.g. `https://your-backend.railway.app`).

## 3. Deploy

- **Redeploy**: Deployments → … on latest → **Redeploy**.
- Or push to `main`; Vercel will auto-deploy if Git is connected.

## 4. Domain

- Production URL: **https://nikhil-ramesh-ai-mfgenie.vercel.app**
- Ensure this domain is set under **Settings → Domains** for the **mutual-fund-genie** project.

## 5. Current status

- Code is pushed to GitHub with Next.js stub API routes (`/api/chat`, `/api/faq`) so the app runs without a separate backend.
- A production deploy was also made via CLI to the **frontend** project:  
  https://frontend-xi-gules-65.vercel.app  
  If you want **nikhil-ramesh-ai-mfgenie.vercel.app** to serve the same app, either:
  - Use the **mutual-fund-genie** project (steps above) with Root Directory = `frontend`, or  
  - In the **frontend** project, add the domain **nikhil-ramesh-ai-mfgenie.vercel.app** under Settings → Domains.
