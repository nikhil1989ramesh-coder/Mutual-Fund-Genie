from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
@app.get("/api/index/health")
async def health():
    return {"status": "ok", "message": "Mutual Fund Genie API is online (Vercel Serverless)"}

@app.post("/api/chat")
@app.post("/api/index/chat")
async def chat(data: dict):
    message = data.get("message", "")
    if not message:
        return {"answer": "Error: No message received.", "sources": []}
    
    return {
        "answer": "Received your query about mutual funds. (Backend connectivity confirmed)",
        "sources": ["https://www.hdfcmf.com"]
    }

@app.get("/api/faq")
@app.get("/api/index/faq")
async def faq():
    return {
        "faqs": [
            "What is the exit load for HDFC Flexi Cap?",
            "How do I start an SIP with HDFC?",
            "What are the benefits of ELSS funds?"
        ]
    }
