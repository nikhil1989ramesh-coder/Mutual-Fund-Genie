# Manual testing – Vercel production app

**Production URL:** https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app

Use this checklist to manually verify the deployed frontend. Automated script results are in **Test results summary** below.

---

## 1. Home page

- [ ] Open the production URL in a browser.
- [ ] Page loads (no blank screen or console errors).
- [ ] Header shows: logo, "Mutual Fund Genie AI Assistant", "HDFC Mutual Fund | Facts-only. No investment advice.", Live badge.
- [ ] Left sidebar: "Schemes in My Scope" with 5 HDFC schemes; "About" with product/AMC/engine/creator.
- [ ] Center: chat input "Ask about HDFC Mutual Fund schemes…" and Send button.
- [ ] Right sidebar (desktop): "Suggested Questions", "Mutual Fund Basics" with question list.
- [ ] Footer: educational disclaimer.
- [ ] On mobile/narrow width: sidebars collapse; Suggested Questions appears in a sensible place.

---

## 2. Chat (stub when no backend / with Railway backend)

**If `NEXT_PUBLIC_API_URL` is not set (stub mode):**

- [ ] Type a question (e.g. "What is NAV?") and click Send.
- [ ] Response appears with an answer and a "Sources" section.
- [ ] Answer includes link to Streamlit RAG chat or similar (stub message).
- [ ] No uncaught errors in console.

**If `NEXT_PUBLIC_API_URL` is set (Railway FastAPI):**

- [ ] Type "What is the exit load for HDFC Flexi Cap?" and Send.
- [ ] Response shows a factual answer with citations.
- [ ] "Sources" section shows at least one URL.
- [ ] Type "What is a mutual fund?" and Send.
- [ ] Response is relevant and has sources.
- [ ] Empty message or only spaces: error or validation message, no crash.

---

## 3. Suggested questions & basics

- [ ] Click a "Suggested Question" (e.g. from FAQ section).
- [ ] Chat input is filled and/or message is sent; reply appears.
- [ ] Click an item under "Mutual Fund Basics".
- [ ] Same behavior: question sent, response shown.
- [ ] On mobile, tapping a sidebar item scrolls to chat and sends the question.

---

## 4. Error handling

- [ ] With backend unreachable (e.g. turn off WiFi or use invalid API URL): send a message.
- [ ] Error banner/message appears (e.g. "Unable to connect to the AI server" or similar).
- [ ] No blank screen or uncaught exception.
- [ ] Restore connectivity; send again — request succeeds or stub response appears.

---

## 5. API routes (automated)

Run from project root:

```bash
python scripts/test_vercel_frontend.py --url https://mutual-fund-genie-nikhil1989ramesh-5219s-projects.vercel.app
```

Expected: **All frontend checks passed** (GET /, GET /api/faq, POST /api/chat).

---

## Test results summary (last run)

- **Backend unit tests (pytest):** 9/9 passed.
- **Frontend unit tests (Jest):** 9/9 passed.
- **Vercel production script:** GET /, GET /api/faq, POST /api/chat — PASS.
- **Deployed backends script:** Streamlit app PASS, Vercel frontend PASS; FastAPI backend SKIP (set `BACKEND_API_URL` to test Railway).

No duplicate or unnecessary committed files were found; structure uses a single App Router (`src/app`) and Pages API routes (`pages/api`) only.
