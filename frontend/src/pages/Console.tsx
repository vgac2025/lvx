import { useState } from "react";

const HELP = `ARTCB Console — commandes:
  help            — cette aide
  health          — GET /api/v1/health
  chain           — GET /api/v1/chain
  chain verify    — GET /api/v1/chain/verify
  pol             — GET /api/v1/pol/score
  wallets         — GET /api/v1/wallet/list
  groups          — GET /api/v1/groups?address=...
  founders        — GET /api/v1/dashboard/founders/allocation
  mining status   — GET /api/v1/dashboard/mining/status
  mining latest   — GET /api/v1/dashboard/logs/mining-latest
  demo log        — GET /api/v1/dashboard/logs/demo-live
  clear           — effacer`;

export function Console() {
  const [lines, setLines] = useState<string[]>(["ARTCB Pixel Console v0.4 — tapez help", "> "]);
  const [input, setInput] = useState("");

  const runCommand = async (cmd: string) => {
    const trimmed = cmd.trim();
    if (!trimmed) return;
    const out: string[] = [`> ${trimmed}`];

    try {
      if (trimmed === "help") {
        out.push(HELP);
      } else if (trimmed === "clear") {
        setLines(["> "]);
        setInput("");
        return;
      } else if (trimmed === "health") {
        out.push(JSON.stringify(await (await fetch("/api/v1/health")).json(), null, 2));
      } else if (trimmed === "chain") {
        out.push(JSON.stringify(await (await fetch("/api/v1/chain")).json(), null, 2));
      } else if (trimmed === "chain verify") {
        out.push(JSON.stringify(await (await fetch("/api/v1/chain/verify")).json(), null, 2));
      } else if (trimmed === "pol") {
        out.push(JSON.stringify(await (await fetch("/api/v1/pol/score")).json(), null, 2));
      } else if (trimmed === "wallets") {
        out.push(JSON.stringify(await (await fetch("/api/v1/wallet/list")).json(), null, 2));
      } else if (trimmed.startsWith("groups ")) {
        const addr = trimmed.slice(7).trim();
        out.push(
          JSON.stringify(
            await (await fetch(`/api/v1/groups?address=${encodeURIComponent(addr)}`)).json(),
            null,
            2,
          ),
        );
      } else if (trimmed === "founders") {
        out.push(JSON.stringify(await (await fetch("/api/v1/dashboard/founders/allocation")).json(), null, 2));
      } else if (trimmed === "mining status") {
        out.push(JSON.stringify(await (await fetch("/api/v1/dashboard/mining/status")).json(), null, 2));
      } else if (trimmed === "mining latest") {
        out.push(JSON.stringify(await (await fetch("/api/v1/dashboard/logs/mining-latest")).json(), null, 2));
      } else if (trimmed === "demo log") {
        out.push(JSON.stringify(await (await fetch("/api/v1/dashboard/logs/demo-live")).json(), null, 2));
      } else {
        out.push(`Commande inconnue: ${trimmed}`);
      }
    } catch (e) {
      out.push(`Erreur: ${e instanceof Error ? e.message : String(e)}`);
    }

    setLines((prev) => [...prev.slice(0, -1), ...out, "> "]);
    setInput("");
  };

  return (
    <div className="mc-page mc-console-page">
      <h1 className="dashboard-title">Console CLI</h1>
      <div className="mc-console" role="log" aria-live="polite">
        {lines.map((line, i) => (
          <div key={i} className="mc-console-line">
            {line}
          </div>
        ))}
      </div>
      <form
        className="mc-console-input-row"
        onSubmit={(e) => {
          e.preventDefault();
          runCommand(input);
        }}
      >
        <input
          className="mc-console-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="help | health | chain | mining status | demo log"
          aria-label="Commande console"
          autoFocus
        />
        <button type="submit">Exécuter</button>
      </form>
    </div>
  );
}
