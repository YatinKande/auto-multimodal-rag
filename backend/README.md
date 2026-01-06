# AutoRAG Diagnostic Assistant - Backend

This folder contains the "brain" of the application. It runs on Python and handles all the logic, database storage, and AI connections.

## Code File Explanations

### `main.py` (The Server)
This is the entry point of the application. It uses **FastAPI** to create a web server.
- **What it does:** It listens for requests from the frontend (like "upload file" or "ask question") and routes them to the right logic.
- **Simple analogy:** It's like the receptionist at a clinic who takes your name and directs you to the right doctor.

### `ingestion.py` (The Reader)
This file handles reading and understanding the files you upload.
- **What it does:** It opens PDFs, DOCX, and images. If it finds text, it saves it. If it finds an **image** (like a diagram), it uses **Ollama (Llama 3.2 Vision)** to look at the image and write a text description of it.
- **Simple analogy:** The assistant who reads all the manuals and diagnostic charts and takes detailed notes so the doctor doesn't have to read everything from scratch.

### `rag_engine.py` (The Thinker)
This contains the core logic for the RAG (Retrieval-Augmented Generation) system.
- **What it does:**
    1.  **Retrieval:** When you ask a question, it searches the database (FAISS) for the most relevant notes/chunks.
    2.  **Generation:** It sends your question + the found notes to **Google Gemini**.
    3.  **Fallback:** If Google Gemini fails (quota issues), it automatically switches to **Ollama (Llama 3)** running locally.
- **Simple analogy:** This is the doctor. It looks at the patient's symptoms (your question), checks the medical library (retrieved docs), and gives a diagnosis.

### `models.py` (The Data Shapes)
This defines what the data looks like.
- **What it does:** It ensures that when the frontend sends a "question", it actually contains text, and when the backend sends an "answer", it includes the source files.
- **Simple analogy:** The standard forms you fill out at the hospital.

### `config.py` (The Settings)
This stores configuration variables.
- **What it does:** It loads secret keys (like your Google API Key) and file paths so they aren't hardcoded in the main logic.
- **Simple analogy:** The rulebook or settings menu.
