import os
import json
import faiss
import numpy as np
import requests
import re
import time
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# Resolve base directory relative to this script
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Setup Groq details
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

if not GROQ_API_KEY and not os.environ.get("VERCEL"):
    # On Vercel, we can also use environment variables set in the dashboard
    print("Warning: GROQ_API_KEY not found. Fallback to Gemini will be required if key is present.")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GEMINI_API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

# Using a faster, smaller model to avoid aggressive Groq rate limits while maintaining quality
MODEL_NAME = "llama-3.1-8b-instant"

# ── Internal data references (ETMoney + Groww) — used for RAG corpus only ───────
# These URLs are NEVER exposed to users in the chat response.
SCHEME_INTERNAL_REFS = {
    "HDFC Flexi Cap Fund": [
        "https://www.etmoney.com/mutual-funds/hdfc-flexi-cap-direct-plan-growth/15593",
        "https://groww.in/mutual-funds/hdfc-equity-fund-direct-growth",
    ],
    "HDFC ELSS Tax Saver": [
        "https://www.etmoney.com/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth/15727",
    ],
    "HDFC Mid-Cap Opportunities Fund": [
        "https://www.etmoney.com/mutual-funds/hdfc-mid-cap-fund-direct-growth/15681",
        "https://groww.in/mutual-funds/hdfc-mid-cap-opportunities-fund-direct-growth",
    ],
    "HDFC Liquid Fund": [
        "https://www.etmoney.com/mutual-funds/hdfc-liquid-direct-plan-growth/15734",
        "https://groww.in/mutual-funds/hdfc-liquid-fund-direct-growth",
    ],
    "HDFC Small Cap Fund": [
        "https://www.etmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth/16180",
        "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    ],
}

# ── User-facing source URLs — ONE IndMoney scheme-specific link per fund ─────────
# These are the ONLY URLs shown to users in chat responses.
SCHEME_USER_URL = {
    "HDFC Flexi Cap Fund":            "https://www.indmoney.com/mutual-funds/hdfc-flexi-cap-fund-direct-plan-growth-option-3184",
    "HDFC ELSS Tax Saver":            "https://www.indmoney.com/mutual-funds/hdfc-elss-taxsaver-direct-plan-growth-option-2685",
    "HDFC Mid-Cap Opportunities Fund": "https://www.indmoney.com/mutual-funds/hdfc-mid-cap-fund-direct-plan-growth-option-3097",
    "HDFC Liquid Fund":               "https://www.indmoney.com/mutual-funds/hdfc-liquid-fund-direct-plan-growth-option-1051",
    "HDFC Small Cap Fund":            "https://www.indmoney.com/mutual-funds/hdfc-small-cap-fund-direct-growth-option-3580",
}

# General HDFC AMC hub — shown when no specific scheme is detected
INDMONEY_AMC_URL = "https://www.indmoney.com/mutual-funds/amc/hdfc-mutual-fund"

# Keyword patterns to detect which scheme the user is asking about
SCHEME_KEYWORDS = [
    ("HDFC Flexi Cap Fund",            ["flexi cap", "flexi-cap", "flexicap"]),
    ("HDFC ELSS Tax Saver",            ["elss", "tax saver", "tax-saver", "80c"]),
    ("HDFC Mid-Cap Opportunities Fund",["mid cap", "mid-cap", "midcap", "mid cap opportunities"]),
    ("HDFC Liquid Fund",               ["liquid fund", "liquid"]),
    ("HDFC Small Cap Fund",            ["small cap", "small-cap", "smallcap"]),
]

def detect_scheme(query: str):
    """Return the scheme name if the query mentions exactly one scheme, else None."""
    query_lower = query.lower()
    matched = []
    for scheme_name, keywords in SCHEME_KEYWORDS:
        if any(kw in query_lower for kw in keywords):
            matched.append(scheme_name)
    # Return only when exactly one scheme is detected to avoid ambiguity
    return matched[0] if len(matched) == 1 else None


class MutualFundRAG:
    def __init__(self, use_mock=False):
        """Initializes the FAISS index and Embedding model"""
        self.use_mock = use_mock
        print("Loading embedding model...")
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Paths to FAISS and Metadata
        self.index_path = os.path.join(BASE_DIR, "Phase_2_Knowledge_Base", "faiss_index.bin")
        self.metadata_path = os.path.join(BASE_DIR, "Phase_2_Knowledge_Base", "faiss_metadata.json")
        
        self.load_vector_db()

    def load_vector_db(self):
        """Loads FAISS index and metadata. Safe to call repeatedly."""
        try:
            print(f"Loading Vector Database from {self.index_path}...")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
        except Exception as e:
            print(f"Error loading Vector Database: {e}")
            self.index = None
            self.metadata = []

    def reload_index(self):
        """Callback function for the Scheduler to hot-reload the index after extraction"""
        try:
            print("Hot-reloading FAISS index and metadata from disk...")
            self.index = faiss.read_index(self.index_path)
            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)
            print("FAISS reload successful. RAG Agent is up to date.")
            return True
        except Exception as e:
            print(f"Error reloading Vector Database: {e}")
            return False

    def retrieve_context(self, query, top_k=15):
        """Embeds the query and searches the FAISS database for top K matches."""
        # Perform vector search (Reduced to k=2 to prevent Groq token limits)
        query_vector = self.encoder.encode([query]).astype('float32')
        distances, indices = self.index.search(query_vector, top_k)
        
        # Retrieve the original text (which was used to create the embeddings) by mapping back
        # The original chunks are in `vector_store_chunks.json`. We need to load them to pass pure text to Groq.
        chunks_path = os.path.join(BASE_DIR, "Phase_2_Knowledge_Base", "vector_store_chunks.json")
        with open(chunks_path, 'r', encoding='utf-8') as f:
            all_chunks = json.load(f)
            
        retrieved_contexts = []
        sources = set() # Use a set to store unique sources
        
        for idx in indices[0]:
            if idx != -1 and idx < len(all_chunks): # FAISS returns -1 if there are not enough results
                chunk_data = all_chunks[idx]
                
                text_content = chunk_data["text"]
                # Hard limit individual chunk length
                
                retrieved_contexts.append(text_content)
                
                # Use the clean source_url from metadata if available
                if idx < len(self.metadata):
                    url = self.metadata[idx].get("source_url", "")
                    if url:
                        sources.add(url)
                        
        return retrieved_contexts, list(sources)

    def is_pii_or_out_of_scope(self, query):
        """Fast pre-check for PII or explicitly out-of-scope non-HDFC queries."""
        query_lower = query.lower()
        
        # Block Personal Identifiable Information (PII)
        pii_keywords = ['pan', 'aadhaar', 'account number', 'phone', 'ssn', 'social security']
        if any(kw in query_lower for kw in pii_keywords):
            return True, "I do not process personal identifiable information."
            
        # Regex for common account number patterns (e.g., "account 12345", "a/c 9876")
        account_patterns = [
            r'account\s*#?\s*\d+',
            r'a/c\s*#?\s*\d+',
            r'\d{9,18}' # Typical Indian bank account length range
        ]
        for pattern in account_patterns:
            if re.search(pattern, query_lower):
                return True, "I cannot process account numbers or specific banking details. That is out of scope."

        # Scope Filter: Reject specific queries explicitly asking for competitor data
        competitors = ['sbi', 'icici', 'axis', 'nippon', 'zerodha']
        if any(comp in query_lower for comp in competitors):
            return True, "I only have information about HDFC Mutual Fund schemes."
            
        # Gibberish/Short query check
        known_acronyms = ['sip', 'nav', 'aum', 'nfo', 'amc', 'mf', 'cagr', 'elss', 'hdfc']
        # If the input is less than 4 characters and not a known critical acronym
        if len(query_lower) < 4 and query_lower not in known_acronyms:
            return True, "I am a Mutual fund assistant. I can only provide factual information about HDFC Mutual Fund schemes and general mutual fund basics. Please ask a relevant mutual fund question."
             
        return False, ""

    def handle_educational_intent(self, query):
        """Hardcoded bypass for purely educational 'MF Basics' questions. Matches exact UI strings."""
        query_lower = query.lower().strip()
        
        # Exact definitions extracted from AMFI
        edu_kb = {
            "mutual fund": "A Mutual Fund is a trust that collects money from a number of investors who share a common investment objective. Then, it invests the money in equities, bonds, money market instruments and/or other securities. Each investor owns units, which represent a portion of the holdings of the fund. The income/gains generated from this collective investment is distributed proportionately amongst the investors after deducting certain expenses, by calculating a scheme's Net Asset Value (NAV).",
            "nav": "NAV (Net Asset Value) represents the market value per unit of a mutual fund scheme. It is calculated by taking the total market value of the assets of the fund, subtracting the liabilities, and dividing by the total number of outstanding units. It changes daily based on market movements.",
            "aum": "AUM (Assets Under Management) is the total market value of all the investments managed by a mutual fund scheme or the entire fund house. It indicates the size and scale of the fund.",
            "expense ratio": "The Expense Ratio is the annual fee that all mutual funds charge their unitholders. It covers the fund's operating expenses, including management fees, administrative costs, and distribution costs. A lower expense ratio means a higher portion of returns is passed on to the investor.",
            "exit load": "An Exit Load is a fee charged by a mutual fund company to an investor when they redeem (sell) their mutual fund units within a specific period after purchase. It is designed to discourage early withdrawals.",
            "sip": "SIP (Systematic Investment Plan) is a facility offered by mutual funds to investors to invest structurally. It allows an investor to invest a fixed amount of money at pre-defined intervals (like monthly or quarterly) in the selected mutual fund scheme.",
            "elss": "ELSS (Equity Linked Savings Scheme) is a type of mutual fund that invests primarily in equity markets and offers tax deductions under Section 80C of the Income Tax Act. It has a mandatory lock-in period of 3 years.",
            "liquidity": "Liquidity in mutual funds refers to how easily you can buy or sell your mutual fund units. Open-ended funds are highly liquid as you can redeem units directly with the fund house on any business day.",
            "index fund": "An Index Fund is a mutual fund that passively tracks the performance of a specific market index, like the Nifty 50 or Sensex. Its portfolio mirrors the index, aiming to match the index's returns rather than beat them.",
            "cagr": "CAGR (Compound Annual Growth Rate) is the mean annual growth rate of an investment over a specified period of time longer than one year. It smooths out the volatility of returns to show a steady rate of growth.",
            "direct plan": "A Direct Plan of a mutual fund is bought directly from the Mutual Fund Company without involving any distributor or broker. It has a lower expense ratio compared to regular plans, which can lead to slightly higher returns.",
            "benchmark": "A benchmark is a standard against which the performance of a mutual fund is measured. It is usually a market index (like Nifty 50) that represents the market or sector the fund invests in.",
            "capital gains tax": "Capital gains tax is the tax levied on the profit made from selling mutual fund units. For equity funds, short-term capital gains (sold < 1 year) are taxed at 15%, and long-term capital gains (sold > 1 year) above ₹1 Lakh are taxed at 10%.",
            "lock-in period": "A lock-in period is the time during which you cannot sell or redeem your mutual fund units. ELSS funds have a mandatory lock-in period of 3 years.",
            "fund manager": "A Fund Manager is a financial professional responsible for making investment decisions for a mutual fund scheme. They manage the portfolio to achieve the investment objective of the fund."
        }
        
        # 1. Exact UI Matches mapping (from frontend page.js)
        exact_matches = {
             "what is a mutual fund?": edu_kb["mutual fund"],
             "what is nav (net asset value)?": edu_kb["nav"],
             "what is aum (assets under management)?": edu_kb["aum"],
             "what is an expense ratio?": edu_kb["expense ratio"],
             "what is an exit load?": edu_kb["exit load"],
             "what is sip (systematic investment plan)?": edu_kb["sip"],
             "what is an elss fund?": edu_kb["elss"],
             "how does liquidity work in mutual funds?": edu_kb["liquidity"],
             "what is an index fund?": edu_kb["index fund"],
             "how is cagr calculated?": edu_kb["cagr"],
             "what is a direct plan vs regular plan?": edu_kb["direct plan"],
             "what is a mutual fund benchmark_?": edu_kb["benchmark"], # Catch potential trailing chars
             "what is capital gains tax on mutual funds?": edu_kb["capital gains tax"],
             "what is a lock-in period?": edu_kb["lock-in period"],
             "who is a fund manager?": edu_kb["fund manager"],
        }
        
        # Add clean versions without punctuation for robust matching
        clean_input = query_lower.replace("?", "").strip()
        for exact_q, ans in exact_matches.items():
            if clean_input == exact_q.replace("?", "").strip():
                return ans

        # 2. General Concept Match (Only if the query is strictly about definitions)
        # Avoid overriding specific scheme queries (e.g. "What is the exit load of HDFC Flexi Cap?")
        if len(query.split()) < 10:
            if "hdfc" not in query_lower:
                for k, v in edu_kb.items():
                    # Ensure it's asking purely about the concept
                    # e.g., "what is exit load", "what is exit load?"
                    clean_q = query_lower.replace("?", "").replace("the", "").strip()
                    if clean_q == f"what is {k}" or clean_q == f"what is an {k}" or clean_q == f"what is a {k}" or clean_q == f"what are {k}":
                        return f"{v}"
                    
        return None

    def call_gemini_fallback(self, system_prompt, user_prompt):
        """Fallback to Gemini 1.5 Flash when Groq is unavailable or rate-limited."""
        if not GEMINI_API_KEY:
            print("Gemini API key not found. Cannot fallback.")
            return None

        print("Calling Gemini 1.5 Flash Fallback...")
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Combine prompts for Gemini's structure
        full_content = f"{system_prompt}\n\nUser Query: {user_prompt}"
        
        payload = {
            "contents": [{
                "parts": [{"text": full_content}]
            }],
            "generationConfig": {
                "temperature": 0.1,
                "maxOutputTokens": 400
            }
        }
        
        try:
            response = requests.post(GEMINI_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            response_json = response.json()
            
            # Extract content from Gemini response
            if 'candidates' in response_json and len(response_json['candidates']) > 0:
                answer = response_json['candidates'][0]['content']['parts'][0]['text']
                return answer.strip()
            return None
        except Exception as e:
            print(f"Error calling Gemini fallback: {e}")
            return None

    def generate_answer(self, query):
        """Passes the retrieved context and query to Groq LLM with strict constraints."""
        
        # 1. PII and Hard Scope Check
        is_blocked, block_msg = self.is_pii_or_out_of_scope(query)
        if is_blocked:
            return block_msg, []
            
        # 1.5. Educational Intent Check
        edu_answer = self.handle_educational_intent(query)
        if edu_answer:
            amfi_url = "https://www.amfiindia.com/investor#knowledge-centre"
            answer = f"{edu_answer}\n\nLast updated from sources: AMFI Mutual Fund Knowledge Centre ({amfi_url})"
            return answer, [amfi_url]
            
        # 2. Retrieve FAISS context
        contexts, sources = self.retrieve_context(query)
        combined_context = "\n\n--- \n\n".join(contexts)
        
        # 3. Construct the Strict Prompt
        system_prompt = f"""You are a helpful mutual fund FAQ assistant named 'Mutual Fund Genie'.
You assist both retail beginners and professionals with questions about HDFC Mutual Fund schemes AND general mutual fund education.

You have two types of knowledge in your context:
1. SCHEME DATA: Factual data about the Top 5 HDFC schemes (Flexi Cap, ELSS Tax Saver, Mid-Cap Opportunities, Small Cap, Liquid Fund) - NAV, AUM, Expense Ratio, Exit Load, SIP amounts, Benchmark, Riskometer.
2. EDUCATIONAL DATA: General mutual fund concepts from AMFI/SEBI sources.

CRITICAL RULES:
1. ANSWER DIRECTLY: NEVER start responses with "According to the context", "Based on the provided information", or "The context states". Provide the answer directly and confidently.
2. FORMAT AS BULLETS: Present financial metrics (NAV, AUM, Expense Ratio, etc.) as clean bullet points for easy reading.
3. CONSOLIDATE DATA: If the context has multiple values for a metric (e.g. Regular vs Direct plan expense ratios), list them cleanly as bullet points. NEVER say "there are multiple instances in the context" or expose the underlying retrieval logic.
4. HDFC EXCLUSIVITY: NEVER output data about competitors (SBI, ICICI, Axis, Nippon, etc.), even if their names appear in the context. Ignore them entirely.
5. NO INVESTMENT ADVICE: State 'I cannot predict or compare performance returns.' if asked.
6. BE FACTUAL: Extract exact numbers from the context. Do not guess.
7. LENGTH LIMIT: Keep all answers very concise, to a maximum of 3 sentences. Do not ramble.
8. OUT OF SCOPE / NONSENSE: If the user query is gibberish, random letters (e.g. 'amu'), or completely unrelated to mutual funds, reply EXACTLY with: 'I am a Mutual fund assistant. I can only provide factual information about HDFC Mutual Fund schemes and general mutual fund basics. For any other questions, please refer to official sources.'

Context from documents:
{combined_context}
"""

        user_prompt = f"""
Using the provided context and rules, answer the following question:
User Query: {query}

Answer strictly according to the rules."""

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.1,  # Slight warmth allows clearer educational explanations
            "max_tokens": 400    # Raised from 150: educational answers need more room
        }
        
        if self.use_mock:
           # Fallback for local testing without spending API credits
           return "[MOCK] Extracted: " + combined_context[:100] + "...", sources
        
        print(f"Sending Query to Groq API ({MODEL_NAME})...")
        
        # ── Pre-compute clean sources so they're available in both success + error paths ──
        detected = detect_scheme(query)
        clean_sources = [SCHEME_USER_URL[detected]] if (detected and detected in SCHEME_USER_URL) else [INDMONEY_AMC_URL]
        
        for attempt in range(2):  # Retry once on 429 rate-limit
            try:
                response = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=30)
                
                # Handle rate-limit (429) with a short back-off then retry
                if response.status_code == 429 and attempt == 0:
                    print("Groq rate limit hit — waiting 5s before retry...")
                    time.sleep(5)
                    continue
                
                response.raise_for_status()
                response_json = response.json()
                answer = response_json['choices'][0]['message']['content']
                
                # ── User-facing source: single IndMoney scheme URL only ──────────
                # ETMoney/Groww are internal refs only (SCHEME_INTERNAL_REFS) — never shown.
                citation_str = ", ".join(clean_sources)
                formatted_answer = f"{answer.strip()}\n\nLast updated from sources: {citation_str}"
                return formatted_answer, clean_sources
                
            except Exception as e:
                print(f"Error calling Groq (attempt {attempt+1}): {e}")
                err_text = ""
                if hasattr(e, 'response') and e.response:
                    err_text = e.response.text
                    print(err_text)
                if attempt == 0:
                    time.sleep(3)
                    continue
                # Final failure — return friendly message with clean IndMoney sources
                err_str = str(e)
                
                # Check if we should try Gemini fallback
                # Only fallback on 429 or general connection failures after retries
                if attempt == 1:
                    fallback_answer = self.call_gemini_fallback(system_prompt, user_prompt)
                    if fallback_answer:
                        citation_str = ", ".join(clean_sources)
                        formatted_answer = f"{fallback_answer}\n\nLast updated from sources: {citation_str}"
                        return formatted_answer, clean_sources

                if '429' in err_str or (hasattr(e, 'response') and e.response and e.response.status_code == 429):
                     return "The AI server is currently receiving too many requests. Please wait a moment and try again.", clean_sources
                
                return "I couldn't reach the AI server right now. Please check your connection and try again in a moment.", clean_sources

if __name__ == "__main__":
    import os
    if not os.path.exists("Phase-3_Query_Generation"):
        os.makedirs("Phase-3_Query_Generation")
        
    rag = MutualFundRAG()
    
    # Run integration test
    print("\n--- Testing Phase 3 Pipeline ---")
    test_queries = [
        "What is the exit load for HDFC Flexi Cap?", # Factual extraction
        "What is a mutual fund?",                    # Beginner educational
        "Which is better, HDFC Flexi Cap or SBI Flexi Cap?", # Competitor/Scope failure
        "Should I invest my life savings in the HDFC liquid fund?" # Advice refusal failure
    ]
    
    for q in test_queries:
        print(f"\nQ: {q}")
        ans, srcs = rag.generate_answer(q)
        safe_ans = ans.encode('cp1252', errors='replace').decode('cp1252')
        print(f"A: {safe_ans}")
        if srcs:
            print("Citations:")
            for s in srcs:
               print(f" - {s}")
