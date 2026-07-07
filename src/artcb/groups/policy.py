"""Group security policy flags."""

from __future__ import annotations

import os


def direct_member_invite_allowed() -> bool:
    """Direct POST /members by address — DEBUG only (insecure for production)."""
    return os.getenv("ARTCB_DEBUG_DIRECT_MEMBER", "false").lower() in ("1", "true", "yes")
