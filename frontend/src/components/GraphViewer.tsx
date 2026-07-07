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
              color: "#ffffff",
              "background-color": "#7f7f7f",
              "border-width": "3px",
              "border-color": "#b0b0b0",
              width: "40px",
              height: "40px",
              shape: "rectangle",
            },
          },
          {
            selector: "node.selected",
            style: {
              "background-color": "#5d9b3a",
              "border-color": "#ffcc00",
              width: "48px",
              height: "48px",
            },
          },
          {
            selector: "node.highlight",
            style: {
              "background-color": "#4aedd9",
              "border-color": "#ffffff",
            },
          },
          {
            selector: "edge",
            style: {
              width: "3px",
              "line-color": "#8b6914",
              "target-arrow-color": "#8b6914",
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
      style={{ width: "100%", height: "100%", borderRadius: 0 }}
      aria-label="Knowledge graph viewer"
    />
  );
}
