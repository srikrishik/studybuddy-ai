import sqlite3
from pathlib import Path


# Store the database inside the backend folder.
DATABASE_PATH = (
    Path(__file__).resolve().parents[2] / "studybuddy.db"
)


def get_connection():
    """
    Create and return a SQLite database connection.
    """

    connection = sqlite3.connect(DATABASE_PATH)

    connection.row_factory = sqlite3.Row

    return connection


def initialize_database():
    """
    Create the required database tables if they do not exist.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS quiz_attempts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                document_id TEXT NOT NULL,
                filename TEXT NOT NULL,
                topic TEXT NOT NULL,
                total_questions INTEGER NOT NULL,
                correct_answers INTEGER NOT NULL,
                score_percentage REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        connection.commit()

    finally:
        connection.close()


def save_quiz_attempt(
    document_id: str,
    filename: str,
    topic: str,
    total_questions: int,
    correct_answers: int,
) -> int:
    """
    Save a completed quiz attempt and return its ID.
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

    connection = get_connection()

    try:
        cursor = connection.execute(
            """
            INSERT INTO quiz_attempts (
                document_id,
                filename,
                topic,
                total_questions,
                correct_answers,
                score_percentage
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                document_id,
                filename,
                topic,
                total_questions,
                correct_answers,
                score_percentage,
            ),
        )

        connection.commit()

        return cursor.lastrowid

    finally:
        connection.close()


def get_quiz_attempts() -> list[dict]:
    """
    Retrieve all saved quiz attempts.

    The newest attempts are returned first.
    """

    connection = get_connection()

    try:
        rows = connection.execute(
            """
            SELECT
                id,
                document_id,
                filename,
                topic,
                total_questions,
                correct_answers,
                score_percentage,
                created_at
            FROM quiz_attempts
            ORDER BY created_at DESC, id DESC
            """
        ).fetchall()

        return [
            dict(row)
            for row in rows
        ]

    finally:
        connection.close()