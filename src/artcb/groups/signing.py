"""Join-request message signing — Ed25519 + optional ML-DSA hybrid."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

from artcb.crypto.hybrid import verify_hybrid
from artcb.wallet.address import address_from_public_key_bytes, verify_address

logger = logging.getLogger("artcb.groups.signing")

JOIN_REQUEST_MAX_AGE_SECONDS = 300


def build_join_challenge(group_id: str, join_code: str, address: str, timestamp: str) -> bytes:
    """Canonical message signed by invitee wallet (private key stays local)."""
    return f"ARTCB-JOIN-REQUEST|{group_id}|{join_code}|{address}|{timestamp}".encode("utf-8")


def verify_join_signature(
    *,
    public_key_hex: str,
    address: str,
    signature_hex: str,
    message: bytes,
    pqc_public_key_hex: str | None = None,
) -> bool:
    """Verify Ed25519 or hybrid signature; pubkey must match claimed address."""
    if not verify_address(address):
        logger.debug("Invalid address format: %s", address[:16])
        return False
    try:
        ed_pubkey = bytes.fromhex(public_key_hex)
        derived = address_from_public_key_bytes(ed_pubkey)
        if derived != address:
            logger.debug("Address mismatch: claimed=%s derived=%s", address[:12], derived[:12])
            return False

        if signature_hex.startswith("hybrid:"):
            if not pqc_public_key_hex:
                logger.debug("Hybrid signature requires pqc_public_key_hex")
                return False
            return verify_hybrid(
                message=message,
                signature_value=signature_hex,
                ed25519_public_key=ed_pubkey,
                pqc_public_key=bytes.fromhex(pqc_public_key_hex),
            )

        verify_key = VerifyKey(ed_pubkey)
        verify_key.verify(message, bytes.fromhex(signature_hex))
        return True
    except (BadSignatureError, ValueError) as exc:
        logger.debug("Signature verification failed: %s", exc)
        return False


def parse_timestamp(ts: str) -> datetime | None:
    try:
        if ts.endswith("Z"):
            return datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        return datetime.fromisoformat(ts)
    except ValueError:
        return None


def timestamp_fresh(ts: str, max_age: int = JOIN_REQUEST_MAX_AGE_SECONDS) -> bool:
    parsed = parse_timestamp(ts)
    if not parsed:
        return False
    now = datetime.now(timezone.utc)
    age = (now - parsed).total_seconds()
    return 0 <= age <= max_age
