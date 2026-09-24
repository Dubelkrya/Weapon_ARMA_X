#!/usr/bin/env python3
"""Build a human-readable index from catalog/weapons/*.json.

This script is intentionally read-only with respect to the ARMST addon and scanner
inputs. It only reads repository JSON and writes/checks WEAPON_INDEX.md.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
WEAPON_DIR = REPO_ROOT / "catalog" / "weapons"
OUTPUT = REPO_ROOT / "WEAPON_INDEX.md"


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
        source_name = source_name or (doc.get("identity") or {}).get("name") or doc.get("id") or path.stem

        magazine = (data.get("magazine") or {}).get("magazine_template")
        magazine_path = magazine.get("path") if isinstance(magazine, dict) else None

        rows.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "id": doc.get("id") or path.stem,
                "name": source_name,
                "role": doc.get("role") or "unknown",
                "prefab": (doc.get("source") or {}).get("resource"),
                "magazine": magazine_path,
                "modes": fire_modes(data),
                "warnings": len(doc.get("warnings") or []),
            }
        )
    return rows


def table(rows: list[dict]) -> list[str]:
    out = [
        "| Entry | Source name | Prefab | Magazine | Fire modes | Warnings |",
        "|---|---|---|---|---|---:|",
    ]
    for row in sorted(rows, key=lambda item: item["id"]):
        modes = ", ".join(row["modes"]) if row["modes"] else "—"
        out.append(
            f"| [`{escape(row['id'])}`]({row['path']}) "
            f"| `{escape(row['name'])}` "
            f"| `{escape(basename(row['prefab']))}` "
            f"| `{escape(basename(row['magazine']))}` "
            f"| {escape(modes)} | {row['warnings']} |"
        )
    return out


def render(rows: list[dict]) -> str:
    leaf = [row for row in rows if row["role"] == "leaf"]
    base = [row for row in rows if row["role"] == "base"]

    lines = [
        "# Weapon index",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED SNAPSHOT.** This index is derived from `catalog/weapons/*.json` and is for navigation. Live addon / Workbench evidence and `reports/KNOWLEDGE_STATUS.md` remain authoritative.",
        "",
        "This page provides a human-readable entry point into the ARMST Arma Reforger weapon catalog. It does not invent missing values: unresolved or absent catalog fields stay unresolved/blank.",
        "",
        f"Current catalog entries: **{len(rows)}** (`{len(leaf)}` leaf entries, `{len(base)}` base/template entries).",
        "",
        "## Leaf weapon entries",
        "",
        *table(leaf),
        "",
        "## Base / template entries",
        "",
        *table(base),
        "",
        "## Reading the index",
        "",
        "- `Source name` is preserved exactly from the generated catalog; localization keys such as `#AR-...` are not guessed or replaced.",
        "- `unresolved` means the current catalog entry does not expose a readable fire-mode label at this level.",
        "- Blank magazine/fire-mode data does not mean the weapon has none; the value may be inherited outside the current local snapshot.",
        "- A warning count greater than zero means the catalog JSON contains source/provenance warnings that should be read before authoring.",
        "",
        "Regenerate this file with `python agent/scripts/build_weapon_index.py` after refreshing the weapon catalog.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Fail if WEAPON_INDEX.md is not up to date.")
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
