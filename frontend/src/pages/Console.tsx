import { useState } from "react";

const HELP = `ARTCB Console — commandes disponibles:
  help          — cette aide
  health        — GET /api/v1/health
  chain         — GET /api/v1/chain
  pol           — GET /api/v1/pol/score
  verify        — GET /api/v1/chain/verify
  wallets       — GET /api/v1/wallet/list
  clear         — effacer l'écran`;

export function Console() {
  const [lines, setLines] = useState<string[]>([
    "ARTCB Pixel Console v0.4 — tapez help",
    "> ",
  ]);
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
        const r = await fetch("/api/v1/health");
        out.push(JSON.stringify(await r.json(), null, 2));
      } else if (trimmed === "chain") {
        const r = await fetch("/api/v1/chain");
        out.push(JSON.stringify(await r.json(), null, 2));
      } else if (trimmed === "pol") {
        const r = await fetch("/api/v1/pol/score");
        out.push(JSON.stringify(await r.json(), null, 2));
      } else if (trimmed === "verify") {
        const r = await fetch("/api/v1/chain/verify");
        out.push(JSON.stringify(await r.json(), null, 2));
      } else if (trimmed === "wallets") {
        const r = await fetch("/api/v1/wallet/list");
        out.push(JSON.stringify(await r.json(), null, 2));
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
          placeholder="help | health | chain | pol | verify | wallets"
          aria-label="Commande console"
          autoFocus
        />
        <button type="submit">Exécuter</button>
      </form>
    </div>
  );
}
