# Audit & Fix Report — Production 405 Error

**Production URL:** https://nikhil-ramesh-ai-mfgenie.vercel.app/  
**Issue:** "Server error: 405. Please try again" when users submit questions.  
**Date:** 2026-03-08

---

## 1. Root cause of 405 error

**Conclusion:** The 405 occurs because the **deployment currently serving production does not expose the Next.js API routes** (`/api/chat`, `/api/faq`) correctly. The frontend sends `POST /api/chat` to the same origin; something in the live deployment responds with **405 Method Not Allowed** (and `/api/faq` with **404**), so the routes either are not deployed or are not being invoked.

**Contributing factors:**

1. **Vercel project settings**  
   If **Root Directory** is not set to **`frontend`**, the build runs from the repo root. The root `vercel.json` uses `outputDirectory: "frontend/.next"`, which can lead to serverless functions not being mounted under `/api/*` as expected. With **Root Directory = frontend**, the build and output are correct and the Pages API routes are included.

2. **Output Directory**  
   If the dashboard had **Output Directory** set to the literal string `"Next.js default"`, Vercel looked for a folder named that instead of **`.next`**, which could break the deployment. The repo now sets **`outputDirectory: ".next"`** in `frontend/vercel.json`.

3. **Build cache**  
   An older build (without or with broken API routes) may have been cached. A redeploy with **build cache disabled** ensures the latest `frontend/pages/api/*` are built and deployed.

**Code-level status:** API routes, frontend calls, and env usage are correct for production. The remaining fix is **deployment configuration and a clean redeploy**.

---

## 2. Files reviewed and updated

### 2.1 API routes (audited and hardened)

| File | Purpose | Changes |
|------|--------|--------|
| **frontend/pages/api/chat.js** | POST /api/chat, OPTIONS | Added `config.api.bodyParser` and `config.api.responseLimit`; CORS headers on all responses; defensive `req.body` handling. |
| **frontend/pages/api/faq.js** | GET /api/faq, OPTIONS | Added `config.api.responseLimit`; CORS headers including `Authorization`. |

**No** routes under `/api` (repo root) or `/app/api` are used for this app when **Root Directory = frontend**; only **frontend/pages/api/** is relevant.

### 2.2 Frontend API calls (audited — no code change)

| File | Finding |
|------|--------|
| **frontend/src/lib/apiService.js** | Uses `API_BASE_URL = process.env.NEXT_PUBLIC_API_URL \|\| ''`. In production (unset) this is `''`, so `fetch('/api/chat')` and `fetch('/api/faq')` are same-origin. No localhost in production. |

### 2.3 Environment variables (audited)

- **NEXT_PUBLIC_API_URL** — Optional. When unset (production), frontend uses relative `/api/*`. When set (e.g. FastAPI backend URL), frontend uses that base. No change needed.
- **API_URL** — Not used in frontend.
- **GEMINI_API_KEY** — Backend-only; not required for Vercel frontend stub.

### 2.4 Vercel and Next config (audited)

| File | Finding |
|------|--------|
| **frontend/vercel.json** | `outputDirectory: ".next"` set so the framework output is correct. |
| **frontend/next.config.mjs** | Rewrites only in development when `NEXT_PUBLIC_API_URL` is set; production returns `[]` — no rewrites. Correct. |
| **vercel.json** (root) | Used when Root Directory is not set; no rewrites. **Recommended:** set Root Directory to **frontend** so only `frontend/` config applies. |

### 2.5 CORS and OPTIONS

- **frontend/pages/api/chat.js** — Handles `OPTIONS` with 200 and CORS headers; `POST` returns JSON with CORS headers.
- **frontend/pages/api/faq.js** — Handles `OPTIONS` with 200 and CORS headers; `GET` returns JSON with CORS headers.

No middleware or other layer was found that could return 405 for `/api/*`.

---

## 3. Exact code changes made

### 3.1 frontend/pages/api/chat.js

- **Added** `config` export:
  - `api.bodyParser.sizeLimit: '256kb'`
  - `api.responseLimit: false`
- **Set** CORS headers on all responses: `Access-Control-Allow-Origin`, `Access-Control-Allow-Methods`, `Access-Control-Allow-Headers` (including `Authorization`), `Access-Control-Max-Age`.
- **Kept** `OPTIONS` → 200 and `POST` → 200/400/500 with JSON.
- **Tightened** `req.body` handling: check `body` is object, not null, has `message`, then use `body.message` (string trim).

### 3.2 frontend/pages/api/faq.js

- **Added** `config` export: `api.responseLimit: false`.
- **Set** CORS headers (including `Authorization` in Allow-Headers).
- **Kept** `OPTIONS` → 200 and `GET` → 200/500 with JSON.

### 3.3 frontend/vercel.json (already present)

- `outputDirectory: ".next"` so Vercel does not look for a literal "Next.js default" directory.

---

## 4. Updated API route snippets (reference)

### POST /api/chat (excerpt)

```js
export const config = {
  api: {
    bodyParser: { sizeLimit: '256kb' },
    responseLimit: false,
  },
};

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  res.setHeader('Access-Control-Max-Age', '86400');

  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'POST') return res.status(405).json({ detail: 'Method not allowed' });

  const body = req.body;
  const message = (body && typeof body === 'object' && body !== null && 'message' in body)
    ? (typeof body.message === 'string' ? body.message.trim() : '')
    : '';
  if (!message) return res.status(400).json({ detail: 'Empty message received.' });

  return res.status(200).json({ answer: '...', sources: ['...'] });
}
```

### GET /api/faq (excerpt)

```js
export const config = { api: { responseLimit: false } };

export default function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  if (req.method === 'OPTIONS') return res.status(200).end();
  if (req.method !== 'GET') return res.status(405).json({ detail: 'Method not allowed' });
  return res.status(200).json({ faqs: [...] });
}
```

---

## 5. Frontend fetch logic (unchanged — correct)

- **Base URL:** `const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';`
- **Chat:** `fetch(\`${API_BASE_URL}/api/chat\`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ message }) })`
- **FAQ:** `fetch(\`${API_BASE_URL}/api/faq\`, { method: 'GET', headers: { 'Content-Type': 'application/json' } })`

In production, `API_BASE_URL` is `''`, so requests go to `/api/chat` and `/api/faq` on the same origin.

---

## 6. Vercel configuration required (checklist)

Before or after deploying the latest code, confirm in the Vercel project:

| Setting | Value |
|---------|--------|
| **Root Directory** | `frontend` |
| **Build Command** | `npm run build` |
| **Output Directory** | Leave **empty** or set to **`.next`** (not "Next.js default") |
| **Install Command** | `npm install` (or default) |

Then:

1. **Redeploy** the latest deployment (or deploy from the branch that has these fixes).
2. **Disable** “Use existing Build Cache” so the build includes `frontend/pages/api/chat.js` and `frontend/pages/api/faq.js`.
3. After deploy, open the build log and confirm **Route (pages):** `/api/chat`, `/api/faq` appear.

---

## 7. Verification

- **Unit tests:** `npm test` in `frontend/` — 9/9 passed.
- **Production build:** `npm run build` in `frontend/` — success; Route (pages) shows `/api/chat` and `/api/faq`.
- **Production request (current live URL):** POST /api/chat → 405, GET /api/faq → 404 (expected until the new build is deployed and used for production).

After a successful redeploy with the correct settings and cache disabled, production should return **200** for POST /api/chat and GET /api/faq and the UI should no longer show "Server error: 405. Please try again."

---

*End of audit report.*
