"""PDF text extraction for real-world ARTCB tests."""

from __future__ import annotations

import os
from pathlib import Path

from pypdf import PdfReader

DEFAULT_BOOK_PATHS = (
    Path(os.getenv("ARTCB_TEST_BOOK_PDF", "")),
    Path("data/fixtures/wailly_le_roi_de_l_inconnu.pdf"),
    Path("/home/lvx/Downloads/wailly_le_roi_de_l_inconnu.pdf"),
    Path("/workspace/data/fixtures/wailly_le_roi_de_l_inconnu.pdf"),
)

BOOK_FILENAME = "wailly_le_roi_de_l_inconnu.pdf"


def resolve_book_path() -> Path | None:
    """Find the Wailly test book PDF on disk."""
    candidates: list[Path] = []
    env_path = os.getenv("ARTCB_TEST_BOOK_PDF")
    if env_path:
        candidates.append(Path(env_path))
    candidates.extend(p for p in DEFAULT_BOOK_PATHS if str(p) and str(p) != ".")
    for path in candidates:
        if path.is_file():
            return path
    return None


def extract_pdf_text(path: Path, max_pages: int | None = None) -> str:
    reader = PdfReader(str(path))
    pages = reader.pages[:max_pages] if max_pages else reader.pages
    chunks: list[str] = []
    for page in pages:
        text = page.extract_text() or ""
        if text.strip():
            chunks.append(text.strip())
    return "\n\n".join(chunks)


def extract_pdf_chunks(path: Path, chunk_size: int = 2000, max_chunks: int = 5) -> list[str]:
    """Split book text into chunks for incremental encode tests."""
    full_text = extract_pdf_text(path)
    if not full_text:
        return []
    chunks: list[str] = []
    start = 0
    while start < len(full_text) and len(chunks) < max_chunks:
        end = min(start + chunk_size, len(full_text))
        piece = full_text[start:end].strip()
        if piece:
            chunks.append(piece)
        start = end
    return chunks
