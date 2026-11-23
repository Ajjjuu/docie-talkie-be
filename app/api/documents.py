"""Documents router: upload PDFs into a chat and list them.

>>> PDF processing (reading, chunking, embedding) STARTS HERE, in upload_document(). <<<

Endpoints:
  POST /api/documents/upload-document/{chat_id}    upload a PDF and make it searchable
  GET  /api/documents/list-documents/{chat_id}     all PDFs in a chat

Called from the frontend by: FE/src/api/documents.js
The work is done by: app/services/document_service.py (DocumentService)
"""

from fastapi import APIRouter, Depends, UploadFile

from app.dependencies import get_chat_service, get_document_service
from app.schemas import DocumentOut
from app.services.chat_service import ChatService
from app.services.document_service import DocumentService

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload-document/{chat_id}", response_model=DocumentOut, status_code=201)
def upload_document(
    chat_id: str,
    file: UploadFile,
    chat_service: ChatService = Depends(get_chat_service),
    document_service: DocumentService = Depends(get_document_service),
):
    """Upload one PDF into a chat, then read, chunk and embed it so it can be searched.

    Triggered by: the "Upload PDF" button (DocumentPanel -> App.handleUpload -> uploadDocument()).
    Request: multipart/form-data with the PDF in a field called "file".

    Steps:
      1. Check the chat exists (404 if not).
      2. DocumentService.upload() then:
         a. checks it is a PDF and not too big (400 / 413 if not)
         b. saves the file to data/uploads/{doc_id}.pdf
         c. inserts a row into the documents table with status "processing"
         d. PDFLoader reads the text of every page       (app/rag/pdf_loader.py)
         e. TextChunker splits the pages into chunks     (app/rag/chunker.py)
         f. VectorStore embeds the chunks with Gemini
            and stores them in Chroma                    (app/rag/vector_store.py)
         g. updates the row: status "ready" (with page and chunk counts),
            or "failed" (with the error message)
      3. Return the document. The frontend checks its status.
    """
    chat_service.get_chat(chat_id)  # Step 1
    return document_service.upload(chat_id, file)  # Steps 2-3


@router.get("/list-documents/{chat_id}", response_model=list[DocumentOut])
def list_documents(
    chat_id: str,
    chat_service: ChatService = Depends(get_chat_service),
    document_service: DocumentService = Depends(get_document_service),
):
    """List all PDFs in a chat, oldest first, with their status.

    Steps:
      1. Check the chat exists (404 if not).
      2. DocumentService.list_documents() reads the documents table for this chat_id.
    """
    chat_service.get_chat(chat_id)
    return document_service.list_documents(chat_id)
