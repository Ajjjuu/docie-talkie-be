"""Splits page Documents into smaller, overlapping chunks for embedding."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    def __init__(self, chunk_size: int, chunk_overlap: int):
        # Tries to split on paragraphs first, then lines, then sentences, then words,
        # so chunks break at natural places. The overlap keeps context that would
        # otherwise be cut in half at a chunk boundary.
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def split(self, pages: list[Document]) -> list[Document]:
        """Split pages into chunks. Each chunk keeps its page number and gets a chunk_index."""
        # split_documents copies each page's metadata (the page number) onto its chunks
        chunks = self.splitter.split_documents(pages)

        for index, chunk in enumerate(chunks):
            chunk.metadata["chunk_index"] = index

        return chunks
