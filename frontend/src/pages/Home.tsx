import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { fetchChain, fetchPolScore } from "../api/client";
import { McBlockRow } from "../components/McBlockRow";
import { McKpiSlot } from "../components/McKpiSlot";
import type { ChainBlock } from "../types";
import axios from "axios";

const CHECKLIST = [
  { id: "mem", label: "Mémoriser un texte", to: "/memorize" },
  { id: "graph", label: "Explorer le graphe", to: "/graph" },
  { id: "search", label: "Rechercher un nœud", to: "/graph" },
  { id: "sign", label: "Reconstruire + signer bloc", to: "/graph" },
];

export function Home() {
  const [pol, setPol] = useState<number | null>(null);
  const [blocks, setBlocks] = useState<ChainBlock[]>([]);
  const [walletCount, setWalletCount] = useState(0);
  const [chainValid, setChainValid] = useState(false);

  useEffect(() => {
    fetchPolScore().then((p) => setPol(p.pol_score)).catch(() => {});
    fetchChain().then(setBlocks).catch(() => {});
    axios.get("/api/v1/wallet/list").then((r) => setWalletCount(r.data.wallets?.length ?? 0)).catch(() => {});
    axios.get("/api/v1/chain/verify").then((r) => setChainValid(r.data.valid)).catch(() => {});
  }, []);

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Accueil</h1>

      <div className="mc-hotbar">
        <McKpiSlot icon="💎" label="PoL" value={pol?.toFixed(2) ?? "—"} barPct={(pol ?? 0) * 100} />
        <McKpiSlot icon="▣" label="Blocs" value={String(blocks.length)} sub={`+${Math.min(blocks.length, 2)} session`} />
        <McKpiSlot icon="◇" label="Wallets" value={String(walletCount)} />
        <McKpiSlot icon="◎" label="Graphes" value={String(blocks.length)} sub="IR live" />
        <McKpiSlot
          icon="✓"
          label="Chain"
          value={chainValid ? "VALID ✓" : "CHECK"}
          gold={chainValid}
        />
      </div>

      <div className="panel mc-checklist">
        <h2>Parcours rapide</h2>
        <ul className="mc-checklist-list">
          {CHECKLIST.map((item) => (
            <li key={item.id}>
              <span className="mc-check-box">[ ]</span>
              <span>{item.label}</span>
              <Link to={item.to} className="mc-link-pill">→ Aller</Link>
            </li>
          ))}
        </ul>
      </div>

      <div className="panel">
        <div className="mc-section-head">
          <h2>Derniers blocs</h2>
          <Link to="/chain" className="mc-link-pill">Voir tout →</Link>
        </div>
        <McBlockRow blocks={blocks} limit={6} />
        <p className="mc-muted mc-reward-note">Reward genesis epoch : 1 ARTCB / bloc</p>
      </div>
    </div>
  );
}
