"""GET /api/health: checks that SQLite and Chroma are reachable."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health(request: Request, db: Session = Depends(get_db)):
    # Query a real table so this also fails if migrations haven't been run
    try:
        db.execute(text("SELECT COUNT(*) FROM chats"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    try:
        collection_count = request.app.state.vector_store.count()
        chroma_status = "ok"
    except Exception:
        collection_count = None
        chroma_status = "error"

    all_ok = db_status == "ok" and chroma_status == "ok"
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        db=db_status,
        chroma=chroma_status,
        collection_count=collection_count,
    )
