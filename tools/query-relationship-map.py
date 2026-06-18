#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict, deque
from pathlib import Path
from typing import Any


DEFAULT_GRAPH = Path("docs/relationship-maps/graphify-sml-relationship-map.json")


def terms(query: str) -> list[str]:
    return [t.lower() for t in re.findall(r"[\w.-]+", query, flags=re.UNICODE) if len(t) >= 2]


def load_graph(path: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    nodes = {node["id"]: node for node in data.get("nodes", [])}
    edges = data.get("edges", [])
    return nodes, edges


def score_node(node: dict[str, Any], query_terms: list[str]) -> int:
    haystack = " ".join(
        str(value)
        for value in (
            node.get("id", ""),
            node.get("label", ""),
            node.get("type", ""),
            node.get("source_file", ""),
            node.get("metadata", {}).get("snippet", ""),
        )
    ).lower()
    score = 0
    for term in query_terms:
        if term in haystack:
            score += 5 if term in str(node.get("label", "")).lower() else 2
    return score


def build_adjacency(edges: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    adjacency: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for edge in edges:
        adjacency[edge["source"]].append(edge)
        reverse = dict(edge)
        reverse["source"], reverse["target"] = edge["target"], edge["source"]
        reverse["relation"] = f"reverse:{edge.get('relation', '')}"
        adjacency[reverse["source"]].append(reverse)
    return adjacency


def query_graph(nodes: dict[str, dict[str, Any]], edges: list[dict[str, Any]], query: str, limit: int, depth: int) -> str:
    query_terms = terms(query)
    if not query_terms:
        return "Нет поисковых терминов."

    scored = sorted(
        ((score_node(node, query_terms), ident) for ident, node in nodes.items()),
        key=lambda item: (-item[0], nodes[item[1]].get("label", "")),
    )
    seeds = [
        ident
        for score, ident in scored
        if score > 0 and nodes[ident].get("type") != "topic"
    ][:limit]
    if not seeds:
        seeds = [ident for score, ident in scored if score > 0][:limit]
    if not seeds:
        return "По карте связей ничего не найдено."

    adjacency = build_adjacency(edges)
    visited = set(seeds)
    queue = deque((seed, 0) for seed in seeds)
    found_edges: list[dict[str, Any]] = []

    while queue:
        current, current_depth = queue.popleft()
        if current_depth >= depth:
            continue
        for edge in adjacency.get(current, [])[:40]:
            target = edge["target"]
            found_edges.append(edge)
            if target not in visited:
                visited.add(target)
                queue.append((target, current_depth + 1))

    degree = Counter()
    for edge in edges:
        degree[edge["source"]] += int(edge.get("weight", 1))
        degree[edge["target"]] += int(edge.get("weight", 1))

    lines = [
        f"# Relationship-map query: {query}",
        "",
        f"Найдено стартовых узлов: {len(seeds)}",
        f"Контекстных узлов: {len(visited)}",
        "",
        "## Лучшие узлы",
    ]
    for ident in seeds:
        node = nodes[ident]
        source = node.get("source_file") or ""
        lines.append(f"- {node.get('label')} (`{node.get('type')}`, degree {degree.get(ident, 0)}) {source}")

    lines += ["", "## Ближайшие связи"]
    shown = 0
    seen_edges: set[tuple[str, str, str]] = set()
    priority_edges = sorted(
        found_edges,
        key=lambda edge: (
            edge.get("relation") == "topic_matches",
            edge.get("confidence") != "EXTRACTED",
            edge.get("relation", ""),
        ),
    )
    for edge in priority_edges:
        key = (edge["source"], edge["target"], edge.get("relation", ""))
        if key in seen_edges:
            continue
        seen_edges.add(key)
        source = nodes.get(edge["source"], {}).get("label", edge["source"])
        target = nodes.get(edge["target"], {}).get("label", edge["target"])
        relation = edge.get("relation", "")
        confidence = edge.get("confidence", "")
        evidence = edge.get("evidence", "")
        lines.append(f"- {source} --{relation} [{confidence}]--> {target}; {evidence}")
        shown += 1
        if shown >= limit * 6:
            break

    lines += ["", "## Следующий шаг"]
    lines.append("Если ответ неочевиден, используй найденные узлы как ключевые слова для `sml.semantic_query` или чтения конкретных файлов.")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Query the generated relationship-map memory layer.")
    parser.add_argument("query", help="Search query in Russian or English.")
    parser.add_argument("--graph", type=Path, default=DEFAULT_GRAPH, help="Path to relationship map JSON.")
    parser.add_argument("--limit", type=int, default=8, help="Seed node limit.")
    parser.add_argument("--depth", type=int, default=2, help="Traversal depth.")
    args = parser.parse_args()

    graph_path = args.graph
    if not graph_path.is_absolute():
        graph_path = Path.cwd() / graph_path
    if not graph_path.exists():
        raise SystemExit(f"Relationship map not found: {graph_path}")

    nodes, edges = load_graph(graph_path)
    print(query_graph(nodes, edges, args.query, args.limit, args.depth))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
