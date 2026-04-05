from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil, os
from pathlib import Path
from pydantic import BaseModel
from app.services.pdf_service import ingest_and_chunk_pdf
from app.services.vector_service import save_to_vector_db, delete_project, get_project_documents
from app.services.verify_service import verify_claim_locally

app = FastAPI(title="ScholarQA")
UPLOAD_DIR = Path("temp_uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

class ClaimRequest(BaseModel):
    claim: str

@app.post("/ingest/{project_id}")
async def ingest(project_id: str, file: UploadFile = File(...)):
    temp_path = UPLOAD_DIR / file.filename
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    chunks = ingest_and_chunk_pdf(str(temp_path))
    num_chunks = save_to_vector_db(project_id, chunks, file.filename)
    os.remove(temp_path)
    return {"status": "success", "chunks": num_chunks}

@app.post("/verify/{project_id}")
async def verify(project_id: str, request: ClaimRequest):
    try:
        # Now returns the dict containing "report" and "raw_chunks"
        data = verify_claim_locally(project_id, request.claim)
        return data 
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: List Documents Endpoint ---
@app.get("/projects/{project_id}/documents")
async def list_documents(project_id: str):
    try:
        docs = get_project_documents(project_id)
        return {"status": "success", "documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- NEW: Delete Project Endpoint ---
@app.delete("/projects/{project_id}")
async def remove_project(project_id: str):
    success = delete_project(project_id)
    if success:
        return {"status": "success", "message": f"Project {project_id} deleted"}
    else:
        raise HTTPException(status_code=404, detail="Project not found")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)