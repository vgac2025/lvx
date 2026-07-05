"""Wallet manager — key storage, balance tracking, transaction history."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

from nacl import encoding, signing

from artcb.config import load_settings
from artcb.wallet.address import address_from_signing_key, generate_address

logger = logging.getLogger("artcb.wallet.manager")


@dataclass
class Wallet:
    """ARTCB wallet with Ed25519 keypair."""
    
    address: str
    signing_key: signing.SigningKey
    public_key_hex: str
    
    @property
    def public_key_b64(self) -> str:
        return self.signing_key.verify_key.encode(encoder=encoding.Base64Encoder).decode("ascii")
    
    def sign(self, message: bytes) -> str:
        """Sign message, return hex signature."""
        signed = self.signing_key.sign(message)
        return signed.signature.hex()
    
    def to_dict(self) -> dict:
        return {
            "address": self.address,
            "public_key_hex": self.public_key_hex,
            "public_key_b64": self.public_key_b64,
        }


class WalletManager:
    """Manages ARTCB wallets — creation, loading, balance tracking."""
    
    def __init__(self, wallet_dir: Path | None = None) -> None:
        settings = load_settings()
        self.wallet_dir = wallet_dir or (settings.data_dir / "wallets")
        self.wallet_dir.mkdir(parents=True, exist_ok=True)
        logger.debug("WalletManager initialized wallet_dir=%s", self.wallet_dir)
    
    def create_wallet(self, *, name: str = "default") -> Wallet:
        """
        Create new wallet with Ed25519 keypair.
        
        Args:
            name: Wallet name (default: "default")
        
        Returns:
            Wallet instance
        """
        key_path = self.wallet_dir / f"{name}.key"
        if key_path.exists():
            raise FileExistsError(f"Wallet {name} already exists at {key_path}")
        
        # Generate Ed25519 keypair
        signing_key = signing.SigningKey.generate()
        address = address_from_signing_key(signing_key)
        
        # Save private key (encrypted in production)
        key_path.write_bytes(signing_key.encode())
        key_path.chmod(0o600)  # Owner read/write only
        
        # Save metadata
        meta_path = self.wallet_dir / f"{name}.json"
        metadata = {
            "address": address,
            "public_key_hex": signing_key.verify_key.encode().hex(),
            "created_at": "2026-07-05T03:25:00Z",  # TODO: use datetime.now()
        }
        meta_path.write_text(json.dumps(metadata, indent=2))
        
        logger.info("Created wallet name=%s address=%s", name, address)
        
        return Wallet(
            address=address,
            signing_key=signing_key,
            public_key_hex=metadata["public_key_hex"],
        )
    
    def load_wallet(self, *, name: str = "default") -> Wallet:
        """
        Load existing wallet.
        
        Args:
            name: Wallet name
        
        Returns:
            Wallet instance
        """
        key_path = self.wallet_dir / f"{name}.key"
        if not key_path.exists():
            raise FileNotFoundError(f"Wallet {name} not found at {key_path}")
        
        # Load private key
        signing_key = signing.SigningKey(key_path.read_bytes())
        address = address_from_signing_key(signing_key)
        
        logger.debug("Loaded wallet name=%s address=%s", name, address)
        
        return Wallet(
            address=address,
            signing_key=signing_key,
            public_key_hex=signing_key.verify_key.encode().hex(),
        )
    
    def list_wallets(self) -> list[dict]:
        """List all wallets with metadata."""
        wallets = []
        for meta_path in self.wallet_dir.glob("*.json"):
            try:
                metadata = json.loads(meta_path.read_text())
                wallets.append(metadata)
            except (json.JSONDecodeError, OSError) as exc:
                logger.warning("Failed to load wallet metadata path=%s error=%s", meta_path, exc)
        return wallets
    
    def get_balance(self, address: str, blocks_path: Path) -> dict:
        """
        Calculate balance from blockchain.
        
        Args:
            address: ARTCB address
            blocks_path: Path to blocks.jsonl
        
        Returns:
            {
                "address": str,
                "balance_satoshi": int,
                "balance_artcb": float,
                "block_count": int,
                "rewards": [{"block_index": int, "reward_satoshi": int, "pol_score": float}]
            }
        """
        if not blocks_path.exists():
            return {
                "address": address,
                "balance_satoshi": 0,
                "balance_artcb": 0.0,
                "block_count": 0,
                "rewards": [],
            }
        
        total_satoshi = 0
        rewards = []
        
        with blocks_path.open(encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if not line:
                    continue
                
                block = json.loads(line)
                contributors = block.get("contributors", [])
                
                for contributor in contributors:
                    if contributor.get("address") == address:
                        reward_satoshi = contributor.get("reward_satoshi", 0)
                        total_satoshi += reward_satoshi
                        rewards.append({
                            "block_index": block["index"],
                            "reward_satoshi": reward_satoshi,
                            "pol_score": contributor.get("pol_score", 0.0),
                        })
        
        return {
            "address": address,
            "balance_satoshi": total_satoshi,
            "balance_artcb": total_satoshi / 1e8,
            "block_count": len(rewards),
            "rewards": rewards,
        }

# Made with Bob
