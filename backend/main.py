
import os
import shutil
from typing import List
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from backend.rag_engine import RAGEngine
from backend.ingestion import IngestionEngine
from backend.models import ChatRequest, ChatResponse
from backend.config import Config

app = FastAPI(title="AutoRAG Diagnostic Assistant")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Engines
rag_engine = RAGEngine()
ingestion_engine = IngestionEngine()

# Ensure upload directory exists
os.makedirs(Config.UPLOAD_DIR, exist_ok=True)

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "faiss_index_size": rag_engine.index.ntotal if rag_engine.index else 0,
        "ollama": "configured", # Could add real check here
        "google_genai": "configured" if Config.GOOGLE_API_KEY else "missing_key"
    }

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    results = []
    for file in files:
        safe_filename = os.path.basename(file.filename)
        file_path = os.path.join(Config.UPLOAD_DIR, safe_filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        try:
            # Process & Ingest
            chunks = ingestion_engine.process_file(file_path, safe_filename)
            rag_engine.add_documents(chunks)
            results.append({"filename": safe_filename, "status": "indexed", "chunks": len(chunks)})
        except Exception as e:
            results.append({"filename": safe_filename, "status": "error", "detail": str(e)})
            
    return {"results": results}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        response = rag_engine.generate_answer(request.question)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/list_uploaded")
async def list_uploaded():
    return {"files": rag_engine.list_uploaded_files()}

# Mount Frontend (Static Files)
# We will create this directory next
if os.path.isdir("frontend"):
    app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
