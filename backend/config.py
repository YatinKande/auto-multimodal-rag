
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    UPLOAD_DIR = "data/uploads"
    FAISS_INDEX_PATH = "data/faiss_index/index.faiss"
    METADATA_PATH = "data/faiss_index/metadata.json"
    EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
    OLLAMA_BASE_URL = "http://localhost:11434"
