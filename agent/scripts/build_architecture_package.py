"""One-command local build of the compact weapon architecture package.

This is the offline entrypoint. It intentionally replaces repeated Workbench
experimentation with a deterministic pipeline:

1. read ARMST + existing read-only materialized vanilla .et/.conf;
2. start only from ARMST weapon-prefab roots, then follow their real dependencies;
3. fetch the pinned official Bohemia script snapshot (unless disabled);
4. index Enforce classes and link serialized component/config classes to code;
5. emit Workbench requests only when the missing target is proven to belong to
   the materialized base-game dependency chain.

A missing reference authored by ARMST is *not* automatically a vanilla export
request: it may be a broken/short ARMST reference. Those gaps remain explicit
source-identity review items instead of causing another broad Workbench scan.

Likewise, a base-game reference whose GUID is already proven to belong to an
ineligible higher-priority ARMST resource is an identity/source conflict, not a
missing vanilla file. Re-exporting that path cannot repair the contradiction and
must never be proposed as Workbench work.

No raw vanilla resources or official script checkout are committed by this
script; their default locations are gitignored.
"""

from __future__ import annotations

import argparse
from collections import defaultdict, deque
import copy
import json
import os
from typing import Iterable, List, Optional, Sequence, Set, Tuple

from architecture_index import build_architecture_package
from scan_build_v2 import DEFAULT_MOD_ROOT, DEFAULT_REPO_ROOT
from script_class_index import build_script_index
from sync_vanilla_scripts import DEFAULT_DESTINATION, ensure_checkout


FOLLOW_EXTENSIONS = {".et", ".conf"}
WEAPON_SEED_PREFIX = "prefabs/weapons/"
BASE_GAME_ORIGIN = "materialized_base"
NON_EXPORTABLE_IDENTITY_REASONS = {
    "guid_target_not_dependency_eligible",
}


def _norm_resource(path: object) -> str:
    return str(path or "").replace("\\", "/").lstrip("./")


def _identity(origin: object, resource: object) -> Tuple[str, str]:
    return str(origin or ""), _norm_resource(resource).casefold()


def _is_weapon_seed(resource: object) -> bool:
    return _norm_resource(resource).casefold().startswith(WEAPON_SEED_PREFIX)


def _safe_base_export_requests(
    missing_edges: List[dict],
) -> Tuple[List[dict], List[dict], List[dict]]:
    """Split actionable base gaps from source/identity review gaps.

    A missing edge authored by ``materialized_base`` is normally safe to request
    from `$ArmaReforger:` because base-game data cannot depend upward on ARMST.
    Two cases are deliberately excluded:

    * missing edges authored by ARMST, where target origin is not proven;
    * base-game edges whose GUID owner is already proven to be an ineligible
      higher-priority resource. That is a source/identity contradiction and
      another export of the same path cannot fix it.
    """
    grouped = {}
    unproven = []
    identity_conflicts = []
    for edge in missing_edges:
        source = edge.get("source") or {}
        ref = edge.get("ref") or {}
        resolution = edge.get("resolution") or {}
        path = _norm_resource(ref.get("path"))
        ext = os.path.splitext(path)[1].lower()
        if ext not in FOLLOW_EXTENSIONS:
            continue
        if source.get("origin") != BASE_GAME_ORIGIN:
            unproven.append(edge)
            continue
        if resolution.get("reason") in NON_EXPORTABLE_IDENTITY_REASONS:
            identity_conflicts.append(edge)
            continue

        key = (str(ref.get("guid") or "").upper(), path.casefold())
        row = grouped.setdefault(
            key,
            {
                "guid": ref.get("guid"),
                "path": path,
                "requested_extension": ext,
                "requested_origin": BASE_GAME_ORIGIN,
                "requested_source_root": "$ArmaReforger:",
                "referred_by": [],
            },
        )
        row["referred_by"].append(
            {
                "origin": source.get("origin"),
                "resource": source.get("resource"),
                "node_path": source.get("node_path"),
            }
        )

    requests = sorted(grouped.values(), key=lambda row: row["path"].casefold())
    return requests, unproven, identity_conflicts


