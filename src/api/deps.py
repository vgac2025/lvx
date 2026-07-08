"""Shared API dependencies and application state."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from artcb.agents.critic import DualAgentLoop
from artcb.chain.manager import ChainManager
from artcb.config import ArtcbSettings, load_settings
from artcb.ir.decoder import IRDecoder
from artcb.ir.encoder import IREncoder
from artcb.ir.models import IRGraph
from artcb.memory.graph_store import GraphStore
from artcb.memory.vector_store import VectorStore
from artcb.pol.scorer import PolScorer
from artcb.groups.join_requests import JoinRequestManager
from artcb.groups.manager import GroupManager
from artcb.governance.manager import GovernanceManager
from artcb.rtleg.timeline import RTLEGTimeline


@dataclass
class AppState:
    settings: ArtcbSettings
    encoder: IREncoder
    decoder: IRDecoder
    dual: DualAgentLoop
    timeline: RTLEGTimeline
    scorer: PolScorer
    graphs: GraphStore
    vectors: VectorStore
    chain: ChainManager
    groups: GroupManager
    join_requests: JoinRequestManager
    governance: GovernanceManager
    pol_state: dict[str, Any] = field(default_factory=lambda: {
        "pol_score": 0.6,
        "delta_compression": 0.68,
        "validation_rate": 1.0,
        "retrieval_accuracy": 1.0,
        "block_accepted": True,
        "blocks_accepted": 0,
        "blocks_rejected": 0,
    })
    node_index: dict[str, tuple[str, str]] = field(default_factory=dict)

    def register_graph(self, graph: IRGraph) -> None:
        self.graphs.save(graph)
        self.vectors.index_graph(graph)
        for node in graph.nodes:
            self.node_index[node.id] = (graph.graph_id, node.txt)

    def get_graph(self, graph_id: str) -> IRGraph | None:
        if graph_id in self.graphs.cache:
            return self.graphs.cache[graph_id]
        return self.graphs.load(graph_id)


def build_app_state() -> AppState:
    settings = load_settings()
    graphs = GraphStore(settings.data_dir / "graphs")
    groups_dir = settings.data_dir / "groups"
    groups = GroupManager(groups_dir)
    governance = GovernanceManager(settings.data_dir)
    state = AppState(
        settings=settings,
        encoder=IREncoder(),
        decoder=IRDecoder(),
        dual=DualAgentLoop(),
        timeline=RTLEGTimeline(),
        scorer=PolScorer(),
        graphs=graphs,
        vectors=VectorStore(),
        chain=ChainManager(settings.data_dir / "chain" / "blocks.jsonl"),
        groups=groups,
        join_requests=JoinRequestManager(groups_dir, groups),
        governance=governance,
    )
    for graph in graphs.load_all():
        state.register_graph(graph)
    return state
