"""Pydantic models for API requests and responses."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class HealthResponse(BaseModel):
    status: str  # "ok" when everything works, otherwise "degraded"
    db: str
    chroma: str
    collection_count: int | None = None


# from_attributes lets these be built straight from ORM objects
class ChatOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime
    updated_at: datetime


class DocumentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    filename: str
    num_pages: int | None
    num_chunks: int | None
    status: str
    error: str | None
    created_at: datetime


class Source(BaseModel):
    doc_id: str
    filename: str
    page: int
    chunk_id: str
    score: float


class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    chat_id: str
    role: str
    content: str
    sources: list[Source] | None
    created_at: datetime


class ChatDetail(ChatOut):
    documents: list[DocumentOut]
    messages: list[MessageOut]


class AskRequest(BaseModel):
    question: str


class AskResponse(BaseModel):
    question: MessageOut
    answer: MessageOut
