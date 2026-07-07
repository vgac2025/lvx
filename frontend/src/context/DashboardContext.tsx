import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";
import type { AgentMessage, ChainBlock, IRGraph, NetworkVisibility, PolMetrics } from "../types";

export interface ChecklistState {
  memorized: boolean;
  explored: boolean;
  searched: boolean;
  signed: boolean;
}

interface DashboardState {
  sessionId: string;
  useLlm: boolean;
  actorAddress: string;
  visibility: NetworkVisibility;
  groupId: string | null;
  text: string;
  graph: IRGraph | null;
  graphId: string | null;
  pol: PolMetrics | null;
  messages: AgentMessage[];
  selectedNodeId: string | null;
  chainBlock: ChainBlock | null;
  checklist: ChecklistState;
  setSessionId: (s: string) => void;
  setUseLlm: (v: boolean) => void;
  setActorAddress: (a: string) => void;
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
  markChecklist: (key: keyof ChecklistState) => void;
}

const CHECKLIST_KEY = "artcb_dashboard_checklist";

const DashboardContext = createContext<DashboardState | null>(null);

function loadChecklist(): ChecklistState {
  try {
    const raw = localStorage.getItem(CHECKLIST_KEY);
    if (raw) return JSON.parse(raw) as ChecklistState;
  } catch { /* ignore */ }
  return { memorized: false, explored: false, searched: false, signed: false };
}

export function DashboardProvider({ children }: { children: ReactNode }) {
  const [sessionId, setSessionId] = useState("demo_hackathon");
  const [useLlm, setUseLlm] = useState(false);
  const [actorAddress, setActorAddress] = useState("");
  const [visibility, setVisibility] = useState<NetworkVisibility>("private");
  const [groupId, setGroupId] = useState<string | null>(null);
  const [text, setText] = useState("");
  const [graph, setGraph] = useState<IRGraph | null>(null);
  const [graphId, setGraphId] = useState<string | null>(null);
  const [pol, setPol] = useState<PolMetrics | null>(null);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [chainBlock, setChainBlock] = useState<ChainBlock | null>(null);
  const [checklist, setChecklist] = useState<ChecklistState>(loadChecklist);

  useEffect(() => {
    localStorage.setItem(CHECKLIST_KEY, JSON.stringify(checklist));
  }, [checklist]);

  const markChecklist = useCallback((key: keyof ChecklistState) => {
    setChecklist((prev) => ({ ...prev, [key]: true }));
  }, []);

  const pushMessage = useCallback((agent: "explorer" | "critic", msgText: string) => {
    setMessages((prev) => [
      ...prev,
      { id: `${agent}-${Date.now()}-${prev.length}`, agent, text: msgText, ts: Date.now() },
    ]);
  }, []);

  const clearMessages = useCallback(() => setMessages([]), []);

  const value = useMemo(
    () => ({
      sessionId,
      useLlm,
      actorAddress,
      visibility,
      groupId,
      text,
      graph,
      graphId,
      pol,
      messages,
      selectedNodeId,
      chainBlock,
      checklist,
      setSessionId,
      setUseLlm,
      setActorAddress,
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
      markChecklist,
    }),
    [
      sessionId,
      useLlm,
      actorAddress,
      visibility,
      groupId,
      text,
      graph,
      graphId,
      pol,
      messages,
      selectedNodeId,
      chainBlock,
      checklist,
      pushMessage,
      clearMessages,
      markChecklist,
    ],
  );

  return <DashboardContext.Provider value={value}>{children}</DashboardContext.Provider>;
}

export function useDashboard() {
  const ctx = useContext(DashboardContext);
  if (!ctx) throw new Error("useDashboard must be used within DashboardProvider");
  return ctx;
}
