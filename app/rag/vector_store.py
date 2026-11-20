"""Stores and searches chunk vectors in a persistent ChromaDB collection.

Every chunk has:
  id       = "{doc_id}:{chunk_index}"
  metadata = {chat_id, doc_id, filename, page, chunk_index}
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_core.documents import Document

from app.rag.embedding import Embedder


class VectorStore:
    def __init__(self, persist_dir: Path, collection_name: str, embedder: Embedder | None = None):
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        # Cosine distance can only be chosen when the collection is first created.
        # It makes scores easy to read later: similarity = 1 - distance.
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
        self.embedder = embedder

    def count(self) -> int:
        """Total number of chunks stored."""
        return self.collection.count()

    def add_chunks(self, chat_id: str, doc_id: str, filename: str, chunks: list[Document]) -> None:
        """Embed and store all chunks of one document."""
        raise NotImplementedError

    def search(self, chat_id: str, query: str, k: int) -> list[tuple[Document, float]]:
        """Return the k most similar chunks in this chat, with similarity scores."""
        raise NotImplementedError

    def delete_document(self, doc_id: str) -> None:
        """Remove every chunk of one document."""
        raise NotImplementedError

    def delete_chat(self, chat_id: str) -> None:
        """Remove every chunk of every document in a chat."""
        raise NotImplementedError
