#!/usr/bin/env python3
"""Capture métriques sécurité + tests avant/après implémentation AES wallets."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


def _run_pytest() -> dict:
    start = time.perf_counter()
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=no"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    elapsed = time.perf_counter() - start
    last_line = proc.stdout.strip().splitlines()[-1] if proc.stdout.strip() else ""
    passed = failed = 0
    if "passed" in last_line:
        parts = last_line.replace(" in ", " ").split()
        for i, p in enumerate(parts):
            if p == "passed":
                passed = int(parts[i - 1])
            if p == "failed":
                failed = int(parts[i - 1])
    return {
        "exit_code": proc.returncode,
        "passed": passed,
        "failed": failed,
        "duration_seconds": round(elapsed, 3),
        "summary_line": last_line,
    }


def _pqc_metrics() -> dict:
    from artcb.crypto.pqc import PQC_SIG_ALGORITHM, pqc_enabled

    result = {"pqc_enabled": pqc_enabled(), "algorithm": PQC_SIG_ALGORITHM}
    try:
        from artcb.crypto.pqc import generate_keypair

        sk, pk = generate_keypair()
        result["keygen_ok"] = True
        result["secret_key_bytes"] = len(sk)
        result["public_key_bytes"] = len(pk)
    except Exception as exc:
        result["keygen_ok"] = False
        result["error"] = str(exc)
    return result


def _wallet_key_metrics() -> dict:
    import os
    import tempfile

    from artcb.wallet.manager import WalletManager

    os.environ.setdefault("ARTCB_WALLET_PASSPHRASE", "metrics-passphrase-artcb-32chars!")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        wm = WalletManager(wallet_dir=tmp_path)
        w = wm.create_wallet(name="metrics_probe")
        key_path = tmp_path / "metrics_probe.key"
        raw = key_path.read_bytes()
        sig = w.sign(b"probe")
        return {
            "key_file_bytes": len(raw),
            "key_starts_with_artcbenc": raw.startswith(b"ARTCBENC1"),
            "key_is_plain_32_bytes": len(raw) == 32,
            "key_encryption": "AES-256-GCM" if raw.startswith(b"ARTCBENC1") else "none/plain",
            "permissions_octal": oct(key_path.stat().st_mode & 0o777),
            "address_prefix": w.address[:6],
            "hybrid_wallet": w.is_hybrid,
            "pqc_key_file_exists": (tmp_path / "metrics_probe.pqc").exists(),
            "sign_works": len(sig) > 64,
            "signature_is_hybrid": sig.startswith("hybrid:"),
        }


def _chain_metrics() -> dict:
    from artcb.chain.ffi import verify_chain_file

    chain_path = ROOT / "data" / "chain" / "blocks.jsonl"
    if chain_path.is_file():
        valid, msg = verify_chain_file(chain_path)
        lines = len(chain_path.read_text().strip().splitlines())
    else:
        valid, msg, lines = False, "no chain file", 0
    return {"chain_path": str(chain_path), "valid": valid, "message": msg, "block_count": lines}


def _security_modules() -> dict:
    mods = [
        "artcb.security.anti_sybil",
        "artcb.security.slashing",
        "artcb.security.rate_limiter",
        "artcb.wallet.encryption",
        "artcb.crypto.pqc",
        "artcb.crypto.hybrid",
        "artcb.governance.manager",
    ]
    loaded = {}
    for m in mods:
        try:
            __import__(m)
            loaded[m] = True
        except ImportError:
            loaded[m] = False
    return loaded


def collect(label: str) -> dict:
    return {
        "label": label,
        "timestamp_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "pytest": _run_pytest(),
        "wallet_key": _wallet_key_metrics(),
        "pqc": _pqc_metrics(),
        "chain": _chain_metrics(),
        "security_modules": _security_modules(),
        "env": {
            "ARTCB_WALLET_PASSPHRASE_set": bool(__import__("os").getenv("ARTCB_WALLET_PASSPHRASE")),
        },
    }


def main() -> None:
    label = sys.argv[1] if len(sys.argv) > 1 else "snapshot"
    data = collect(label)
    log_dir = ROOT / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    out = log_dir / f"metrics_{label}.json"
    out.write_text(json.dumps(data, indent=2), encoding="utf-8")
    print(json.dumps(data, indent=2))
    print(f"\nWrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
