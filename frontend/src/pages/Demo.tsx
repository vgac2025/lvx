import { useCallback, useEffect, useState } from "react";
import {
  decodeGraph,
  fetchGraph,
  fetchWaillyExcerpt,
  runAgents,
  searchNodes,
  storeGraph,
  wsUrl,
} from "../api/client";
import { AgentPanel } from "../components/AgentPanel";
import { GraphViewer } from "../components/GraphViewer";
import { PolGauge } from "../components/PolGauge";
import { Reconstruct } from "../components/Reconstruct";
import type { AgentMessage, ChainBlock, IRGraph, PolMetrics } from "../types";

const SESSION_ID = "demo_hackathon";

export function Demo() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [graph, setGraph] = useState<IRGraph | null>(null);
  const [graphId, setGraphId] = useState<string | null>(null);
  const [pol, setPol] = useState<PolMetrics | null>(null);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightIds, setHighlightIds] = useState<string[]>([]);
  const [showReconstruct, setShowReconstruct] = useState(false);
  const [reconstructed, setReconstructed] = useState("");
  const [similarity, setSimilarity] = useState(1);
  const [reversible, setReversible] = useState(false);
  const [chainBlock, setChainBlock] = useState<ChainBlock | null>(null);
  const [nodeDetail, setNodeDetail] = useState("");

  const pushMessage = useCallback((agent: "explorer" | "critic", msgText: string) => {
    setMessages((prev) => [
      ...prev,
      { id: `${agent}-${Date.now()}-${prev.length}`, agent, text: msgText, ts: Date.now() },
    ]);
  }, []);

  useEffect(() => {
    fetchWaillyExcerpt(2)
      .then(setText)
      .catch(() => {
        setText("Chargement du livre Wailly indisponible — collez votre texte ici.");
      });
  }, []);

  const animateViaWebSocket = (inputText: string): Promise<void> => {
    return new Promise((resolve, reject) => {
      const ws = new WebSocket(wsUrl(SESSION_ID));
      ws.onopen = () => {
        ws.send(JSON.stringify({ type: "encode", payload: { text: inputText } }));
      };
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
  };

  const handleMemorize = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setMessages([]);
    setShowReconstruct(false);
    setChainBlock(null);
    setHighlightIds([]);
    setSelectedNodeId(null);

    try {
      pushMessage("explorer", "Decomposing text into IR nodes…");
      await animateViaWebSocket(text);

      pushMessage("critic", "Validating coherence and computing PoL…");
      const result = await runAgents(text, SESSION_ID);
      setGraphId(result.graph_id);
      setPol(result.pol);

      const fullGraph = await fetchGraph(result.graph_id);
      setGraph(fullGraph);
      pushMessage("critic", `PoL ${result.pol.pol_score.toFixed(2)} — ${result.node_count} nodes validated`);
    } catch (err) {
      pushMessage("critic", `Error: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async () => {
    if (!graphId || !searchQuery.trim()) return;
    const results = await searchNodes(searchQuery, graphId);
    if (results.length) {
      setHighlightIds(results.map((r) => r.node_id));
      setSelectedNodeId(results[0].node_id);
      pushMessage("explorer", `Found: "${results[0].text.slice(0, 80)}…"`);
    }
  };

  const handleReconstruct = async () => {
    if (!graphId) return;
    const data = await decodeGraph(graphId);
    setReconstructed(data.original_text);
    setSimilarity(data.similarity);
    setReversible(data.reversible);
    setShowReconstruct(true);
  };

  const handleStore = async () => {
    if (!graphId) return;
    setLoading(true);
    try {
      const block = await storeGraph(graphId, SESSION_ID);
      setChainBlock({
        index: block.block_index,
        hash: block.hash,
        signature: block.signature,
        pol_score: block.pol_score,
        graph_id: graphId,
      });
      pushMessage("critic", `Block #${block.block_index} signed on chain`);
    } catch (err) {
      pushMessage("critic", `Store failed: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReadAloud = () => {
    if (!selectedNodeId || !graph) return;
    const node = graph.nodes.find((n) => n.id === selectedNodeId);
    if (!node) return;
    setNodeDetail(node.txt);
    if ("speechSynthesis" in window) {
      const utter = new SpeechSynthesisUtterance(node.txt);
      utter.lang = "fr-FR";
      window.speechSynthesis.speak(utter);
    }
  };

  useEffect(() => {
    if (!selectedNodeId || !graph) {
      setNodeDetail("");
      return;
    }
    const node = graph.nodes.find((n) => n.id === selectedNodeId);
    setNodeDetail(node?.txt ?? "");
  }, [selectedNodeId, graph]);

  return (
    <div className="app-shell">
      <header style={{ marginBottom: "1rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.5rem" }}>ARTCB — Persistent AI Memory</h1>
        <p style={{ color: "var(--muted)", margin: "0.35rem 0 0" }}>
          Reversible IR graph · Dual agents · Proof-of-Learning · Signed blockchain
        </p>
      </header>

      <div className="panel">
        <h2>1. Paste conversation or paragraph</h2>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="Paste text… (Wailly book excerpt loads by default)"
          aria-label="Input text"
        />
        <div className="toolbar">
          <button className="primary" onClick={handleMemorize} disabled={loading}>
            {loading ? "Memorizing…" : "Memorize"}
          </button>
          <button onClick={() => fetchWaillyExcerpt(3).then(setText)}>Load Wailly excerpt</button>
        </div>
      </div>

      <div className="demo-grid" style={{ marginTop: "1rem" }}>
        <div>
          <div className="panel">
            <h2>2–4. Graph · Explore · Search</h2>
            <GraphViewer
              graph={graph}
              selectedNodeId={selectedNodeId}
              highlightIds={highlightIds}
              onSelectNode={setSelectedNodeId}
            />
            {nodeDetail && (
              <div style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "var(--muted)" }}>
                <strong>Selected:</strong> {nodeDetail}
              </div>
            )}
            <div className="toolbar">
              <input
                style={{ flex: 1, minWidth: 180 }}
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search e.g. decision, unknown, king…"
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
              />
              <button onClick={handleSearch}>Search</button>
              <button onClick={handleReconstruct}>Reconstruct</button>
              <button onClick={handleReadAloud} disabled={!selectedNodeId}>
                Read aloud
              </button>
              <button onClick={handleStore} disabled={!graphId || loading}>
                Sign block
              </button>
            </div>
          </div>
          <Reconstruct
            original={text}
            reconstructed={reconstructed}
            similarity={similarity}
            reversible={reversible}
            visible={showReconstruct}
          />
        </div>

        <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
          <AgentPanel messages={messages} />
          <PolGauge pol={pol} />
        </div>
      </div>

      {chainBlock && (
        <div className="chain-footer" role="status">
          Block #{chainBlock.index} signed ✓ — hash {chainBlock.hash.slice(0, 16)}… · PoL{" "}
          {chainBlock.pol_score.toFixed(2)}
        </div>
      )}
    </div>
  );
}
