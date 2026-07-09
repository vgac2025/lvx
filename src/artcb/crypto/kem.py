"""Post-quantum key encapsulation — ML-KEM-768 (NIST) via liboqs."""

from __future__ import annotations

import hashlib
import logging
import os
import secrets
from typing import Final

from cryptography.hazmat.primitives.ciphers.aead import AESGCM

logger = logging.getLogger("artcb.crypto.kem")

KEM_ALGORITHM: Final[str] = "ML-KEM-768"
ENV_KEM_ENABLED = "ARTCB_KEM_ENABLED"
NONCE_LEN = 12
POOL_CHUNK_CONTEXT: Final[bytes] = b"artcb-pool-chunk-v1"
POOL_RESULT_CONTEXT: Final[bytes] = b"artcb-pool-result-v1"


class KEMError(Exception):
    """ML-KEM operation failed."""


def kem_enabled() -> bool:
    return os.getenv(ENV_KEM_ENABLED, "true").lower() in ("1", "true", "yes", "on")


def _import_oqs():
    try:
        import oqs
    except ImportError as exc:
        raise KEMError("liboqs-python not installed — pip install liboqs-python") from exc
    return oqs


def generate_kem_keypair() -> tuple[bytes, bytes]:
    """Return (secret_key, public_key) for ML-KEM-768."""
    oqs = _import_oqs()
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        public_key = kem.generate_keypair()
        secret_key = kem.export_secret_key()
    logger.debug("Generated %s keypair pub=%d bytes", KEM_ALGORITHM, len(public_key))
    return secret_key, public_key


def encapsulate(peer_public_key: bytes) -> tuple[bytes, bytes]:
    """Return (ciphertext, shared_secret) for sending to peer."""
    oqs = _import_oqs()
    with oqs.KeyEncapsulation(KEM_ALGORITHM) as kem:
        ciphertext, shared_secret = kem.encap_secret(peer_public_key)
    return ciphertext, shared_secret


def decapsulate(ciphertext: bytes, secret_key: bytes) -> bytes:
    """Recover shared secret from ciphertext using our secret key."""
    oqs = _import_oqs()
    with oqs.KeyEncapsulation(KEM_ALGORITHM, secret_key=secret_key) as kem:
        return kem.decap_secret(ciphertext)


def derive_aes_key(shared_secret: bytes, *, context: bytes = b"artcb-p2p-v1") -> bytes:
    return hashlib.sha256(shared_secret + context).digest()


def encrypt_payload(
    plaintext: bytes,
    peer_public_key: bytes,
    *,
    context: bytes = b"artcb-p2p-v1",
) -> dict[str, str]:
    """ML-KEM encapsulation + AES-256-GCM payload."""
    if not kem_enabled():
        raise KEMError("ML-KEM disabled — set ARTCB_KEM_ENABLED=true")
    ciphertext, shared = encapsulate(peer_public_key)
    key = derive_aes_key(shared, context=context)
    nonce = secrets.token_bytes(NONCE_LEN)
    sealed = AESGCM(key).encrypt(nonce, plaintext, None)
    return {
        "kem_alg": KEM_ALGORITHM,
        "kem_ct": ciphertext.hex(),
        "nonce": nonce.hex(),
        "ciphertext": sealed.hex(),
        "context": context.decode("ascii", errors="replace"),
    }


def decrypt_payload(
    envelope: dict[str, str],
    secret_key: bytes,
    *,
    context: bytes | None = None,
) -> bytes:
    """Decrypt envelope received from a peer."""
    if envelope.get("kem_alg") != KEM_ALGORITHM:
        raise KEMError(f"Unsupported KEM: {envelope.get('kem_alg')}")
    ctx = context
    if ctx is None and envelope.get("context"):
        ctx = envelope["context"].encode("utf-8")
    if ctx is None:
        ctx = b"artcb-p2p-v1"
    kem_ct = bytes.fromhex(envelope["kem_ct"])
    nonce = bytes.fromhex(envelope["nonce"])
    sealed = bytes.fromhex(envelope["ciphertext"])
    shared = decapsulate(kem_ct, secret_key)
    key = derive_aes_key(shared, context=ctx)
    return AESGCM(key).decrypt(nonce, sealed, None)
