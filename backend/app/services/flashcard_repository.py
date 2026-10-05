from datetime import datetime, timezone

from app.services.mongodb import database


# MongoDB collection
flashcards_collection = database["flashcards"]


def save_flashcards(
    flashcard_set_id: str,
    document_id: str,
    topic: str,
    flashcards: list[dict],
) -> str:
    """
    Save a generated flashcard set to MongoDB.
    """

    flashcard_document = {
        "flashcard_set_id": flashcard_set_id,
        "document_id": document_id,
        "topic": topic,
        "flashcards": flashcards,
        "created_at": datetime.now(timezone.utc),
    }

    flashcards_collection.insert_one(flashcard_document)

    return flashcard_set_id


def get_flashcards(
    flashcard_set_id: str,
) -> dict | None:
    """
    Retrieve a flashcard set using its ID.
    """

    return flashcards_collection.find_one(
        {"flashcard_set_id": flashcard_set_id},
        {"_id": 0},
    )


def get_flashcard_sets() -> list[dict]:
    """
    Retrieve all saved flashcard sets.
    Newest sets are returned first.
    """

    flashcard_sets = flashcards_collection.find(
        {},
        {"_id": 0},
    ).sort("created_at", -1)

    return list(flashcard_sets)

def update_flashcard_revision(
    flashcard_set_id: str,
    card_index: int,
    marked_for_revision: bool,
) -> bool:
    """
    Update the revision status of one flashcard.
    """

    if card_index < 0:
        raise ValueError(
            "Card index cannot be negative."
        )

    result = flashcards_collection.update_one(
        {"flashcard_set_id": flashcard_set_id},
        {
            "$set": {
                f"flashcards.{card_index}.marked_for_revision":
                    marked_for_revision
            }
        },
    )

    return result.modified_count > 0