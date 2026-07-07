import { useEffect, useState } from "react";
import {
  decodeGraph,
  fetchGraph,
  fetchWallets,
  searchNodes,
  storeGraph,
} from "../api/client";
import { GraphViewer } from "../components/GraphViewer";
import { Reconstruct } from "../components/Reconstruct";
import { useDashboard } from "../context/DashboardContext";

export function GraphPage() {
  const {
    sessionId,
    graph,
    setGraph,
    graphId,
    text,
    selectedNodeId,
    setSelectedNodeId,
    pushMessage,
    setChainBlock,
    visibility,
    groupId,
  } = useDashboard();
  const [searchQuery, setSearchQuery] = useState("");
  const [highlightIds, setHighlightIds] = useState<string[]>([]);
  const [showReconstruct, setShowReconstruct] = useState(false);
  const [reconstructed, setReconstructed] = useState("");
  const [similarity, setSimilarity] = useState(1);
  const [reversible, setReversible] = useState(false);
  const [nodeDetail, setNodeDetail] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (graphId && !graph) {
      fetchGraph(graphId).then(setGraph).catch(() => {});
    }
  }, [graphId, graph, setGraph]);

  useEffect(() => {
    if (!selectedNodeId || !graph) {
      setNodeDetail("");
      return;
    }
    const node = graph.nodes.find((n) => n.id === selectedNodeId);
    setNodeDetail(node?.txt ?? "");
  }, [selectedNodeId, graph]);

  const handleSearch = async () => {
    if (!graphId || !searchQuery.trim()) return;
    const results = await searchNodes(searchQuery, graphId);
    if (results.length) {
      setHighlightIds(results.map((r) => r.node_id));
      setSelectedNodeId(results[0].node_id);
      pushMessage("explorer", `Trouvé: "${results[0].text.slice(0, 80)}…"`);
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
      let actorAddress: string | undefined;
      if (visibility === "group") {
        if (!groupId) {
          pushMessage("critic", "Sélectionnez un groupe (V10)");
          return;
        }
        const wallets = await fetchWallets();
        actorAddress = wallets[0]?.address;
        if (!actorAddress) {
          pushMessage("critic", "Wallet requis pour mode groupe");
          return;
        }
      }
      const block = await storeGraph(
        graphId,
        sessionId,
        visibility,
        visibility === "group" ? groupId : null,
        actorAddress,
      );
      setChainBlock({
        index: block.block_index,
        hash: block.hash,
        signature: block.signature,
        pol_score: block.pol_score,
        graph_id: graphId,
        block_reward: block.block_reward,
      });
      pushMessage("critic", `Bloc #${block.block_index} signé`);
    } catch (err) {
      pushMessage("critic", `Erreur: ${err instanceof Error ? err.message : String(err)}`);
    } finally {
      setLoading(false);
    }
  };

  const handleReadAloud = () => {
    if (!nodeDetail || !("speechSynthesis" in window)) return;
    const utter = new SpeechSynthesisUtterance(nodeDetail);
    utter.lang = "fr-FR";
    window.speechSynthesis.speak(utter);
  };

  if (!graphId) {
    return (
      <div className="mc-page mc-empty">
        <h1 className="dashboard-title">Graphe</h1>
        <div className="panel mc-empty-panel">
          <p className="mc-empty-icon">📄</p>
          <p>Aucun graphe encore — allez sur Mémoriser.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mc-page">
      <h1 className="dashboard-title">Graphe · chunks 2D</h1>
      <div className="panel mc-graph-panel">
        <div className="mc-graph-viewport mc-graph-viewport-tall">
          <GraphViewer
            graph={graph}
            selectedNodeId={selectedNodeId}
            highlightIds={highlightIds}
            onSelectNode={setSelectedNodeId}
          />
        </div>
        {nodeDetail && (
          <div className="mc-node-detail">
            <strong>Sélectionné:</strong> {nodeDetail}
          </div>
        )}
        <div className="toolbar">
          <input
            className="mc-search-input"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Rechercher decision, king…"
            onKeyDown={(e) => e.key === "Enter" && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
          <button onClick={handleReconstruct}>Reconstruire</button>
          <button onClick={handleReadAloud} disabled={!selectedNodeId}>
            Lire
          </button>
          <button className="primary" onClick={handleStore} disabled={loading}>
            Signer bloc
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
  );
}
