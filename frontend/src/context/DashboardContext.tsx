import { createContext, useCallback, useContext, useMemo, useState, type ReactNode } from "react";
import type { AgentMessage, ChainBlock, IRGraph, NetworkVisibility, PolMetrics } from "../types";

interface DashboardState {
  sessionId: string;
  visibility: NetworkVisibility;
  groupId: string | null;
  text: string;
  graph: IRGraph | null;
  graphId: string | null;
  pol: PolMetrics | null;
  messages: AgentMessage[];
  selectedNodeId: string | null;
  chainBlock: ChainBlock | null;
  setVisibility: (v: NetworkVisibility) => void;
  setGroupId: (id: string | null) => void;
  setText: (t: string) => void;
  setGraph: (g: IRGraph | null) => void;
  setGraphId: (id: string | null) => void;
  setPol: (p: PolMetrics | null) => void;
  pushMessage: (agent: "explorer" | "critic", msgText: string) => void;
  clearMessages: () => void;
  setSelectedNodeId: (id: string | null) => void;
  setChainBlock: (b: ChainBlock | null) => void;
}

const DashboardContext = createContext<DashboardState | null>(null);

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [visibility, setVisibility] = useState<NetworkVisibility>("private");
  const [groupId, setGroupId] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [graph, setGraph] = useState<IRGraph | null>(null);
  const [graphId, setGraphId] = useState<string | null>(null);
  const [pol, setPol] = useState<PolMetrics | null>(null);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [chainBlock, setChainBlock] = useState<ChainBlock | null>(null);

  const pushMessage = useCallback((agent: "explorer" | "critic", msgText: string) => {
    setMessages((prev) => [
      ...prev,
      { id: `${agent}-${Date.now()}-${prev.length}`, agent, text: msgText, ts: Date.now() },
    ]);
  }, []);

  const clearMessages = useCallback(() => setMessages([]), []);

  const value = useMemo(
    () => ({
      sessionId: "demo_hackathon",
      visibility,
      groupId,
      text,
      graph,
      graphId,
      pol,
      messages,
      selectedNodeId,
      chainBlock,
      setVisibility,
      setGroupId,
      setText,
      setGraph,
      setGraphId,
      setPol,
      pushMessage,
      clearMessages,
      setSelectedNodeId,
      setChainBlock,
    }),
    [
      visibility,
      groupId,
      text,
      graph,
      graphId,
      pol,
      messages,
      selectedNodeId,
      chainBlock,
      pushMessage,
      clearMessages,
    ],
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
