# models/chat.py
from pydantic import BaseModel
from typing import List, Optional


class ChatMessage(BaseModel):
    message: str
    is_ai: bool
    similarity: Optional[float] = None
