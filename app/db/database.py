"""SQLite connection: engine, session factory, ORM base class and the get_db dependency."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

# URL.create avoids problems with spaces or "&" in the file path
engine = create_engine(
    URL.create("sqlite", database=str(settings.sqlite_file)),
    # FastAPI may use a session from a different thread than the one that opened it
    connect_args={"check_same_thread": False},
)


@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, _connection_record):
    # SQLite ignores foreign keys (and ON DELETE CASCADE) unless this is
    # switched on for every new connection.
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Parent class for all ORM models."""


def get_db():
    """FastAPI dependency: one DB session per request, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
