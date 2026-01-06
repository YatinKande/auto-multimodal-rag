
from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str

class Source(BaseModel):
    filename: str
    page: Optional[int] = None
    type: str # "text" or "image_description"
    content_preview: str

class ChatResponse(BaseModel):
    answer: str
    sources: List[Source]
    status: str
    error: Optional[str] = None
