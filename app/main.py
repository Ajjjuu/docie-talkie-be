"""FastAPI entry point. Run with: python -m uvicorn app.main:app --reload"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chats, documents, health, messages
from app.config import settings
from app.rag.chunker import TextChunker
from app.rag.embedding import Embedder
from app.rag.llm import LLMClient
from app.rag.pdf_loader import PDFLoader
from app.rag.query import QueryEngine
from app.rag.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Stop early with a clear message instead of failing on the first request
    settings.check_api_keys()

    # Long-lived objects are created once here and shared by all requests
    embedder = Embedder(settings.embedding_model, settings.google_api_key)
    llm = LLMClient(settings.groq_model, settings.groq_api_key)
    vector_store = VectorStore(settings.chroma_path, settings.chroma_collection, embedder)

    app.state.vector_store = vector_store
    app.state.pdf_loader = PDFLoader()
    app.state.chunker = TextChunker(settings.chunk_size, settings.chunk_overlap)
    app.state.query_engine = QueryEngine(vector_store, llm, settings.top_k)
    yield


app = FastAPI(title="Docie Talkie API", lifespan=lifespan)

# Let the React dev server call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Every endpoint lives under /api. One router per area:
#   app/api/health.py     /api/check-health
#   app/api/chats.py      /api/chats/...       create-chat, list-chats, get-chat
#   app/api/documents.py  /api/documents/...   upload-document, list-documents
#   app/api/messages.py   /api/messages/...    ask-question, list-messages
for router in (health.router, chats.router, documents.router, messages.router):
    app.include_router(router, prefix="/api")
