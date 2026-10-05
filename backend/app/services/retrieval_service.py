import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """
    Convert text into lowercase words for simple keyword matching.
    """

    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def calculate_score(
    query_words: list[str],
    chunk_text: str,
) -> int:
    """
    Calculate a simple keyword-overlap score.

    A higher score means the chunk contains more
    words that also appear in the student's question.
    """

    chunk_words = tokenize(chunk_text)

    if not chunk_words:
        return 0

    query_counts = Counter(query_words)
    chunk_counts = Counter(chunk_words)

    score = 0

    for word, query_count in query_counts.items():
        if word in chunk_counts:
            score += min(
                query_count,
                chunk_counts[word],
            )

    return score


def retrieve_relevant_chunks(
    query: str,
    chunks: list[dict],
    top_k: int = 3,
) -> list[dict]:
    """
    Return the most relevant chunks for a student's question.
    """

    if not query.strip():
        return []

    if top_k <= 0:
        return []

    query_words = tokenize(query)

    if not query_words:
        return []

    scored_chunks = []

    for chunk in chunks:
        score = calculate_score(
            query_words,
            chunk["text"],
        )

        if score > 0:
            scored_chunks.append(
                {
                    **chunk,
                    "score": score,
                }
            )

    scored_chunks.sort(
        key=lambda chunk: chunk["score"],
        reverse=True,
    )

    return scored_chunks[:top_k]