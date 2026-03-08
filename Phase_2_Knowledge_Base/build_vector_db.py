import json
import os
import chromadb
from chromadb.utils import embedding_functions

def build_vector_store():
    # 1. Initialize ChromaDB client with persistent local storage
    db_path = os.path.join(os.getcwd(), "chroma_db")
    client = chromadb.PersistentClient(path=db_path)
    
    # 2. Setup the embedding function (Using a fast, default SentenceTransformer model)
    # This model 'all-MiniLM-L6-v2' is standard, local, and excellent for basic RAG.
    sentence_transformer_ef = embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    
    # 3. Create or get the collection
    collection_name = "hdfc_mutual_funds"
    try:
        # Try to delete if it exists so we start fresh for this run
        client.delete_collection(name=collection_name)
    except ValueError:
        pass
        
    collection = client.create_collection(
        name=collection_name, 
        embedding_function=sentence_transformer_ef
    )
    
    # 4. Load the vector chunks we prepared in the earlier Phase 2 script
    chunks_path = "vector_store_chunks.json"
    if not os.path.exists(chunks_path):
        print(f"Error: {chunks_path} not found. Please run processor.py first.")
        return
        
    with open(chunks_path, "r", encoding="utf-8") as f:
        chunks = json.load(f)
        
    print(f"Loading {len(chunks)} chunks into ChromaDB at {db_path}...")
    
    # 5. Prepare data for Chroma ingestion
    ids = []
    documents = []
    metadatas = []
    
    for chunk in chunks:
        ids.append(chunk["id"])
        documents.append(chunk["text"])
        metadatas.append({
            "scheme_name": chunk["scheme"],
            "source_url": chunk["source"]
        })
        
    # 6. Add to Vector DB in batches to prevent memory spikes
    batch_size = 100
    for i in range(0, len(ids), batch_size):
        end = min(i + batch_size, len(ids))
        print(f"Inserting batch {i} to {end}...")
        collection.add(
            ids=ids[i:end],
            documents=documents[i:end],
            metadatas=metadatas[i:end]
        )
        
    print("====================================")
    print("Vector Store successfully built and populated!")
    print(f"Total documents in collection: {collection.count()}")
    
    # Quick sanity check retrieval
    print("\n--- Test Retrieval ---")
    results = collection.query(
        query_texts=["What is the exit load for HDFC Flexi Cap?"],
        n_results=1
    )
    print(f"Retrieved Document: {results['documents'][0][0]}")
    print(f"Source metadata: {results['metadatas'][0][0]}")

if __name__ == "__main__":
    build_vector_store()
