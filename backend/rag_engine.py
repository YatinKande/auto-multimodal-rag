
import os
import json
import faiss
import numpy as np
import ollama
from typing import List, Dict, Any, Tuple
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from backend.config import Config

class RAGEngine:
    def __init__(self):
        self.encoder = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.dimension = 384 # Dimension for all-MiniLM-L6-v2
        self.index = None
        self.metadata = [] # List of dicts, index corresponds to FAISS ID
        
        # Setup Google GenAI
        if Config.GOOGLE_API_KEY:
            genai.configure(api_key=Config.GOOGLE_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
        else:
            self.model = None
            print("Warning: GOOGLE_API_KEY not found. Generation will fail.")
            
        self._load_index()

    def _load_index(self):
        if os.path.exists(Config.FAISS_INDEX_PATH):
            self.index = faiss.read_index(Config.FAISS_INDEX_PATH)
            if os.path.exists(Config.METADATA_PATH):
                with open(Config.METADATA_PATH, 'r') as f:
                    self.metadata = json.load(f)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            self.metadata = []

    def _save_index(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(Config.FAISS_INDEX_PATH), exist_ok=True)
        faiss.write_index(self.index, Config.FAISS_INDEX_PATH)
        with open(Config.METADATA_PATH, 'w') as f:
            json.dump(self.metadata, f)

    def add_documents(self, chunks: List[Dict[str, Any]]):
        if not chunks:
            return
            
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.encoder.encode(texts)
        
        # Add to FAISS
        self.index.add(np.array(embeddings).astype('float32'))
        
        # Add metadata
        for chunk in chunks:
            self.metadata.append({
                "text": chunk["text"],
                "source": chunk["metadata"]
            })
            
        self._save_index()

    def list_uploaded_files(self) -> List[str]:
        files = set()
        for item in self.metadata:
            if "filename" in item["source"]:
                files.add(item["source"]["filename"])
        return list(files)

    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        query_vector = self.encoder.encode([query]).astype('float32')
        D, I = self.index.search(query_vector, k)
        
        results = []
        for i in range(k):
            idx = I[0][i]
            if idx != -1 and idx < len(self.metadata):
                results.append(self.metadata[idx])
        return results

    def generate_answer(self, query: str) -> Dict[str, Any]:
        retrieved_docs = self.search(query)
        context = "\n\n".join([f"Source ({doc['source'].get('filename', 'unknown')}): {doc['text']}" for doc in retrieved_docs])
        
        sources_list = []
        for doc in retrieved_docs:
            sources_list.append({
                "filename": doc['source'].get('filename', 'unknown'),
                "page": doc['source'].get('page'),
                "type": doc['source'].get('type'),
                "content_preview": doc['text'][:100] + "..."
            })

        # Prompt Engineering
        prompt = f"""You are an expert Automotive Diagnostic Assistant. 
        Answer the specific question using strictly the provided context. 
        If the context does not contain the answer, say "I cannot find the answer in the provided documents."
        
        Context:
        {context}
        
        Question: {query}
        
        Answer:"""

        try:
            if self.model:
                response = self.model.generate_content(prompt)
                return {
                    "answer": response.text,
                    "sources": sources_list,
                    "status": "success"
                }
            else:
                 return {
                    "answer": "[Error: No Google API Key] " + self._fallback_extractive(retrieved_docs),
                    "sources": sources_list,
                    "status": "fallback_no_key"
                }

        except Exception as e:
            print(f"GenAI Error: {e}")
            # Fallback to Ollama
            try:
                print("Attempting fallback to local Ollama (llama3)...")
                ollama_response = ollama.chat(model='llama3', messages=[
                    {'role': 'system', 'content': f"You are an expert Automotive Diagnostic Assistant. Answer strictly based on the provided context. If the answer is not in the context, say so.\n\nContext:\n{context}"},
                    {'role': 'user', 'content': query}
                ])
                return {
                    "answer": f"[Ollama Fallback] {ollama_response['message']['content']}",
                    "sources": sources_list,
                    "status": "success_ollama"
                }
            except Exception as ollama_e:
                print(f"Ollama Error: {ollama_e}")
                return {
                    "answer": f"[All AI Failed. Google: {str(e)} | Ollama: {str(ollama_e)}] " + self._fallback_extractive(retrieved_docs),
                    "sources": sources_list,
                    "status": "fallback_error"
                }

    def _fallback_extractive(self, docs) -> str:
        return "Here is the most relevant information found:\n" + "\n".join([f"- {d['text']}" for d in docs])
