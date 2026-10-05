from io import BytesIO

from pypdf import PdfReader


def extract_pdf_text(file_bytes: bytes) -> list[dict]:
    """
    Extract text from a PDF while preserving page numbers.

    Returns:
        A list containing one dictionary per page.
    """

    reader = PdfReader(BytesIO(file_bytes))

    pages = []

    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""

        pages.append(
            {
                "page": page_number,
                "text": text.strip(),
            }
        )

    return pages