"""Tests ML-KEM transport P2P."""

from __future__ import annotations

import pytest

from cryptography.exceptions import InvalidTag

from artcb.crypto.kem import decrypt_payload, encrypt_payload, generate_kem_keypair


def test_kem_roundtrip_encrypt_decrypt() -> None:
    sk_a, pk_a = generate_kem_keypair()
    sk_b, pk_b = generate_kem_keypair()
    plaintext = b"ARTCB P2P public blocks payload test"
    envelope = encrypt_payload(plaintext, pk_b)
    decrypted = decrypt_payload(envelope, sk_b)
    assert decrypted == plaintext
    # Wrong key fails
    with pytest.raises(InvalidTag):
        decrypt_payload(envelope, sk_a)


def test_kem_keypair_sizes() -> None:
    sk, pk = generate_kem_keypair()
    assert len(sk) > 0
    assert len(pk) > 0
