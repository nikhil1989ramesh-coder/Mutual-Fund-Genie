import sys
import os

# Adjust sys.path to include root for imports
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Import RAG Agent
try:
    from Phase_3_Query_Generation.rag_agent import MutualFundRAG
except ImportError:
    # Fallback for dynamic loading if package structure isn't recognized
    from importlib.machinery import SourceFileLoader
    rag_module_path = os.path.join(BASE_DIR, 'Phase_3_Query_Generation', 'rag_agent.py')
    rag_agent_module = SourceFileLoader("rag_agent", rag_module_path).load_module()
    MutualFundRAG = rag_agent_module.MutualFundRAG

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG agent (Eager load for warm start)
rag_agent = MutualFundRAG()

class ChatRequest(BaseModel):
    message: str

@app.get("/api/health")
async def health():
    return {"status": "ok", "message": "Mutual Fund Genie API is online (Production RAG)"}

@app.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.message:
        return {"answer": "Error: No message received.", "sources": []}
    
    try:
        answer, sources = rag_agent.generate_answer(request.message)
        return {"answer": answer, "sources": sources}
    except Exception as e:
        print(f"API Error: {e}")
        return {"answer": "I'm sorry, I encountered an error. Please try again later.", "sources": []}

@app.get("/api/faq")
async def faq():
    # Return a set of default FAQs for quick UI response
    return {
        "faqs": [
            "What is the exit load for HDFC Flexi Cap?",
            "How do I start an SIP with HDFC?",
            "What are the benefits of ELSS funds?"
        ]
    }
