"""Persist IR graphs to disk."""

from __future__ import annotations

import json
import logging
from pathlib import Path

from artcb.ir.models import IRGraph

logger = logging.getLogger("artcb.memory.graph_store")


class GraphStore:
    def __init__(self, directory: Path) -> None:
        self.directory = directory
        self.directory.mkdir(parents=True, exist_ok=True)
        self.cache: dict[str, IRGraph] = {}

    def _path(self, graph_id: str) -> Path:
        return self.directory / f"{graph_id}.json"

    def save(self, graph: IRGraph) -> None:
        path = self._path(graph.graph_id)
        path.write_text(graph.to_json(), encoding="utf-8")
        self.cache[graph.graph_id] = graph
        logger.debug("Saved graph_id=%s path=%s", graph.graph_id, path)

    def load(self, graph_id: str) -> IRGraph | None:
        if graph_id in self.cache:
            return self.cache[graph_id]
        path = self._path(graph_id)
        if not path.exists():
            return None
        data = json.loads(path.read_text(encoding="utf-8"))
        graph = IRGraph.from_dict(data)
        self.cache[graph_id] = graph
        return graph

    def load_all(self) -> list[IRGraph]:
        graphs: list[IRGraph] = []
        for path in self.directory.glob("g_*.json"):
            graph_id = path.stem
            graph = self.load(graph_id)
            if graph:
                graphs.append(graph)
        return graphs
