# Frontend — MF Genie

Next.js 15 app for the Mutual Fund Genie chat UI.

- **Setup:** From repo root see [README.md](../README.md). From here: `npm install`
- **Dev:** Run `npm run dev` from this folder → http://localhost:3000. Or from repo root run `npm run dev` (same result).
- **Build:** `npm run build`
- **Tests:** `npm test`

API base URL is set via `NEXT_PUBLIC_API_URL` (defaults to same origin). Leave it **unset** to use built-in API routes (/api/chat, /api/faq). For local RAG backend, run Phase-4_Backend_API on port 8000 and set `NEXT_PUBLIC_API_URL=http://localhost:8000` in `.env.local`.
