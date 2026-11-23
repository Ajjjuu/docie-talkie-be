"""Messages router: ask a question about a chat's PDFs, and read the chat history.

>>> Answering a question (search + LLM) STARTS HERE, in ask_question(). <<<

Endpoints:
  POST /api/messages/ask-question/{chat_id}     ask a question, get an answer with sources
  GET  /api/messages/list-messages/{chat_id}    the full chat history

Called from the frontend by: FE/src/api/messages.js
The work is done by: app/rag/query.py (QueryEngine) and app/services/chat_service.py (ChatService)
"""

from fastapi import APIRouter, Depends, HTTPException

from app.dependencies import get_chat_service, get_query_engine
from app.rag.query import QueryEngine
from app.schemas import AskRequest, AskResponse, MessageOut
from app.services.chat_service import ChatService

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("/ask-question/{chat_id}", response_model=AskResponse)
def ask_question(
    chat_id: str,
    body: AskRequest,
    chat_service: ChatService = Depends(get_chat_service),
    query_engine: QueryEngine = Depends(get_query_engine),
):
    """Answer a question using only this chat's PDFs. Saves both the question and the answer.

    Triggered by: pressing Send or Enter (ChatInput -> App.handleSend -> askQuestion()).
    Request body: {"question": "..."}

    Steps:
      1. Reject an empty question (400).
      2. Load the last few messages, so follow-up questions make sense (404 if the chat is missing).
      3. QueryEngine.answer()                           (app/rag/query.py)
         a. VectorStore.search() embeds the question with Gemini and finds
            the most similar chunks, in THIS chat only
         b. builds the prompt: rules + those chunks + history + question
         c. sends it to the Groq LLM and gets the answer text
      4. Save the question and the answer (with its sources) in the messages table.
         The first question also becomes the chat's title.
      5. Return both saved messages.
    """
    # Step 1
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    # Step 2: read the history BEFORE saving the new question, so it isn't in there twice
    history = chat_service.get_history(chat_id)

    # Step 3
    try:
        result = query_engine.answer(chat_id, question, history)
    except Exception as error:
        # Usually a problem reaching Groq or Gemini (bad key, wrong model, rate limit, network)
        raise HTTPException(status_code=502, detail=f"Could not get an answer: {error}")

    # Step 4: save only once we have an answer, so a failed request leaves no half-finished pair
    user_message = chat_service.add_message(chat_id, "user", question)
    assistant_message = chat_service.add_message(
        chat_id, "assistant", result["answer"], result["sources"]
    )

    # Step 5
    return {"question": user_message, "answer": assistant_message}


@router.get("/list-messages/{chat_id}", response_model=list[MessageOut])
def list_messages(chat_id: str, chat_service: ChatService = Depends(get_chat_service)):
    """Return the full chat history, oldest first.

    Steps:
      1. ChatService.get_messages() loads the chat (404 if missing) and returns its messages.
    """
    return chat_service.get_messages(chat_id)
