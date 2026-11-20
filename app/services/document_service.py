"""Handles PDF uploads: save the file, record it in SQLite, index it in Chroma."""

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.db.models import Document
from app.rag.chunker import TextChunker
from app.rag.pdf_loader import PDFLoader
from app.rag.vector_store import VectorStore


class DocumentService:
    def __init__(
        self,
        db: Session,
        vector_store: VectorStore,
        loader: PDFLoader,
        chunker: TextChunker,
    ):
        self.db = db
        self.vector_store = vector_store
        self.loader = loader
        self.chunker = chunker

    def upload(self, chat_id: str, file: UploadFile) -> Document:
        """Validate, save to disk, load + chunk + embed, then mark the document ready."""
        raise NotImplementedError

    def list_documents(self, chat_id: str) -> list[Document]:
        """All documents in a chat."""
        raise NotImplementedError

    def delete_document(self, doc_id: str) -> None:
        """Remove the document row, its vectors and its file."""
        raise NotImplementedError
