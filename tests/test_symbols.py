"""Tests for original AI-minted symbols."""

from artcb.ir.encoder import IREncoder
from artcb.ir.symbols import SymbolRegistry


def test_mint_original_symbol_stable():
    registry = SymbolRegistry()
    first = registry.mint_original("quantum entanglement reasoning")
    second = registry.mint_original("quantum entanglement reasoning")
    assert first == second
    assert registry.is_original(first)


def test_encoder_stores_orig_symbols():
    text = "The flarnick process requires careful observation."
    graph = IREncoder().encode(text)
    assert graph.orig_symbols
    assert any("flarnick" in key for key in graph.orig_symbols)


def test_original_symbol_in_node():
    text = "We must analyze the zorbax mechanism today."
    graph = IREncoder().encode(text)
    symbols = [n.sym for n in graph.nodes]
    assert any(any(c in s for c in "αβγδεζηθ∇") for s in symbols)
