"""Chats router: create a chat, list chats, open one chat.

A chat is the container for everything else: its PDFs and its messages
all belong to one chat_id.

Endpoints:
  POST /api/chats/create-chat            start a new, empty chat
  GET  /api/chats/list-chats             all chats, for the sidebar
  GET  /api/chats/get-chat/{chat_id}     one chat with its documents and messages

Called from the frontend by: FE/src/api/chats.js
The work is done by: app/services/chat_service.py (ChatService)
"""

from fastapi import APIRouter, Depends

from app.dependencies import get_chat_service
from app.schemas import ChatDetail, ChatOut
from app.services.chat_service import ChatService

router = APIRouter(prefix="/chats", tags=["chats"])


@router.post("/create-chat", response_model=ChatOut, status_code=201)
def create_chat(chat_service: ChatService = Depends(get_chat_service)):
    """Start a new, empty chat.

    Triggered by: the "+ New chat" button (Sidebar -> App.handleNewChat -> createChat()),
    or by uploading a PDF when no chat is open.

    Steps:
      1. ChatService.create_chat() inserts a row into the chats table.
         The chat_id (a uuid) and the title "New chat" are set automatically.
      2. Return the new chat. The frontend uses its id for every later call.
    """
    return chat_service.create_chat()


@router.get("/list-chats", response_model=list[ChatOut])
def list_chats(chat_service: ChatService = Depends(get_chat_service)):
    """List all chats, most recently used first.

    Triggered by: the page loading, and again after every answer
    (the title or the order may have changed).

    Steps:
      1. ChatService.list_chats() reads the chats table, sorted by updated_at (newest first).
    """
    return chat_service.list_chats()


@router.get("/get-chat/{chat_id}", response_model=ChatDetail)
def get_chat(chat_id: str, chat_service: ChatService = Depends(get_chat_service)):
    """Open one chat: return it with all of its documents and messages.

    Triggered by: clicking a chat in the sidebar (Sidebar -> App.handleSelectChat -> getChat()).

    Steps:
      1. ChatService.get_chat() loads the chat row, or returns 404 if it doesn't exist.
      2. Its documents and messages come along through the ORM relationships (oldest first).
    """
    return chat_service.get_chat(chat_id)
