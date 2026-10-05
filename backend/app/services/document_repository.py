from datetime import datetime, timezone

from app.services.mongodb import database


# MongoDB collection
documents_collection = database["documents"]


def save_document(
    document_id: str,
    filename: str,
    size: int,
    pages: int,
    characters: int,
    chunk_count: int,
    status: str = "uploaded",
) -> str:
    """
    Save document metadata to MongoDB.
    """

    document = {
        "document_id": document_id,
        "filename": filename,
        "size": size,
        "pages": pages,
        "characters": characters,
        "chunk_count": chunk_count,
        "status": status,
        "created_at": datetime.now(timezone.utc),
    }

    documents_collection.insert_one(document)

    return document_id


def get_document(document_id: str) -> dict | None:
    """
    Retrieve document metadata using its document ID.
    """

    return documents_collection.find_one(
        {"document_id": document_id},
        {"_id": 0},
    )


def get_documents() -> list[dict]:
    """
    Retrieve all saved documents.
    Newest documents are returned first.
    """

    documents = documents_collection.find(
        {},
        {"_id": 0},
    ).sort("created_at", -1)

    return list(documents)