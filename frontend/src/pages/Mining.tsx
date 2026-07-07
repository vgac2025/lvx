import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { chainQueryParams, fetchChain, fetchMiningLatest, fetchMiningStatus } from "../api/client";
import { McBlockRow } from "../components/McBlockRow";
import { McKpiSlot } from "../components/McKpiSlot";
import { useDashboard } from "../context/DashboardContext";
import type { ChainBlock } from "../types";

export function Mining() {
  const { visibility, groupId } = useDashboard();
  const [blocks, setBlocks] = useState<ChainBlock[]>([]);
  const [status, setStatus] = useState<{
    current_reward_artcb: number;
    blocks_until_halving: number;
    total_rewards_artcb: number;
    pol_score: number;
  } | null>(null);
  const [miningLog, setMiningLog] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    const q = chainQueryParams(visibility, groupId);
    fetchChain(q).then(setBlocks).catch(() => {});
    fetchMiningStatus().then(setStatus).catch(() => {});
    fetchMiningLatest()
      .then((m) => setMiningLog(m.data))
      .catch(() => setMiningLog(null));
  }, [visibility, groupId]);

  const summary = miningLog?.summary as Record<string, unknown> | undefined;
  const lastResult = (miningLog?.results as Array<Record<string, unknown>> | undefined)?.[0];

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Minage ⛏</h1>

      <div className="panel mc-mining-panel">
        <div className="mc-mining-hero">
          <span className="mc-pickaxe" aria-hidden>
            ⛏
          </span>
          <div>
            <h2>Proof-of-Learning Mining</h2>
            <p className="mc-muted">Epoch : {status?.current_reward_artcb ?? 1} ARTCB/bloc — pas de PoW</p>
          </div>
        </div>

        <div className="mc-hotbar">
          <McKpiSlot
            icon="💎"
            label="PoL session"
            value={status?.pol_score?.toFixed(2) ?? "—"}
            gold
          />
          <McKpiSlot icon="▣" label="Blocs minés" value={String(blocks.length)} />
          <McKpiSlot
            icon="₳"
            label="Rewards total"
            value={`${status?.total_rewards_artcb?.toFixed(1) ?? "0"} ₳`}
          />
          <McKpiSlot
            icon="◷"
            label="Halving dans"
            value={String(status?.blocks_until_halving ?? "—")}
            sub="blocs"
          />
        </div>

        {lastResult && (
          <div className="panel">
            <h3>Dernier mining_results (fichier réel)</h3>
            <p className="mc-muted">
              pol: {String(lastResult.pol_score)} · reversible: {String(lastResult.reversible)} · nodes:{" "}
              {String(lastResult.nodes_count)}
            </p>
            {summary && (
              <p className="mc-gold-text">total_reward_artcb: {String(summary.total_reward_artcb)}</p>
            )}
          </div>
        )}

        <h3>Blocs minés</h3>
        <McBlockRow blocks={blocks} limit={10} />
        <p className="mc-muted">
          Lancer minage via <Link to="/console">Console</Link> — scripts réels sur machine utilisateur
        </p>
      </div>
    </div>
  );
}