def scope_weapon_architecture(architecture: dict) -> dict:
    """Restrict roots to ARMST weapon prefabs while preserving dependency closure.

    The underlying index contains every parsed record because those records can
    become dependencies. They must not all become *roots*: an unrelated ARMST
    `.et` must never manufacture a Workbench export request. We seed only
    `Prefabs/Weapons/**.et`, then follow resolved `.et/.conf` references to any
    path they actually require, including resources outside the weapon folder.
    """
    scoped = copy.deepcopy(architecture)
    graph = scoped.get("graph") or {}
    resource_index = graph.get("resource_index") or []
    edges = graph.get("reference_edges") or []

    by_source = defaultdict(list)
    for edge in edges:
        source = edge.get("source") or {}
        by_source[_identity(source.get("origin"), source.get("resource"))].append(edge)

    seeds = [
        _identity(row.get("origin"), row.get("resource"))
        for row in resource_index
        if row.get("origin") == "armst"
        and row.get("kind") == "et"
        and _is_weapon_seed(row.get("resource"))
    ]

    queue = deque(seeds)
    seen = set()
    missing = []
    ambiguous = []
    followed = []

    while queue:
        source_id = queue.popleft()
        if source_id in seen:
            continue
        seen.add(source_id)
        for edge in by_source.get(source_id, []):
            ref = edge.get("ref") or {}
            ref_path = _norm_resource(ref.get("path"))
            if os.path.splitext(ref_path)[1].lower() not in FOLLOW_EXTENSIONS:
                continue
            followed.append(edge)
            resolution = edge.get("resolution") or {}
            status = resolution.get("status")
            target_resource = resolution.get("resource")
            target_origin = resolution.get("origin")
            if status == "local" and target_resource and target_origin:
                queue.append(_identity(target_origin, target_resource))
            elif status == "ambiguous":
                ambiguous.append(edge)
            else:
                missing.append(edge)

    export_requests, unproven_origin, identity_conflicts = _safe_base_export_requests(
        missing
    )
    graph["closure"] = {
        "seed_scope": "armst:Prefabs/Weapons/**/*.et",
        "seed_count": len(set(seeds)),
        "reachable_resource_identities": [
            {"origin": origin, "resource_key": resource_key}
            for origin, resource_key in sorted(seen)
        ],
        "followed_serialized_edge_count": len(followed),
        "missing_edges": missing,
        "unproven_target_origin_edges": unproven_origin,
        "non_exportable_identity_edges": identity_conflicts,
        "ambiguous_identity_edges": ambiguous,
    }
    scoped["graph"] = graph

    scoped["blueprints"] = [
        row
        for row in scoped.get("blueprints") or []
        if row.get("origin") == "armst" and _is_weapon_seed(row.get("resource"))
    ]
    scoped["export_requests"] = export_requests

    summary = dict(scoped.get("summary") or {})
    summary.update(
        {
            "seed_scope": "armst:Prefabs/Weapons/**/*.et",
            "seed_count": len(set(seeds)),
            "reachable_resource_count": len(seen),
            "missing_serialized_edge_count": len(missing),
            "unproven_target_origin_edge_count": len(unproven_origin),
            "non_exportable_identity_edge_count": len(identity_conflicts),
            "ambiguous_identity_edge_count": len(ambiguous),
            "exact_export_request_count": len(export_requests),
            "armst_blueprint_count": len(scoped["blueprints"]),
        }
    )
    scoped["summary"] = summary
    return scoped


def _walk_tree_dict(node):
    if not isinstance(node, dict):
        return
    yield node
    for child in node.get("children") or []:
        yield from _walk_tree_dict(child)


