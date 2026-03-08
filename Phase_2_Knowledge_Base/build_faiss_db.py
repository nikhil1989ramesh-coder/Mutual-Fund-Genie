import json
import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

def build_vector_store():
    # Robust absolute path handling
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load the SentenceTransformer model
    print("Loading embedding model (all-MiniLM-L6-v2)...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # 2. Load the vector chunks
    chunks_path = os.path.join(current_dir, "vector_store_chunks.json")
    if not os.path.exists(chunks_path):
        print(f"Error: {chunks_path} not found. Please run processor.py first.")
        return
        
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    print(f"Encoding {len(chunks)} chunks into embeddings...")
    
    # 3. Prepare texts and metadata
    documents = [chunk["text"] for chunk in chunks]
    metadatas = [{"scheme_name": c["scheme"], "source_url": c["source"]} for c in chunks]
    
    # Generate embeddings
    embeddings = model.encode(documents, show_progress_bar=True)
    embeddings = np.array(embeddings).astype('float32')
    
    # 4. Initialize FAISS Index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    
    # 5. Add embeddings
    index.add(embeddings)
    
    # 6. Save the Index and Metadata
    faiss_path = os.path.join(current_dir, "faiss_index.bin")
    metadata_path = os.path.join(current_dir, "faiss_metadata.json")
    
    faiss.write_index(index, faiss_path)
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadatas, f, indent=4)
        
    print("====================================")
    print(f"FAISS Vector Store built: {faiss_path}")
    print(f"Total indexed: {index.ntotal}")

if __name__ == "__main__":
    build_vector_store()
