"""Reads and writes chats and messages in SQLite."""

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chat, Message, utc_now

DEFAULT_TITLE = "New chat"
TITLE_LENGTH = 50


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_chat(self) -> Chat:
        """Create an empty chat. Its chat_id (uuid) is generated automatically."""
        chat = Chat(title=DEFAULT_TITLE)
        self.db.add(chat)
        self.db.commit()
        return chat

    def list_chats(self) -> list[Chat]:
        """All chats, most recently used first."""
        query = select(Chat).order_by(Chat.updated_at.desc())
        return list(self.db.scalars(query))

    def get_chat(self, chat_id: str) -> Chat:
        """One chat with its documents and messages. Raises 404 if it doesn't exist."""
        chat = self.db.get(Chat, chat_id)
        if chat is None:
            raise HTTPException(status_code=404, detail="Chat not found")
        return chat

    def add_message(self, chat_id: str, role: str, content: str, sources: list | None = None) -> Message:
        """Save a user question or an assistant answer."""
        chat = self.get_chat(chat_id)

        # The first question becomes the chat's title in the sidebar
        if role == "user" and chat.title == DEFAULT_TITLE:
            chat.title = " ".join(content.split())[:TITLE_LENGTH]

        message = Message(chat_id=chat_id, role=role, content=content, sources=sources)
        self.db.add(message)
        chat.updated_at = utc_now()  # moves the chat to the top of the list
        self.db.commit()
        return message

    def get_messages(self, chat_id: str) -> list[Message]:
        """Full history of a chat, oldest first."""
        return self.get_chat(chat_id).messages

    def get_history(self, chat_id: str, limit: int = 6) -> list[dict]:
        """The last few messages as {"role", "content"} dicts, for the LLM prompt."""
        recent = self.get_messages(chat_id)[-limit:]
        return [{"role": message.role, "content": message.content} for message in recent]
