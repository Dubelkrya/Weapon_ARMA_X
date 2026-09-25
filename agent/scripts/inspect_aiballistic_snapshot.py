#!/usr/bin/env python3
"""Inspect materialized Arma Reforger AI ballistic-table configs without guessing.

This tool is intentionally read-only. It parses the existing local
Imported/VanillaSources/Configs/Weapons/AIBallisticTables/*.conf snapshot with
Weapon_ARMA_X's generic ET/CONF parser and emits:

- the complete parsed config tree;
- every numeric leaf with its structural node path;
- conservative candidate trajectory triplets (3-number leaves), without
  assigning semantics to their positions.

It does NOT infer a maximum range from filenames or field names. The first goal
is to capture the real serialized shape of BallisticTableArray configs so a
source-backed extractor can be written from evidence.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
from typing import Iterable

from et_parser import parse_file


SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_REPO_ROOT = SCRIPT_DIR.parent.parent
DEFAULT_SNAPSHOT_ROOT = (
    DEFAULT_REPO_ROOT
    / "Imported"
    / "VanillaSources"
    / "Configs"
    / "Weapons"
    / "AIBallisticTables"
)

DEFAULT_TARGETS = (
    "AIBT_545x39_Ball_7N6.conf",
    "AIBT_556x45_Ball_M855.conf",
    "AIBT_762x54r_Ball_7N1.conf",
    "AIBT_9x39_Ball_SP5.conf",
)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _node_rows(node, path: tuple[str, ...] = ()) -> Iterable[dict]:
    label = node.name
    if node.type:
        label += f":{node.type}"
    if node.id:
        label += f"#{node.id}"
    current = path + (label,)

    numeric_values = [value for value in node.value if _is_number(value)]
    if numeric_values:
        yield {
            "node_path": "/".join(current),
            "name": node.name,
            "type": node.type,
            "id": node.id,
            "values": list(node.value),
            "numeric_values": numeric_values,
            "all_values_numeric": len(numeric_values) == len(node.value),
            "candidate_triplet": (
                list(node.value)
                if len(node.value) == 3 and len(numeric_values) == 3
                else None
            ),
            "line": node.line,
        }

    for child in node.children:
        yield from _node_rows(child, current)


def inspect_file(path: Path, snapshot_root: Path) -> dict:
    resource = parse_file(str(path), str(snapshot_root))
    numeric_rows = list(_node_rows(resource.root))
    triplets = [
        {
            "node_path": row["node_path"],
            "values": row["candidate_triplet"],
            "line": row["line"],
        }
        for row in numeric_rows
        if row["candidate_triplet"] is not None
    ]

    return {
        "file": path.name,
        "relative_path": path.relative_to(snapshot_root).as_posix(),
        "class": resource.et_class,
        "resource_ref": resource.resource_ref,
        "parsed_tree": resource.root.to_dict(),
        "numeric_leaf_count": len(numeric_rows),
        "numeric_leaves": numeric_rows,
        "candidate_triplet_count": len(triplets),
        "candidate_triplets": triplets,
    }


def select_files(root: Path, targets: list[str], inspect_all: bool) -> list[Path]:
    if inspect_all:
        return sorted(root.glob("*.conf"), key=lambda p: p.name.casefold())

    selected = []
    for name in targets:
        path = root / name
        if not path.is_file():
            raise FileNotFoundError(f"missing AIBT snapshot file: {path}")
        selected.append(path)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect materialized BallisticTableArray .conf snapshots."
    )
    parser.add_argument(
        "--snapshot-root",
        type=Path,
        default=DEFAULT_SNAPSHOT_ROOT,
        help="Directory containing materialized AIBT .conf files.",
    )
    parser.add_argument(
        "--target",
        action="append",
        default=None,
        help="AIBT filename to inspect. Repeatable. Defaults to four reference tables.",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Inspect every .conf in the snapshot directory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. Otherwise JSON is printed.",
    )
    args = parser.parse_args()

    root = args.snapshot_root.resolve()
    if not root.is_dir():
        raise SystemExit(
            "AIBT snapshot directory does not exist: "
            f"{root}\n"
            "Expected an existing materialized snapshot under "
            "Imported/VanillaSources; this tool never launches Workbench."
        )

    targets = args.target or list(DEFAULT_TARGETS)
    files = select_files(root, targets, args.all)

    payload = {
        "contract": "WEAPON_ARMA_X_AIBT_SNAPSHOT_INSPECTION_V1",
        "authority": "READ_ONLY_MATERIALIZED_VANILLA_SNAPSHOT",
        "snapshot_root": str(root),
        "file_count": len(files),
        "semantic_policy": (
            "Candidate numeric triplets are structural evidence only. "
            "Do not label any element as distance/height/time or max range "
            "until the serialized class shape is verified."
        ),
        "files": [inspect_file(path, root) for path in files],
    }

    rendered = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
