from app.services.ai_engine import (
    get_ai_response,
    AIProviderError,
    AIProviderTimeoutError,
)

from app.services.retrieval_service import (
    retrieve_relevant_chunks,
)


def build_context(chunks: list[dict]) -> str:
    """
    Build a context string from retrieved PDF chunks.
    """

    context_parts = []

    for chunk in chunks:
        context_parts.append(
            f"[Page {chunk['page']}]\n"
            f"{chunk['text']}"
        )

    return "\n\n".join(context_parts)


def answer_from_document(
    question: str,
    chunks: list[dict],
    top_k: int = 3,
) -> dict:
    """
    Retrieve relevant document chunks and ask Gemma
    to answer using those chunks.
    """

    relevant_chunks = retrieve_relevant_chunks(
        question,
        chunks,
        top_k=top_k,
    )

    if not relevant_chunks:
        return {
            "answer": (
                "I could not find relevant information "
                "in the uploaded document."
            ),
            "sources": [],
        }

    context = build_context(relevant_chunks)

    prompt = f"""
You are StudyBuddy AI, a document-grounded study tutor.

Answer the student's question using ONLY the information
provided in the document context below.

If the answer is not supported by the context, clearly say
that the information was not found in the uploaded document.

Do not invent facts or information.

Document context:
{context}

Student's question:
{question}

Answer in a clear and beginner-friendly way.
"""

    answer = get_ai_response(prompt)

    sources = [
        {
            "chunk_id": chunk["chunk_id"],
            "page": chunk["page"],
            "score": chunk["score"],
        }
        for chunk in relevant_chunks
    ]

    return {
        "answer": answer,
        "sources": sources,
    }