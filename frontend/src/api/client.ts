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
  groupId?: string | null,
  actorAddress?: string | null,
) {
  const { data } = await api.post("/store", {
    graph_id: graphId,
    session_id: sessionId,
    visibility,
    group_id: groupId ?? undefined,
    actor_address: actorAddress ?? undefined,
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

export interface GroupData {
  group_id: string;
  name: string;
  founder_address: string;
  created_at: string;
  join_code?: string;
  dissolved: boolean;
  members: Array<{ address: string; role: string; joined_at: string }>;
}

export async function createGroup(name: string, founderAddress: string) {
  const { data } = await api.post("/groups", { name, founder_address: founderAddress });
  return data as GroupData;
}

export async function fetchGroupsForAddress(address: string) {
  const { data } = await api.get("/groups", { params: { address } });
  return data as { groups: GroupData[]; count: number };
}

export async function fetchGroupByJoinCode(joinCode: string) {
  const { data } = await api.get(`/groups/by-code/${joinCode}`);
  return data as { group_id: string; name: string; join_code: string; member_count: number };
}

export async function signJoinWithWallet(walletName: string, joinCode: string) {
  const { data } = await api.post("/groups/join-requests/sign-with-wallet", {
    wallet_name: walletName,
    join_code: joinCode,
  });
  return data as {
    message: string;
    request: { request_id: string; address: string; status: string };
  };
}

export async function fetchJoinRequests(groupId: string, actorAddress: string, status?: string) {
  const { data } = await api.get(`/groups/${groupId}/join-requests`, {
    params: { actor_address: actorAddress, status },
  });
  return data as {
    requests: Array<{
      request_id: string;
      address: string;
      status: string;
      created_at: string;
    }>;
    count: number;
  };
}

export async function approveJoinRequest(groupId: string, actorAddress: string, requestId: string) {
  const { data } = await api.post(`/groups/${groupId}/join-requests/${requestId}/approve`, {
    actor_address: actorAddress,
  });
  return data;
}

export async function rejectJoinRequest(groupId: string, actorAddress: string, requestId: string) {
  const { data } = await api.post(`/groups/${groupId}/join-requests/${requestId}/reject`, {
    actor_address: actorAddress,
  });
  return data;
}

export async function inviteGroupMember(
  groupId: string,
  actorAddress: string,
  address: string,
  role: string = "contributor",
) {
  const { data } = await api.post(`/groups/${groupId}/members`, {
    actor_address: actorAddress,
    address,
    role,
  });
  return data as GroupData;
}

export async function promoteGroupMember(
  groupId: string,
  actorAddress: string,
  targetAddress: string,
  role: string,
) {
  const { data } = await api.post(`/groups/${groupId}/members/${targetAddress}/role`, {
    actor_address: actorAddress,
    role,
  });
  return data as GroupData;
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

export async function fetchChain(params?: {
  visibility?: string;
  groupId?: string;
}): Promise<ChainBlock[]> {
  const { data } = await api.get("/chain", {
    params: {
      visibility: params?.visibility,
      group_id: params?.groupId,
    },
  });
  return data.blocks as ChainBlock[];
}

export async function createWallet(name: string) {
  const { data } = await api.post("/wallet/create", { name });
  return data as { name: string; address: string; public_key_hex: string };
}

export async function fetchBlockDetail(index: number) {
  const { data } = await api.get(`/chain/block/${index}`);
  return data.block as ChainBlock;
}

export async function fetchChainVerify() {
  const { data } = await api.get("/chain/verify");
  return data as { valid: boolean; message: string; block_count: number };
}

export async function fetchDemoLiveLog() {
  const { data } = await api.get("/dashboard/logs/demo-live");
  return data as { content: string; lines: string[]; line_count: number };
}

export async function fetchMiningLatest() {
  const { data } = await api.get("/dashboard/logs/mining-latest");
  return data as { path: string; data: Record<string, unknown> };
}

export async function fetchMiningStatus() {
  const { data } = await api.get("/dashboard/mining/status");
  return data as {
    block_count: number;
    current_reward_artcb: number;
    blocks_until_halving: number;
    total_rewards_artcb: number;
    pol_score: number;
  };
}

export async function fetchFoundersAllocation() {
  const { data } = await api.get("/dashboard/founders/allocation");
  return data as {
    founders_total_artcb: number;
    balances: Array<{ founder_id: number; name: string; balance_artcb: number }>;
  };
}

export async function fetchWalletRewards(address: string) {
  const { data } = await api.get(`/dashboard/wallet/${encodeURIComponent(address)}/rewards`);
  return data as {
    rewards: Array<{ block_index: number; reward_artcb: number; pol_score: number; timestamp: string }>;
    total_artcb: number;
  };
}

export async function fetchHealth() {
  const { data } = await api.get("/health");
  return data as { status: string; chain?: { valid?: boolean } };
}

export function chainQueryParams(visibility: string, groupId: string | null) {
  if (visibility === "group" && groupId) return { groupId };
  if (visibility !== "private") return { visibility };
  return {};
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
