from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.services.ai_engine import (
    get_ai_response,
    AIProviderError,
    AIProviderTimeoutError,
)


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
# STUDY NOTES
# ============================================================

class StudyNotesRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    difficulty: str = Field(default="beginner", max_length=50)


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
    question: str = Field(min_length=1, max_length=2000)


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