"""Pytest fixtures — build C chain library + shared test paths."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest


@pytest.fixture(scope="session", autouse=True)
def ensure_c_chain_library() -> None:
    lib = Path(__file__).resolve().parents[1] / "src" / "c" / "libartcb_chain.so"
    if lib.exists():
        return
    c_dir = lib.parent
    result = subprocess.run(["make", "-C", str(c_dir), "all"], capture_output=True, text=True)
    if result.returncode != 0:
        pytest.fail(f"Failed to build libartcb_chain.so:\n{result.stderr}")


@pytest.fixture(scope="session")
def book_pdf_path() -> Path:
    path = Path(__file__).resolve().parents[1] / "data" / "fixtures" / "wailly_le_roi_de_l_inconnu.pdf"
    if not path.exists():
        pytest.skip(f"Book PDF not found: {path}")
    return path
