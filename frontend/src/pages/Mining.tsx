import { useEffect, useState } from "react";
import { fetchChain, fetchPolScore } from "../api/client";
import { McBlockRow } from "../components/McBlockRow";
import type { ChainBlock } from "../types";

export function Mining() {
  const [blocks, setBlocks] = useState<ChainBlock[]>([]);
  const [pol, setPol] = useState<number | null>(null);

  useEffect(() => {
    fetchChain().then(setBlocks).catch(() => {});
    fetchPolScore().then((p) => setPol(p.pol_score)).catch(() => {});
  }, []);

  const lastReward = blocks.length
    ? (blocks[blocks.length - 1].block_reward ?? 100_000_000) / 1e8
    : 1;

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Minage ⛏</h1>

      <div className="panel mc-mining-panel">
        <div className="mc-mining-hero">
          <span className="mc-pickaxe" aria-hidden>⛏</span>
          <div>
            <h2>Proof-of-Learning Mining</h2>
            <p className="mc-muted">
              Un bloc est miné quand PoL ≥ seuil et le graphe est signé sur chaîne.
            </p>
          </div>
        </div>

        <div className="mc-hotbar">
          <div className="mc-slot mc-slot-gold">
            <div className="mc-kpi-label">Reward actuel</div>
            <div className="mc-kpi-value mc-gold-text">{lastReward} ARTCB</div>
          </div>
          <div className="mc-slot">
            <div className="mc-kpi-label">PoL session</div>
            <div className="mc-kpi-value">{pol?.toFixed(2) ?? "—"}</div>
          </div>
          <div className="mc-slot">
            <div className="mc-kpi-label">Blocs minés</div>
            <div className="mc-kpi-value">{blocks.length}</div>
          </div>
        </div>

        <h3>Derniers blocs minés</h3>
        <McBlockRow blocks={blocks} limit={10} />
      </div>
    </div>
  );
}
