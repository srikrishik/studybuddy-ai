import json

from app.services.ai_engine import (
    get_ai_response,
    AIProviderError,
    AIProviderTimeoutError,
)

from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


def generate_quiz(
    topic: str,
    chunks: list[dict],
    number_of_questions: int = 5,
) -> list[dict]:
    """
    Generate a multiple-choice quiz from relevant study material.
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
You are StudyBuddy AI, a careful study quiz generator.

Generate a multiple-choice quiz about the requested topic
using ONLY the relevant study material provided below.

Requested topic:
{topic}

Number of questions:
{number_of_questions}

Relevant study material:
{context}

Rules:

1. Create exactly {number_of_questions} questions.
2. Every question must be directly related to the requested topic.
3. Each question must have exactly 4 options.
4. Each option must be a short answer choice.
5. Include exactly one correct answer.
6. The correct answer must be directly supported by the study material.
7. Do not use information that is not present in the study material.
8. Keep the questions beginner-friendly.
9. Avoid duplicate questions.
10. Do not create questions about unrelated topics in the document.
11. Return ONLY valid JSON.
12. Do not include Markdown code fences.
13. Use this exact JSON structure:

[
  {{
    "question": "Question text",
    "options": [
      "Option A",
      "Option B",
      "Option C",
      "Option D"
    ],
    "correct_answer": "Option A",
    "explanation": "Short explanation"
  }}
]
"""

    try:
        response = get_ai_response(prompt)

        quiz = json.loads(response)

    except json.JSONDecodeError as exc:
        raise AIProviderError(
            "The AI returned invalid quiz data."
        ) from exc

    except AIProviderTimeoutError:
        raise

    except AIProviderError:
        raise

    except Exception as exc:
        raise AIProviderError(
            "Could not generate the quiz."
        ) from exc

    if not isinstance(quiz, list):
        raise AIProviderError(
            "The AI returned an invalid quiz format."
        )

    if len(quiz) != number_of_questions:
        raise AIProviderError(
            "The AI returned the wrong number of questions."
        )

    for question in quiz:

        if not isinstance(question, dict):
            raise AIProviderError(
                "The AI returned an invalid question."
            )

        required_fields = {
            "question",
            "options",
            "correct_answer",
            "explanation",
        }

        if not required_fields.issubset(question):
            raise AIProviderError(
                "A quiz question is missing required fields."
            )

        options = question["options"]

        if not isinstance(options, list) or len(options) != 4:
            raise AIProviderError(
                "Each quiz question must contain exactly 4 options."
            )

        if question["correct_answer"] not in options:
            raise AIProviderError(
                "The correct answer must be one of the options."
            )

    return quiz