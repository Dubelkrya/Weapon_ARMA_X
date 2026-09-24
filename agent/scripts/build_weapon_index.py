#!/usr/bin/env python3
"""Build a human-readable index from catalog/weapons/*.json.

This script is intentionally read-only with respect to the ARMST addon and scanner
inputs. It only reads repository JSON / authoring samples and writes or checks
WEAPON_INDEX.md.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WEAPON_DIR = REPO_ROOT / "catalog" / "weapons"
SAMPLE_DIR = REPO_ROOT / "reports" / "samples"
OUTPUT = REPO_ROOT / "WEAPON_INDEX.md"

TYPE_ORDER = (
    "Rifles",
    "Shotguns",
    "Handguns",
    "Machine guns",
    "Other / unresolved",
)

CALIBER_MARKERS = (
    ("12ga", "12 ga"),
    ("545x39", "5.45×39"),
    ("556x45", "5.56×45"),
    ("762x39", "7.62×39"),
    ("762x51", "7.62×51"),
    ("762x54r", "7.62×54R"),
    ("763x25", "7.63×25"),
    ("9x18", "9×18"),
    ("9x19", "9×19"),
    ("9x39", "9×39"),
    ("127x99", "12.7×99"),
    ("127x108", "12.7×108"),
    ("145x114", "14.5×114"),
)

# Curated from reports/KNOWLEDGE_STATUS.md. These are intentionally separate
# from the generated catalog: a validated control is not silently promoted into
# catalog/weapons until the scanner snapshot actually contains it.
WORKBENCH_CONTROLS = (
    {
        "name": "AEK-971 prototype",
        "status": "Workbench validated",
        "catalog": "Not present in current generated catalog",
        "sample": "reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et",
        "note": "Current weapon control point in reports/KNOWLEDGE_STATUS.md",
    },
)


def basename(value: str | None) -> str:
    return Path(value).name if value else "—"


def escape(value: object) -> str:
    return str(value).replace("|", "\\|")


def fire_modes(data: dict) -> list[str]:
    modes = []
    for mode in data.get("fire_modes") or []:
        label = mode.get("ui_name")
        if not label and mode.get("path"):
            label = Path(mode["path"]).stem.removeprefix("FireMode_")
        modes.append(label or "unresolved")
    return modes


def weapon_type(prefab: str | None) -> str:
    value = (prefab or "").lower()
    if "/machineguns/" in value:
        return "Machine guns"
    if "/handguns/" in value:
        return "Handguns"
    if "/shotgun/" in value:
        return "Shotguns"
    if "/rifles/" in value:
        return "Rifles"
    return "Other / unresolved"


def caliber_from_paths(*values: str | None) -> str:
    joined = " ".join(value or "" for value in values).lower()
    for marker, label in CALIBER_MARKERS:
        if marker in joined:
            return label
    return "—"


def sample_for(entry_id: str) -> str | None:
    if not SAMPLE_DIR.exists():
        return None
    token = entry_id.lower()
    for path in sorted(SAMPLE_DIR.iterdir()):
        if not path.is_file():
            continue
        stem = path.stem.lower()
        if stem == token or stem.startswith(token + "_") or stem.startswith(token + "-"):
            return path.relative_to(REPO_ROOT).as_posix()
    return None


def load_rows() -> list[dict]:
    rows = []
    for path in sorted(WEAPON_DIR.glob("*.json")):
        doc = json.loads(path.read_text(encoding="utf-8"))
        data = doc.get("data") or {}
        identity_data = data.get("identity") or {}
        name_field = identity_data.get("name")
        source_name = None
        if isinstance(name_field, dict):
            source_name = name_field.get("value")
        source_name = (
            source_name
            or (doc.get("identity") or {}).get("name")
            or doc.get("id")
            or path.stem
        )

        magazine_data = data.get("magazine") or {}
        magazine = magazine_data.get("magazine_template")
        magazine_path = magazine.get("path") if isinstance(magazine, dict) else None

        ammo_config = magazine_data.get("ammo_config")
        ammo_config_path = ammo_config.get("path") if isinstance(ammo_config, dict) else None

        projectile = magazine_data.get("loaded_projectile")
        projectile_path = projectile.get("path") if isinstance(projectile, dict) else None

        entry_id = doc.get("id") or path.stem
        sample = sample_for(entry_id)
        prefab = (doc.get("source") or {}).get("resource")

        rows.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "id": entry_id,
                "name": source_name,
                "role": doc.get("role") or "unknown",
                "prefab": prefab,
                "magazine": magazine_path,
                "modes": fire_modes(data),
                "warnings": len(doc.get("warnings") or []),
                "type": weapon_type(prefab),
                "caliber": caliber_from_paths(
                    magazine_path,
                    ammo_config_path,
                    projectile_path,
                ),
                "sample": sample,
                "evidence": (
                    "Catalog snapshot + authoring sample"
                    if sample
                    else "Catalog snapshot"
                ),
            }
        )
    return rows


def table(rows: list[dict]) -> list[str]:
    out = [
        "| Entry | Role | Source name | Prefab | Magazine | Fire modes | Evidence | Warnings |",
        "|---|---|---|---|---|---|---|---:|",
    ]
    for row in sorted(rows, key=lambda item: item["id"]):
        modes = ", ".join(row["modes"]) if row["modes"] else "—"
        evidence = row["evidence"]
        if row["sample"]:
            evidence = f"[{evidence}]({row['sample']})"
        out.append(
            f"| [`{escape(row['id'])}`]({row['path']}) "
            f"| {escape(row['role'])} "
            f"| `{escape(row['name'])}` "
            f"| `{escape(basename(row['prefab']))}` "
            f"| `{escape(basename(row['magazine']))}` "
            f"| {escape(modes)} "
            f"| {evidence} "
            f"| {row['warnings']} |"
        )
    return out


def overview_table(rows: list[dict]) -> list[str]:
    type_counts = Counter(row["type"] for row in rows)
    caliber_counts = Counter(row["caliber"] for row in rows)

    out = [
        "### By weapon type",
        "",
        "| Type | Entries |",
        "|---|---:|",
    ]
    for group in TYPE_ORDER:
        if type_counts[group]:
            out.append(f"| {group} | {type_counts[group]} |")

    out.extend(
        [
            "",
            "### By explicit caliber evidence",
            "",
            "| Caliber | Entries |",
            "|---|---:|",
        ]
    )
    for caliber, count in sorted(
        caliber_counts.items(),
        key=lambda item: (item[0] == "—", item[0]),
    ):
        label = "Unresolved in current catalog entry" if caliber == "—" else caliber
        out.append(f"| {label} | {count} |")
    return out


def workbench_controls() -> list[str]:
    out = [
        "## Workbench-validated control points",
        "",
        "These controls are kept separate from the generated catalog so validation evidence is not confused with scanner coverage.",
        "",
        "| Control | Status | Catalog coverage | Sample | Note |",
        "|---|---|---|---|---|",
    ]
    for control in WORKBENCH_CONTROLS:
        sample = control["sample"]
        out.append(
            f"| {control['name']} "
            f"| **{control['status']}** "
            f"| {control['catalog']} "
            f"| [`{Path(sample).name}`]({sample}) "
            f"| {control['note']} |"
        )
    return out


def catalog_sections(rows: list[dict]) -> list[str]:
    out = ["## Catalog by weapon type and caliber", ""]
    for group in TYPE_ORDER:
        group_rows = [row for row in rows if row["type"] == group]
        if not group_rows:
            continue

        out.extend([f"### {group} ({len(group_rows)})", ""])
        calibers = sorted(
            {row["caliber"] for row in group_rows},
            key=lambda value: (value == "—", value),
        )
        for caliber in calibers:
            caliber_rows = [row for row in group_rows if row["caliber"] == caliber]
            heading = "Caliber unresolved" if caliber == "—" else caliber
            out.extend([f"#### {heading} ({len(caliber_rows)})", "", *table(caliber_rows), ""])
    return out


def render(rows: list[dict]) -> str:
    leaf = [row for row in rows if row["role"] == "leaf"]
    base = [row for row in rows if row["role"] == "base"]

    lines = [
        "# Weapon index",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED SNAPSHOT + VALIDATION NAVIGATION.** Catalog rows are derived from `catalog/weapons/*.json`. Workbench control points are listed separately. Live addon / Workbench evidence and `reports/KNOWLEDGE_STATUS.md` remain authoritative.",
        "",
        "This page is the human-readable entry point into the ARMST Arma Reforger weapon catalog. It does not invent missing values: unresolved or absent fields stay unresolved.",
        "",
        f"Current catalog entries: **{len(rows)}** (`{len(leaf)}` leaf entries, `{len(base)}` base/template entries).",
        "",
        "## Catalog overview",
        "",
        *overview_table(rows),
        "",
        *workbench_controls(),
        "",
        *catalog_sections(rows),
        "## Reading the index",
        "",
        "- `Type` grouping comes only from the prefab resource path (`Rifles`, `Shotgun`, `Handguns`, `MachineGuns`); unknown paths remain unresolved.",
        "- Caliber is shown only when an explicit magazine / AmmoConfig / loaded-projectile path contains a recognized caliber marker. It is never inferred from a weapon name.",
        "- `Source name` is preserved exactly from the generated catalog; localization keys such as `#AR-...` are not guessed or replaced.",
        "- `unresolved` means the current catalog entry does not expose a readable fire-mode label at this level.",
        "- Blank magazine/fire-mode data does not mean the weapon has none; the value may be inherited outside the current local snapshot.",
        "- `Catalog snapshot + authoring sample` means a matching file exists in `reports/samples/`; it does **not** automatically mean Workbench validation.",
        "- A warning count greater than zero means the catalog JSON contains source/provenance warnings that should be read before authoring.",
        "",
        "Regenerate this file with `python agent/scripts/build_weapon_index.py` after refreshing the weapon catalog.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--check",
        action="store_true",
        help="Fail if WEAPON_INDEX.md is not up to date.",
    )
    args = parser.parse_args()

    rendered = render(load_rows())
    if args.check:
        current = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else ""
        if current != rendered:
            print("WEAPON_INDEX.md is out of date. Run: python agent/scripts/build_weapon_index.py")
            return 1
        print("WEAPON_INDEX.md is up to date.")
        return 0

    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"Wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
