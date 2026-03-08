import json
import re
import os
import csv

# We will read the extracted_corpus.json and parse out specific structured facts via regex 

def extract_structured_data(text):
    """
    Extracts financial metrics directly from the injected 'FACT SHEET' block.
    """
    structured_data = {}
    
    # Expense Ratio
    expense = re.search(r'Expense Ratio:\s*(.*?%)', text, re.IGNORECASE)
    structured_data['Expense Ratio'] = expense.group(1).strip() if expense else "Not Found"

    # Exit Load
    exit_load = re.search(r'Exit Load:\s*(.*?)\n', text, re.IGNORECASE)
    structured_data['Exit Load'] = exit_load.group(1).strip() if exit_load else "Not Found"

    # Minimum SIP
    min_sip = re.search(r'Minimum SIP:\s*([^\n]+)', text, re.IGNORECASE)
    structured_data['Minimum SIP'] = min_sip.group(1).strip() if min_sip else "Not Found"

    # Riskometer
    risk = re.search(r'Risk Rating:\s*([^\n]+)', text, re.IGNORECASE)
    structured_data['Riskometer'] = risk.group(1).strip() if risk else "Not Found"

    # AUM / Fund Size
    aum = re.search(r'AUM \(Fund Size\):\s*([^\n]+)', text, re.IGNORECASE)
    structured_data['AUM'] = aum.group(1).strip() if aum else "Not Found"
    
    # NAV
    nav = re.search(r'NAV:\s*([^\n]+)', text, re.IGNORECASE)
    structured_data['NAV'] = nav.group(1).strip() if nav else "Not Found"
    
    return structured_data

def process_knowledge_base():
    # Robust absolute path handling
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corpus_path = os.path.join(base_dir, "Phase_1_Data_Ingestion", "extracted_corpus.json")
    
    if not os.path.exists(corpus_path):
        print(f"Error: {corpus_path} not found. Please run scraper.py first.")
        return

    with open(corpus_path, "r", encoding="utf-8") as f:
        corpus = json.load(f)
        
    structured_results = []
    vector_chunks = []
    
    print("Starting Phase 2: Knowledge Base Processing\n===========================================")
    
    for i, doc in enumerate(corpus):
        scheme = doc['scheme_name']
        source = doc['source_url']
        text = doc['content']
        
        # 1. Store structured metadata
        structured_metadata = extract_structured_data(text)
        
        structured_row = {
            "Scheme Name": scheme,
            "Source URL": source,
            **structured_metadata
        }
        structured_results.append(structured_row)
        
        # Inject highly dense structured fact chunk into FAISS
        fact_chunk = (
            f"[{scheme}] FACT SHEET: "
            f"NAV is {structured_metadata.get('NAV', 'N/A')}. "
            f"Expense Ratio is {structured_metadata.get('Expense Ratio', 'N/A')}. "
            f"Exit Load is {structured_metadata.get('Exit Load', 'N/A')}. "
            f"Minimum SIP is {structured_metadata.get('Minimum SIP', 'N/A')}. "
            f"Riskometer is {structured_metadata.get('Riskometer', 'N/A')}. "
            f"AUM (Fund Size) is {structured_metadata.get('AUM', 'N/A')}."
        )
        vector_chunks.append({
            "id": f"chunk_{i}_facts",
            "scheme": scheme,
            "source": source,
            "text": fact_chunk
        })
        
        # 2. Chunking the raw textual narrative
        sentences = [s.strip() for s in text.split('.') if len(s.strip()) > 10]
        
        current_chunk = ""
        for sentence in sentences:
            if len(current_chunk) + len(sentence) < 800:
                current_chunk += sentence + ". "
            else:
                vector_chunks.append({
                    "id": f"chunk_{i}_{len(vector_chunks)}",
                    "scheme": scheme,
                    "source": source,
                    "text": f"[{scheme}] {current_chunk.strip()}"
                })
                current_chunk = sentence + ". "
                
        if current_chunk:
             vector_chunks.append({
                    "id": f"chunk_{i}_{len(vector_chunks)}",
                    "scheme": scheme,
                    "source": source,
                    "text": f"[{scheme}] {current_chunk.strip()}"
                })
                
    # Save files in the Phase 2 directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    csv_path = os.path.join(current_dir, "structured_store.csv")
    with open(csv_path, "w", newline='', encoding="utf-8") as csvfile:
        fieldnames = ["Scheme Name", "NAV", "Expense Ratio", "Exit Load", "Minimum SIP", "Riskometer", "AUM", "Source URL"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in structured_results:
            writer.writerow(row)
            
    vector_path = os.path.join(current_dir, "vector_store_chunks.json")
    with open(vector_path, "w", encoding="utf-8") as vfile:
        json.dump(vector_chunks, vfile, indent=4)
        
    print(f"Generated Structured Store: {csv_path}")
    print(f"Generated Vector Store Objects: {vector_path}")

if __name__ == "__main__":
    process_knowledge_base()
