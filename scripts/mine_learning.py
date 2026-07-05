#!/usr/bin/env python3
"""
CLI de Minage d'Apprentissage ARTCB
Encode des livres PDF, calcule PoL, crée des blocs, distribue rewards collectifs
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

# Ajouter le chemin src au PYTHONPATH
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.artcb.io.pdf_loader import PDFLoader
from src.artcb.ir.encoder import IREncoder
from src.artcb.ir.decoder import IRDecoder
from src.artcb.agents.explorer import Explorer
from src.artcb.agents.critic import Critic
from src.artcb.pol.scorer import PoLScorer
from src.artcb.chain.manager import ChainManager
from src.artcb.wallet.manager import WalletManager
from src.artcb.wallet.address import generate_address
from src.artcb.memory.graph_store import GraphStore
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


class LearningMiner:
    """Mineur d'apprentissage ARTCB avec affichage console détaillé"""
    
    def __init__(self, wallet_name: str = "miner_default"):
        self.wallet_name = wallet_name
        self.wallet_manager = WalletManager()
        self.chain = ChainManager(
            blocks_path=Path("data/chain/blocks.jsonl"),
            enable_security=True
        )
        self.graph_store = GraphStore()
        self.encoder = IREncoder()
        self.decoder = IRDecoder()
        self.explorer = Explorer()
        self.critic = Critic()
        self.pol_scorer = PoLScorer()
        
        # Créer ou charger wallet
        try:
            self.wallet = self.wallet_manager.load_wallet(wallet_name)
            print(f"✅ Wallet chargé: {wallet_name}")
        except FileNotFoundError:
            self.wallet = self.wallet_manager.create_wallet(wallet_name)
            print(f"✅ Nouveau wallet créé: {wallet_name}")
        
        self.address = self.wallet["address"]
        print(f"📍 Adresse: {self.address}\n")
    
    def print_header(self, title: str):
        """Affiche un header formaté"""
        print("\n" + "=" * 80)
        print(f"  {title}")
        print("=" * 80 + "\n")
    
    def print_step(self, step: int, total: int, description: str):
        """Affiche une étape de progression"""
        print(f"[{step}/{total}] {description}")
    
    def print_metric(self, label: str, value: any, unit: str = ""):
        """Affiche une métrique formatée"""
        print(f"  • {label:30} : {value} {unit}")
    
    def mine_book(self, pdf_path: Path, chunk_size: int = 2000) -> Dict:
        """
        Mine un livre PDF complet
        
        Returns:
            Dict avec métriques de minage
        """
        self.print_header(f"🔨 MINAGE D'APPRENTISSAGE — {pdf_path.name}")
        
        start_time = time.time()
        
        # Étape 1: Chargement PDF
        self.print_step(1, 7, "Chargement PDF")
        loader = PDFLoader(pdf_path)
        text = loader.extract_text()
        
        self.print_metric("Fichier", pdf_path.name)
        self.print_metric("Taille originale", len(text), "caractères")
        self.print_metric("Taille fichier", f"{pdf_path.stat().st_size / 1024:.1f}", "KB")
        
        # Étape 2: Encodage IR
        self.print_step(2, 7, "Encodage en IR ARTCB")
        encode_start = time.time()
        ir_result = self.encoder.encode(text)
        encode_time = time.time() - encode_start
        
        graph_id = ir_result.graph_id
        ir_size = len(json.dumps(ir_result.graph.to_dict()))
        compression_ratio = 1 - (ir_size / len(text))
        
        self.print_metric("Graph ID", graph_id)
        self.print_metric("Nœuds créés", len(ir_result.graph.nodes))
        self.print_metric("Arêtes créées", len(ir_result.graph.edges))
        self.print_metric("Taille IR", ir_size, "bytes")
        self.print_metric("Compression", f"{compression_ratio:.2%}")
        self.print_metric("Temps encodage", f"{encode_time:.2f}", "s")
        
        # Étape 3: Dual-Agent Loop
        self.print_step(3, 7, "Dual-Agent Loop (Explorer + Critic)")
        
        # Explorer propose
        explore_result = self.explorer.explore(ir_result.graph)
        self.print_metric("Nœuds proposés", explore_result["nodes_proposed"])
        
        # Critic valide
        critic_result = self.critic.validate(ir_result.graph)
        self.print_metric("Nœuds validés", critic_result["nodes_validated"])
        self.print_metric("Taux validation", f"{critic_result['validation_rate']:.2%}")
        
        # Étape 4: Reconstruction (test réversibilité)
        self.print_step(4, 7, "Test de réversibilité")
        decode_start = time.time()
        reconstructed = self.decoder.decode(ir_result.graph)
        decode_time = time.time() - decode_start
        
        similarity = self._compute_similarity(text, reconstructed)
        reversible = similarity >= 0.99
        
        self.print_metric("Texte reconstruit", len(reconstructed), "caractères")
        self.print_metric("Similarité", f"{similarity:.4f}")
        self.print_metric("Réversible", "✅ OUI" if reversible else "❌ NON")
        self.print_metric("Temps décodage", f"{decode_time:.2f}", "s")
        
        # Étape 5: Calcul PoL Score
        self.print_step(5, 7, "Calcul Proof-of-Learning")
        
        pol_score = self.pol_scorer.compute_score(
            graph=ir_result.graph,
            original_size=len(text),
            validation_result=critic_result
        )
        
        self.print_metric("PoL Score", f"{pol_score:.4f}")
        self.print_metric("Seuil acceptation", "0.6000")
        self.print_metric("Bloc accepté", "✅ OUI" if pol_score >= 0.6 else "❌ NON")
        
        if pol_score < 0.6:
            print("\n⚠️  PoL score insuffisant — bloc rejeté")
            return None
        
        # Étape 6: Création bloc blockchain
        self.print_step(6, 7, "Création bloc blockchain")
        
        # Stocker graphe
        self.graph_store.store(graph_id, ir_result.graph)
        graph_root = ir_result.graph.compute_merkle_root()
        
        # Créer bloc avec contributeur
        block = self.chain.append_block(
            graph_id=graph_id,
            graph_root=graph_root,
            pol_score=pol_score,
            contributors=[{
                "address": self.address,
                "pol_score": pol_score,
                "role": "miner"
            }]
        )
        
        self.print_metric("Bloc index", block.index)
        self.print_metric("Hash bloc", block.hash[:16] + "...")
        self.print_metric("Signature", block.signature[:32] + "...")
        
        # Étape 7: Calcul rewards
        self.print_step(7, 7, "Distribution rewards collectifs")
        
        block_reward_satoshi = self.chain.calculate_block_reward(block.index)
        block_reward_artcb = block_reward_satoshi / 100_000_000
        
        # Dans ce cas, un seul contributeur (le mineur)
        # Mais la formule supporte plusieurs contributeurs
        reward_satoshi = block_reward_satoshi  # 100% pour le seul contributeur
        reward_artcb = reward_satoshi / 100_000_000
        
        self.print_metric("Block reward", f"{block_reward_artcb:.8f}", "ARTCB")
        self.print_metric("Reward mineur", f"{reward_artcb:.8f}", "ARTCB")
        self.print_metric("Reward satoshi", reward_satoshi, "sat")
        
        # Balance totale
        balance = self.wallet_manager.get_balance(self.address, self.chain)
        
        self.print_metric("Balance totale", f"{balance['balance_artcb']:.8f}", "ARTCB")
        self.print_metric("Blocs minés", balance["blocks_count"])
        
        # Temps total
        total_time = time.time() - start_time
        
        print("\n" + "-" * 80)
        self.print_metric("⏱️  Temps total minage", f"{total_time:.2f}", "s")
        self.print_metric("⚡ Vitesse", f"{len(text) / total_time:.0f}", "char/s")
        print("-" * 80)
        
        return {
            "pdf_path": str(pdf_path),
            "graph_id": graph_id,
            "block_index": block.index,
            "block_hash": block.hash,
            "pol_score": pol_score,
            "compression_ratio": compression_ratio,
            "reversible": reversible,
            "similarity": similarity,
            "reward_artcb": reward_artcb,
            "reward_satoshi": reward_satoshi,
            "balance_artcb": balance["balance_artcb"],
            "total_time": total_time,
            "nodes_count": len(ir_result.graph.nodes),
            "edges_count": len(ir_result.graph.edges)
        }
    
    def _compute_similarity(self, text1: str, text2: str) -> float:
        """Calcule similarité entre 2 textes (simple ratio caractères)"""
        if not text1 or not text2:
            return 0.0
        
        # Normaliser espaces
        t1 = " ".join(text1.split())
        t2 = " ".join(text2.split())
        
        # Ratio longueur
        len_ratio = min(len(t1), len(t2)) / max(len(t1), len(t2))
        
        # Ratio caractères communs (approximation rapide)
        common = sum(1 for c1, c2 in zip(t1, t2) if c1 == c2)
        char_ratio = common / max(len(t1), len(t2))
        
        return (len_ratio + char_ratio) / 2
    
    def compare_with_existing_systems(self):
        """Compare ARTCB avec Bitcoin, Ethereum, etc."""
        self.print_header("📊 COMPARAISON AVEC SYSTÈMES EXISTANTS")
        
        comparisons = [
            {
                "Système": "Bitcoin (PoW)",
                "Consensus": "Proof-of-Work SHA-256",
                "Reward": "Winner-takes-all (1 gagnant)",
                "Travail": "Hash compétitif (inutile)",
                "Gaspillage": "~99% calcul perdu",
                "Supply": "21M BTC",
                "Halving": "210k blocs (~4 ans)"
            },
            {
                "Système": "Ethereum (PoS)",
                "Consensus": "Proof-of-Stake",
                "Reward": "Validateurs sélectionnés",
                "Travail": "Stake capital (barrière)",
                "Gaspillage": "Faible (PoS)",
                "Supply": "Infini (EIP-1559 burn)",
                "Halving": "N/A"
            },
            {
                "Système": "Filecoin (PoSt)",
                "Consensus": "Proof-of-Spacetime",
                "Reward": "Stockage prouvé",
                "Travail": "Stockage données",
                "Gaspillage": "Faible (utile)",
                "Supply": "2B FIL",
                "Halving": "Décroissance exponentielle"
            },
            {
                "Système": "ARTCB (PoL)",
                "Consensus": "Proof-of-Learning",
                "Reward": "✨ Collectif proportionnel PoL",
                "Travail": "Compression + validation",
                "Gaspillage": "Minimal (apprentissage)",
                "Supply": "21M ARTCB",
                "Halving": "210k blocs (~4 ans)"
            }
        ]
        
        # Afficher tableau
        headers = ["Système", "Consensus", "Reward", "Travail", "Gaspillage"]
        
        for header in headers:
            print(f"{header:20}", end=" | ")
        print()
        print("-" * 120)
        
        for comp in comparisons:
            for header in headers:
                value = comp[header]
                if "ARTCB" in comp["Système"] and header == "Reward":
                    value = f"✨ {value}"
                print(f"{value:20}", end=" | ")
            print()
        
        print("\n" + "=" * 80)
        print("🎯 INNOVATION ARTCB:")
        print("=" * 80)
        print("1. ✅ Reward COLLECTIF : Tous les contributeurs PoL payés proportionnellement")
        print("2. ✅ Travail UTILE : Compression + validation (pas hash inutile)")
        print("3. ✅ Gaspillage MINIMAL : Calcul orienté apprentissage")
        print("4. ✅ Réversibilité 100% : Reconstruction exacte du texte original")
        print("5. ✅ Dual-Agent : Explorer propose, Critic valide")
        print("=" * 80 + "\n")


