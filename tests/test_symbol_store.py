"""Tests registre symboles persistant."""

from __future__ import annotations

from pathlib import Path

from artcb.ir.symbol_store import PersistentSymbolRegistry


def test_persistent_registry_save_reload(tmp_path: Path) -> None:
    reg = PersistentSymbolRegistry(tmp_path)
    sym = reg.mint_original("flarnick process")
    assert sym
    assert reg.path.is_file()

    reg2 = PersistentSymbolRegistry(tmp_path)
    exported = reg2.export()
    assert any("flarnick" in k for k in exported)


def test_merge_remote_symbols(tmp_path: Path) -> None:
    reg = PersistentSymbolRegistry(tmp_path)
    remote = {"zorbax|abc123": "alpha1"}
    merged = reg.merge_remote(remote, from_node_id="node_b")
    assert merged >= 1
    assert reg.path.is_file()


def test_publish_from_graph(tmp_path: Path) -> None:
    reg = PersistentSymbolRegistry(tmp_path)
    out = reg.publish_from_graph({"testconcept|deadbeef": "beta1"})
    assert len(out) >= 1
