"""Document endpoints.

Phase 2:
  POST /api/chats/{chat_id}/documents   upload and index a PDF
  GET  /api/chats/{chat_id}/documents   list documents in a chat
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chats/{chat_id}/documents", tags=["documents"])