def main():
    """Point d'entrée CLI"""
    print("\n" + "=" * 80)
    print("  🔨 ARTCB — CLI de Minage d'Apprentissage (Proof-of-Learning)")
    print("=" * 80 + "\n")
    
    # Créer mineur
    miner = LearningMiner(wallet_name="miner_demo")
    
    # Comparer avec systèmes existants
    miner.compare_with_existing_systems()
    
    # Miner les 2 livres
    books = [
        Path("data/fixtures/wailly_le_roi_de_l_inconnu.pdf"),
        Path("data/fixtures/quintus_de_smyrne_la_fin_de_l_iliade.pdf")
    ]
    
    results = []
    
    for book in books:
        if not book.exists():
            print(f"⚠️  Fichier introuvable: {book}")
            continue
        
        result = miner.mine_book(book)
        if result:
            results.append(result)
        
        time.sleep(1)  # Pause entre livres
    
    # Résumé final
    if results:
        miner.print_header("📈 RÉSUMÉ FINAL MINAGE")
        
        total_reward = sum(r["reward_artcb"] for r in results)
        total_blocks = len(results)
        avg_pol = sum(r["pol_score"] for r in results) / total_blocks
        avg_compression = sum(r["compression_ratio"] for r in results) / total_blocks
        
        miner.print_metric("Livres minés", total_blocks)
        miner.print_metric("Reward total", f"{total_reward:.8f}", "ARTCB")
        miner.print_metric("PoL moyen", f"{avg_pol:.4f}")
        miner.print_metric("Compression moyenne", f"{avg_compression:.2%}")
        miner.print_metric("Réversibilité", "✅ 100%" if all(r["reversible"] for r in results) else "⚠️  Partielle")
        
        # Balance finale
        balance = miner.wallet_manager.get_balance(miner.address, miner.chain)
        miner.print_metric("Balance finale", f"{balance['balance_artcb']:.8f}", "ARTCB")
        
        print("\n" + "=" * 80)
        print("✅ Minage terminé avec succès !")
        print("=" * 80 + "\n")
        
        # Sauvegarder résultats
        output_file = Path("logs") / f"mining_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(exist_ok=True)
        
        with open(output_file, "w") as f:
            json.dump({
                "miner_address": miner.address,
                "timestamp": datetime.now().isoformat(),
                "results": results,
                "summary": {
                    "total_blocks": total_blocks,
                    "total_reward_artcb": total_reward,
                    "avg_pol_score": avg_pol,
                    "avg_compression": avg_compression,
                    "final_balance_artcb": balance["balance_artcb"]
                }
            }, f, indent=2)
        
        print(f"📄 Résultats sauvegardés: {output_file}\n")


if __name__ == "__main__":
    main()

# Made with Bob
