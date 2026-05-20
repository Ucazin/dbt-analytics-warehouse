"""
render_dag.py — render the dbt project's lineage DAG to outputs/dag.png.

Reads target/manifest.json after `dbt docs generate`.
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
MANIFEST = Path("target") / "manifest.json"

LAYER_COLORS = {
    "source":       "#9CA3AF",
    "staging":      "#BFDBFE",
    "intermediate": "#FCD34D",
    "marts":        "#34D399",
    "seed":         "#E5E7EB",
    "snapshot":     "#A78BFA",
}


def layer_for(node_id: str, node: dict) -> str:
    if node_id.startswith("source."):
        return "source"
    if node["resource_type"] == "seed":
        return "seed"
    if node["resource_type"] == "snapshot":
        return "snapshot"
    path = node.get("path", "")
    if "staging" in path:
        return "staging"
    if "intermediate" in path:
        return "intermediate"
    if "marts" in path:
        return "marts"
    return "marts"


def short_name(node_id: str, node: dict) -> str:
    if node_id.startswith("source."):
        return f"src.{node_id.split('.')[-1]}"
    return node.get("name", node_id.split(".")[-1])


def main() -> None:
    if not MANIFEST.exists():
        raise SystemExit("Run `dbt docs generate` first — target/manifest.json missing.")

    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    nodes = {**data.get("nodes", {}), **data.get("sources", {})}

    # Skip tests + exposures + analyses
    keep_types = {"model", "seed", "snapshot", "source"}
    nodes = {k: v for k, v in nodes.items()
             if v.get("resource_type") in keep_types}

    g = nx.DiGraph()
    for node_id, node in nodes.items():
        g.add_node(node_id,
                   layer=layer_for(node_id, node),
                   label=short_name(node_id, node))

    parents = data.get("parent_map", {})
    for child, parent_list in parents.items():
        if child in nodes:
            for parent in parent_list:
                if parent in nodes:
                    g.add_edge(parent, child)

    # Group by layer, assign columns left-to-right
    order = ["source", "seed", "staging", "intermediate", "marts", "snapshot"]
    columns = {layer: [] for layer in order}
    for n in g.nodes:
        columns[g.nodes[n]["layer"]].append(n)
    for layer in columns:
        columns[layer].sort(key=lambda n: g.nodes[n]["label"])

    pos = {}
    x_gap = 3.5
    for x, layer in enumerate(order):
        col = columns[layer]
        n_in_col = len(col)
        for y, node in enumerate(col):
            pos[node] = (x * x_gap, -y + (n_in_col - 1) / 2)

    fig, ax = plt.subplots(figsize=(18, max(8, max(len(c) for c in columns.values()) * 0.55)))

    # Edges
    nx.draw_networkx_edges(g, pos, ax=ax, edge_color="#9CA3AF",
                           arrows=True, arrowsize=12, width=1.0,
                           connectionstyle="arc3,rad=0.04")

    # Nodes by layer
    for layer in order:
        node_list = columns[layer]
        if not node_list:
            continue
        nx.draw_networkx_nodes(g, pos, nodelist=node_list,
                               node_color=LAYER_COLORS[layer],
                               node_size=2200, edgecolors="#374151",
                               linewidths=1.0, ax=ax)

    # Labels
    labels = {n: g.nodes[n]["label"] for n in g.nodes}
    nx.draw_networkx_labels(g, pos, labels=labels, font_size=9, ax=ax)

    # Layer headers
    for x, layer in enumerate(order):
        if columns[layer]:
            ax.text(x * x_gap, max(p[1] for p in pos.values()) + 1.3,
                    layer.upper(), fontsize=13, fontweight="bold",
                    ha="center", color="#374151")

    ax.set_title("dbt analytics_warehouse — lineage DAG", fontsize=15)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(OUT / "dag.png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    print(f"Wrote {OUT / 'dag.png'}")

    # Also write a markdown summary that doesn't need anything to render.
    rows = ["# Lineage summary", "",
            "| Layer | Model | Materialization | Depends on |",
            "|-------|-------|-----------------|------------|"]
    for n in sorted(g.nodes, key=lambda n: (order.index(g.nodes[n]["layer"]),
                                            g.nodes[n]["label"])):
        node = nodes[n]
        layer = g.nodes[n]["layer"]
        mat = node.get("config", {}).get("materialized", "view") if layer != "source" else "—"
        deps = ", ".join(g.nodes[p]["label"] for p in g.predecessors(n)) or "—"
        rows.append(f"| {layer} | {g.nodes[n]['label']} | {mat} | {deps} |")
    (OUT / "lineage_summary.md").write_text("\n".join(rows), encoding="utf-8")
    print(f"Wrote {OUT / 'lineage_summary.md'}")


if __name__ == "__main__":
    main()