def _add_serialized_class_seed(out: Set[str], node: dict) -> None:
    """Add the serialized class represented by one prefab/config node.

    `Field SomeType "{INSTANCE}"` serializes a field named ``Field`` whose
    class is ``SomeType``. The field name must not be reported as a missing
    Enforce class merely because it also has an instance id. For untyped
    component/config instances, the serialized node name itself is the class.
    """
    name = node.get("name")
    typ = node.get("type")
    instance_id = node.get("id")

    if isinstance(typ, str) and typ:
        out.add(typ)
        return

    if not isinstance(name, str) or not name:
        return
    if instance_id is not None or name.endswith("Component") or name.startswith("SCR_"):
        out.add(name)


def serialized_class_names(blueprints: Iterable[dict]) -> Set[str]:
    """Collect actual serialized class names/types used by ARMST architecture."""
    out: Set[str] = set()
    for blueprint in blueprints:
        local_tree = blueprint.get("local_tree")
        for node in _walk_tree_dict(local_tree):
            _add_serialized_class_seed(out, node)
        for subtree in blueprint.get("effective_component_subtrees") or []:
            tree = subtree.get("tree")
            for node in _walk_tree_dict(tree):
                _add_serialized_class_seed(out, node)
    return out


def link_script_classes(blueprints: List[dict], script_index: dict) -> dict:
    """Return declarations for serialized classes plus their base-class closure."""
    seeds = serialized_class_names(blueprints)
    declarations = script_index.get("classes") or []
    by_name = script_index.get("by_name") or {}

    resolved_names: Set[str] = set()
    missing_names: Set[str] = set()
    declaration_indexes: Set[int] = set()
    queue = deque(sorted(seeds))

    while queue:
        name = queue.popleft()
        if name in resolved_names or name in missing_names:
            continue
        indexes = by_name.get(name) or []
        if not indexes:
            missing_names.add(name)
            continue
        resolved_names.add(name)
        for index in indexes:
            if not isinstance(index, int) or index < 0 or index >= len(declarations):
                continue
            declaration_indexes.add(index)
            base = declarations[index].get("base")
            if base and base not in resolved_names:
                queue.append(base)

    linked = [declarations[index] for index in sorted(declaration_indexes)]
    return {
        "serialized_class_seed_count": len(seeds),
        "resolved_class_name_count": len(resolved_names),
        "missing_class_name_count": len(missing_names),
        "serialized_class_seeds": sorted(seeds),
        "resolved_class_names": sorted(resolved_names),
        "missing_class_names": sorted(missing_names),
        "declarations": linked,
    }


def architecture_decision(architecture_summary: dict, script_summary: Optional[dict] = None) -> dict:
    """Separate actionable exports from identity/parser/source blockers."""
    exact = int(architecture_summary.get("exact_export_request_count") or 0)
    unproven = int(architecture_summary.get("unproven_target_origin_edge_count") or 0)
    identity_conflicts = int(
        architecture_summary.get("non_exportable_identity_edge_count") or 0
    )
    ambiguous = int(architecture_summary.get("ambiguous_identity_edge_count") or 0)
    warnings = int(architecture_summary.get("resolver_warning_count") or 0)
    script_failures = int((script_summary or {}).get("parse_failure_count") or 0)

    if exact:
        code = "EXACT_WORKBENCH_EXPORT_REQUIRED"
    elif unproven or identity_conflicts:
        code = "SOURCE_IDENTITY_REVIEW_REQUIRED"
    elif ambiguous:
        code = "IDENTITY_EVIDENCE_REQUIRED"
    elif warnings:
        code = "RESOLVER_REVIEW_REQUIRED"
    elif script_failures:
        code = "SCRIPT_INDEX_REVIEW_REQUIRED"
    else:
        code = "WORKBENCH_NOT_NEEDED"

    return {
        "code": code,
        "architecture_ready": not (
            exact or unproven or identity_conflicts or ambiguous or warnings or script_failures
        ),
        "workbench_needed": bool(exact),
        "exact_request_count": exact,
        "unproven_target_origin_edge_count": unproven,
        "non_exportable_identity_edge_count": identity_conflicts,
        "ambiguous_identity_edge_count": ambiguous,
        "resolver_warning_count": warnings,
        "script_parse_failure_count": script_failures,
    }


