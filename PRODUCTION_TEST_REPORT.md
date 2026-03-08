# Production Test Report — nikhil-ramesh-ai-mfgenie.vercel.app

**Report date:** 2026-03-08  
**Production URL:** https://nikhil-ramesh-ai-mfgenie.vercel.app/

---

## 1. Unit tests (local codebase)

### 1.1 Frontend (Jest)

| Suite | Result | Tests |
|-------|--------|--------|
| `src/lib/apiService.test.js` | **PASS** | 4/4 (returns answer on success, throws on non-ok, throws on network failure, throws on empty message) |
| `src/components/ChatInterface.test.js` | **PASS** | 5/5 (welcome screen, send message, error banner, reset, fallback query) |

**Total:** 9 passed, 0 failed.

### 1.2 Backend (pytest)

| Suite | Result | Tests |
|-------|--------|--------|
| `tests/test_api.py` | **PASS** | 9/9 (chat valid/empty/whitespace/422/500, FAQ list/fallback, docs, openapi) |

**Total:** 9 passed, 0 failed.

---

## 2. Production API tests (live URL)

Base URL: `https://nikhil-ramesh-ai-mfgenie.vercel.app`

### 2.1 GET / (home page)

| Input | Expected | Actual | Result |
|-------|----------|--------|--------|
| `GET /` | 200, HTML page | 200, body length 16049 | **PASS** |

### 2.2 GET /api/faq

| Input | Expected | Actual | Result |
|-------|----------|--------|--------|
| `GET /api/faq` | 200, JSON `{ faqs: string[] }` | **404 Not Found** | **FAIL** |

### 2.3 OPTIONS /api/chat (CORS preflight)

| Input | Expected | Actual | Result |
|-------|----------|--------|--------|
| `OPTIONS /api/chat` | 200, CORS headers | 204 with headers `X-Next-Error-Status: 404`, `X-Matched-Path: /404` | **FAIL** (treated as 404) |

### 2.4 POST /api/chat (send message)

| Input | Expected | Actual | Result |
|-------|----------|--------|--------|
| `POST /api/chat` body `{"message":"What is NAV?"}` | 200, JSON `{ answer, sources }` | **405 Method Not Allowed**, empty body | **FAIL** |

### 2.5 GET /api/chat

| Input | Expected | Actual | Result |
|-------|----------|--------|--------|
| `GET /api/chat` | 405 (method not allowed) | **404 Not Found** | **FAIL** (route not found) |

### 2.6 POST /api/chat/ (trailing slash)

| Input | Expected | Actual | Result |
|-------|----------|--------|--------|
| `POST /api/chat/` | 200 or redirect to /api/chat | 308 (redirect) | **INFO** (redirect; follow-up not tested) |

---

## 3. Manual / E2E behaviour (in-browser)

When a user opens the production app and sends a chat message:

- **Expected:** Request to `POST /api/chat` returns 200 with stub answer; UI shows the answer.
- **Actual:** Request to `POST /api/chat` returns **405 Method Not Allowed**; UI shows **"Server error: 405. Please try again."**

So the **manual test case “Send a chat message” fails** with 405 on production.

---

## 4. Failure summary (for your review)

| # | Test / scenario | Expected | Actual | Severity |
|---|-----------------|----------|--------|----------|
| 1 | **GET /api/faq** | 200 + JSON | 404 Not Found | High |
| 2 | **OPTIONS /api/chat** | 200 + CORS | 204 with 404-style headers | High |
| 3 | **POST /api/chat** | 200 + JSON answer | 405 Method Not Allowed | **Critical** (breaks chat) |
| 4 | **GET /api/chat** | 405 | 404 | Medium (route missing) |
| 5 | **Manual: send chat message** | Stub answer shown | “Server error: 405. Please try again.” | **Critical** |

---

## 5. Root cause (inference from tests)

- **Local build** includes App Router API routes: `ƒ /api/chat`, `ƒ /api/faq` (confirmed via `npm run build`).
- **Production** returns 404 for `/api/faq` and `/api/chat` (GET) and 405 for `POST /api/chat`, which suggests either:
  1. **Root Directory** in Vercel is not set to **`frontend`**, so the deployed build is not the Next.js app that contains these API routes, or  
  2. The **deployed deployment** is an older build that does not include the App Router API routes, or  
  3. A **Vercel rewrite/edge/proxy** is serving `/api/*` with a handler that returns 404/405 instead of the Next.js serverless functions.

So the **405 and 404** are likely **deployment/configuration** issues (what is built and how `/api/*` is routed on Vercel), not a failure of the current route handler code in the repo.

---

## 6. Recommended checks (when you initiate fixes)

1. **Vercel → Project Settings → General**  
   - Confirm **Root Directory** is exactly **`frontend`** (no leading/trailing slash).

2. **Vercel → Deployments**  
   - Confirm the **production deployment** is from the latest commit that includes `frontend/src/app/api/chat/route.js` and `frontend/src/app/api/faq/route.js`.  
   - Trigger a **Redeploy** (or push a new commit) with **Build Command** = **`npm run build`** and no custom rewrites overriding `/api/*`.

3. **Vercel → Project Settings → Build & Development**  
   - Ensure there are **no rewrites or functions** that map `/api/*` to a different backend or static response.

4. After changing settings, **re-run** the production API tests above and the manual “send chat message” test to confirm 405 and 404 are resolved.

---

*End of report. No code changes were made; this is for review only.*
