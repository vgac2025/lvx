"""Hybrid classical + post-quantum signatures."""

from __future__ import annotations

import logging
from dataclasses import dataclass

from nacl import signing

from src.artcb.crypto.pqc import PQC_SIG_ALGORITHM, sign_message, verify_message

logger = logging.getLogger("artcb.crypto.hybrid")

HYBRID_PREFIX = "hybrid:"
ED25519_PREFIX = "ed25519:"


@dataclass(frozen=True)
class HybridSignature:
    ed25519_hex: str
    mldsa_hex: str

    def serialize(self) -> str:
        return f"{HYBRID_PREFIX}{ED25519_PREFIX}{self.ed25519_hex}|mldsa65:{self.mldsa_hex}"

    @classmethod
    def parse(cls, value: str) -> HybridSignature | None:
        if not value.startswith(HYBRID_PREFIX):
            return None
        body = value[len(HYBRID_PREFIX) :]
        if "|mldsa65:" not in body:
            return None
        ed_part, mldsa_part = body.split("|mldsa65:", 1)
        if not ed_part.startswith(ED25519_PREFIX):
            return None
        return cls(ed25519_hex=ed_part[len(ED25519_PREFIX) :], mldsa_hex=mldsa_part)


def sign_hybrid(
    *,
    ed25519_key: signing.SigningKey,
    pqc_secret_key: bytes,
    message: bytes,
) -> str:
    ed_sig = ed25519_key.sign(message).signature.hex()
    pqc_sig = sign_message(message, pqc_secret_key).hex()
    return HybridSignature(ed25519_hex=ed_sig, mldsa_hex=pqc_sig).serialize()


def verify_hybrid(
    *,
    message: bytes,
    signature_value: str,
    ed25519_public_key: bytes,
    pqc_public_key: bytes,
) -> bool:
    parsed = HybridSignature.parse(signature_value)
    if parsed:
        try:
            verify_key = signing.VerifyKey(ed25519_public_key)
            verify_key.verify(message, bytes.fromhex(parsed.ed25519_hex))
            if not verify_message(message, bytes.fromhex(parsed.mldsa_hex), pqc_public_key):
                logger.debug("ML-DSA leg of hybrid signature invalid")
                return False
            return True
        except Exception as exc:
            logger.debug("Hybrid verify failed: %s", exc)
            return False

    # Legacy ed25519-only: "ed25519:hex" or raw hex with VerifyKey
    sig_hex = signature_value[len(ED25519_PREFIX):] if signature_value.startswith(ED25519_PREFIX) else signature_value
    try:
        verify_key = signing.VerifyKey(ed25519_public_key)
        verify_key.verify(message, bytes.fromhex(sig_hex))
        return True
    except Exception:
        return False


def algorithm_label() -> str:
    return f"Ed25519+{PQC_SIG_ALGORITHM}"
