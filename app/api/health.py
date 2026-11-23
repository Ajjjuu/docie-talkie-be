"""Health router: is the backend up and can it reach its databases?

Endpoints:
  GET /api/check-health    check that SQLite and Chroma both respond

Called from the frontend by: FE/src/api/health.js -> checkHealth()
"""

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/check-health", response_model=HealthResponse)
def check_health(request: Request, db: Session = Depends(get_db)):
    """Check that SQLite and Chroma both respond.

    Triggered by: the page loading (App.jsx useEffect). The result colours the header dot.

    Steps:
      1. Count the rows in the chats table. This fails if `alembic upgrade head` was never run.
      2. Count the chunks in the Chroma collection.
      3. Return status "ok" if both worked, otherwise "degraded".
    """
    # Step 1: SQLite
    try:
        db.execute(text("SELECT COUNT(*) FROM chats"))
        db_status = "ok"
    except Exception:
        db_status = "error"

    # Step 2: Chroma
    try:
        collection_count = request.app.state.vector_store.count()
        chroma_status = "ok"
    except Exception:
        collection_count = None
        chroma_status = "error"

    # Step 3: overall status
    all_ok = db_status == "ok" and chroma_status == "ok"
    return HealthResponse(
        status="ok" if all_ok else "degraded",
        db=db_status,
        chroma=chroma_status,
        collection_count=collection_count,
    )
