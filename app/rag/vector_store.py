"""Stores and searches chunk vectors in a persistent ChromaDB collection.

Every chunk is saved with:
  id       = "{doc_id}:{chunk_index}"
  metadata = {chat_id, doc_id, filename, page, chunk_index}
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.rag.embedding import Embedder


class VectorStore:
    def __init__(self, persist_dir: Path, collection_name: str, embedder: Embedder):
        client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        # Raw Chroma collection, used for counting and deleting.
        # Cosine distance can only be chosen when the collection is first created.
        # It makes scores easy to read: similarity = 1 - distance (higher is better).
        self.collection = client.get_or_create_collection(
            name=collection_name,
            configuration={"hnsw": {"space": "cosine"}},
        )

        # LangChain wrapper around the same collection, used for adding and searching.
        # It calls the embedding model for us.
        self.store = Chroma(
            client=client,
            collection_name=collection_name,
            embedding_function=embedder.model,
        )

    def count(self) -> int:
        """Total number of chunks stored."""
        return self.collection.count()

    def add_chunks(self, chat_id: str, doc_id: str, filename: str, chunks: list[Document]) -> None:
        """Embed and store all chunks of one document."""
        ids = []
        for chunk in chunks:
            # Tag every chunk so we can filter by chat and delete by document later
            chunk.metadata["chat_id"] = chat_id
            chunk.metadata["doc_id"] = doc_id
            chunk.metadata["filename"] = filename
            ids.append(f"{doc_id}:{chunk.metadata['chunk_index']}")

        self.store.add_documents(chunks, ids=ids)

    def search(self, chat_id: str, query: str, k: int) -> list[tuple[Document, float]]:
        """Return the k chunks in this chat most similar to the query, with scores from 0 to 1."""
        results = self.store.similarity_search_with_score(
            query,
            k=k,
            filter={"chat_id": chat_id},  # only search this chat's documents
        )

        # Chroma returns cosine *distance* (0 = identical). Turn it into a similarity
        # score where 1 = identical. Unrelated text can go slightly below 0, so clamp it.
        return [(chunk, max(0.0, 1 - distance)) for chunk, distance in results]

    def delete_document(self, doc_id: str) -> None:
        """Remove every chunk of one document."""
        self.collection.delete(where={"doc_id": doc_id})
