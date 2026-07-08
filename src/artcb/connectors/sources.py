"""Lecture des sources d'apprentissage externes — base de données client (lecture seule)."""

from __future__ import annotations

import json
import logging
import sqlite3
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx

from artcb.connectors.manager import ConnectorRecord

logger = logging.getLogger("artcb.connectors.sources")


class DataSourceError(Exception):
    """Failed to read external data source."""


def fetch_learning_text(
    record: ConnectorRecord,
    *,
    limit: int = 50,
) -> str:
    """
    Récupère du texte depuis la source connectée par l'utilisateur.
    Lecture seule — ne modifie jamais la base du client.
    """
    if not record._api_key:
        raise DataSourceError("Connector has no API key / secret")

    if record.provider == "supabase":
        return _fetch_supabase(record, limit=limit)
    if record.provider == "sqlite":
        return _fetch_sqlite(record, limit=limit)
    if record.provider == "postgres":
        return _fetch_postgres(record, limit=limit)
    if record.provider == "mysql":
        return _fetch_mysql(record, limit=limit)
    raise DataSourceError(f"Unsupported data source: {record.provider}")


def _fetch_supabase(record: ConnectorRecord, *, limit: int) -> str:
    base_url = record.config.get("project_url", "").rstrip("/")
    table = record.config.get("table", "")
    if not base_url or not table:
        raise DataSourceError("supabase requires config.project_url and config.table")
    api_key = record._api_key or ""
    url = f"{base_url}/rest/v1/{table}?select=*&limit={limit}"
    with httpx.Client(timeout=30.0) as client:
        r = client.get(
            url,
            headers={
                "apikey": api_key,
                "Authorization": f"Bearer {api_key}",
                "Accept": "application/json",
            },
        )
        r.raise_for_status()
        rows = r.json()
    return _rows_to_text(rows, source_label=f"Supabase:{table}")


def _fetch_sqlite(record: ConnectorRecord, *, limit: int) -> str:
    db_path = record.config.get("database_path") or record.config.get("path", "")
    table = record.config.get("table", "")
    text_column = record.config.get("text_column", "content")
    if not db_path or not table:
        raise DataSourceError("sqlite requires config.database_path and config.table")
    path = Path(db_path)
    if not path.is_file():
        raise DataSourceError(f"SQLite file not found: {db_path}")
    conn = sqlite3.connect(str(path))
    try:
        cur = conn.execute(
            f"SELECT * FROM {table} LIMIT ?",  # noqa: S608 — table from user config
            (limit,),
        )
        cols = [d[0] for d in cur.description or []]
        rows = [dict(zip(cols, row)) for row in cur.fetchall()]
    finally:
        conn.close()
    if text_column in cols:
        texts = [str(row.get(text_column, "")) for row in rows if row.get(text_column)]
        return "\n\n".join(texts)
    return _rows_to_text(rows, source_label=f"SQLite:{table}")


def _fetch_postgres(record: ConnectorRecord, *, limit: int) -> str:
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
    except ImportError as exc:
        raise DataSourceError("pip install psycopg2-binary for postgres connector") from exc

    dsn = record._api_key or record.config.get("connection_string", "")
    table = record.config.get("table", "")
    text_column = record.config.get("text_column", "content")
    if not dsn or not table:
        raise DataSourceError("postgres requires api_key=connection_string and config.table")
    conn = psycopg2.connect(dsn)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(f"SELECT * FROM {table} LIMIT %s", (limit,))  # noqa: S608
            rows = [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()
    if rows and text_column in rows[0]:
        return "\n\n".join(str(r.get(text_column, "")) for r in rows if r.get(text_column))
    return _rows_to_text(rows, source_label=f"Postgres:{table}")


def _fetch_mysql(record: ConnectorRecord, *, limit: int) -> str:
    try:
        import pymysql
        from pymysql.cursors import DictCursor
    except ImportError as exc:
        raise DataSourceError("pip install pymysql for mysql connector") from exc

    dsn = record._api_key or ""
    table = record.config.get("table", "")
    text_column = record.config.get("text_column", "content")
    if not dsn or not table:
        raise DataSourceError("mysql requires api_key=connection_string and config.table")
    parsed = urlparse(dsn)
    conn = pymysql.connect(
        host=parsed.hostname or "localhost",
        port=parsed.port or 3306,
        user=parsed.username,
        password=parsed.password,
        database=(parsed.path or "/").lstrip("/"),
        cursorclass=DictCursor,
    )
    try:
        with conn.cursor() as cur:
            cur.execute(f"SELECT * FROM `{table}` LIMIT %s", (limit,))  # noqa: S608
            rows = list(cur.fetchall())
    finally:
        conn.close()
    if rows and text_column in rows[0]:
        return "\n\n".join(str(r.get(text_column, "")) for r in rows if r.get(text_column))
    return _rows_to_text(rows, source_label=f"MySQL:{table}")


def _rows_to_text(rows: list[Any], *, source_label: str) -> str:
    if not rows:
        return f"[{source_label}] Aucune ligne récupérée."
    parts = [f"--- {source_label} row {i} ---\n{json.dumps(row, ensure_ascii=False, default=str)}" for i, row in enumerate(rows)]
    return "\n\n".join(parts)


def test_connector(record: ConnectorRecord) -> tuple[bool, str]:
    """Teste la connexion sans stocker de données ARTCB."""
    try:
        if record.provider in {"openai", "anthropic", "bob"}:
            from artcb.connectors.llm_router import LLMRouter

            result = LLMRouter().classify_sentences(
                ["Test de connexion ARTCB."],
                record=record,
                api_key=record._api_key or "",
            )
            if result is None:
                return False, "LLM n'a pas répondu — vérifiez la clé et le modèle"
            return True, f"LLM {record.provider} connecté"
        text = fetch_learning_text(record, limit=3)
        preview = text[:120].replace("\n", " ")
        return True, f"Source OK — aperçu: {preview}…"
    except Exception as exc:
        return False, str(exc)
