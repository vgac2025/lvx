"""Tests wallet AES-256-GCM encryption at rest."""

from __future__ import annotations

from pathlib import Path

import pytest
from nacl import signing

from artcb.wallet.encryption import (
    WalletEncryptionError,
    decrypt_private_key,
    encrypt_legacy_key_file,
    encrypt_private_key,
    is_encrypted_key_blob,
    is_plain_ed25519_seed,
)
from artcb.wallet.manager import WalletManager


class TestWalletEncryptionModule:
    def test_encrypt_decrypt_roundtrip(self):
        seed = signing.SigningKey.generate().encode()
        blob = encrypt_private_key(seed, passphrase="test-passphrase-artcb-dev-32chars!")
        assert is_encrypted_key_blob(blob)
        assert not is_plain_ed25519_seed(blob)
        assert len(blob) > 32
        recovered = decrypt_private_key(blob, passphrase="test-passphrase-artcb-dev-32chars!")
        assert recovered == seed

    def test_wrong_passphrase_fails(self):
        seed = signing.SigningKey.generate().encode()
        blob = encrypt_private_key(seed, passphrase="test-passphrase-artcb-dev-32chars!")
        with pytest.raises(WalletEncryptionError):
            decrypt_private_key(blob, passphrase="wrong-passphrase-xxx")

    def test_legacy_plain_seed_still_loads(self):
        seed = signing.SigningKey.generate().encode()
        assert is_plain_ed25519_seed(seed)
        assert decrypt_private_key(seed, passphrase="test-passphrase-artcb-dev-32chars!") == seed

    def test_missing_passphrase_raises(self, monkeypatch: pytest.MonkeyPatch):
        monkeypatch.delenv("ARTCB_WALLET_PASSPHRASE", raising=False)
        seed = signing.SigningKey.generate().encode()
        with pytest.raises(WalletEncryptionError):
            encrypt_private_key(seed)

    def test_migrate_legacy_key_file(self, tmp_path: Path):
        seed = signing.SigningKey.generate().encode()
        key_path = tmp_path / "legacy.key"
        key_path.write_bytes(seed)
        assert encrypt_legacy_key_file(key_path, passphrase="test-passphrase-artcb-dev-32chars!")
        blob = key_path.read_bytes()
        assert is_encrypted_key_blob(blob)
        assert decrypt_private_key(blob, passphrase="test-passphrase-artcb-dev-32chars!") == seed


class TestWalletManagerEncrypted:
    def test_create_wallet_encrypted_on_disk(self, tmp_path: Path):
        wm = WalletManager(wallet_dir=tmp_path)
        wallet = wm.create_wallet(name="secure")
        key_bytes = (tmp_path / "secure.key").read_bytes()
        assert is_encrypted_key_blob(key_bytes)
        assert not is_plain_ed25519_seed(key_bytes)
        meta = (tmp_path / "secure.json").read_text()
        assert "AES-256-GCM" in meta
        loaded = wm.load_wallet(name="secure")
        assert loaded.address == wallet.address

    def test_plain_key_auto_migrates_on_load(self, tmp_path: Path):
        seed = signing.SigningKey.generate().encode()
        key_path = tmp_path / "old.key"
        key_path.write_bytes(seed)
        (tmp_path / "old.json").write_text('{"address":"x"}')
        wm = WalletManager(wallet_dir=tmp_path)
        wm.load_wallet(name="old")
        assert is_encrypted_key_blob(key_path.read_bytes())
