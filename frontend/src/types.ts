export interface IRNode {
  id: string;
  t: string;
  sym: string;
  txt: string;
  checksum: string;
}

export interface IREdge {
  from: string;
  to: string;
  rel: string;
}

export interface IRGraph {
  graph_id: string;
  source_text: string;
  nodes: IRNode[];
  edges: IREdge[];
}

export interface PolMetrics {
  pol_score: number;
  delta_compression: number;
  validation_rate: number;
  retrieval_accuracy: number;
  block_accepted: boolean;
  blocks_accepted?: number;
  blocks_rejected?: number;
}

export interface AgentMessage {
  id: string;
  agent: "explorer" | "critic";
  text: string;
  ts: number;
}

export interface ChainBlock {
  index: number;
  hash: string;
  signature: string;
  pol_score: number;
  graph_id: string;
  block_reward?: number;
  visibility?: string;
  group_id?: string | null;
  timestamp?: string;
  contributors?: Array<{
    address: string;
    pol_score: number;
    reward_satoshi: number;
  }>;
}

export interface WalletInfo {
  address: string;
  name: string;
  balance_satoshi?: number;
}

export type NetworkVisibility = "private" | "group" | "public";
