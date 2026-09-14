"""Focused diagnostics for unresolved resolver-v2 outputs.

ARMST is the only editable game-resource source. Materialized vanilla is
read-only evidence used to resolve inheritance/dependencies that ARMST still
references. Diagnostics therefore show candidates in both roots, but never
suggest editing vanilla.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from typing import Dict, Iterable, Optional, Sequence


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_ARMST_ROOT = (
    r"C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench"
    r"\addons\ARMST-PLATFORM---Weapons"
)


def _norm(path: Optional[str]) -> str:
    return str(path or "").replace("\\", "/").lstrip("./")


def _load_docs(catalog_root: str) -> Iterable[dict]:
    if not os.path.isdir(catalog_root):
        return []
    docs = []
    for dirpath, _dirs, filenames in os.walk(catalog_root):
        for filename in filenames:
            if not filename.lower().endswith(".json"):
                continue
            path = os.path.join(dirpath, filename)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    docs.append(json.load(handle))
            except (OSError, json.JSONDecodeError):
                continue
    return docs


def _candidates(path: Optional[str], roots: Dict[str, str]) -> list[dict]:
    rel = _norm(path)
    if not rel:
        return []
    out = []
    for label, root in roots.items():
        absolute = os.path.join(root, *rel.split("/"))
        if os.path.isfile(absolute):
            out.append(
                {
                    "origin": label,
                    "path": absolute,
                    "editable": label == "armst",
                }
            )
    return out


def build_report(catalog_root: str, roots: Dict[str, str]) -> dict:
    partial = []
    ammo_gaps = []
    status_counts: Counter = Counter()

    for doc in _load_docs(catalog_root):
        entity_id = doc.get("id")
        source = doc.get("source") or {}
        resolution = doc.get("resolution") or {}
        if resolution.get("status") == "partial":
            missing = resolution.get("missing_parent") or {}
            partial.append(
                {
                    "id": entity_id,
                    "resource": source.get("resource"),
                    "missing_parent": missing,
                    "missing_parent_candidates": _candidates(missing.get("path"), roots),
                    "chain": resolution.get("chain") or [],
                }
            )

        if (doc.get("classification") or {}).get("kind") != "weapon":
            continue
        ammo = doc.get("ammo_resolution") or {}
        status = ammo.get("status")
        status_counts[str(status)] += 1
        if status in (None, "resolved", "resolved_with_warnings"):
            continue

        resolved = doc.get("resolved") or {}
        template = ((resolved.get("magazine") or {}).get("magazine_template") or {})
        mag = ammo.get("magazine") or {}
        mag_resource = ammo.get("magazine_target") or mag.get("resource")
        ammo_cfg = mag.get("ammo_config") or {}
        ammo_gaps.append(
            {
                "id": entity_id,
                "resource": source.get("resource"),
                "status": status,
                "magazine_template": template,
                "magazine_target": mag_resource,
                "magazine_target_candidates": _candidates(
                    mag_resource or template.get("path"), roots
                ),
                "magazine_component": mag.get("magazine_component"),
                "magazine_inheritance_status": mag.get("inheritance_status"),
                "ammo_config": ammo_cfg,
                "ammo_config_candidates": _candidates(ammo_cfg.get("path"), roots),
                "magazine_warnings": mag.get("warnings") or [],
            }
        )

    collision_gaps = [
        row for row in ammo_gaps if len(row.get("magazine_target_candidates") or []) > 1
    ]
    return {
        "source_policy": "armst_editable_vanilla_readonly",
        "editing_policy": "edit_armst_only",
        "partial_count": len(partial),
        "partial": partial,
        "weapon_ammo_status": dict(status_counts),
        "ammo_gap_count": len(ammo_gaps),
        "ammo_gaps": ammo_gaps,
        "ammo_gaps_with_path_collision": len(collision_gaps),
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Diagnose ARMST resolver-v2 using read-only vanilla inheritance evidence"
    )
    parser.add_argument("--repo-root", default=os.environ.get("REPO_ROOT", DEFAULT_REPO_ROOT))
    parser.add_argument("--armst-root", default=os.environ.get("ARMST_ROOT", DEFAULT_ARMST_ROOT))
    parser.add_argument("--vanilla-root", default=os.environ.get("VANILLA_ROOT"))
    parser.add_argument("--output-root", default=None)
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo_root)
    output_root = os.path.abspath(
        args.output_root or os.path.join(repo_root, "agent", "v2_output")
    )
    vanilla_root = os.path.abspath(
        args.vanilla_root or os.path.join(repo_root, "Imported", "VanillaSources")
    )
    roots = {
        "armst": os.path.abspath(args.armst_root),
        "materialized_base": vanilla_root,
    }
    report = build_report(os.path.join(output_root, "catalog"), roots)
    report["roots"] = roots

    report_root = os.path.join(output_root, "reports")
    os.makedirs(report_root, exist_ok=True)
    path = os.path.join(report_root, "diagnostics_v2.json")
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
