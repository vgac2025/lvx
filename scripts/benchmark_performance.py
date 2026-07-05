#!/usr/bin/env python3
"""Benchmark performance ARTCB — encodage, décodage, blockchain C."""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from artcb.ir.encoder import IREncoder
from artcb.ir.decoder import IRDecoder
from artcb.chain import ffi
from artcb.pol.scorer import PolScorer


def benchmark_ir_encoding():
    """Benchmark encodage IR."""
    text = "Nous avons décidé d'utiliser FastAPI pour le backend. " * 10
    encoder = IREncoder()
    
    start = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        graph = encoder.encode(text)
    encode_time = (time.perf_counter() - start) / iterations
    
    return {
        "text_length": len(text),
        "encode_ms": encode_time * 1000,
        "nodes": len(graph.nodes),
        "edges": len(graph.edges),
        "json_size": len(graph.to_json()),
        "compression_ratio": 1 - len(graph.to_json()) / len(text),
    }


def benchmark_ir_decoding():
    """Benchmark décodage IR."""
    text = "Nous avons décidé d'utiliser FastAPI pour le backend. " * 10
    encoder = IREncoder()
    decoder = IRDecoder()
    graph = encoder.encode(text)
    
    start = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        result = decoder.decode(graph)
    decode_time = (time.perf_counter() - start) / iterations
    
    return {
        "decode_ms": decode_time * 1000,
        "reversible": decoder.decode_with_metrics(graph)["reversible"],
        "similarity": decoder.decode_with_metrics(graph)["similarity"],
    }


def benchmark_blockchain_c():
    """Benchmark blockchain C (SHA-256)."""
    data = "ARTCB" * 100
    
    start = time.perf_counter()
    iterations = 1000
    for _ in range(iterations):
        digest = ffi.sha256_hex(data)
    hash_time = (time.perf_counter() - start) / iterations
    
    return {
        "data_length": len(data),
        "hash_ms": hash_time * 1000,
        "digest_length": len(digest),
    }


def benchmark_pol_scoring():
    """Benchmark calcul PoL."""
    encoder = IREncoder()
    scorer = PolScorer()
    graph = encoder.encode("Nous avons décidé d'utiliser FastAPI. Le problème est la perte de contexte.")
    
    start = time.perf_counter()
    iterations = 100
    for _ in range(iterations):
        result = scorer.score(graph)
    pol_time = (time.perf_counter() - start) / iterations
    
    return {
        "pol_ms": pol_time * 1000,
        "pol_score": result.pol_score,
        "block_accepted": result.block_accepted,
    }


def main():
    print("=== ARTCB Performance Benchmark ===\n")
    
    print("1. IR Encoding")
    enc = benchmark_ir_encoding()
    print(f"   Texte: {enc['text_length']} chars")
    print(f"   Temps: {enc['encode_ms']:.2f}ms/op")
    print(f"   Nœuds: {enc['nodes']}, Liens: {enc['edges']}")
    print(f"   Compression: {enc['compression_ratio']:.1%}")
    print(f"   Taille JSON: {enc['json_size']} bytes\n")
    
    print("2. IR Decoding")
    dec = benchmark_ir_decoding()
    print(f"   Temps: {dec['decode_ms']:.2f}ms/op")
    print(f"   Réversible: {dec['reversible']}")
    print(f"   Similarité: {dec['similarity']:.2%}\n")
    
    print("3. Blockchain C (SHA-256)")
    chain = benchmark_blockchain_c()
    print(f"   Données: {chain['data_length']} bytes")
    print(f"   Temps: {chain['hash_ms']:.3f}ms/op")
    print(f"   Digest: {chain['digest_length']} chars\n")
    
    print("4. PoL Scoring")
    pol = benchmark_pol_scoring()
    print(f"   Temps: {pol['pol_ms']:.2f}ms/op")
    print(f"   Score: {pol['pol_score']:.2f}")
    print(f"   Bloc accepté: {pol['block_accepted']}\n")
    
    print("=== Benchmark Complete ===")
    
    # Critères performance CDC NF-01, NF-02
    if enc['encode_ms'] < 2000:
        print("✅ NF-01: Encodage 500 mots < 2s")
    else:
        print(f"⚠️ NF-01: Encodage {enc['encode_ms']:.0f}ms > 2000ms")
    
    if dec['decode_ms'] < 1000:
        print("✅ NF-02: Reconstruction < 1s")
    else:
        print(f"⚠️ NF-02: Décodage {dec['decode_ms']:.0f}ms > 1000ms")


if __name__ == "__main__":
    main()

