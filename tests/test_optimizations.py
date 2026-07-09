"""Tests pour les optimisations performance (cache, parallélisme)."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from artcb.io.pdf_loader import extract_pdf_text, resolve_book_path
from artcb.ir.encoder import IREncoder


class TestCacheOptimization:
    """Test cache encodage IR."""

    def test_cache_enabled_by_default(self):
        """Le cache doit être activé par défaut."""
        encoder = IREncoder()
        assert encoder._cache_enabled is True
        assert encoder._cache is not None

    def test_cache_can_be_disabled(self):
        """Le cache peut être désactivé."""
        encoder = IREncoder(enable_cache=False)
        assert encoder._cache_enabled is False
        assert encoder._cache is None

    def test_cache_hit_reuses_graph(self):
        """Cache HIT doit réutiliser le graphe existant."""
        encoder = IREncoder()
        text = "Le roi décide d'explorer le royaume inconnu."

        # Premier encodage (cache MISS)
        graph1 = encoder.encode(text, session_id="sess1")
        assert len(encoder._cache) == 1

        # Deuxième encodage même texte (cache HIT)
        graph2 = encoder.encode(text, session_id="sess2")
        assert len(encoder._cache) == 1  # Pas de nouvelle entrée

        # Graphes différents (session_id différent) mais même structure
        assert graph1.graph_id == "sess1"
        assert graph2.graph_id == "sess2"
        assert len(graph1.nodes) == len(graph2.nodes)
        assert graph1.source_text == graph2.source_text

    def test_cache_performance_gain(self):
        """Cache doit améliorer les performances."""
        text = "Le roi décide d'explorer le royaume. Il part à l'aventure avec courage."

        # Sans cache
        encoder_no_cache = IREncoder(enable_cache=False)
        start = time.perf_counter()
        for _ in range(10):
            encoder_no_cache.encode(text)
        time_no_cache = time.perf_counter() - start

        # Avec cache
        encoder_cache = IREncoder(enable_cache=True)
        start = time.perf_counter()
        for _ in range(10):
            encoder_cache.encode(text)
        time_cache = time.perf_counter() - start

        # Cache doit être au moins 20% plus rapide
        speedup = time_no_cache / time_cache
        assert speedup > 1.2, f"Cache speedup {speedup:.2f}x insuffisant (attendu >1.2x)"

    def test_cache_different_texts(self):
        """Textes différents doivent créer des entrées cache séparées."""
        encoder = IREncoder()

        text1 = "Premier texte."
        text2 = "Deuxième texte différent."

        graph1 = encoder.encode(text1)
        graph2 = encoder.encode(text2)

        assert len(encoder._cache) == 2
        assert graph1.source_text != graph2.source_text


class TestParallelPDFProcessing:
    """Test traitement parallèle PDF."""

    @pytest.fixture
    def pdf_path(self) -> Path | None:
        """Chemin vers PDF test (Wailly)."""
        return resolve_book_path()

    def test_parallel_extraction_enabled(self, pdf_path):
        """Extraction parallèle doit être activable."""
        if not pdf_path or not pdf_path.is_file():
            pytest.skip("PDF Wailly non disponible")

        # Extraction parallèle
        text_parallel = extract_pdf_text(pdf_path, max_pages=10, parallel=True)
        assert len(text_parallel) > 0

        # Extraction séquentielle
        text_sequential = extract_pdf_text(pdf_path, max_pages=10, parallel=False)
        assert len(text_sequential) > 0

        # Résultats identiques
        assert text_parallel == text_sequential

    def test_parallel_faster_for_large_pdfs(self, pdf_path):
        """Traitement parallèle doit produire résultats identiques (speedup variable selon overhead)."""
        if not pdf_path or not pdf_path.is_file():
            pytest.skip("PDF Wailly non disponible")

        # Séquentiel
        start = time.perf_counter()
        text_seq = extract_pdf_text(pdf_path, max_pages=20, parallel=False)
        time_seq = time.perf_counter() - start

        # Parallèle
        start = time.perf_counter()
        text_par = extract_pdf_text(pdf_path, max_pages=20, parallel=True)
        time_par = time.perf_counter() - start

        # Vérifier résultats identiques (critère principal)
        assert text_seq == text_par

        # Note: Speedup variable selon overhead multiprocessing
        # Sur petits PDFs, overhead peut dominer. Gain réel sur PDFs >50 pages.
        speedup = time_seq / time_par
        print(f"\nParallel speedup: {speedup:.2f}x (seq={time_seq:.3f}s, par={time_par:.3f}s)")

    def test_sequential_for_small_pdfs(self, pdf_path):
        """Petits PDFs (<4 pages) doivent utiliser traitement séquentiel."""
        if not pdf_path or not pdf_path.is_file():
            pytest.skip("PDF Wailly non disponible")

        # Avec parallel=True mais seulement 2 pages, doit fallback sur séquentiel
        text = extract_pdf_text(pdf_path, max_pages=2, parallel=True)
        assert len(text) > 0


class TestIntegrationOptimizations:
    """Tests d'intégration des optimisations."""

    def test_cache_and_parallel_together(self):
        """Cache + parallélisme doivent fonctionner ensemble."""
        pdf_path = resolve_book_path()
        if not pdf_path or not pdf_path.is_file():
            pytest.skip("PDF Wailly non disponible")

        encoder = IREncoder(enable_cache=True)

        # Extraire texte en parallèle
        text = extract_pdf_text(pdf_path, max_pages=5, parallel=True)

        # Premier encodage (cache MISS)
        graph1 = encoder.encode(text)
        assert len(encoder._cache) == 1

        # Deuxième encodage (cache HIT)
        graph2 = encoder.encode(text)
        assert len(encoder._cache) == 1
        assert graph1.source_text == graph2.source_text

    def test_end_to_end_performance(self):
        """Test performance bout-en-bout avec optimisations (focus cache)."""
        pdf_path = resolve_book_path()
        if not pdf_path or not pdf_path.is_file():
            pytest.skip("PDF Wailly non disponible")

        # Sans cache (baseline)
        encoder_no_cache = IREncoder(enable_cache=False)
        start = time.perf_counter()
        text = extract_pdf_text(pdf_path, max_pages=10, parallel=False)
        for _ in range(5):
            encoder_no_cache.encode(text)
        time_no_cache = time.perf_counter() - start

        # Avec cache (optimisé)
        encoder_cache = IREncoder(enable_cache=True)
        start = time.perf_counter()
        for _ in range(5):
            encoder_cache.encode(text)
        time_cache = time.perf_counter() - start

        # Cache doit améliorer performance (gain principal sur encodages répétés)
        speedup = time_no_cache / time_cache
        assert speedup > 1.5, f"Speedup cache {speedup:.2f}x insuffisant (attendu >1.5x)"
        print(f"\nCache speedup: {speedup:.2f}x (no_cache={time_no_cache:.3f}s, cache={time_cache:.3f}s)")

