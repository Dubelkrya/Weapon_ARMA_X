"""One-command local build of the compact weapon architecture package.

This is the offline entrypoint. It intentionally replaces repeated Workbench
experimentation with a deterministic pipeline:

1. read ARMST + existing read-only materialized vanilla .et/.conf;
2. build strict resource/inheritance/reference architecture;
3. fetch the pinned official Bohemia script snapshot (unless disabled);
4. index Enforce classes and link serialized component/config classes to code;
5. emit exact missing .et/.conf requests for a later targeted Workbench export.

No raw vanilla resources or official script checkout are committed by this
script; their default locations are gitignored.
"""

from __future__ import annotations

import argparse
from collections import deque
import json
import os
from typing import Iterable, List, Optional, Sequence, Set

from architecture_index import build_architecture_package
from scan_build_v2 import DEFAULT_MOD_ROOT, DEFAULT_REPO_ROOT
from script_class_index import build_script_index
from sync_vanilla_scripts import DEFAULT_DESTINATION, ensure_checkout


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


def architecture_decision(architecture_summary: dict) -> dict:
    """Separate missing-resource work from identity/parser correctness blockers.

    A non-empty Workbench request list is actionable by an exact exporter.
    Ambiguous identity is deliberately *not* a Workbench request: copying the
    same collided path again cannot prove which resource a serialized GUID owns.
    Resolver warnings likewise require parser/resolver review before declaring
    the architecture package ready.
    """
    exact = int(architecture_summary.get("exact_export_request_count") or 0)
    ambiguous = int(architecture_summary.get("ambiguous_identity_edge_count") or 0)
    warnings = int(architecture_summary.get("resolver_warning_count") or 0)

    if exact:
        code = "EXACT_WORKBENCH_EXPORT_REQUIRED"
    elif ambiguous:
        code = "IDENTITY_EVIDENCE_REQUIRED"
    elif warnings:
        code = "RESOLVER_REVIEW_REQUIRED"
    else:
        code = "WORKBENCH_NOT_NEEDED"

    return {
        "code": code,
        "architecture_ready": not (exact or ambiguous or warnings),
        "workbench_needed": bool(exact),
        "exact_request_count": exact,
        "ambiguous_identity_edge_count": ambiguous,
        "resolver_warning_count": warnings,
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
    architecture = build_architecture_package(armst_root, vanilla_roots)
    script_index = None
    script_links = None
    if script_source_root:
        script_index = build_script_index(script_source_root)
        script_links = link_script_classes(architecture["blueprints"], script_index)

    decision = architecture_decision(architecture["summary"])
    manifest = {
        "schema_version": 1,
        "source_policy": "armst_editable_vanilla_readonly",
        "architecture_summary": architecture["summary"],
        "script_summary": (script_index or {}).get("summary"),
        "script_link_summary": {
            key: value
            for key, value in (script_links or {}).items()
            if key.endswith("_count")
        },
        "decision": decision,
        # Backward-compatible top-level fields for existing readers.
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
