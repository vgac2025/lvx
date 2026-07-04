"""ctypes bindings to libartcb_chain (C)."""

from __future__ import annotations

import ctypes
import logging
from pathlib import Path

logger = logging.getLogger("artcb.chain.ffi")

ARTCB_HASH_HEX_LEN = 65
ARTCB_MAX_ERR = 512

_LIB: ctypes.CDLL | None = None


def _library_path() -> Path:
    root = Path(__file__).resolve().parents[2]
    return root / "c" / "libartcb_chain.so"


def load_library() -> ctypes.CDLL:
    global _LIB
    if _LIB is not None:
        return _LIB
    path = _library_path()
    if not path.exists():
        raise FileNotFoundError(
            f"libartcb_chain.so not built — run: make -C {path.parent}"
        )
    _LIB = ctypes.CDLL(str(path))
    _LIB.artcb_sha256_hex.argtypes = [ctypes.c_char_p, ctypes.c_size_t, ctypes.c_char_p]
    _LIB.artcb_sha256_hex.restype = ctypes.c_int
    _LIB.artcb_build_canonical.argtypes = [
        ctypes.c_int,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_double,
        ctypes.c_char_p,
        ctypes.c_size_t,
    ]
    _LIB.artcb_build_canonical.restype = ctypes.c_int
    _LIB.artcb_hash_canonical.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    _LIB.artcb_hash_canonical.restype = ctypes.c_int
    _LIB.artcb_verify_chain_file.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_size_t]
    _LIB.artcb_verify_chain_file.restype = ctypes.c_int
    _LIB.artcb_count_blocks.argtypes = [ctypes.c_char_p]
    _LIB.artcb_count_blocks.restype = ctypes.c_int
    logger.debug("Loaded C library path=%s", path)
    return _LIB


def sha256_hex(data: str) -> str:
    lib = load_library()
    out = ctypes.create_string_buffer(ARTCB_HASH_HEX_LEN)
    encoded = data.encode("utf-8")
    rc = lib.artcb_sha256_hex(encoded, len(encoded), out)
    if rc != 0:
        raise RuntimeError("artcb_sha256_hex failed")
    return out.value.decode("ascii")


def build_block_hash(
    index: int,
    timestamp: str,
    prev_hash: str,
    graph_root: str,
    merkle_root: str,
    pol_score: float,
) -> str:
    lib = load_library()
    canonical = ctypes.create_string_buffer(16384)
    rc = lib.artcb_build_canonical(
        index,
        timestamp.encode("utf-8"),
        prev_hash.encode("utf-8"),
        graph_root.encode("utf-8"),
        merkle_root.encode("utf-8"),
        pol_score,
        canonical,
        16384,
    )
    if rc != 0:
        raise RuntimeError("artcb_build_canonical failed")
    out = ctypes.create_string_buffer(ARTCB_HASH_HEX_LEN)
    rc2 = lib.artcb_hash_canonical(canonical, out)
    if rc2 != 0:
        raise RuntimeError("artcb_hash_canonical failed")
    return out.value.decode("ascii")


def verify_chain_file(path: Path) -> tuple[bool, str]:
    lib = load_library()
    err = ctypes.create_string_buffer(ARTCB_MAX_ERR)
    rc = lib.artcb_verify_chain_file(str(path).encode("utf-8"), err, ARTCB_MAX_ERR)
    message = err.value.decode("utf-8", errors="replace")
    return rc == 0, message


def count_blocks(path: Path) -> int:
    lib = load_library()
    if not path.exists():
        return 0
    return int(lib.artcb_count_blocks(str(path).encode("utf-8")))
