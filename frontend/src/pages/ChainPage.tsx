import { useEffect, useState } from "react";
import axios from "axios";
import { fetchChain } from "../api/client";
import { McBlockRow } from "../components/McBlockRow";
import type { ChainBlock } from "../types";

export function ChainPage() {
  const [blocks, setBlocks] = useState<ChainBlock[]>([]);
  const [verify, setVerify] = useState<{ valid: boolean; message?: string } | null>(null);

  useEffect(() => {
    fetchChain().then(setBlocks).catch(() => {});
    axios.get("/api/v1/chain/verify").then((r) => setVerify(r.data)).catch(() => {});
  }, []);

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Chaîne · blocs MC</h1>

      <div className="mc-hotbar">
        <div className="mc-slot">
          <div className="mc-kpi-label">Hauteur</div>
          <div className="mc-kpi-value">{blocks.length}</div>
        </div>
        <div className="mc-slot">
          <div className="mc-kpi-label">Vérification</div>
          <div className="mc-kpi-value">{verify?.valid ? "OK ✓" : verify ? "FAIL" : "…"}</div>
        </div>
      </div>

      <div className="panel">
        <h2>Blocs récents</h2>
        <McBlockRow blocks={blocks} limit={20} />
      </div>

      <div className="panel mc-chain-table-wrap">
        <h2>Table détaillée</h2>
        <table className="mc-table">
          <thead>
            <tr>
              <th>#</th>
              <th>Hash</th>
              <th>PoL</th>
              <th>Reward</th>
              <th>graph_id</th>
            </tr>
          </thead>
          <tbody>
            {[...blocks].reverse().map((b) => (
              <tr key={b.index}>
                <td>{b.index}</td>
                <td className="mc-mono">{b.hash.slice(0, 16)}…</td>
                <td>{b.pol_score?.toFixed(2)}</td>
                <td className="mc-gold-text">
                  {b.block_reward != null ? `${(b.block_reward / 1e8).toFixed(2)} ₳` : "1 ₳"}
                </td>
                <td className="mc-mono">{b.graph_id?.slice(0, 12)}…</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
