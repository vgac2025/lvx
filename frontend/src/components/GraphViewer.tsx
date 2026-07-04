import { useEffect, useRef } from "react";
import cytoscape, { Core } from "cytoscape";
import type { IRGraph } from "../types";

interface Props {
  graph: IRGraph | null;
  selectedNodeId: string | null;
  highlightIds?: string[];
  onSelectNode: (nodeId: string) => void;
}

export function GraphViewer({ graph, selectedNodeId, highlightIds = [], onSelectNode }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const cyRef = useRef<Core | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    if (!cyRef.current) {
      cyRef.current = cytoscape({
        container: containerRef.current,
        style: [
          {
            selector: "node",
            style: {
              label: "data(label)",
              "text-wrap": "wrap",
              "text-max-width": "80px",
              "font-size": "10px",
              color: "#e8eef7",
              "background-color": "#334155",
              "border-width": "2px",
              "border-color": "#64748b",
              width: "36px",
              height: "36px",
            },
          },
          {
            selector: "node.selected",
            style: {
              "background-color": "#7c3aed",
              "border-color": "#c4b5fd",
              width: "44px",
              height: "44px",
            },
          },
          {
            selector: "node.highlight",
            style: {
              "background-color": "#2563eb",
              "border-color": "#93c5fd",
            },
          },
          {
            selector: "edge",
            style: {
              width: "2px",
              "line-color": "#475569",
              "target-arrow-color": "#475569",
              "target-arrow-shape": "triangle",
              "curve-style": "bezier",
            },
          },
        ],
        layout: { name: "breadthfirst", directed: true, padding: 30 },
      });

      cyRef.current.on("tap", "node", (evt) => {
        onSelectNode(evt.target.id());
      });
    }

    const cy = cyRef.current;
    cy.elements().remove();

    if (!graph || graph.nodes.length === 0) return;

    graph.nodes.forEach((node, index) => {
      cy.add({
        group: "nodes",
        data: {
          id: node.id,
          label: `${node.sym}\n${node.t}`,
        },
        position: { x: 80 + (index % 6) * 90, y: 60 + Math.floor(index / 6) * 80 },
      });
    });

    graph.edges.forEach((edge) => {
      if (cy.getElementById(edge.from).length && cy.getElementById(edge.to).length) {
        cy.add({
          group: "edges",
          data: { id: `${edge.from}-${edge.to}`, source: edge.from, target: edge.to },
        });
      }
    });

    cy.layout({ name: "breadthfirst", directed: true, padding: 30 }).run();
  }, [graph, onSelectNode]);

  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;
    cy.nodes().removeClass("selected highlight");
    if (selectedNodeId) {
      cy.getElementById(selectedNodeId).addClass("selected");
      cy.getElementById(selectedNodeId).neighborhood().addClass("highlight");
    }
    highlightIds.forEach((id) => {
      if (cy.getElementById(id).length) cy.getElementById(id).addClass("highlight");
    });
  }, [selectedNodeId, highlightIds]);

  return (
    <div
      ref={containerRef}
      style={{ width: "100%", height: 420, borderRadius: 8, border: "1px solid #1e2a3a" }}
      aria-label="Knowledge graph viewer"
    />
  );
}
