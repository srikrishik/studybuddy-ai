def chunk_pages(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[dict]:
    """
    Split extracted PDF text into overlapping chunks.

    Each chunk keeps its original page number.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be greater than 0.")

    if overlap < 0 or overlap >= chunk_size:
        raise ValueError(
            "overlap must be greater than or equal to 0 "
            "and smaller than chunk_size."
        )

    chunks = []

    chunk_id = 1

    for page in pages:
        page_number = page["page"]
        text = page["text"].strip()

        if not text:
            continue

        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:
                chunks.append(
                    {
                        "chunk_id": chunk_id,
                        "page": page_number,
                        "text": chunk_text,
                    }
                )

                chunk_id += 1

            if end >= len(text):
                break

            start = end - overlap

    return chunks