from uuid import uuid4

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.ai_engine import (
    get_ai_response,
    AIProviderError,
    AIProviderTimeoutError,
)

from app.services.pdf_service import extract_pdf_text
from app.services.chunk_service import chunk_pages
from app.services.rag_service import answer_from_document


app = FastAPI(
    title="StudyBuddy AI",
    description="Your Personal Open-Source Learning Companion",
    version="0.1.0",
)


# Allow the frontend to communicate with the backend.
# For local development only; restrict origins before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# TEMPORARY DOCUMENT STORAGE
# ============================================================

# Documents are stored in memory while the backend is running.
# This is temporary storage for the current development phase.
DOCUMENT_STORE: dict[str, dict] = {}


# ============================================================
# BASIC ENDPOINTS
# ============================================================

@app.get("/")
def home():
    return {"message": "Welcome to StudyBuddy AI!"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "StudyBuddy AI",
    }


# ============================================================
# PDF DOCUMENT UPLOAD
# ============================================================

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB


@app.post("/documents")
async def upload_document(file: UploadFile = File(...)):

    # Validate file type.
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    # Read the uploaded file.
    file_bytes = await file.read()

    # Validate file size.
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail="PDF file is too large. Maximum size is 10 MB.",
        )

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded PDF is empty.",
        )

    try:
        # Extract text from the PDF.
        pages = extract_pdf_text(file_bytes)

    except Exception as exc:
        print(
            f"PDF extraction error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=400,
            detail="Could not extract text from the PDF.",
        ) from exc

    total_characters = sum(
        len(page["text"])
        for page in pages
    )

    # Split extracted text into chunks.
    chunks = chunk_pages(pages)

    # Create a unique ID for this document.
    document_id = str(uuid4())

    # Store the document and its chunks temporarily.
    DOCUMENT_STORE[document_id] = {
        "filename": file.filename,
        "size": len(file_bytes),
        "pages": len(pages),
        "characters": total_characters,
        "chunks": chunks,
    }

    return {
        "document_id": document_id,
        "filename": file.filename,
        "size": len(file_bytes),
        "pages": len(pages),
        "characters": total_characters,
        "chunk_count": len(chunks),
        "status": "uploaded",
    }


# ============================================================
# DOCUMENT QUESTION ANSWERING
# ============================================================

class DocumentQuestionRequest(BaseModel):
    document_id: str = Field(
        min_length=1,
        max_length=100,
    )

    question: str = Field(
        min_length=1,
        max_length=2000,
    )


@app.post("/documents/ask")
def ask_document(request: DocumentQuestionRequest):

    # Find the uploaded document.
    document = DOCUMENT_STORE.get(
        request.document_id
    )

    if document is None:
        raise HTTPException(
            status_code=404,
            detail="Document not found. Please upload the PDF again.",
        )

    try:
        result = answer_from_document(
            question=request.question,
            chunks=document["chunks"],
            top_k=3,
        )

        return {
            "document_id": request.document_id,
            "filename": document["filename"],
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"],
            "status": "success",
        }

    except AIProviderTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=(
                "The AI tutor took too long to answer. "
                "Please try again."
            ),
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI tutor is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    except Exception as exc:
        print(
            f"Unexpected document question error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from exc


# ============================================================
# STUDY NOTES
# ============================================================

class StudyNotesRequest(BaseModel):
    topic: str = Field(
        min_length=1,
        max_length=200,
    )

    difficulty: str = Field(
        default="beginner",
        max_length=50,
    )


@app.post("/study-notes")
def generate_study_notes(request: StudyNotesRequest):

    prompt = f"""
You are StudyBuddy AI, a friendly and patient study tutor.

Create study notes about the topic below.

Topic:
{request.topic}

Difficulty level:
{request.difficulty}

Follow these rules:

1. Start with a clear title.
2. Give a simple definition or introduction.
3. Explain the important concepts.
4. Use bullet points where useful.
5. Include a short Python code example if the topic is related to programming.
6. Explain the code briefly.
7. End with a short "Key Takeaways" section.
8. Keep the explanation focused and beginner-friendly.
9. Avoid unnecessary repetition.

Return only the study notes.
"""

    try:
        notes = get_ai_response(prompt)

        return {
            "topic": request.topic,
            "difficulty": request.difficulty,
            "notes": notes,
            "status": "success",
        }

    except AIProviderTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=(
                "The AI tutor took too long to generate the study notes. "
                "Please try again."
            ),
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI tutor is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    except Exception as exc:
        print(
            f"Unexpected study notes error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from exc


# ============================================================
# AI TUTOR
# ============================================================

class TutorRequest(BaseModel):
    question: str = Field(
        min_length=1,
        max_length=2000,
    )


@app.post("/tutor/ask")
def ask_tutor(request: TutorRequest):

    prompt = f"""
You are StudyBuddy AI, a friendly and patient study tutor.

Explain the answer in simple, beginner-friendly language.
Be concise and focus on the most important points.
Use a short Python code example when helpful.
Avoid unnecessary introductions and repetition.

Student's question:
{request.question}
"""

    try:
        answer = get_ai_response(prompt)

        return {
            "question": request.question,
            "answer": answer,
            "status": "success",
        }

    except AIProviderTimeoutError as exc:
        raise HTTPException(
            status_code=504,
            detail=(
                "The AI tutor took too long to respond. "
                "Please try again."
            ),
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                "The AI tutor is temporarily unavailable. "
                "Please try again."
            ),
        ) from exc

    except Exception as exc:
        print(
            f"Unexpected tutor endpoint error: "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="An unexpected server error occurred.",
        ) from exc