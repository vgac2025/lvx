"""P2P node identity — ML-KEM keypair persistant."""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.artcb.crypto.kem import KEMError, generate_kem_keypair

logger = logging.getLogger("artcb.p2p.node_identity")

NETWORK_ID = "artcb-devnet-1"
DEFAULT_P2P_PORT = int(os.getenv("ARTCB_P2P_PORT", "18444"))


@dataclass
class NodeIdentity:
    network_id: str
    node_id: str
    kem_public_key_hex: str
    kem_secret_key_hex: str
    api_port: int
    p2p_port: int

    def public_dict(self) -> dict[str, Any]:
        return {
            "network_id": self.network_id,
            "node_id": self.node_id,
            "kem_public_key_hex": self.kem_public_key_hex,
            "api_port": self.api_port,
            "p2p_port": self.p2p_port,
        }


class NodeIdentityStore:
    """Persiste l'identité P2P du nœud (clé ML-KEM)."""

    def __init__(self, data_dir: Path) -> None:
        self.path = Path(data_dir) / "p2p" / "node_identity.json"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def load_or_create(self, *, api_port: int = 8000) -> NodeIdentity:
        if self.path.is_file():
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return NodeIdentity(
                network_id=data.get("network_id", NETWORK_ID),
                node_id=data["node_id"],
                kem_public_key_hex=data["kem_public_key_hex"],
                kem_secret_key_hex=data["kem_secret_key_hex"],
                api_port=int(data.get("api_port", api_port)),
                p2p_port=int(data.get("p2p_port", DEFAULT_P2P_PORT)),
            )
        try:
            secret, public = generate_kem_keypair()
        except KEMError as exc:
            raise KEMError(f"Cannot init P2P node identity: {exc}") from exc
        import uuid

        identity = NodeIdentity(
            network_id=NETWORK_ID,
            node_id=f"node_{uuid.uuid4().hex[:12]}",
            kem_public_key_hex=public.hex(),
            kem_secret_key_hex=secret.hex(),
            api_port=api_port,
            p2p_port=DEFAULT_P2P_PORT,
        )
        self._save(identity)
        logger.info("Created P2P node identity %s", identity.node_id)
        return identity

    def _save(self, identity: NodeIdentity) -> None:
        payload = {
            "network_id": identity.network_id,
            "node_id": identity.node_id,
            "kem_public_key_hex": identity.kem_public_key_hex,
            "kem_secret_key_hex": identity.kem_secret_key_hex,
            "api_port": identity.api_port,
            "p2p_port": identity.p2p_port,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self.path.chmod(0o600)
