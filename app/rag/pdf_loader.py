"""Reads a PDF file into one LangChain Document per page."""

from pathlib import Path

from langchain_core.documents import Document
from pypdf import PdfReader


class PDFLoader:
    def load(self, path: Path) -> list[Document]:
        """Return one Document per page, with the page number (starting at 1) in metadata."""
        reader = PdfReader(path)
        pages = []

        for page_number, page in enumerate(reader.pages, start=1):
            # Image-only pages have no text layer and come back as an empty string
            text = page.extract_text() or ""
            pages.append(Document(page_content=text, metadata={"page": page_number}))

        return pages
