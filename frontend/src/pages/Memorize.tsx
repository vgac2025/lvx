import { useEffect, useState } from "react";
import {
  fetchGraph,
  fetchWaillyExcerpt,
  fetchWallets,
  runAgents,
  storeGraph,
  wsUrl,
} from "../api/client";
import { AgentPanel } from "../components/AgentPanel";
import { GraphViewer } from "../components/GraphViewer";
import { PolGauge } from "../components/PolGauge";
import { useDashboard } from "../context/DashboardContext";

export function Memorize() {
  const {
    sessionId,
    setSessionId,
    useLlm,
    setUseLlm,
    actorAddress,
    setActorAddress,
    text,
    setText,
    graph,
    setGraph,
    graphId,
    setGraphId,
    pol,
    setPol,
    messages,
    pushMessage,
    clearMessages,
    setChainBlock,
    visibility,
    groupId,
    markChecklist,
  } = useDashboard();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (text) return;
    fetchWaillyExcerpt(2)
      .then(setText)
      .catch(() => setText("Collez votre texte ici — extrait Wailly indisponible."));
  }, [text, setText]);

  useEffect(() => {
    fetchWallets()
      .then((w) => {
        if (w.length && !actorAddress) setActorAddress(w[0].address);
      })
      .catch(() => {});
  }, [actorAddress, setActorAddress]);

  const animateViaWebSocket = (inputText: string): Promise<void> =>
    new Promise((resolve, reject) => {
      const ws = new WebSocket(wsUrl(sessionId));
      ws.onopen = () => ws.send(JSON.stringify({ type: "encode", payload: { text: inputText } }));
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === "node_added") {
          pushMessage("explorer", `Node ${data.node.id} (${data.node.t}): ${data.node.txt.slice(0, 60)}…`);
        }
        if (data.type === "encode_complete") {
          ws.close();
          resolve();
        }
        if (data.type === "error") {
          ws.close();
          reject(new Error(data.message));
        }
      };
      ws.onerror = () => reject(new Error("WebSocket connection failed"));
    });

  const handleMemorize = async () => {
    if (!text.trim()) return;
    setLoading(true);
    clearMessages();
    setChainBlock(null);

    try {
      pushMessage("explorer", "Décomposition IR en cours…");
      await animateViaWebSocket(text);
      pushMessage("critic", "Validation PoL…");
      const result = await runAgents(text, sessionId, useLlm);
      setGraphId(result.graph_id);
      setPol(result.pol);
      const fullGraph = await fetchGraph(result.graph_id);
      setGraph(fullGraph);
      markChecklist("memorized");
      pushMessage("critic", `PoL ${result.pol.pol_score.toFixed(2)} — ${result.node_count} nœuds validés`);
    } catch (err) {
      pushMessage("critic", `Erreur: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleStore = async () => {
    if (!graphId) return;
    setLoading(true);
    try {
      if (visibility === "group") {
        if (!groupId) {
          pushMessage("critic", "Sélectionnez un groupe (V10)");
          return;
        }
        if (!actorAddress) {
          pushMessage("critic", "Wallet requis");
          return;
        }
      }
      const block = await storeGraph(
        graphId,
        sessionId,
        visibility,
        visibility === "group" ? groupId : null,
        visibility === "group" ? actorAddress : undefined,
      );
      setChainBlock({
        index: block.block_index,
        hash: block.hash,
        signature: block.signature,
        pol_score: block.pol_score,
        graph_id: graphId,
        block_reward: block.block_reward,
      });
      markChecklist("signed");
      pushMessage("critic", `Bloc #${block.block_index} signé (${visibility})`);
    } catch (err) {
      pushMessage("critic", `Store failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Mémoriser</h1>

      <div className="panel">
        <h2>Session</h2>
        <div className="toolbar">
          <label>
            session_id:
            <input value={sessionId} onChange={(e) => setSessionId(e.target.value)} />
          </label>
          <label>
            <input type="checkbox" checked={useLlm} onChange={(e) => setUseLlm(e.target.checked)} /> use_llm
          </label>
        </div>
      </div>

      <div className="panel mc-crafting">
        <h2>Source — grille crafting</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Texte à mémoriser…"
          aria-label="Texte source"
          className="mc-crafting-area"
        />
        <div className="toolbar">
          <button className="primary" onClick={handleMemorize} disabled={loading}>
            {loading ? "Mémorisation…" : "Mémoriser"}
          </button>
          <button onClick={() => fetchWaillyExcerpt(3).then(setText)}>Charger Wailly</button>
          {graphId && (
            <button onClick={handleStore} disabled={loading}>
              Signer bloc
            </button>
          )}
        </div>
      </div>

      <div className="demo-grid">
        <div className="panel mc-graph-panel">
          <h2>Graphe en construction</h2>
          <div className="mc-graph-viewport">
            <GraphViewer graph={graph} selectedNodeId={null} onSelectNode={() => {}} />
          </div>
          {graphId && (
            <p className="mc-muted">
              graph_id={graphId} · {graph?.nodes.length ?? 0} nœuds
            </p>
          )}
        </div>
        <div className="mc-side-stack">
          <AgentPanel messages={messages} />
          <PolGauge pol={pol} />
        </div>
      </div>
    </div>
  );
}
