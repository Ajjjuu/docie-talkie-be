"""Answers a question: find relevant chunks, build the prompt, ask the LLM."""

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from app.rag.llm import LLMClient
from app.rag.vector_store import VectorStore

SYSTEM_PROMPT = """You are Docie Talkie, an assistant that answers questions about the user's PDF documents.

Rules:
- Answer using ONLY the context below. Do not use outside knowledge.
- If the answer is not in the context, say: "I couldn't find that in your documents."
- After each fact, cite where it came from, like [report.pdf, p. 3].
- Keep answers clear and to the point.

Context:
{context}"""

# The prompt has three parts: the rules and context, the recent chat history
# (so follow-up questions make sense), and the new question.
PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("history"),
        ("human", "{question}"),
    ]
)

NO_DOCUMENTS_ANSWER = "There are no documents in this chat yet. Upload a PDF first."


class QueryEngine:
    def __init__(self, vector_store: VectorStore, llm: LLMClient, top_k: int):
        self.vector_store = vector_store
        self.top_k = top_k
        # prompt -> Groq model -> plain text answer
        self.chain = PROMPT | llm.model | StrOutputParser()

    def answer(self, chat_id: str, question: str, history: list[dict]) -> dict:
        """Return {"answer": str, "sources": [...]} for a question in this chat.

        history is a list of {"role": "user" | "assistant", "content": str}.
        """
        results = self.vector_store.search(chat_id, question, self.top_k)
        if not results:
            return {"answer": NO_DOCUMENTS_ANSWER, "sources": []}

        answer = self.chain.invoke(
            {
                "context": self.format_context(results),
                "history": history,
                "question": question,
            }
        )
        return {"answer": answer, "sources": self.format_sources(results)}

    def format_context(self, results: list[tuple[Document, float]]) -> str:
        """Turn the retrieved chunks into one block of text for the prompt."""
        parts = []
        for chunk, _score in results:
            filename = chunk.metadata["filename"]
            page = chunk.metadata["page"]
            parts.append(f"[{filename}, p. {page}]\n{chunk.page_content}")
        return "\n\n---\n\n".join(parts)

    def format_sources(self, results: list[tuple[Document, float]]) -> list[dict]:
        """Turn the retrieved chunks into the sources list saved with the answer."""
        sources = []
        for chunk, score in results:
            sources.append(
                {
                    "doc_id": chunk.metadata["doc_id"],
                    "filename": chunk.metadata["filename"],
                    "page": chunk.metadata["page"],
                    "chunk_id": f"{chunk.metadata['doc_id']}:{chunk.metadata['chunk_index']}",
                    "score": round(score, 3),
                    "text": chunk.page_content,
                }
            )
        return sources
