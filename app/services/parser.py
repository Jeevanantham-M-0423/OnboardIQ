from pathlib import Path
import re

import fitz
from docx import Document


def clean_text(text: str) -> str:
    if not text:
        return ""

    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    normalized = re.sub(r"[\t\f\v]+", " ", normalized)
    normalized = re.sub(r"[ ]{2,}", " ", normalized)
    normalized = re.sub(r"\n{3,}", "\n\n", normalized)

    return normalized.strip()


def extract_text_from_pdf(path: Path) -> str:
    try:
        pages: list[str] = []

        with fitz.open(path) as document:
            for page in document:
                pages.append(page.get_text("text") or "")

        return clean_text("\n".join(pages))
    except Exception:
        # Corrupted files or parser failures should not crash the server.
        return ""


def extract_text_from_docx(path: Path) -> str:
    try:
        document = Document(path)
        content = "\n".join(paragraph.text for paragraph in document.paragraphs)
        return clean_text(content)
    except Exception:
        # Corrupted files or parser failures should not crash the server.
        return ""
