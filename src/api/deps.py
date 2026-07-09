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
from artcb.connectors.manager import ConnectorManager
from artcb.notifications.manager import NotificationManager
from artcb.p2p.node_identity import NodeIdentityStore
from artcb.p2p.peers import PeerManager
from artcb.p2p.public_archive import PublicBlockArchive
from artcb.p2p.sync import P2PSyncService
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
    connectors: ConnectorManager
    notifications: NotificationManager
    p2p_peers: PeerManager
    p2p_identity: Any
    p2p_sync: P2PSyncService
    p2p_archive: PublicBlockArchive
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
    connectors = ConnectorManager(settings.data_dir)
    notifications = NotificationManager(settings.data_dir)
    p2p_peers = PeerManager(settings.data_dir)
    p2p_identity = NodeIdentityStore(settings.data_dir).load_or_create(api_port=8000)
    p2p_archive = PublicBlockArchive(settings.data_dir)
    chain = ChainManager(settings.data_dir / "chain" / "blocks.jsonl")
    p2p_sync = P2PSyncService(
        chain=chain,
        peers=p2p_peers,
        identity=p2p_identity,
        archive=p2p_archive,
    )
    state = AppState(
        settings=settings,
        encoder=IREncoder(),
        decoder=IRDecoder(),
        dual=DualAgentLoop(),
        timeline=RTLEGTimeline(),
        scorer=PolScorer(),
        graphs=graphs,
        vectors=VectorStore(),
        chain=chain,
        groups=groups,
        join_requests=JoinRequestManager(groups_dir, groups),
        governance=governance,
        connectors=connectors,
        notifications=notifications,
        p2p_peers=p2p_peers,
        p2p_identity=p2p_identity,
        p2p_sync=p2p_sync,
        p2p_archive=p2p_archive,
    )
    for graph in graphs.load_all():
        state.register_graph(graph)
    return state
