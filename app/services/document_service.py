"""Handles PDF uploads: save the file, record it in SQLite, index it in Chroma."""

from fastapi import HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import Document, new_uuid
from app.rag.chunker import TextChunker
from app.rag.pdf_loader import PDFLoader
from app.rag.vector_store import VectorStore


class DocumentService:
    def __init__(self, db: Session, vector_store: VectorStore, loader: PDFLoader, chunker: TextChunker):
        self.db = db
        self.vector_store = vector_store
        self.loader = loader
        self.chunker = chunker

    def upload(self, chat_id: str, file: UploadFile) -> Document:
        """Save the PDF, then load + chunk + embed it. Returns the document with its final status."""
        content = file.file.read()
        self.validate(file.filename, content)

        # 1. Save the original file as data/uploads/{doc_id}.pdf
        doc_id = new_uuid()
        file_path = settings.upload_path / f"{doc_id}.pdf"
        file_path.write_bytes(content)

        # 2. Record it in SQLite as "processing"
        document = Document(
            id=doc_id,
            chat_id=chat_id,
            filename=file.filename,
            # Stored the way UPLOAD_DIR is written in .env (relative to BE/ by default),
            # so the project folder can be moved without breaking these paths
            file_path=f"{settings.upload_dir}/{doc_id}.pdf",
            status="processing",
        )
        self.db.add(document)
        self.db.commit()

        # 3. Read, chunk and embed it
        try:
            pages = self.loader.load(file_path)
            chunks = self.chunker.split(pages)
            if not chunks:
                raise ValueError("No text found in this PDF. Scanned (image-only) PDFs aren't supported yet.")

            self.vector_store.add_chunks(chat_id, doc_id, file.filename, chunks)

            document.num_pages = len(pages)
            document.num_chunks = len(chunks)
            document.status = "ready"
        except Exception as error:
            # Keep the row so the UI can show what went wrong, but drop any half-saved vectors
            self.vector_store.delete_document(doc_id)
            document.status = "failed"
            document.error = str(error)

        self.db.commit()
        return document

    def validate(self, filename: str | None, content: bytes) -> None:
        """Reject files that aren't PDFs or are too big."""
        # Every PDF file starts with the bytes "%PDF"
        if not filename or not filename.lower().endswith(".pdf") or not content.startswith(b"%PDF"):
            raise HTTPException(status_code=400, detail="Only PDF files are supported.")

        max_bytes = settings.max_upload_mb * 1024 * 1024
        if len(content) > max_bytes:
            raise HTTPException(status_code=413, detail=f"File is larger than {settings.max_upload_mb} MB.")

    def list_documents(self, chat_id: str) -> list[Document]:
        """All documents in a chat, oldest first."""
        query = select(Document).where(Document.chat_id == chat_id).order_by(Document.created_at)
        return list(self.db.scalars(query))
