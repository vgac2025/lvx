"""Real-world tests using Wailly book PDF — skipped if file absent."""

from __future__ import annotations

import pytest

from artcb.io.pdf_loader import extract_pdf_chunks, extract_pdf_text
from artcb.ir.decoder import IRDecoder
from artcb.ir.encoder import IREncoder


@pytest.fixture
def encoder() -> IREncoder:
    return IREncoder()


@pytest.fixture
def decoder() -> IRDecoder:
    return IRDecoder()


def test_book_file_readable(book_pdf_path, encoder: IREncoder, decoder: IRDecoder) -> None:
    """Integration: extract text from PDF and verify non-empty content."""
    text = extract_pdf_text(book_pdf_path, max_pages=3)
    assert len(text) > 100


def test_book_first_pages_reversibility(book_pdf_path, encoder: IREncoder, decoder: IRDecoder) -> None:
    """Integration: encode/decode first 3 pages with 100% reversibility."""
    text = extract_pdf_text(book_pdf_path, max_pages=3)
    graph = encoder.encode(text)
    result = decoder.decode_with_metrics(graph)
    assert result["exact"] is True
    assert result["text"] == text


def test_book_chunk_reversibility(book_pdf_path, encoder: IREncoder, decoder: IRDecoder) -> None:
    """Integration: each 2000-char chunk must round-trip exactly."""
    chunks = extract_pdf_chunks(book_pdf_path, chunk_size=2000, max_chunks=5)
    assert chunks
    for chunk in chunks:
        graph = encoder.encode(chunk)
        result = decoder.decode_with_metrics(graph)
        assert result["text"] == chunk


def test_book_orig_symbols_minted(book_pdf_path, encoder: IREncoder) -> None:
    """Integration: novel words in book trigger original AI symbols."""
    text = extract_pdf_text(book_pdf_path, max_pages=5)
    graph = encoder.encode(text)
    assert graph.orig_symbols or any(n.sym for n in graph.nodes)


def test_book_node_count_scales(book_pdf_path, encoder: IREncoder) -> None:
    """Integration: longer excerpt produces multiple graph nodes."""
    text = extract_pdf_text(book_pdf_path, max_pages=10)
    graph = encoder.encode(text)
    assert len(graph.nodes) >= 5
