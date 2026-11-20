"""Reads a PDF file into one LangChain Document per page."""

from pathlib import Path

from langchain_core.documents import Document


class PDFLoader:
    def load(self, path: Path) -> list[Document]:
        """Return one Document per page, with the page number in metadata["page"].

        Phase 2: use langchain_community PyPDFLoader.
        """
        raise NotImplementedError
