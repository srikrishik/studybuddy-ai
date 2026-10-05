import json

from app.services.ai_engine import (
    get_ai_response,
    AIProviderError,
    AIProviderTimeoutError,
)

from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


def generate_flashcards(
    topic: str,
    chunks: list[dict],
    number_of_cards: int = 5,
) -> list[dict]:
    """
    Generate flashcards from relevant study material.
    """

    # Retrieve chunks relevant to the requested topic.
    relevant_chunks = retrieve_relevant_chunks(
        query=topic,
        chunks=chunks,
        top_k=5,
    )

    if not relevant_chunks:
        raise AIProviderError(
            "Could not find relevant study material "
            f"for the topic '{topic}'."
        )

    # Build context from the relevant chunks.
    context_parts = []

    for chunk in relevant_chunks:
        context_parts.append(
            f"[Page {chunk['page']}]\n"
            f"{chunk['text']}"
        )

    context = "\n\n".join(context_parts)

    prompt = f"""
You are StudyBuddy AI, a careful study flashcard generator.

Create flashcards about the requested topic using ONLY
the relevant study material provided below.

Requested topic:
{topic}

Number of flashcards:
{number_of_cards}

Relevant study material:
{context}

Rules:

1. Create exactly {number_of_cards} flashcards.
2. Every flashcard must be directly related to the requested topic.
3. The front should contain a clear question or term.
4. The back should contain a short, accurate answer.
5. The answer must be directly supported by the study material.
6. Do not use information that is not present in the study material.
7. Keep the flashcards beginner-friendly.
8. Avoid duplicate flashcards.
9. Do not create flashcards about unrelated topics in the document.
10. Return ONLY valid JSON.
11. Do not include Markdown code fences.
12. Use this exact JSON structure:

[
  {{
    "front": "Question or term",
    "back": "Short answer or explanation",
    "source_page": 1
  }}
]
"""

    try:
        response = get_ai_response(prompt)

        flashcards = json.loads(response)

    except json.JSONDecodeError as exc:
        raise AIProviderError(
            "The AI returned invalid flashcard data."
        ) from exc

    except AIProviderTimeoutError:
        raise

    except AIProviderError:
        raise

    except Exception as exc:
        raise AIProviderError(
            "Could not generate the flashcards."
        ) from exc

    # Validate the overall response.
    if not isinstance(flashcards, list):
        raise AIProviderError(
            "The AI returned an invalid flashcard format."
        )

    if len(flashcards) != number_of_cards:
        raise AIProviderError(
            "The AI returned the wrong number of flashcards."
        )

    # Validate every flashcard.
    for flashcard in flashcards:

        if not isinstance(flashcard, dict):
            raise AIProviderError(
                "The AI returned an invalid flashcard."
            )

        required_fields = {
            "front",
            "back",
            "source_page",
        }

        if not required_fields.issubset(flashcard):
            raise AIProviderError(
                "A flashcard is missing required fields."
            )

        if not isinstance(flashcard["front"], str):
            raise AIProviderError(
                "Flashcard front must be text."
            )

        if not isinstance(flashcard["back"], str):
            raise AIProviderError(
                "Flashcard back must be text."
            )

        if not flashcard["front"].strip():
            raise AIProviderError(
                "Flashcard front cannot be empty."
            )

        if not flashcard["back"].strip():
            raise AIProviderError(
                "Flashcard back cannot be empty."
            )

        if not isinstance(flashcard["source_page"], int):
            raise AIProviderError(
                "Flashcard source_page must be an integer."
            )

    return flashcards