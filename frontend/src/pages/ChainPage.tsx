import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  chainQueryParams,
  fetchBlockDetail,
  fetchChain,
  fetchChainVerify,
} from "../api/client";
import { McBlockRow } from "../components/McBlockRow";
import { useDashboard } from "../context/DashboardContext";
import type { ChainBlock } from "../types";

export function ChainPage() {
  const { blockIndex } = useParams();
  const { visibility, groupId } = useDashboard();
  const [blocks, setBlocks] = useState<ChainBlock[]>([]);
  const [verify, setVerify] = useState<{ valid: boolean; message?: string; block_count?: number } | null>(null);
  const [detail, setDetail] = useState<ChainBlock | null>(null);

  useEffect(() => {
    const q = chainQueryParams(visibility, groupId);
    fetchChain(q).then(setBlocks).catch(() => {});
    fetchChainVerify().then(setVerify).catch(() => {});
  }, [visibility, groupId]);

  useEffect(() => {
    if (!blockIndex) {
      setDetail(null);
      return;
    }
    fetchBlockDetail(Number(blockIndex))
      .then(setDetail)
      .catch(() => setDetail(null));
  }, [blockIndex]);

  if (blockIndex && detail) {
    return (
      <div className="mc-page">
        <h1 className="dashboard-title">
          Bloc #{detail.index}{" "}
          <Link to="/chain" className="mc-link-pill">
            ← retour
          </Link>
        </h1>
        <div className="panel">
          <p>
            <strong>timestamp:</strong> {detail.timestamp ?? "—"}
          </p>
          <p className="mc-mono">
            <strong>hash:</strong> {detail.hash}
          </p>
          <p className="mc-mono">
            <strong>signature:</strong> {detail.signature}
          </p>
          <p>
            <strong>graph_id:</strong> {detail.graph_id}
          </p>
          <p className="mc-gold-text">
            <strong>reward:</strong>{" "}
            {detail.block_reward != null ? `${(detail.block_reward / 1e8).toFixed(8)} ARTCB` : "1 ARTCB"}
          </p>
          {detail.contributors && detail.contributors.length > 0 && (
            <table className="mc-table">
              <thead>
                <tr>
                  <th>Contributor</th>
                  <th>PoL</th>
                  <th>Reward ₳</th>
                </tr>
              </thead>
              <tbody>
                {detail.contributors.map((c) => (
                  <tr key={c.address}>
                    <td className="mc-mono">{c.address.slice(0, 16)}…</td>
                    <td>{c.pol_score?.toFixed(2)}</td>
                    <td>{(c.reward_satoshi / 1e8).toFixed(8)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>
      </div>
    );
  }

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
          <div className="mc-kpi-value">{verify?.valid ? "OK OK" : verify ? "FAIL" : "…"}</div>
        </div>
        <div className="mc-slot">
          <div className="mc-kpi-label">epoch reward</div>
          <div className="mc-kpi-value mc-gold-text">1 ARTCB</div>
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
              <th>Vis.</th>
              <th>graph_id</th>
            </tr>
          </thead>
          <tbody>
            {[...blocks].reverse().map((b) => (
              <tr key={b.index}>
                <td>
                  <Link to={`/chain/block/${b.index}`}>#{b.index}</Link>
                </td>
                <td className="mc-mono">{b.hash.slice(0, 16)}…</td>
                <td>{b.pol_score?.toFixed(2)}</td>
                <td className="mc-gold-text">
                  {b.block_reward != null ? `${(b.block_reward / 1e8).toFixed(2)} ₳` : "1 ₳"}
                </td>
                <td>{b.visibility ?? "private"}</td>
                <td className="mc-mono">{b.graph_id?.slice(0, 12)}…</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
