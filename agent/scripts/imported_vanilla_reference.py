#!/usr/bin/env python3
"""Read-only adapter for imported vanilla weapon reference prefabs.

This tool deliberately does NOT participate in the canonical ARMST scan.
It inspects a separate local reference root (for example the user's
Weapon_ARMA_X Workbench folder), verifies three fixed imported vanilla magazine
resources, and emits reference-only JSON evidence.

The output must be treated as STRUCTURED_REFERENCE_SOURCE, never as live
base-game authority.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from et_parser import GUID_REF_RE, find_child, find_recursive, parse_file

TARGETS = (
    {
        "guid": "9569026177545A20",
        "filename": "Magazine_545x39_RPK_45rnd_Base.et",
        "resource": "Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et",
    },
    {
        "guid": "761A03A9C5BA8D68",
        "filename": "Magazine_762x54_SVD_10rnd_Base.et",
        "resource": "Prefabs/Weapons/Magazines/Magazine_762x54_SVD_10rnd_Base.et",
    },
    {
        "guid": "9B5AA2C731485ACA",
        "filename": "Magazine_9x18_PM_8rnd_Base.et",
        "resource": "Prefabs/Weapons/Magazines/Magazine_9x18_PM_8rnd_Base.et",
    },
)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def scalar(node):
    if node is None or not node.value:
        return None
    return node.value[0]


def array_values(node):
    if node is None:
        return []
    values = list(node.value)
    for child in node.children:
        if child.name == "__elem__":
            values.extend(child.value)
    return values


def field_score(node) -> int:
    weights = {
        "AmmoConfig": 8,
        "AmmoMapping": 4,
        "MaxAmmo": 2,
        "MagazineWell": 1,
    }
    return sum(weight for name, weight in weights.items()
               if find_child(node, name) is not None)


def functional_magazine_component(root):
    candidates = find_recursive(root, "MagazineComponent")
    return max(candidates, key=field_score) if candidates else None


def meta_guid(meta_path: Path, root: Path):
    if not meta_path.exists():
        return None
    parsed = parse_file(meta_path, root)
    names = find_recursive(parsed.root, "Name")
    for node in names:
        if not node.value:
            continue
        match = GUID_REF_RE.match(str(node.value[0]))
        if match:
            return match.group(1).upper()
    return None


def find_unique(root: Path, filename: str):
    matches = [path for path in root.rglob(filename) if path.is_file()]
    if len(matches) == 1:
        return matches[0], None
    if not matches:
        return None, "NOT_FOUND"
    return None, f"AMBIGUOUS_{len(matches)}"


def extract_target(root: Path, target: dict) -> dict:
    et_path, problem = find_unique(root, target["filename"])
    row = {
        "status": "UNRESOLVED",
        "source_classification": "STRUCTURED_REFERENCE_SOURCE",
        "expected_guid": target["guid"],
        "canonical_resource": target["resource"],
        "physical_file": None,
        "meta_file": None,
        "meta_guid": None,
        "meta_imported_vanilla": None,
        "sha256_et": None,
        "sha256_meta": None,
        "max_ammo": None,
        "ammo_mapping_length": None,
        "ammo_mapping": None,
        "ammo_config": None,
        "magazine_well": None,
        "notes": [],
    }
    if problem:
        row["notes"].append(problem)
        return row

    row["physical_file"] = et_path.relative_to(root).as_posix()
    meta_path = Path(str(et_path) + ".meta")
    if meta_path.exists():
        row["meta_file"] = meta_path.relative_to(root).as_posix()
        row["meta_guid"] = meta_guid(meta_path, root)
        meta_text = meta_path.read_text(encoding="utf-8", errors="replace")
        row["meta_imported_vanilla"] = "Imported/VanillaSources" in meta_text
        row["sha256_meta"] = sha256(meta_path)
    else:
        row["notes"].append("META_MISSING")

    row["sha256_et"] = sha256(et_path)
    parsed = parse_file(et_path, root)
    mag = functional_magazine_component(parsed.root)
    if mag is None:
        row["notes"].append("MAGAZINE_COMPONENT_MISSING")
        return row

    max_ammo = find_child(mag, "MaxAmmo")
    mapping = find_child(mag, "AmmoMapping")
    ammo_config = find_child(mag, "AmmoConfig")
    well = find_child(mag, "MagazineWell")

    row["max_ammo"] = scalar(max_ammo)
    row["ammo_mapping"] = array_values(mapping)
    row["ammo_mapping_length"] = len(row["ammo_mapping"])
    row["magazine_well"] = {
        "name": well.name,
        "class": well.type,
    } if well is not None else None
    if ammo_config is not None and ammo_config.ref:
        row["ammo_config"] = {
            "guid": ammo_config.ref.get("guid"),
            "path": ammo_config.ref.get("path"),
        }

    if row["meta_guid"] and row["meta_guid"] != target["guid"]:
        row["notes"].append("GUID_MISMATCH")
    if row["meta_imported_vanilla"] is False:
        row["notes"].append("META_NOT_MARKED_IMPORTED_VANILLA")

    if (
        row["max_ammo"] is not None
        and row["meta_guid"] == target["guid"]
        and row["meta_imported_vanilla"] is True
    ):
        row["status"] = "REFERENCE_RESOLVED"
    else:
        row["notes"].append("REFERENCE_IDENTITY_OR_VALUE_INCOMPLETE")

    return row


def build_report(root: Path) -> dict:
    return {
        "contract": "WEAPON_ARMA_X_IMPORTED_VANILLA_REFERENCE_V1",
        "authority": "STRUCTURED_REFERENCE_SOURCE",
        "canonical_authority": False,
        "reference_root": str(root),
        "target_count": len(TARGETS),
        "targets": [extract_target(root, target) for target in TARGETS],
        "policy": (
            "Reference evidence may corroborate unresolved external magazine "
            "parents but must not silently replace current primary-addon or "
            "Workbench-mounted evidence."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--reference-root",
        required=True,
        type=Path,
        help="Read-only root containing imported vanilla .et/.meta reference files.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional JSON output path. If omitted, JSON is printed to stdout.",
    )
    args = parser.parse_args()

    root = args.reference_root.resolve()
    if not root.is_dir():
        raise SystemExit(f"reference root does not exist: {root}")

    report = build_report(root)
    rendered = json.dumps(report, indent=2, ensure_ascii=False)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
