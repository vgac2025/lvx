"""Tests ingestion multimédia."""

from __future__ import annotations

from pathlib import Path

import pytest

from artcb.io.media_ingest import ingest_file, ingest_folder


def test_ingest_text_file(tmp_path: Path) -> None:
    f = tmp_path / "note.txt"
    f.write_text("Première phrase. Deuxième phrase.", encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "text"
    assert "Première phrase" in result.text


def test_ingest_folder_pagination(tmp_path: Path) -> None:
    for i in range(3):
        (tmp_path / f"doc{i}.txt").write_text(f"Contenu fichier {i}.", encoding="utf-8")
    text, count, has_more = ingest_folder(tmp_path, limit=2, offset=0)
    assert count == 2
    assert has_more is True
    assert "doc0" in text or "Contenu" in text
