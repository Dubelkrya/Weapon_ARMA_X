"""Build a compact, provenance-preserving weapon architecture graph offline.

This script is intentionally independent of Workbench GUI iteration. It reads:

* ARMST as the editable source root;
* the existing materialized vanilla ``.et/.conf`` dataset as read-only evidence;
* strict resolver identity/provenance rules.

It emits a compact graph, ARMST prefab blueprints, and an *exact* list of
missing serialized resources. Only that missing list should ever drive a later
Workbench export. The script never broadens the exporter to the whole game.

Architecture output keeps raw instance GUIDs and source order. The semantic
resolver's ``_prefer_functional_components`` heuristic is deliberately NOT
used to construct architecture trees.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict, deque
import json
import os
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from resolver_v2 import RNode, _norm_key, merge_pair, rnode_from_parsed
from resolver_v2_extract import classify
from scan_build_v2 import DEFAULT_MOD_ROOT, DEFAULT_REPO_ROOT
from scan_build_v2_strict import build_store


FOLLOW_EXTENSIONS = {".et", ".conf"}


def _norm(path: Optional[str]) -> str:
    return str(path or "").replace("\\", "/").lstrip("./")


def _identity(origin: str, resource: str) -> Tuple[str, str]:
    return origin, _norm_key(resource)


def _identity_key(origin: str, resource: str) -> str:
    return f"{origin}:{_norm(resource)}"


def _record_identity(record) -> Tuple[str, str]:
    return _identity(record.origin, record.relpath)


def _node_segment(node: RNode, occurrence: int) -> str:
    if node.id is not None:
        return f"{node.name}[id={node.id}]"
    return f"{node.name}[{occurrence}]"


def walk_rnodes(root: Optional[RNode], prefix: str = "$" ):
    if root is None:
        return
    counts: Counter = Counter()
    for child in root.children:
        occurrence = counts[child.name]
        counts[child.name] += 1
        path = prefix + "/" + _node_segment(child, occurrence)
        yield child, path
        yield from walk_rnodes(child, path)


def compact_tree(node: Optional[RNode]) -> Optional[dict]:
    """Loss-minimized JSON tree used for prefab reconstruction.

    Empty/default metadata is omitted, but source order, instance ids, refs,
    values, provenance, and children are preserved.
    """
    if node is None:
        return None
    out = {"name": node.name}
    if node.type is not None:
        out["type"] = node.type
    if node.id is not None:
        out["id"] = node.id
    if node.value:
        out["value"] = list(node.value)
    if node.ref:
        out["ref"] = dict(node.ref)
    if node.append:
        out["append"] = True
    if node.line:
        out["line"] = node.line
    if node.defined_in is not None:
        out["defined_in"] = node.defined_in
    if node.origin is not None:
        out["origin"] = node.origin
    if node.children:
        out["children"] = [compact_tree(child) for child in node.children]
    return out


def instance_index(root: Optional[RNode]) -> List[dict]:
    rows = []
    for node, structural_path in walk_rnodes(root):
        if node.id is None:
            continue
        rows.append(
            {
                "node_path": structural_path,
                "name": node.name,
                "type": node.type,
                "instance_id": node.id,
                "ref": dict(node.ref) if node.ref else None,
                "defined_in": node.defined_in,
                "origin": node.origin,
            }
        )
    return rows


def component_subtrees(root: Optional[RNode]) -> List[dict]:
    """Return every serialized ``components`` block in source order."""
    rows = []
    for node, structural_path in walk_rnodes(root):
        if node.name != "components":
            continue
        rows.append(
            {
                "node_path": structural_path,
                "tree": compact_tree(node),
            }
        )
    return rows


def _resolved_architecture_tree(store, record):
    """Merge inheritance/configs without semantic component reordering."""
    chain, missing = store.build_chain(record.relpath, origin=record.origin)
    records = [
        store._record_for(row["resource"], row.get("origin"))
        for row in chain
        if row.get("status") == "local"
    ]
    records = [item for item in records if item is not None]
    if not records:
        return None, chain, missing

    trees = [
        rnode_from_parsed(item.resource.root, item.relpath, item.origin)
        for item in records
    ]
    resolved = trees[-1]
    for child_tree in reversed(trees[:-1]):
        resolved = merge_pair(resolved, child_tree)
    resolved = store._hydrate_config_refs(resolved)
    return resolved, chain, missing


def _edge_payload(store, record, ref: dict, source_node: str, edge_kind: str) -> dict:
    resolved = store.resolve_ref(
        ref.get("guid"),
        ref.get("path"),
        origin_hint=record.origin,
    )
    return {
        "source": {
            "origin": record.origin,
            "resource": record.relpath,
            "node_path": source_node,
        },
        "kind": edge_kind,
        "ref": {
            "guid": ref.get("guid"),
            "path": _norm(ref.get("path")),
        },
        "resolution": {
            "status": resolved.get("status"),
            "resource": resolved.get("resource"),
            "origin": resolved.get("origin"),
            "resolved_by": resolved.get("resolved_by"),
            "reason": resolved.get("reason"),
            "candidates": resolved.get("candidates") or [],
            "guid_candidates": resolved.get("guid_candidates") or [],
        },
    }


def reference_edges(store, record) -> List[dict]:
    rows = []
    if record.kind == "et" and record.parent:
        rows.append(
            _edge_payload(store, record, record.parent, "$parent", "inheritance")
        )
    root = record.resource.root
    if root is None:
        return rows
    raw = rnode_from_parsed(root, record.relpath, record.origin)
    for node, structural_path in walk_rnodes(raw):
        if not node.ref:
            continue
        rows.append(
            _edge_payload(store, record, node.ref, structural_path, "resource_ref")
        )
    return rows


def resource_index(store) -> List[dict]:
    rows = []
    for record in sorted(
        store._all_records(),
        key=lambda item: (item.origin, item.relpath.casefold()),
    ):
        record_id = _record_identity(record)
        guids = sorted(store._guids_by_identity.get(record_id, []))
        candidates, _mode = store._candidate_records(record.relpath)
        rows.append(
            {
                "origin": record.origin,
                "resource": record.relpath,
                "kind": record.kind,
                "class": record.resource.et_class,
                "priority": record.priority,
                "proven_live_guids": guids,
                "path_collision_count": len(candidates),
                "parent_ref": dict(record.parent) if record.parent else None,
            }
        )
    return rows


def build_graph(store) -> dict:
    records = store._all_records()
    edges = []
    by_source: Dict[Tuple[str, str], List[dict]] = defaultdict(list)
    for record in records:
        if record.kind not in {"et", "conf"}:
            continue
        rows = reference_edges(store, record)
        edges.extend(rows)
        by_source[_record_identity(record)].extend(rows)

    # Start dependency closure from every editable ARMST .et. This is broader
    # than only catalogued leaf weapons but still bounded to the addon itself.
    queue = deque(
        _record_identity(record)
        for record in records
        if record.origin == "armst" and record.kind == "et"
    )
    seen = set()
    missing = []
    ambiguous = []
    followed_edges = []

    while queue:
        source_id = queue.popleft()
        if source_id in seen:
            continue
        seen.add(source_id)
        for edge in by_source.get(source_id, []):
            ref_path = _norm((edge.get("ref") or {}).get("path"))
            if os.path.splitext(ref_path)[1].lower() not in FOLLOW_EXTENSIONS:
                continue
            followed_edges.append(edge)
            resolution = edge.get("resolution") or {}
            status = resolution.get("status")
            if status == "local" and resolution.get("resource") and resolution.get("origin"):
                queue.append(
                    _identity(resolution["origin"], resolution["resource"])
                )
            elif status == "ambiguous":
                ambiguous.append(edge)
            else:
                missing.append(edge)

    return {
        "resource_index": resource_index(store),
        "reference_edges": edges,
        "closure": {
            "reachable_resource_identities": [
                {"origin": origin, "resource_key": resource_key}
                for origin, resource_key in sorted(seen)
            ],
            "followed_serialized_edge_count": len(followed_edges),
            "missing_edges": missing,
            "ambiguous_identity_edges": ambiguous,
        },
    }


def exact_export_requests(graph: dict) -> List[dict]:
    grouped = {}
    missing = ((graph.get("closure") or {}).get("missing_edges") or [])
    for edge in missing:
        ref = edge.get("ref") or {}
        path = _norm(ref.get("path"))
        ext = os.path.splitext(path)[1].lower()
        if ext not in FOLLOW_EXTENSIONS:
            continue
        key = (str(ref.get("guid") or "").upper(), path.casefold())
        row = grouped.setdefault(
            key,
            {
                "guid": ref.get("guid"),
                "path": path,
                "requested_extension": ext,
                "referred_by": [],
            },
        )
        source = edge.get("source") or {}
        row["referred_by"].append(
            {
                "origin": source.get("origin"),
                "resource": source.get("resource"),
                "node_path": source.get("node_path"),
            }
        )
    return sorted(grouped.values(), key=lambda row: row["path"].casefold())


def build_blueprints(store, graph: dict) -> List[dict]:
    edges_by_source = defaultdict(list)
    for edge in graph.get("reference_edges") or []:
        source = edge.get("source") or {}
        edges_by_source[_identity(source.get("origin"), source.get("resource"))].append(edge)

    out = []
    for record in sorted(
        store._all_records(),
        key=lambda item: item.relpath.casefold(),
    ):
        if record.origin != "armst" or record.kind != "et":
            continue

        raw = rnode_from_parsed(record.resource.root, record.relpath, record.origin)
        architecture_resolved, chain, missing = _resolved_architecture_tree(store, record)

        # Semantic classification is allowed to use the semantic resolver; its
        # reordered tree is never written as architecture evidence.
        semantic = store.resolve_entity(record.relpath, record.origin)
        classification = classify(
            semantic.resolved,
            record.relpath,
            record.resource.et_class,
        ) if semantic.resolved is not None else {
            "kind": "unknown",
            "family": None,
        }

        out.append(
            {
                "origin": record.origin,
                "resource": record.relpath,
                "class": record.resource.et_class,
                "classification": classification,
                "parent_ref": dict(record.parent) if record.parent else None,
                "resolution": {
                    "status": "resolved" if missing is None else "partial",
                    "chain": chain,
                    "missing_parent": missing,
                },
                "local_tree": compact_tree(raw),
                "local_instances": instance_index(raw),
                "effective_component_subtrees": component_subtrees(
                    architecture_resolved
                ),
                "effective_instances": instance_index(architecture_resolved),
                "resource_refs": edges_by_source.get(
                    _record_identity(record), []
                ),
            }
        )
    return out


def write_json(path: str, payload) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)


def build_architecture_package(armst_root: str, vanilla_roots: Sequence[str]) -> dict:
    store = build_store(os.path.abspath(armst_root), vanilla_roots)
    graph = build_graph(store)
    blueprints = build_blueprints(store, graph)
    requests = exact_export_requests(graph)
    summary = {
        "schema_version": 1,
        "source_policy": "armst_editable_vanilla_readonly",
        "resource_count": len(graph["resource_index"]),
        "reference_edge_count": len(graph["reference_edges"]),
        "reachable_resource_count": len(graph["closure"]["reachable_resource_identities"]),
        "missing_serialized_edge_count": len(graph["closure"]["missing_edges"]),
        "ambiguous_identity_edge_count": len(graph["closure"]["ambiguous_identity_edges"]),
        "exact_export_request_count": len(requests),
        "armst_blueprint_count": len(blueprints),
        "resolver_warning_count": len(store.warnings),
    }
    return {
        "summary": summary,
        "graph": graph,
        "blueprints": blueprints,
        "export_requests": requests,
        "resolver_warnings": store.warnings,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build offline ARMST + vanilla weapon architecture graph"
    )
    parser.add_argument("--armst-root", default=os.environ.get("MOD_ROOT", DEFAULT_MOD_ROOT))
    parser.add_argument(
        "--vanilla-root",
        action="append",
        default=None,
        help="Read-only materialized vanilla root, optionally label=path. Repeatable.",
    )
    parser.add_argument("--repo-root", default=os.environ.get("REPO_ROOT", DEFAULT_REPO_ROOT))
    parser.add_argument("--output-root", default=None)
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo_root)
    vanilla_roots = args.vanilla_root or [
        "materialized_base=" + os.path.join(repo_root, "Imported", "VanillaSources")
    ]
    output_root = os.path.abspath(
        args.output_root or os.path.join(repo_root, "agent", "architecture_output")
    )

    package = build_architecture_package(args.armst_root, vanilla_roots)
    write_json(os.path.join(output_root, "architecture_summary.json"), package["summary"])
    write_json(os.path.join(output_root, "architecture_graph.json"), package["graph"])
    write_json(os.path.join(output_root, "weapon_blueprints.json"), package["blueprints"])
    write_json(
        os.path.join(output_root, "workbench_export_requests.json"),
        package["export_requests"],
    )
    write_json(
        os.path.join(output_root, "resolver_warnings.json"),
        package["resolver_warnings"],
    )

    print(json.dumps({"output_root": output_root, **package["summary"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
