from fastapi import FastAPI, HTTPException
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


@app.get("/")
def home():
    return {"message": "Welcome to StudyBuddy AI!"}


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "app": "StudyBuddy AI",
    }


# Request model for study notes
class StudyNotesRequest(BaseModel):
    topic: str = Field(min_length=1, max_length=200)
    difficulty: str = Field(default="beginner", max_length=50)


# Existing Study Notes endpoint (placeholder for now)
@app.post("/study-notes")
def generate_study_notes(request: StudyNotesRequest):
    return {
        "topic": request.topic,
        "difficulty": request.difficulty,
        "notes": (
            f"Study notes for {request.topic} "
            f"will be generated at the {request.difficulty} level."
        ),
        "status": "success",
    }


# Request model for the AI tutor
class TutorRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


# AI Tutor endpoint powered by Gemma
@app.post("/tutor/ask")
def ask_tutor(request: TutorRequest):
    prompt = f"""
You are StudyBuddy AI, a friendly and patient study tutor.

Answer the student's question clearly and accurately.
Use beginner-friendly language and examples where helpful.
Organize longer answers with headings and bullet points.

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
            detail="The AI tutor took too long to respond. Please try again.",
        ) from exc

    except AIProviderError as exc:
        raise HTTPException(
            status_code=502,
            detail="The AI tutor is temporarily unavailable. Please try again.",
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=503,
            detail="The AI tutor is not configured correctly.",
        ) from exc
