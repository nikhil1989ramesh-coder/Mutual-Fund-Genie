from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from typing import List, Optional
from pydantic import BaseModel
import sys
import os
import uvicorn

# Ensure path is correct for local and Vercel environments
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

# Import RAG Agent and Scheduler
try:
    from Phase_3_Query_Generation.rag_agent import MutualFundRAG
    from Phase_5_Scheduler.scheduler import start_scheduler
except ImportError:
    # Fallback for dynamic loading if package structure isn't recognized
    from importlib.machinery import SourceFileLoader
    rag_module_path = os.path.join(BASE_DIR, 'Phase_3_Query_Generation', 'rag_agent.py')
    rag_agent_module = SourceFileLoader("rag_agent", rag_module_path).load_module()
    MutualFundRAG = rag_agent_module.MutualFundRAG
    
    sched_module_path = os.path.join(BASE_DIR, 'Phase_5_Scheduler', 'scheduler.py')
    sched_module = SourceFileLoader("scheduler", sched_module_path).load_module()
    start_scheduler = sched_module.start_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle startup and shutdown lifecycle."""
    global scheduler
    scheduler = start_scheduler(reload_callback=rag_agent.reload_index)
    print("Background Scheduler Initialized with Reload Callback.")
    yield
    if scheduler:
        scheduler.shutdown()
        print("Background Scheduler Shutdown.")


app = FastAPI(
    title="Mutual Fund RAG API",
    description="Backend API serving the HDFC Mutual Fund factual knowledge base.",
    version="1.0.0",
    lifespan=lifespan,
)

# Enable CORS for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize eagerly (needed by lifespan before app starts)
rag_agent = MutualFundRAG()
scheduler = None

# Data models
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]

class FAQResponse(BaseModel):
    faqs: List[str]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Takes a user query, checks it against constraints (PII, Scope),
    retrieves context from FAISS, and returns the LLM generated answer.
    """
    if not request.message or not request.message.strip():
        raise HTTPException(status_code=400, detail="Empty message received.")
        
    try:
        # The generate_answer function already handles PII and scope rejection internally
        answer, sources = rag_agent.generate_answer(request.message)
        return ChatResponse(answer=answer, sources=sources)
    except Exception as e:
        print(f"API Error during chat completion: {e}")
        raise HTTPException(status_code=500, detail="Internal server error generating response.")

@app.get("/api/faq", response_model=FAQResponse)
async def generate_dynamic_faqs():
    """
    Generates dynamic FAQs using the strict prompt constraints.
    We instruct the LLM to generate 3 extremely brief FAQs purely based on the top 5 schemes.
    """
    prompt = "Generate exactly 3 short, realistic frequently asked questions about the HDFC mutual funds (Flexi Cap, Small Cap, Mid-Cap, ELSS, Liquid) based on the provided context. Format the output as a simple numbered list. No extra conversational text."
    
    try:
        # We use generate_answer to ensure it ONLY uses factual FAISS data
        answer, _ = rag_agent.generate_answer(prompt)
        
        # Parse the numbered list back into an array for the frontend
        faqs = []
        for line in answer.split('\n'):
            line = line.strip()
            # Clean up the numbering and output formatting (e.g., "1. What is...")
            if line and line[0].isdigit() and '. ' in line:
                clean_q = line.split('. ', 1)[1]
                faqs.append(clean_q)
                
        # Fallback if the LLM formatting was weird
        if not faqs:
            faqs = [
                "What is the exit load for HDFC Flexi Cap?",
                "What is a mutual fund?",
                "What is the AUM of the HDFC Liquid Fund?"
            ]
            
        return FAQResponse(faqs=faqs[:3]) # Strictly return 3
        
    except Exception as e:
        print(f"API Error generating FAQs: {e}")
        # Always fallback to static list so UI doesn't break
        return FAQResponse(faqs=[
            "What is the exit load for HDFC Flexi Cap?",
            "What is a mutual fund?",
            "What is the AUM of the HDFC Liquid Fund?"
        ])

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
