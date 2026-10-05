from datetime import datetime, timezone

from app.services.mongodb import database


# MongoDB collections
quizzes_collection = database["quizzes"]
quiz_attempts_collection = database["quiz_attempts"]


def save_quiz(
    quiz_id: str,
    document_id: str,
    filename: str,
    topic: str,
    quiz: list[dict],
) -> str:
    """
    Save a generated quiz to MongoDB.
    """

    quiz_document = {
        "quiz_id": quiz_id,
        "document_id": document_id,
        "filename": filename,
        "topic": topic,
        "quiz": quiz,
        "created_at": datetime.now(timezone.utc),
    }

    quizzes_collection.insert_one(quiz_document)

    return quiz_id


def get_quiz(quiz_id: str) -> dict | None:
    """
    Retrieve a quiz from MongoDB using its quiz ID.
    """

    return quizzes_collection.find_one(
        {"quiz_id": quiz_id},
        {"_id": 0},
    )


def save_quiz_attempt(
    attempt_id: str,
    quiz_id: str,
    document_id: str,
    filename: str,
    topic: str,
    total_questions: int,
    correct_answers: int,
) -> str:
    """
    Save a completed quiz attempt to MongoDB.
    """

    if total_questions <= 0:
        raise ValueError(
            "Total questions must be greater than zero."
        )

    if correct_answers < 0:
        raise ValueError(
            "Correct answers cannot be negative."
        )

    if correct_answers > total_questions:
        raise ValueError(
            "Correct answers cannot exceed total questions."
        )

    score_percentage = (
        correct_answers / total_questions
    ) * 100

    attempt_document = {
        "attempt_id": attempt_id,
        "quiz_id": quiz_id,
        "document_id": document_id,
        "filename": filename,
        "topic": topic,
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percentage": score_percentage,
        "created_at": datetime.now(timezone.utc),
    }

    quiz_attempts_collection.insert_one(attempt_document)

    return attempt_id


def get_quiz_attempts() -> list[dict]:
    """
    Retrieve all quiz attempts.
    Newest attempts are returned first.
    """

    attempts = quiz_attempts_collection.find(
        {},
        {"_id": 0},
    ).sort("created_at", -1)

    return list(attempts)