"""Shared pytest fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest

from artcb.config import load_settings

TEST_WALLET_PASSPHRASE = "test-passphrase-artcb-dev-32chars!"


@pytest.fixture(autouse=True)
def _wallet_passphrase_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """All tests use encrypted wallets — ARTCB_WALLET_PASSPHRASE required."""
    monkeypatch.setenv("ARTCB_WALLET_PASSPHRASE", TEST_WALLET_PASSPHRASE)
    monkeypatch.setenv("ARTCB_PQC_ENABLED", "true")


@pytest.fixture
def book_pdf_path() -> Path:
    """Wailly demo PDF — skip tests if missing."""
    path = load_settings().demo_book_pdf
    if not path.is_file():
        pytest.skip(f"Book PDF not found: {path}")
    return path
