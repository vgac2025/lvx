"""ARTCB address generation — Bech32-like format with Ed25519 pubkey hash."""

from __future__ import annotations

import hashlib
import logging

from nacl import encoding, signing

logger = logging.getLogger("artcb.wallet.address")

# Bech32 charset (lowercase only)
BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def _bech32_polymod(values: list[int]) -> int:
    """Bech32 checksum polymod."""
    GEN = [0x3B6A57B2, 0x26508E6D, 0x1EA119FA, 0x3D4233DD, 0x2A1462B3]
    chk = 1
    for value in values:
        b = chk >> 25
        chk = (chk & 0x1FFFFFF) << 5 ^ value
        for i in range(5):
            chk ^= GEN[i] if ((b >> i) & 1) else 0
    return chk


def _bech32_hrp_expand(hrp: str) -> list[int]:
    """Expand HRP for checksum."""
    return [ord(x) >> 5 for x in hrp] + [0] + [ord(x) & 31 for x in hrp]


def _bech32_create_checksum(hrp: str, data: list[int]) -> list[int]:
    """Create Bech32 checksum."""
    values = _bech32_hrp_expand(hrp) + data
    polymod = _bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1
    return [(polymod >> 5 * (5 - i)) & 31 for i in range(6)]


def _bech32_encode(hrp: str, data: list[int]) -> str:
    """Encode Bech32 string."""
    combined = data + _bech32_create_checksum(hrp, data)
    return hrp + "1" + "".join([BECH32_CHARSET[d] for d in combined])


def _convertbits(data: bytes, frombits: int, tobits: int, pad: bool = True) -> list[int]:
    """Convert between bit groups."""
    acc = 0
    bits = 0
    ret = []
    maxv = (1 << tobits) - 1
    max_acc = (1 << (frombits + tobits - 1)) - 1
    for value in data:
        acc = ((acc << frombits) | value) & max_acc
        bits += frombits
        while bits >= tobits:
            bits -= tobits
            ret.append((acc >> bits) & maxv)
    if pad:
        if bits:
            ret.append((acc << (tobits - bits)) & maxv)
    elif bits >= frombits or ((acc << (tobits - bits)) & maxv):
        raise ValueError("Invalid padding")
    return ret


def generate_address(public_key_bytes: bytes, *, prefix: str = "artcb") -> str:
    """
    Generate ARTCB address from Ed25519 public key.
    
    Format: artcb1<bech32_encoded_hash>
    
    Args:
        public_key_bytes: 32-byte Ed25519 public key
        prefix: Address prefix (default: "artcb")
    
    Returns:
        Bech32-encoded address (e.g., "artcb1q...")
    """
    if len(public_key_bytes) != 32:
        raise ValueError(f"Public key must be 32 bytes, got {len(public_key_bytes)}")
    
    # Hash pubkey (SHA-256 then RIPEMD-160 like Bitcoin)
    sha256_hash = hashlib.sha256(public_key_bytes).digest()
    ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()
    
    # Convert to 5-bit groups for Bech32
    data = _convertbits(ripemd160_hash, 8, 5)
    
    # Encode with checksum
    address = _bech32_encode(prefix, data)
    
    logger.debug("Generated address=%s from pubkey_hash=%s", address, ripemd160_hash.hex()[:16])
    return address


def verify_address(address: str, *, prefix: str = "artcb") -> bool:
    """
    Verify ARTCB address format and checksum.
    
    Args:
        address: Address to verify
        prefix: Expected prefix
    
    Returns:
        True if valid, False otherwise
    """
    if not address.startswith(prefix + "1"):
        return False
    
    try:
        hrp, data_part = address.split("1", 1)
        if hrp != prefix:
            return False
        
        # Decode data
        data = [BECH32_CHARSET.index(c) for c in data_part]
        
        # Verify checksum
        hrp_expand = _bech32_hrp_expand(hrp)
        if _bech32_polymod(hrp_expand + data) != 1:
            return False
        
        # Verify length (20 bytes RIPEMD-160 → ~32 chars + 6 checksum)
        if len(data) < 6:
            return False
        
        return True
    except (ValueError, IndexError):
        return False


def address_from_signing_key(signing_key: signing.SigningKey, *, prefix: str = "artcb") -> str:
    """Generate address from SigningKey."""
    pubkey_bytes = signing_key.verify_key.encode()
    return generate_address(pubkey_bytes, prefix=prefix)

# Made with Bob
