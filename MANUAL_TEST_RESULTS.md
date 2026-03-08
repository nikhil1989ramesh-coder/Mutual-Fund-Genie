# Manual Testing Results — Production & Scenarios

**Date:** 2026-03-08  
**Production URL:** https://nikhil-ramesh-ai-mfgenie.vercel.app/  
**Git push:** Completed (commit `fb3661c`).  
**Vercel deploy:** CLI deploy failed (project/scope); if repo is connected to Vercel, deployment may run from GitHub. Production was tested immediately after push; latest build may not be live yet.

---

## 1. Unit tests (all passed)

| Suite | Result | Count |
|-------|--------|--------|
| Frontend (Jest) — apiService + ChatInterface | **PASS** | 9/9 |
| Backend (pytest) — test_api.py | **PASS** | 9/9 |

---

## 2. Production API test matrix

Base URL: `https://nikhil-ramesh-ai-mfgenie.vercel.app`

### 2.1 Home page

| # | Scenario | Method | URL | Input | Expected | Actual | Result |
|---|----------|--------|-----|--------|----------|--------|--------|
| 1 | Load home page | GET | / | — | 200, HTML | 200, HTML | **PASS** |

### 2.2 FAQ endpoint

| # | Scenario | Method | URL | Input | Expected | Actual | Result |
|---|----------|--------|-----|--------|----------|--------|--------|
| 2 | Get FAQ list | GET | /api/faq | — | 200, JSON `{ faqs: [] }` | **404 Not Found** | **FAIL** |

### 2.3 Chat endpoint — method & preflight

| # | Scenario | Method | URL | Input | Expected | Actual | Result |
|---|----------|--------|-----|--------|----------|--------|--------|
| 3 | CORS preflight | OPTIONS | /api/chat | — | 200 | 204 | **PASS** (acceptable) |
| 4 | Wrong method | GET | /api/chat | — | 405 Method Not Allowed | **404 Not Found** | **FAIL** |
| 5 | Valid message | POST | /api/chat | `{"message":"What is NAV?"}` | 200, JSON `{ answer, sources }` | **405 Method Not Allowed** | **FAIL** |

### 2.4 Chat endpoint — input combinations

| # | Scenario | Method | URL | Input | Expected | Actual | Result |
|---|----------|--------|-----|--------|----------|--------|--------|
| 6 | Empty message | POST | /api/chat | `{"message":""}` | 400, `{ detail: "Empty message received." }` | **405** | **FAIL** |
| 7 | Missing message (empty body) | POST | /api/chat | `{}` | 400 or 422 | **405** | **FAIL** |
| 8 | Long message (500 chars) | POST | /api/chat | `{"message":"x"...500}` | 200 or 400 | **405** | **FAIL** |

---

## 3. Failure modes and errors (for your review)

### 3.1 Summary

| Severity | Count | Description |
|----------|--------|-------------|
| **Critical** | 2 | Chat and FAQ APIs not available on production (404/405). |
| **High** | 4 | All POST /api/chat and GET /api/faq scenarios fail with 404/405. |
| **Pass** | 2 | GET / (home) and OPTIONS /api/chat (204). |

### 3.2 Detailed failure list

1. **GET /api/faq → 404 Not Found**  
   - **Scenario:** Load FAQ list for suggested questions.  
   - **Expected:** 200 with JSON `{ faqs: string[] }`.  
   - **Actual:** 404.  
   - **Impact:** FAQ section may fall back to static list; any dynamic FAQ fetch fails.

2. **POST /api/chat → 405 Method Not Allowed**  
   - **Scenario:** Send any chat message (valid, empty, or malformed).  
   - **Expected:** 200 with stub answer, or 400 for invalid input.  
   - **Actual:** 405 for all POST requests.  
   - **Impact:** Users see “Server error: 405. Please try again.” and cannot use chat.

3. **GET /api/chat → 404 Not Found**  
   - **Scenario:** Call chat endpoint with GET (wrong method).  
   - **Expected:** 405 Method Not Allowed.  
   - **Actual:** 404.  
   - **Interpretation:** Same as below — `/api/chat` and `/api/faq` are not exposed by the current deployment.

### 3.3 Root cause (inference)

- **404/405 on /api/faq and /api/chat** indicate the **current production build does not serve these API routes**.
- Possible reasons:
  1. **New code not deployed yet** — Push completed; Vercel CLI deploy failed; production may still be on an older commit. Trigger a redeploy from the Vercel dashboard (Deployments → Redeploy or new deployment from `main`).
  2. **Root Directory** — In Vercel, **Root Directory** must be **`frontend`** so the build uses `frontend/pages/api/` and produces the Pages Router serverless functions.
  3. **Build command** — Must be **`npm run build`** (not `npm run`).

---

## 4. Scenarios not tested (require browser or deployed fix)

- **UI: click suggested question** — Requires production chat API to return 200.
- **UI: type message and send** — Same.
- **UI: Mutual Fund Basics click** — Same.
- **UI: reset / new session** — Client-side only; not blocked by API.
- **Local app (npm run dev)** — Not run in this session; unit tests and build confirm code path.

---

## 5. Recommended next steps

1. **Vercel dashboard**  
   - Confirm **Root Directory** = **`frontend`**.  
   - Confirm **Build Command** = **`npm run build`**.  
   - Open **Deployments** and either **Redeploy** the latest or ensure the latest deployment is from commit **`fb3661c`** (Pages API routes).

2. **After a successful deploy**  
   - Re-run this test matrix (GET /, GET /api/faq, OPTIONS /api/chat, POST /api/chat with valid, empty, `{}`, long message).  
   - In browser: open production URL, send a chat message, click suggested questions, and confirm no 405/404 errors.

3. **If 404/405 persist after deploy**  
   - Check the deployment build logs for errors.  
   - Confirm the build output lists **Route (pages):** `/api/chat`, `/api/faq`.

---

*End of report. All scenario results and failure modes are listed above for your review.*
