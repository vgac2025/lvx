"""Blockchain C + Python integration tests."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from artcb.chain import ffi
from artcb.chain.manager import ChainManager


@pytest.fixture
def chain_tmp(tmp_path: Path) -> ChainManager:
    return ChainManager(tmp_path / "blocks.jsonl", key_path=tmp_path / "chain.key")


def test_c_library_sha256() -> None:
    digest = ffi.sha256_hex("ARTCB")
    assert len(digest) == 64


def test_append_and_verify_chain(chain_tmp: ChainManager) -> None:
    block = chain_tmp.append_block(
        graph_id="g_test001",
        graph_root="abc123" * 8,
        pol_score=0.81,
    )
    assert block.index == 0
    verify = chain_tmp.verify()
    assert verify["valid"] is True
    assert verify["block_count"] == 1


def test_chain_prev_hash_links(chain_tmp: ChainManager) -> None:
    b0 = chain_tmp.append_block(graph_id="g1", graph_root="a" * 64, pol_score=0.7)
    b1 = chain_tmp.append_block(graph_id="g2", graph_root="b" * 64, pol_score=0.8)
    assert b1.prev_hash == b0.hash
    assert chain_tmp.verify()["valid"] is True


def test_tampered_chain_detected(chain_tmp: ChainManager) -> None:
    chain_tmp.append_block(graph_id="g1", graph_root="a" * 64, pol_score=0.7)
    lines = chain_tmp.blocks_path.read_text(encoding="utf-8").strip().splitlines()
    block = json.loads(lines[0])
    block["pol_score"] = 0.1
    block["hash"] = "0" * 64
    chain_tmp.blocks_path.write_text(json.dumps(block, separators=(",", ":")) + "\n", encoding="utf-8")
    verify = chain_tmp.verify()
    assert verify["valid"] is False