def write_json(path: str, payload) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def build_package(
    armst_root: str,
    vanilla_roots: Sequence[str],
    script_source_root: Optional[str],
) -> dict:
    architecture = scope_weapon_architecture(
        build_architecture_package(armst_root, vanilla_roots)
    )
    script_index = None
    script_links = None
    if script_source_root:
        script_index = build_script_index(script_source_root)
        script_links = link_script_classes(architecture["blueprints"], script_index)

    script_summary = (script_index or {}).get("summary")
    decision = architecture_decision(architecture["summary"], script_summary)
    manifest = {
        "schema_version": 1,
        "source_policy": "armst_editable_vanilla_readonly",
        "architecture_summary": architecture["summary"],
        "script_summary": script_summary,
        "script_link_summary": {
            key: value
            for key, value in (script_links or {}).items()
            if key.endswith("_count")
        },
        "decision": decision,
        "workbench_needed": decision["workbench_needed"],
        "workbench_exact_request_count": decision["exact_request_count"],
        "architecture_ready": decision["architecture_ready"],
    }
    return {
        "manifest": manifest,
        "architecture": architecture,
        "script_index": script_index,
        "script_links": script_links,
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build compact weapon architecture package")
    parser.add_argument("--armst-root", default=os.environ.get("MOD_ROOT", DEFAULT_MOD_ROOT))
    parser.add_argument(
        "--vanilla-root",
        action="append",
        default=None,
        help="Read-only materialized vanilla root, optionally label=path. Repeatable.",
    )
    parser.add_argument("--repo-root", default=os.environ.get("REPO_ROOT", DEFAULT_REPO_ROOT))
    parser.add_argument("--output-root", default=None)
    parser.add_argument("--script-source-root", default=DEFAULT_DESTINATION)
    parser.add_argument(
        "--skip-script-sync",
        action="store_true",
        help="Use --script-source-root as-is and do not fetch/update the official checkout.",
    )
    parser.add_argument(
        "--no-scripts",
        action="store_true",
        help="Build only resource architecture; omit script class indexing.",
    )
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo_root)
    output_root = os.path.abspath(
        args.output_root or os.path.join(repo_root, "agent", "architecture_output")
    )
    vanilla_roots = args.vanilla_root or [
        "materialized_base=" + os.path.join(repo_root, "Imported", "VanillaSources")
    ]

    script_root = None
    if not args.no_scripts:
        script_root = os.path.abspath(args.script_source_root)
        if not args.skip_script_sync:
            ensure_checkout(script_root)

    package = build_package(args.armst_root, vanilla_roots, script_root)
    architecture = package["architecture"]

    write_json(os.path.join(output_root, "package_manifest.json"), package["manifest"])
    write_json(os.path.join(output_root, "architecture_summary.json"), architecture["summary"])
    write_json(os.path.join(output_root, "architecture_graph.json"), architecture["graph"])
    write_json(os.path.join(output_root, "weapon_blueprints.json"), architecture["blueprints"])
    write_json(
        os.path.join(output_root, "workbench_export_requests.json"),
        architecture["export_requests"],
    )
    write_json(
        os.path.join(output_root, "resolver_warnings.json"),
        architecture["resolver_warnings"],
    )
    if package["script_index"] is not None:
        write_json(
            os.path.join(output_root, "script_class_index.json"),
            package["script_index"],
        )
        write_json(
            os.path.join(output_root, "script_class_links.json"),
            package["script_links"],
        )

    print(json.dumps({"output_root": output_root, **package["manifest"]}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())