# Docie Talkie: Backend

FastAPI backend for Docie Talkie, a RAG app for asking questions about PDFs. It uses Groq for the LLM, Gemini for embeddings, ChromaDB for vectors and SQLite for chats.

## Setup (first time)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env    # then fill in GROQ_API_KEY and GOOGLE_API_KEY
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Run

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- API: http://localhost:8000/api
- Swagger docs: http://localhost:8000/docs
- Health check: http://localhost:8000/api/check-health

## API

| Method | Path | What it does | Router file |
|---|---|---|---|
| GET | `/api/check-health` | DB and Chroma status | `api/health.py` |
| POST | `/api/chats/create-chat` | create a chat | `api/chats.py` |
| GET | `/api/chats/list-chats` | list chats, most recent first | `api/chats.py` |
| GET | `/api/chats/get-chat/{chat_id}` | chat with its documents and messages | `api/chats.py` |
| POST | `/api/documents/upload-document/{chat_id}` | upload a PDF (form field `file`) and index it | `api/documents.py` |
| GET | `/api/documents/list-documents/{chat_id}` | list a chat's documents | `api/documents.py` |
| POST | `/api/messages/ask-question/{chat_id}` | `{"question": "..."}` → answer with sources | `api/messages.py` |
| GET | `/api/messages/list-messages/{chat_id}` | chat history | `api/messages.py` |

## Database migrations (Alembic)

```powershell
# after changing app/db/models.py
.\.venv\Scripts\python.exe -m alembic revision --autogenerate -m "describe the change"
.\.venv\Scripts\python.exe -m alembic upgrade head
```

## Layout

```
app/
  main.py          FastAPI app, CORS, routers
  config.py        settings from .env
  schemas.py       request/response models
  dependencies.py  gives each route its services
  db/              SQLAlchemy engine + ORM models
  api/             route handlers
  rag/             PDF loading, chunking, embeddings, vector store, LLM, query
  services/        chat and document logic
alembic/           migrations
data/              SQLite DB, Chroma vectors, uploaded PDFs (gitignored)
```

> Tools are run with `python -m ...` because the `&` in the project path breaks the Windows `.exe`/`.cmd` launchers.
