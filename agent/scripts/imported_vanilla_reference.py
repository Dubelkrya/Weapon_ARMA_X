#!/usr/bin/env python3
"""Read-only adapter for imported vanilla weapon reference resources.

This tool deliberately does NOT participate in the canonical ARMST scan.
It inspects the imported vanilla corpus checked into Weapon_ARMA_X and emits
reference-only JSON evidence.

Important identity rule:
the GUID in Imported/VanillaSources metadata is a *local import GUID*. It is
not required to equal a live/base-game GUID referenced by ARMST. Identity is
verified by the declared original resource path carried after the
Imported/VanillaSources/ prefix.

All output is STRUCTURED_REFERENCE_SOURCE and canonical_authority=false.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from et_parser import GUID_REF_RE, find_child, find_recursive, parse_file

IMPORTED_PREFIX = "Imported/VanillaSources/"

TARGETS = (
    {
        "kind": "magazine",
        "live_reference_guid": "9569026177545A20",
        "filename": "Magazine_545x39_RPK_45rnd_Base.et",
        "resource": "Prefabs/Weapons/Magazines/Magazine_545x39_RPK_45rnd_Base.et",
    },
    {
        "kind": "magazine",
        "live_reference_guid": "761A03A9C5BA8D68",
        "filename": "Magazine_762x54_SVD_10rnd_Base.et",
        "resource": "Prefabs/Weapons/Magazines/Magazine_762x54_SVD_10rnd_Base.et",
    },
    {
        "kind": "magazine",
        "live_reference_guid": "9B5AA2C731485ACA",
        "filename": "Magazine_9x18_PM_8rnd_Base.et",
        "resource": "Prefabs/Weapons/Magazines/Magazine_9x18_PM_8rnd_Base.et",
    },
    {
        "kind": "projectile",
        "live_reference_guid": "AC29AE3D5ECD6390",
        "filename": "Ammo_762x54r_Ball_57N323S.et",
        "resource": "Prefabs/Weapons/Ammo/Ammo_762x54r_Ball_57N323S.et",
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


def meta_identity(meta_path: Path, root: Path) -> dict:
    result = {
        "import_guid": None,
        "declared_name": None,
        "declared_original_resource": None,
        "imported_vanilla": False,
    }
    if not meta_path.exists():
        return result

    parsed = parse_file(meta_path, root)
    names = find_recursive(parsed.root, "Name")
    for node in names:
        if not node.value:
            continue
        raw = str(node.value[0])
        match = GUID_REF_RE.match(raw)
        if not match:
            continue

        path = match.group(2).replace("\\", "/")
        result["import_guid"] = match.group(1).upper()
        result["declared_name"] = path
        if path.startswith(IMPORTED_PREFIX):
            result["imported_vanilla"] = True
            result["declared_original_resource"] = path[len(IMPORTED_PREFIX):]
        return result

    return result


def find_unique(root: Path, filename: str):
    matches = [path for path in root.rglob(filename) if path.is_file()]
    if len(matches) == 1:
        return matches[0], None
    if not matches:
        return None, "NOT_FOUND"
    return None, f"AMBIGUOUS_{len(matches)}"


def base_row(target: dict) -> dict:
    return {
        "status": "UNRESOLVED",
        "kind": target["kind"],
        "source_classification": "STRUCTURED_REFERENCE_SOURCE",
        "canonical_authority": False,
        "live_reference_guid": target["live_reference_guid"],
        "canonical_resource": target["resource"],
        "physical_file": None,
        "meta_file": None,
        "meta_import_guid": None,
        "meta_declared_name": None,
        "meta_declared_original_resource": None,
        "meta_imported_vanilla": None,
        "identity_match": False,
        "sha256_et": None,
        "sha256_meta": None,
        "notes": [],
    }


def extract_magazine(row: dict, parsed) -> None:
    row.update({
        "max_ammo": None,
        "ammo_mapping_length": None,
        "ammo_mapping": None,
        "ammo_config": None,
        "magazine_well": None,
    })

    mag = functional_magazine_component(parsed.root)
    if mag is None:
        row["notes"].append("MAGAZINE_COMPONENT_MISSING")
        return

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


def extract_projectile(row: dict, parsed) -> None:
    row.update({
        "projectile_damage_found": False,
        "damage_value": None,
        "damage_type": None,
        "minimum_damage": None,
    })

    effects = find_recursive(parsed.root, "ProjectileDamage")
    if not effects:
        row["notes"].append("PROJECTILE_DAMAGE_MISSING")
        return

    effect = effects[0]
    row["projectile_damage_found"] = True
    row["damage_value"] = scalar(find_child(effect, "DamageValue"))
    row["damage_type"] = scalar(find_child(effect, "DamageType"))
    row["minimum_damage"] = scalar(find_child(effect, "MinimumDamage"))


def extract_target(root: Path, target: dict) -> dict:
    et_path, problem = find_unique(root, target["filename"])
    row = base_row(target)
    if problem:
        row["notes"].append(problem)
        return row

    row["physical_file"] = et_path.relative_to(root).as_posix()
    row["sha256_et"] = sha256(et_path)

    meta_path = Path(str(et_path) + ".meta")
    if meta_path.exists():
        row["meta_file"] = meta_path.relative_to(root).as_posix()
        row["sha256_meta"] = sha256(meta_path)
        identity = meta_identity(meta_path, root)
        row["meta_import_guid"] = identity["import_guid"]
        row["meta_declared_name"] = identity["declared_name"]
        row["meta_declared_original_resource"] = identity["declared_original_resource"]
        row["meta_imported_vanilla"] = identity["imported_vanilla"]
        row["identity_match"] = (
            identity["imported_vanilla"]
            and identity["declared_original_resource"] == target["resource"]
        )
    else:
        row["notes"].append("META_MISSING")

    parsed = parse_file(et_path, root)
    if target["kind"] == "magazine":
        extract_magazine(row, parsed)
        value_present = row["max_ammo"] is not None
    else:
        extract_projectile(row, parsed)
        value_present = row["projectile_damage_found"]

    if not row["identity_match"]:
        row["notes"].append("DECLARED_RESOURCE_IDENTITY_MISMATCH")

    if row["identity_match"] and value_present:
        row["status"] = "REFERENCE_RESOLVED"
    else:
        row["notes"].append("REFERENCE_IDENTITY_OR_VALUE_INCOMPLETE")

    return row


def build_report(root: Path) -> dict:
    return {
        "contract": "WEAPON_ARMA_X_IMPORTED_VANILLA_REFERENCE_V2",
        "authority": "STRUCTURED_REFERENCE_SOURCE",
        "canonical_authority": False,
        "identity_policy": (
            "Imported metadata GUID is local import provenance only. "
            "Imported identity is matched by the declared original resource path."
        ),
        "reference_root": str(root),
        "target_count": len(TARGETS),
        "targets": [extract_target(root, target) for target in TARGETS],
        "policy": (
            "Reference evidence may corroborate unresolved external magazine "
            "or projectile parents but must not silently replace current "
            "primary-addon or Workbench-mounted evidence."
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
