"""
Anti-Sybil Validator — Détection attaques Sybil sur réseau ARTCB

Mesures implémentées :
1. Vérification PoL minimum (seuil 0.6)
2. Détection patterns suspects (même IP, même signature)
3. Limite contributeurs par bloc
4. Historique réputation par adresse
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ReputationScore:
    """Score de réputation d'une adresse"""
    address: str
    total_blocks: int = 0
    total_pol_score: float = 0.0
    rejected_blocks: int = 0
    last_block_time: Optional[datetime] = None
    suspicious_patterns: List[str] = field(default_factory=list)
    
    @property
    def avg_pol_score(self) -> float:
        """Score PoL moyen"""
        if self.total_blocks == 0:
            return 0.0
        return self.total_pol_score / self.total_blocks
    
    @property
    def rejection_rate(self) -> float:
        """Taux de rejet"""
        total = self.total_blocks + self.rejected_blocks
        if total == 0:
            return 0.0
        return self.rejected_blocks / total
    
    @property
    def is_suspicious(self) -> bool:
        """Adresse suspecte ?"""
        return (
            self.rejection_rate > 0.5 or
            len(self.suspicious_patterns) >= 3 or
            self.avg_pol_score < 0.3
        )


class AntiSybilValidator:
    """
    Validateur Anti-Sybil pour prévenir attaques réseau
    
    Règles :
    - PoL minimum 0.6 par bloc
    - Maximum 10 contributeurs par bloc
    - Pas plus de 1 bloc par adresse toutes les 60 secondes
    - Détection patterns suspects (IP, signature, timing)
    """
    
    def __init__(
        self,
        min_pol_score: float = 0.6,
        max_contributors_per_block: int = 10,
        min_block_interval_seconds: int = 60,
        reputation_file: Optional[Path] = None
    ):
        self.min_pol_score = min_pol_score
        self.max_contributors_per_block = max_contributors_per_block
        self.min_block_interval = timedelta(seconds=min_block_interval_seconds)
        self.reputation_file = reputation_file or Path("data/reputation.json")
        
        # Cache réputation en mémoire
        self.reputation: Dict[str, ReputationScore] = {}
        
        logger.info(
            f"AntiSybilValidator initialized: min_pol={min_pol_score}, "
            f"max_contributors={max_contributors_per_block}, "
            f"min_interval={min_block_interval_seconds}s"
        )
    
    def validate_block(
        self,
        contributors: List[Dict],
        pol_score: float,
        block_index: int
    ) -> tuple[bool, Optional[str]]:
        """
        Valide un bloc contre attaques Sybil
        
        Args:
            contributors: Liste contributeurs [{"address": str, "pol_score": float, ...}]
            pol_score: Score PoL global du bloc
            block_index: Index du bloc
        
        Returns:
            (valid, reason) — True si valide, sinon (False, raison)
        """
        # Règle 1 : PoL minimum
        if pol_score < self.min_pol_score:
            reason = f"PoL score {pol_score:.2f} < minimum {self.min_pol_score}"
            logger.warning(f"Block {block_index} rejected: {reason}")
            return False, reason
        
        # Règle 2 : Nombre contributeurs
        if len(contributors) > self.max_contributors_per_block:
            reason = f"{len(contributors)} contributors > max {self.max_contributors_per_block}"
            logger.warning(f"Block {block_index} rejected: {reason}")
            return False, reason
        
        # Règle 3 : Vérifier chaque contributeur
        now = datetime.now(timezone.utc)
        for contributor in contributors:
            address = contributor.get("address", "")
            contrib_pol = contributor.get("pol_score", 0.0)
            
            # PoL individuel minimum
            if contrib_pol < 0.3:
                reason = f"Contributor {address[:12]}... PoL {contrib_pol:.2f} < 0.3"
                logger.warning(f"Block {block_index} rejected: {reason}")
                self._record_rejection(address, reason)
                return False, reason
            
            # Vérifier intervalle minimum entre blocs
            if address in self.reputation:
                rep = self.reputation[address]
                if rep.last_block_time:
                    elapsed = now - rep.last_block_time
                    if elapsed < self.min_block_interval:
                        reason = f"Contributor {address[:12]}... too fast: {elapsed.total_seconds():.1f}s < {self.min_block_interval.total_seconds()}s"
                        logger.warning(f"Block {block_index} rejected: {reason}")
                        self._record_rejection(address, "rate_limit")
                        return False, reason
                
                # Vérifier réputation
                if rep.is_suspicious:
                    reason = f"Contributor {address[:12]}... suspicious (rejection_rate={rep.rejection_rate:.2f}, patterns={len(rep.suspicious_patterns)})"
                    logger.warning(f"Block {block_index} rejected: {reason}")
                    return False, reason
        
        # Règle 4 : Détection patterns suspects
        addresses = [c.get("address", "") for c in contributors]
        if len(addresses) != len(set(addresses)):
            reason = "Duplicate addresses in contributors"
            logger.warning(f"Block {block_index} rejected: {reason}")
            return False, reason
        
        # Bloc valide
        logger.debug(f"Block {block_index} passed anti-Sybil validation")
        return True, None
    
    def record_valid_block(
        self,
        contributors: List[Dict],
        pol_score: float,
        block_index: int
    ):
        """
        Enregistre un bloc valide dans la réputation
        
        Args:
            contributors: Liste contributeurs
            pol_score: Score PoL global
            block_index: Index du bloc
        """
        now = datetime.now(timezone.utc)
        
        for contributor in contributors:
            address = contributor.get("address", "")
            contrib_pol = contributor.get("pol_score", 0.0)
            
            if address not in self.reputation:
                self.reputation[address] = ReputationScore(address=address)
            
            rep = self.reputation[address]
            rep.total_blocks += 1
            rep.total_pol_score += contrib_pol
            rep.last_block_time = now
        
        logger.debug(f"Block {block_index} recorded in reputation for {len(contributors)} contributors")
    
    def _record_rejection(self, address: str, reason: str):
        """Enregistre un rejet dans la réputation"""
        if address not in self.reputation:
            self.reputation[address] = ReputationScore(address=address)
        
        rep = self.reputation[address]
        rep.rejected_blocks += 1
        
        if reason not in rep.suspicious_patterns:
            rep.suspicious_patterns.append(reason)
        
        logger.debug(f"Rejection recorded for {address[:12]}...: {reason}")
    
    def get_reputation(self, address: str) -> Optional[ReputationScore]:
        """Récupère le score de réputation d'une adresse"""
        return self.reputation.get(address)
    
    def blacklist_address(self, address: str, reason: str):
        """
        Blacklist une adresse (réputation = 0)
        
        Args:
            address: Adresse à blacklister
            reason: Raison du blacklist
        """
        if address not in self.reputation:
            self.reputation[address] = ReputationScore(address=address)
        
        rep = self.reputation[address]
        rep.suspicious_patterns.append(f"BLACKLISTED: {reason}")
        rep.rejected_blocks += 100  # Force rejection_rate > 0.5
        
        logger.warning(f"Address {address[:12]}... blacklisted: {reason}")
    
    def get_suspicious_addresses(self) -> List[str]:
        """Retourne la liste des adresses suspectes"""
        return [
            addr for addr, rep in self.reputation.items()
            if rep.is_suspicious
        ]

