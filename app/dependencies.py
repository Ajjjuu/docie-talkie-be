"""FastAPI dependencies: hand each route the services it needs.

The heavy objects (vector store, chunker, query engine...) are created once at
startup in main.py and kept on app.state. The services are cheap, so a new one
is made for every request with that request's DB session.
"""

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.rag.query import QueryEngine
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService


def get_chat_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


def get_document_service(request: Request, db: Session = Depends(get_db)) -> DocumentService:
    state = request.app.state
    return DocumentService(db, state.vector_store, state.pdf_loader, state.chunker)


def get_query_engine(request: Request) -> QueryEngine:
    return request.app.state.query_engine
