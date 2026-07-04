"""Blockchain manager — persistence + Ed25519 signatures (Python) + C hash chain."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from nacl import encoding, signing

from artcb.chain import ffi
from artcb.config import load_settings

logger = logging.getLogger("artcb.chain.manager")


@dataclass
class ChainBlock:
    index: int
    timestamp: str
    prev_hash: str
    graph_root: str
    merkle_root: str
    pol_score: float
    hash: str
    signature: str
    graph_id: str
    visibility: str = "private"

    def to_json_line(self) -> str:
        payload = {
            "index": self.index,
            "timestamp": self.timestamp,
            "prev_hash": self.prev_hash,
            "graph_root": self.graph_root,
            "merkle_root": self.merkle_root,
            "pol_score": self.pol_score,
            "hash": self.hash,
            "signature": self.signature,
            "graph_id": self.graph_id,
            "visibility": self.visibility,
        }
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


GENESIS_PREV_HASH = "0" * 64


class ChainManager:
    def __init__(self, blocks_path: Path, key_path: Path | None = None) -> None:
        settings = load_settings()
        self.blocks_path = blocks_path
        self.blocks_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path = key_path or (settings.data_dir / "chain.key")
        self._signing_key = self._load_or_create_key()

    def _load_or_create_key(self) -> signing.SigningKey:
        if self.key_path.exists():
            raw = self.key_path.read_bytes()
            return signing.SigningKey(raw)
        key = signing.SigningKey.generate()
        self.key_path.parent.mkdir(parents=True, exist_ok=True)
        self.key_path.write_bytes(key.encode())
        logger.debug("Generated new Ed25519 chain key path=%s", self.key_path)
        return key

    @property
    def public_key_b64(self) -> str:
        return self._signing_key.verify_key.encode(encoder=encoding.Base64Encoder).decode("ascii")

    def list_blocks(self) -> list[dict]:
        if not self.blocks_path.exists():
            return []
        blocks: list[dict] = []
        with self.blocks_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    blocks.append(json.loads(line))
        return blocks

    def last_hash(self) -> str:
        blocks = self.list_blocks()
        if not blocks:
            return GENESIS_PREV_HASH
        return blocks[-1]["hash"]

    def append_block(
        self,
        *,
        graph_id: str,
        graph_root: str,
        pol_score: float,
        merkle_root: str | None = None,
        visibility: str = "private",
    ) -> ChainBlock:
        index = len(self.list_blocks())
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        prev_hash = self.last_hash()
        merkle = merkle_root or graph_root
        block_hash = ffi.build_block_hash(
            index, timestamp, prev_hash, graph_root, merkle, pol_score
        )
        signed = self._signing_key.sign(block_hash.encode("utf-8"))
        signature = f"ed25519:{signed.signature.hex()}"

        block = ChainBlock(
            index=index,
            timestamp=timestamp,
            prev_hash=prev_hash,
            graph_root=graph_root,
            merkle_root=merkle,
            pol_score=pol_score,
            hash=block_hash,
            signature=signature,
            graph_id=graph_id,
            visibility=visibility,
        )
        with self.blocks_path.open("a", encoding="utf-8") as handle:
            handle.write(block.to_json_line() + "\n")
        logger.debug("Appended block index=%d hash=%s", index, block_hash)
        return block

    def verify(self) -> dict:
        try:
            valid, message = ffi.verify_chain_file(self.blocks_path)
        except FileNotFoundError as exc:
            return {"valid": False, "message": str(exc), "block_count": 0}
        return {
            "valid": valid,
            "message": message,
            "block_count": len(self.list_blocks()),
            "public_key": self.public_key_b64,
        }
