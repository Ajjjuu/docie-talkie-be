"""Answers a question: retrieve relevant chunks, build the prompt, ask the LLM."""

from langchain_core.documents import Document
from langchain_core.messages import BaseMessage

from app.rag.llm import LLMClient
from app.rag.vector_store import VectorStore


class QueryEngine:
    def __init__(self, vector_store: VectorStore, llm: LLMClient, top_k: int):
        self.vector_store = vector_store
        self.llm = llm
        self.top_k = top_k

    def answer(self, chat_id: str, question: str, history: list[dict]) -> dict:
        """Return {"answer": str, "sources": [...]} for a question in this chat."""
        raise NotImplementedError

    def build_prompt(
        self, question: str, chunks: list[tuple[Document, float]], history: list[dict]
    ) -> list[BaseMessage]:
        """System rules + numbered context chunks + recent history + the question."""
        raise NotImplementedError
