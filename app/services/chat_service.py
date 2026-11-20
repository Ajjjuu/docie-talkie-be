"""Reads and writes chats and messages in SQLite."""

from sqlalchemy.orm import Session

from app.db.models import Chat, Message


class ChatService:
    def __init__(self, db: Session):
        self.db = db

    def create_chat(self) -> Chat:
        """Create an empty chat with a new chat_id."""
        raise NotImplementedError

    def list_chats(self) -> list[Chat]:
        """All chats, newest first."""
        raise NotImplementedError

    def get_chat(self, chat_id: str) -> Chat:
        """One chat with its documents and messages (404 if missing)."""
        raise NotImplementedError

    def add_message(self, chat_id: str, role: str, content: str, sources: list | None = None) -> Message:
        """Save a user question or an assistant answer."""
        raise NotImplementedError

    def get_messages(self, chat_id: str) -> list[Message]:
        """Full history of a chat, oldest first."""
        raise NotImplementedError

    def get_history(self, chat_id: str, limit: int = 6) -> list[dict]:
        """Last few messages as {"role", "content"} dicts, for the LLM prompt."""
        raise NotImplementedError
