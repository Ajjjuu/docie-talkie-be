"""FastAPI entry point. Run with: python -m uvicorn app.main:app --reload"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import chats, documents, health, messages
from app.config import settings
from app.rag.vector_store import VectorStore


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Long-lived objects are created once here and shared by all requests
    app.state.vector_store = VectorStore(settings.chroma_path, settings.chroma_collection)
    yield


app = FastAPI(title="Docie Talkie API", lifespan=lifespan)

# Let the React dev server call this API from the browser
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router in (health.router, chats.router, documents.router, messages.router):
    app.include_router(router, prefix="/api")
