"""Environment configuration loader — secrets from .env only (never committed)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class ArtcbSettings:
    debug: bool
    encode_mode: str
    llm_enabled: bool
    bob_api_key: str | None
    bob_api_base: str
    bob_model: str
    bob_team_id: str | None
    bob_instance_id: str | None
    gradium_api_key: str | None
    gradium_api_url: str
    github_token: str | None
    data_dir: Path
    log_dir: Path
    reports_dir: Path
    demo_book_pdf: Path
    pol_alpha: float
    pol_beta: float
    pol_gamma: float
    pol_threshold: float


def load_settings() -> ArtcbSettings:
    def _bool(name: str, default: str = "true") -> bool:
        return os.getenv(name, default).lower() in {"1", "true", "yes", "on"}

    return ArtcbSettings(
        debug=_bool("ARTCB_DEBUG", "true"),
        encode_mode=os.getenv("ARTCB_ENCODE_MODE", "rule-based"),
        llm_enabled=_bool("ARTCB_LLM_ENABLED", "false"),
        bob_api_key=os.getenv("BOB_API_KEY") or os.getenv("OPENROUTER_API_KEY") or None,
        bob_api_base=os.getenv("BOB_API_BASE", "https://api.us-east.bob.ibm.com"),
        bob_model=os.getenv("BOB_MODEL", "ibm/granite-3-8b-instruct"),
        bob_team_id=os.getenv("BOB_TEAM_ID") or None,
        bob_instance_id=os.getenv("BOB_INSTANCE_ID") or None,
        gradium_api_key=os.getenv("GRADIUM_API_KEY") or None,
        gradium_api_url=os.getenv("GRADIUM_API_URL", "https://api.gradium.ai"),
        github_token=os.getenv("GITHUB_TOKEN") or None,
        data_dir=Path(os.getenv("ARTCB_DATA_DIR", "./data")),
        log_dir=Path(os.getenv("ARTCB_LOG_DIR", "./logs")),
        reports_dir=Path(os.getenv("ARTCB_REPORTS_DIR", "./rapports")),
        demo_book_pdf=Path(
            os.getenv(
                "ARTCB_DEMO_BOOK_PDF",
                "data/fixtures/wailly_le_roi_de_l_inconnu.pdf",
            )
        ),
        pol_alpha=float(os.getenv("ARTCB_POL_ALPHA", "0.4")),
        pol_beta=float(os.getenv("ARTCB_POL_BETA", "0.3")),
        pol_gamma=float(os.getenv("ARTCB_POL_GAMMA", "0.3")),
        pol_threshold=float(os.getenv("ARTCB_POL_THRESHOLD", "0.6")),
    )
