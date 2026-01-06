
#!/bin/bash

# Check if .venv exists
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r backend/requirements.txt
else
    source .venv/bin/activate
fi

# Check for .env
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    echo "GOOGLE_API_KEY=your_key_here" > .env
    echo "Please edit .env and add your GOOGLE_API_KEY"
fi

echo "Starting AutoRAG Diagnostic Assistant..."
echo "Ensure Ollama is running (ollama serve) and you have pulled models (ollama pull llava, ollama pull llama3)"
echo "App will be available at http://127.0.0.1:8000"

uvicorn backend.main:app --reload
