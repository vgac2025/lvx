"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from artcb.io.pdf_loader import BOOK_FILENAME, resolve_book_path


@pytest.fixture(scope="session")
def book_pdf_path() -> Path:
    path = resolve_book_path()
    if path is None:
        pytest.skip(
            f"PDF '{BOOK_FILENAME}' not found. Copy to data/fixtures/ or set ARTCB_TEST_BOOK_PDF"
        )
    return path
