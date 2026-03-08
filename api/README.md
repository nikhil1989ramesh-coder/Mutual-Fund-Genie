# Optional Vercel serverless API

This folder is **optional**. It provides a lightweight FastAPI app for Vercel serverless:

- `GET /api/health` — health check
- `POST /api/chat` — stub (returns a connectivity message)
- `GET /api/faq` — static FAQ list

For full RAG (Groq, FAISS, scheduler), run **Phase-4_Backend_API** locally or on another host and set the frontend `NEXT_PUBLIC_API_URL` to that backend.

`.vercelignore` may exclude this folder so deployment is frontend-only by default.
