# Root Cause Analysis: Production Server Error (nikhil-ramesh-ai-mfgenie.vercel.app)

**Date:** 2025-03-08  
**Production URL:** https://nikhil-ramesh-ai-mfgenie.vercel.app/  
**Symptom:** Server error when using the app; API routes return 404.

---

## 1. Confirmed behavior

| Check | Result |
|-------|--------|
| **GET** `https://nikhil-ramesh-ai-mfgenie.vercel.app/` | 200 – App shell loads (HTML) |
| **GET** `https://nikhil-ramesh-ai-mfgenie.vercel.app/api/faq` | **404 Not Found** |
| **POST** `https://nikhil-ramesh-ai-mfgenie.vercel.app/api/chat` | Expected to 404/405 (API route not deployed) |

So the Next.js **Pages API routes** (`/api/chat`, `/api/faq`) are **not deployed** on this Vercel project. The UI loads, but any call to `/api/chat` or `/api/faq` fails (404 or 405), which the frontend shows as “Server error”.

---

## 2. Root cause: Vercel project root vs app root

The repo has two layouts:

- **Repo root:** `vercel.json`, `frontend/`, backend folders, etc.
- **Next.js app:** only inside `frontend/` (e.g. `frontend/pages/api/chat.js`, `frontend/pages/api/faq.js`).

There are two `vercel.json` files:

| File | Role |
|------|------|
| **Root** `vercel.json` | Used when Vercel’s **Root Directory** is the repo root. Runs `cd frontend && npm run build`, `outputDirectory: "frontend/.next"`. |
| **Frontend** `frontend/vercel.json` | Used when Root Directory is `frontend`. Standard Next.js build inside `frontend/`. |

If the Vercel project **“nikhil-ramesh-ai-mfgenie”** was created with:

- **Root Directory:** empty (i.e. repository root)

then:

1. Vercel uses the **root** `vercel.json`.
2. Build runs from repo root with `cd frontend && npm run build` and output in `frontend/.next`.
3. The deployment is still rooted at the **repo root**, not at the Next.js app root.
4. Next.js serverless functions for `frontend/pages/api/*` are built under `frontend/.next`, but the Vercel runtime may not map them to `/api/*` correctly when the project root is the repo root, or the framework may not be detected as Next.js when the app lives in a subfolder without Root Directory set.

Result: `/api/chat` and `/api/faq` are not available → **404** (and the UI shows “Server error”).

---

## 3. Why this matches your setup

- The **same codebase** deploys correctly when the deployment root is `frontend/` (e.g. CLI deploy from `frontend/` or a different project with Root Directory = `frontend`), and the build output shows `Route (pages) /api/chat`, `/api/faq`.
- Only the production URL **nikhil-ramesh-ai-mfgenie.vercel.app** (likely using repo root) returns 404 on `/api/faq` and fails on chat.

So the failure is **deployment/configuration**, not application code.

---

## 4. Fix (Vercel project settings)

Do this for the project that serves **https://nikhil-ramesh-ai-mfgenie.vercel.app**:

1. Open **Vercel Dashboard** → your project (**nikhil-ramesh-ai-mfgenie** or similar).
2. Go to **Settings** → **General**.
3. Set **Root Directory** to **`frontend`** (and save).
   - Use “Edit” next to Root Directory, enter `frontend`, save.
4. **Redeploy** the latest commit (e.g. **Deployments** → … → **Redeploy**).
   - Optionally enable **“Use existing Build Cache”** = **No** for one deploy to avoid stale build artifacts.

After redeploy:

- Build will run from `frontend/` (`npm install`, `npm run build`).
- `frontend/vercel.json` will be used (framework Next.js, output `.next`).
- Pages API routes will be deployed and **GET /api/faq** and **POST /api/chat** will return 200 (no 404).

No code change is required for this fix.

---

## 5. Local app not working

You mentioned the **local app is not working fine**. Typical causes:

| Scenario | What happens | Fix |
|----------|----------------------|-----|
| Run from **repo root** (`npm run dev`) | Previously no `package.json` at root. | You can now run **`npm run dev`** from repo root (it runs the frontend). Or run **`cd frontend && npm run dev`**. |
| **Backend expected but not running** | If `NEXT_PUBLIC_API_URL=http://localhost:8000`, chat/faq calls go to FastAPI. If FastAPI is not running → “Could not reach the backend”. | Either run the FastAPI backend (e.g. Phase-4_Backend_API on port 8000) or **unset** `NEXT_PUBLIC_API_URL` (or leave it empty) so the app uses the Next.js API routes at `localhost:3000/api/chat` and `localhost:3000/api/faq`. |
| **Wrong port** | App runs on 3000; backend on 8000. | Use `NEXT_PUBLIC_API_URL=http://localhost:8000` only when the backend is running on 8000. |

**Recommended local workflow:**

- From repo root: run **`npm run dev`** (or `cd frontend && npm run dev`), then open **http://localhost:3000**.
- Do **not** set `NEXT_PUBLIC_API_URL` (or set it to empty) unless the FastAPI backend is running; then chat and FAQs will use the Next.js stubs and the app should work.

---

## 6. Summary

| Item | Conclusion |
|------|------------|
| **Production 404 / server error** | API routes are not deployed because the Vercel project is using the **repo root** instead of **`frontend`** as Root Directory. |
| **Fix** | In Vercel project settings, set **Root Directory** to **`frontend`** and redeploy (without cache if needed). |
| **Local** | Run dev server from **`frontend/`**; only set `NEXT_PUBLIC_API_URL` when the FastAPI backend is running. |

After applying the Root Directory change and redeploying, **https://nikhil-ramesh-ai-mfgenie.vercel.app** should serve `/api/faq` and `/api/chat` correctly and the “server error” should stop.
