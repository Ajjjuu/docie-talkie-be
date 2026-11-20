"""ORM models: chats, documents and messages.

Schema changes are made with Alembic migrations (see BE/alembic/versions/).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    title: Mapped[str] = mapped_column(String(200), default="New chat")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )

    # Deleting a chat deletes its documents and messages too
    documents: Mapped[list["Document"]] = relationship(
        back_populates="chat", cascade="all, delete-orphan", passive_deletes=True
    )
    messages: Mapped[list["Message"]] = relationship(
        back_populates="chat",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="Message.created_at",
    )


class Document(Base):
    __tablename__ = "documents"

    # Same id is stored in Chroma chunk metadata as doc_id
    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    chat_id: Mapped[str] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), index=True
    )
    filename: Mapped[str] = mapped_column(String(255))  # original name shown in the UI
    file_path: Mapped[str] = mapped_column(String(500))  # where the PDF is saved on disk
    num_pages: Mapped[int | None] = mapped_column(Integer)
    num_chunks: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="processing")  # processing | ready | failed
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chat: Mapped[Chat] = relationship(back_populates="documents")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_uuid)
    chat_id: Mapped[str] = mapped_column(
        ForeignKey("chats.id", ondelete="CASCADE"), index=True
    )
    role: Mapped[str] = mapped_column(String(20))  # user | assistant
    content: Mapped[str] = mapped_column(Text)
    # Assistant answers only: [{doc_id, filename, page, chunk_id, score}, ...]
    sources: Mapped[list | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    chat: Mapped[Chat] = relationship(back_populates="messages")
