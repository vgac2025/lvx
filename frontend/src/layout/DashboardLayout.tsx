import { useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import axios from "axios";
import { fetchChain, fetchPolScore } from "../api/client";
import { useDashboard } from "../context/DashboardContext";
import type { ChainBlock } from "../types";

const NAV = [
  { section: "CORE", items: [
    { to: "/", label: "Accueil", icon: "▶" },
    { to: "/memorize", label: "Mémoriser", icon: " " },
    { to: "/graph", label: "Graphe", icon: " " },
  ]},
  { section: "CHAIN", items: [
    { to: "/chain", label: "Chaîne", icon: "▣" },
    { to: "/wallets", label: "Wallets", icon: "◇" },
    { to: "/mining", label: "Minage", icon: "⛏" },
  ]},
  { section: "SYSTEM", items: [
    { to: "/system", label: "Système", icon: "⚙" },
    { to: "/logs", label: "Logs", icon: "📜" },
    { to: "/console", label: "Console", icon: "⌨" },
    { to: "/groups", label: "Groupes", icon: "👥" },
  ]},
];

export function DashboardLayout() {
  const { visibility, setVisibility, chainBlock } = useDashboard();
  const [apiOk, setApiOk] = useState<boolean | null>(null);
  const [polScore, setPolScore] = useState<number | null>(null);
  const [blocks, setBlocks] = useState<ChainBlock[]>([]);
  const [chainValid, setChainValid] = useState<boolean | null>(null);

  useEffect(() => {
    const tick = async () => {
      try {
        await axios.get("/api/v1/health", { timeout: 3000 });
        setApiOk(true);
      } catch {
        setApiOk(false);
      }
      try {
        const pol = await fetchPolScore();
        setPolScore(pol.pol_score);
      } catch { /* keep last */ }
      try {
        const chain = await fetchChain();
        setBlocks(chain);
      } catch { /* keep last */ }
      try {
        const { data } = await axios.get("/api/v1/chain/verify");
        setChainValid(data.valid ?? false);
      } catch {
        setChainValid(null);
      }
    };
    tick();
    const id = setInterval(tick, 5000);
    return () => clearInterval(id);
  }, []);

  const lastBlock = chainBlock ?? blocks[blocks.length - 1] ?? null;

  return (
    <div className="mc-dashboard">
      <header className="mc-header">
        <div className="mc-header-left">
          <span className="mc-logo">⛏ ARTCB</span>
          <span className={`mc-api-badge${apiOk === false ? " mc-api-down" : ""}`}>
            {apiOk === null ? "…" : apiOk ? "♥ API OK" : "✕ API DOWN"}
          </span>
          {polScore !== null && <span className="mc-header-kpi">◆ PoL {polScore.toFixed(2)}</span>}
          <span className="mc-header-kpi">▣ Blocs {blocks.length}</span>
          {chainValid !== null && (
            <span className="mc-header-kpi">{chainValid ? "Chain ✓" : "Chain ✕"}</span>
          )}
        </div>
        <div className="mc-header-right">
          <span className="badge-debug">DEBUG</span>
          <Link to="/console" className="mc-console-link">⌨ CONSOLE</Link>
        </div>
      </header>

      <div className="mc-body">
        <nav className="mc-sidebar" aria-label="Navigation dashboard">
          {NAV.map((group) => (
            <div key={group.section} className="mc-nav-group">
              <div className="mc-nav-section">{group.section}</div>
              {group.items.map((item) => (
                <NavLink
                  key={item.to}
                  to={item.to}
                  end={item.to === "/"}
                  className={({ isActive }) => `mc-nav-item${isActive ? " mc-nav-active" : ""}`}
                >
                  <span className="mc-nav-icon">{item.icon}</span>
                  {item.label}
                </NavLink>
              ))}
            </div>
          ))}
        </nav>

        <main className="mc-main">
          <Outlet />
        </main>
      </div>

      <footer className="chain-footer mc-footer">
        <span>
          {lastBlock
            ? `Bloc #${lastBlock.index} · hash ${lastBlock.hash.slice(0, 8)}…`
            : "Aucun bloc"}
          {lastBlock?.pol_score != null && ` · PoL ${lastBlock.pol_score.toFixed(2)}`}
        </span>
        <label className="mc-network-select">
          Réseau:
          <select
            value={visibility}
            onChange={(e) => setVisibility(e.target.value as "private" | "group" | "public")}
          >
            <option value="private">PRIVÉ</option>
            <option value="group">GROUPE</option>
            <option value="public">PUBLIC</option>
          </select>
        </label>
      </footer>
    </div>
  );
}
