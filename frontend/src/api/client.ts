import axios from "axios";
import type { IRGraph, PolMetrics, ChainBlock } from "../types";

const api = axios.create({ baseURL: "/api/v1" });

export async function fetchWaillyExcerpt(maxPages = 3): Promise<string> {
  const { data } = await api.get<{ text: string }>("/demo/wailly-excerpt", {
    params: { max_pages: maxPages },
  });
  return data.text;
}

export async function runAgents(text: string, sessionId: string, useLlm = false) {
  const { data } = await api.post("/agents/run", {
    text,
    session_id: sessionId,
    use_llm: useLlm,
  });
  return data as {
    graph_id: string;
    pol: PolMetrics;
    node_count: number;
  };
}

export async function fetchGraph(graphId: string): Promise<IRGraph> {
  const { data } = await api.get(`/graph/${graphId}`);
  return {
    graph_id: data.graph_id,
    source_text: data.source_text,
    nodes: data.nodes,
    edges: data.edges.map((e: { fr?: string; from?: string; to: string; rel: string }) => ({
      from: e.fr ?? e.from,
      to: e.to,
      rel: e.rel,
    })),
  };
}

export async function searchNodes(query: string, graphId: string) {
  const { data } = await api.post("/search", { query, graph_id: graphId, top_k: 3 });
  return data.results as Array<{ node_id: string; score: number; text: string }>;
}

export async function decodeGraph(graphId: string) {
  const { data } = await api.post("/decode", { graph_id: graphId });
  return data as { original_text: string; similarity: number; reversible: boolean };
}

export async function storeGraph(
  graphId: string,
  sessionId: string,
  visibility: "private" | "group" | "public" = "private",
) {
  const { data } = await api.post("/store", {
    graph_id: graphId,
    session_id: sessionId,
    visibility,
  });
  return data as {
    block_index: number;
    hash: string;
    signature: string;
    pol_score: number;
    block_reward?: number;
  };
}

export async function fetchWallets() {
  const { data } = await api.get("/wallet/list");
  return data.wallets as Array<{ address: string; name: string }>;
}

export async function fetchWalletBalance(address: string) {
  const { data } = await api.get(`/wallet/balance/${address}`);
  return data as { balance_satoshi: number; balance_artcb: number };
}

export async function fetchRtlegEvents() {
  const { data } = await api.get("/rtleg/events");
  return data.events as Array<{
    event_id: string;
    timestamp: string;
    session_id: string;
    agent: string;
    event_type: string;
    payload?: Record<string, unknown>;
  }>;
}

export async function fetchChain(): Promise<ChainBlock[]> {
  const { data } = await api.get("/chain");
  return data.blocks as ChainBlock[];
}

export async function fetchPolScore() {
  const { data } = await api.get("/pol/score");
  return data;
}

export function wsUrl(sessionId: string): string {
  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  const host = window.location.host;
  return `${proto}://${host}/ws/graph/${sessionId}`;
}
