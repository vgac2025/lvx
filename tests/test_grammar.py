"""Tests unitaires grammaire et macros."""

from artcb.ir.encoder import IREncoder
from artcb.ir.macros import detect_macros


def test_detect_macros_empty_on_short_text():
    encoder = IREncoder()
    graph = encoder.encode("Phrase unique.")
    assert detect_macros(graph) == {}


def test_symbols_assigned():
    encoder = IREncoder()
    graph = encoder.encode("Observer le monde pour apprendre.")
    assert all(n.sym for n in graph.nodes)
    assert all(n.checksum.startswith("sha256:") for n in graph.nodes)
