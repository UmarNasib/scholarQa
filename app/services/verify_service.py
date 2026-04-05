import ollama
from app.services.vector_service import client, ollama_ef

def verify_claim_locally(project_id: str, claim: str):
    collection = client.get_collection(name=f"project_{project_id}", embedding_function=ollama_ef)
    
    # Retrieve top 5 most relevant chunks and their metadata
    results = collection.query(query_texts=[claim], n_results=5)
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]

    # --- NEW: Traceability (Attach filenames to chunks) ---
    context_blocks = []
    for idx, (doc, meta) in enumerate(zip(documents, metadatas)):
        source_name = meta.get("source", "Unknown PDF")
        context_blocks.append(f"[SOURCE FILE: {source_name}]\n{doc}")

    full_context = "\n\n---\n\n".join(context_blocks)

    # --- NEW: Advanced Prompting ---
    prompt = f"""
    You are a strict, objective Academic Research Auditor. 
    Verify the user's CLAIM against the provided CONTEXT.

    CLAIM: {claim}

    CONTEXT:
    {full_context}

    INSTRUCTIONS:
    1. If the CONTEXT does not contain enough information to verify the claim, you MUST set the VERDICT to "Not Found". Do not guess or use outside knowledge.
    2. Otherwise, set VERDICT to "Supports", "Contradicts", or "Neutral".
    3. Provide a brief REASONING based strictly on the text.
    4. Provide an EVIDENCE quote and state the [SOURCE FILE] it came from.

    Format strictly as:
    VERDICT: [Verdict]
    REASONING: [Your explanation]
    EVIDENCE: [Quote] - [Source File]
    """
    
    response = ollama.generate(model='llama3', prompt=prompt)
    
    # Return both the LLM report AND the raw chunks for transparency
    return {
        "report": response['response'],
        "raw_chunks": context_blocks 
    }