"""Original symbol registry — AI-minted symbols for ARTCB language."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

ORIGIN_ALPHABET = list("αβγδεζηθικλμνξοπρστυφχψω")
ORIGIN_PREFIX = "∇"


@dataclass
class SymbolRegistry:
    """Mints unique original symbols for concepts not in the fixed USP dictionary."""

    _concept_to_symbol: dict[str, str] = field(default_factory=dict)
    _symbol_counter: int = 1

    def normalize_concept(self, text: str) -> str:
        cleaned = re.sub(r"\s+", " ", text.lower().strip())
        return cleaned[:120]

    def concept_key(self, text: str) -> str:
        normalized = self.normalize_concept(text)
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
        return f"{normalized}|{digest}"

    def mint_original(self, concept: str) -> str:
        """Return a stable original symbol for a novel concept."""
        key = self.concept_key(concept)
        if key in self._concept_to_symbol:
            return self._concept_to_symbol[key]

        index = self._symbol_counter
        self._symbol_counter += 1
        if index <= len(ORIGIN_ALPHABET):
            symbol = f"{ORIGIN_ALPHABET[index - 1]}{index}"
        else:
            symbol = f"{ORIGIN_PREFIX}{index}"

        self._concept_to_symbol[key] = symbol
        return symbol

    def is_original(self, symbol: str) -> bool:
        return symbol.startswith(ORIGIN_PREFIX) or (
            len(symbol) >= 2 and symbol[0] in ORIGIN_ALPHABET
        )

    def export(self) -> dict[str, str]:
        return dict(self._concept_to_symbol)

    @classmethod
    def from_export(cls, data: dict[str, str]) -> SymbolRegistry:
        registry = cls()
        registry._concept_to_symbol = dict(data)
        if data:
            registry._symbol_counter = len(data) + 1
        return registry
