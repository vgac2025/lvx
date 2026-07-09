"""Tests ingestion multimédia — tous formats structurés."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from artcb.io.media_ingest import (
    ALL_SUPPORTED_EXTENSIONS,
    detect_media_type,
    ingest_file,
    ingest_folder,
    list_supported_formats,
)


def test_list_supported_formats_includes_json_csv() -> None:
    fmts = list_supported_formats()
    assert ".json" in fmts["json"]
    assert ".csv" in fmts["csv_tsv"]
    assert ".yaml" in fmts["yaml"]
    assert len(fmts["all_extensions"]) == len(ALL_SUPPORTED_EXTENSIONS)


def test_ingest_text_file(tmp_path: Path) -> None:
    f = tmp_path / "note.txt"
    f.write_text("Première phrase. Deuxième phrase.", encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "plain_text"
    assert "Première phrase" in result.text


def test_ingest_json_file(tmp_path: Path) -> None:
    data = {"title": "ARTCB", "items": [1, 2, 3]}
    f = tmp_path / "data.json"
    f.write_text(json.dumps(data), encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "json"
    assert "ARTCB" in result.text
    assert "items" in result.text


def test_ingest_jsonl_file(tmp_path: Path) -> None:
    f = tmp_path / "lines.jsonl"
    f.write_text('{"a": 1}\n{"b": 2}\n', encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "json"
    assert '"a"' in result.text


def test_ingest_csv_file(tmp_path: Path) -> None:
    f = tmp_path / "table.csv"
    f.write_text("name,score\nAlice,90\nBob,85\n", encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "csv"
    assert "Alice" in result.text
    assert "90" in result.text


def test_ingest_tsv_file(tmp_path: Path) -> None:
    f = tmp_path / "table.tsv"
    f.write_text("col1\tcol2\nval1\tval2\n", encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "csv"
    assert "val1" in result.text


def test_ingest_xml_file(tmp_path: Path) -> None:
    f = tmp_path / "doc.xml"
    f.write_text("<root><item>Contenu XML</item></root>", encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "xml"
    assert "Contenu XML" in result.text


def test_ingest_html_file(tmp_path: Path) -> None:
    f = tmp_path / "page.html"
    f.write_text("<html><body><p>Hello ARTCB</p></body></html>", encoding="utf-8")
    result = ingest_file(f)
    assert result.media_type == "html"
    assert "Hello ARTCB" in result.text


def test_detect_media_type_json() -> None:
    assert detect_media_type(Path("x.json")) == "json"
    assert detect_media_type(Path("x.csv")) == "csv"


def test_ingest_folder_mixed_formats(tmp_path: Path) -> None:
    (tmp_path / "a.json").write_text('{"k": "v"}', encoding="utf-8")
    (tmp_path / "b.csv").write_text("x,y\n1,2\n", encoding="utf-8")
    (tmp_path / "c.md").write_text("# Titre", encoding="utf-8")
    text, count, has_more = ingest_folder(tmp_path, limit=10, offset=0)
    assert count == 3
    assert has_more is False
    assert "k" in text or "v" in text
    assert "x" in text or "1" in text


def test_local_folder_connector_learn_json_csv(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Intégration : connecteur local_folder + JSON/CSV → apprentissage IR."""
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    monkeypatch.setenv("ARTCB_LOG_DIR", str(tmp_path / "logs"))

    folder = tmp_path / "sources"
    folder.mkdir()
    (folder / "config.json").write_text('{"projet": "LVX", "version": 1}', encoding="utf-8")
    (folder / "users.csv").write_text("nom,role\nAlice,admin\n", encoding="utf-8")

    from fastapi.testclient import TestClient

    from api.main import create_app

    client = TestClient(create_app())
    save = client.post(
        "/api/v1/connectors",
        json={
            "provider": "local_folder",
            "label": "Mes fichiers",
            "api_key": "local-folder-key",
            "config": {"folder_path": str(folder)},
        },
    )
    assert save.status_code == 200, save.text
    cid = save.json()["connector"]["connector_id"]
    learn = client.post(
        f"/api/v1/connectors/{cid}/learn",
        json={"connector_id": cid, "use_llm": False, "limit": 10},
    )
    assert learn.status_code == 200, learn.text
    body = learn.json()
    assert body["node_count"] >= 1
    assert body["chars_ingested"] > 20


def test_connectors_formats_api(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("ARTCB_DATA_DIR", str(tmp_path / "data"))
    from fastapi.testclient import TestClient

    from api.main import create_app

    client = TestClient(create_app())
    r = client.get("/api/v1/connectors/formats")
    assert r.status_code == 200
    assert r.json()["total_extensions"] >= 40
    assert ".json" in r.json()["formats"]["json"]
