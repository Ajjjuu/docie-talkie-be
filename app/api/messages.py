"""Message endpoints.

Phase 2:
  POST /api/chats/{chat_id}/messages   ask a question, get an answer with sources
  GET  /api/chats/{chat_id}/messages   chat history
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chats/{chat_id}/messages", tags=["messages"])
