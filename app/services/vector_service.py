import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./data/chroma_db")
default_ef = embedding_functions.DefaultEmbeddingFunction()

def save_to_vector_db(project_id: str, chunks: list, filename: str):
    collection = client.get_or_create_collection(
        name=f"project_{project_id}", 
        embedding_function=default_ef
    )
    ids = [f"{filename}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename} for _ in chunks]
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    return len(ids)

import chromadb
from chromadb.utils import embedding_functions

client = chromadb.PersistentClient(path="./data/chroma_db")

ollama_ef = embedding_functions.OllamaEmbeddingFunction(
    url="http://localhost:11434/api/embeddings",
    model_name="nomic-embed-text"
)

def save_to_vector_db(project_id: str, chunks: list, filename: str):
    collection = client.get_or_create_collection(
        name=f"project_{project_id}", 
        embedding_function=ollama_ef
    )
    ids = [f"{filename}_{i}" for i in range(len(chunks))]
    metadatas = [{"source": filename} for _ in chunks]
    collection.add(documents=chunks, metadatas=metadatas, ids=ids)
    return len(ids)

# --- NEW FUNCTION: Data Management ---
def delete_project(project_id: str):
    """Deletes a collection and all its vectors to free up space."""
    try:
        client.delete_collection(name=f"project_{project_id}")
        return True
    except Exception:
        return False # Collection likely didn't exist
    
def get_project_documents(project_id: str):
    """Retrieves a list of unique filenames stored in the project."""
    try:
        # Grab the collection
        collection = client.get_collection(name=f"project_{project_id}", embedding_function=ollama_ef)
        # Fetch all metadata
        data = collection.get(include=["metadatas"])
        
        # Extract unique filenames using a Set
        unique_files = set()
        for meta in data['metadatas']:
            if meta and 'source' in meta:
                unique_files.add(meta['source'])
                
        return list(unique_files)
    except Exception:
        # If the collection doesn't exist yet, return an empty list
        return []