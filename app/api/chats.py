"""Chat endpoints.

Phase 2:
  POST /api/chats             create a chat
  GET  /api/chats             list chats (newest first)
  GET  /api/chats/{chat_id}   one chat with its documents and messages
"""

from fastapi import APIRouter

router = APIRouter(prefix="/chats", tags=["chats"])
