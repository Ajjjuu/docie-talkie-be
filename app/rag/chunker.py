"""Splits page Documents into smaller, overlapping chunks for embedding."""

from langchain_core.documents import Document


class TextChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, pages: list[Document]) -> list[Document]:
        """Split pages into chunks, keeping the page number and adding chunk_index.

        Phase 2: use RecursiveCharacterTextSplitter.
        """
        raise NotImplementedError
