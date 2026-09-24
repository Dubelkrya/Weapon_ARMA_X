#!/usr/bin/env python3
"""Build generated comparison pages for important ARMST weapon families."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEAPONS = ROOT / "catalog" / "weapons"
OUT_DIR = ROOT / "reports" / "families"

FILES = {
    "README.md",
    "AK_FAMILY.md",
    "CALIBER_9X39.md",
    "SHOTGUNS.md",
}


def base(value: str | None) -> str:
    return Path(value).name if value else "—"


def value(field):
    return field.get("value") if isinstance(field, dict) else None


def row_from(path: Path) -> dict:
    doc = json.loads(path.read_text(encoding="utf-8"))
    data = doc.get("data") or {}
    mag = data.get("magazine") or {}
    ballistics = data.get("ballistics") or {}
    identity = data.get("identity") or {}
    name_field = identity.get("name")
    name = value(name_field) or (doc.get("identity") or {}).get("name") or doc.get("id") or path.stem

    parent = None
    chain = (doc.get("inheritance") or {}).get("chain") or []
    if len(chain) > 1:
        parent = chain[1].get("resource")
    if not parent:
        parents = (doc.get("inheritance") or {}).get("external_parents") or []
        if parents:
            parent = parents[0].get("path")

    rpms = [
        value(mode.get("rounds_per_minute"))
        for mode in (data.get("fire_modes") or [])
    ]
    rpms = [rpm for rpm in rpms if isinstance(rpm, (int, float))]

    magazine = mag.get("magazine_template")
    magazine_path = magazine.get("path") if isinstance(magazine, dict) else None

    derived = doc.get("derived") or {}

    return {
        "id": doc.get("id") or path.stem,
        "path": path.relative_to(ROOT).as_posix(),
        "name": name,
        "role": doc.get("role") or "unknown",
        "prefab": (doc.get("source") or {}).get("resource"),
        "parent": parent,
        "magwell": (mag.get("magazine_well") or {}).get("class") if isinstance(mag.get("magazine_well"), dict) else None,
        "magazine": magazine_path,
        "rpm": max(rpms) if rpms else None,
        "velocity": value(ballistics.get("bullet_init_speed_coef")),
        "dispersion_diameter": value(ballistics.get("dispersion_diameter")),
        "dispersion_range": value(ballistics.get("dispersion_range")),
        "moa": value(derived.get("approx_moa")),
        "slots": len(data.get("attachment_slots") or []),
        "warnings": len(doc.get("warnings") or []),
    }


def load_rows() -> list[dict]:
    return [row_from(path) for path in sorted(WEAPONS.glob("*.json"))]


def cell(value_) -> str:
    return "—" if value_ is None else str(value_)


def dispersion(row: dict) -> str:
    diameter = row["dispersion_diameter"]
    distance = row["dispersion_range"]
    moa = row["moa"]
    if diameter is None and distance is None:
        return "—"
    parts = []
    if diameter is not None:
        parts.append(f"D={diameter}")
    if distance is not None:
        parts.append(f"R={distance}")
    if moa is not None:
        parts.append(f"{moa} MOA")
    return ", ".join(parts)


def table(rows: list[dict]) -> list[str]:
    out = [
        "| Entry | Role | Parent | Magazine | RPM | Velocity coef | Dispersion | Slots | Warnings |",
        "|---|---|---|---|---:|---:|---|---:|---:|",
    ]
    for row in sorted(rows, key=lambda r: r["id"]):
        out.append(
            f"| [`{row['id']}`](../../{row['path']}) "
            f"| {row['role']} "
            f"| `{base(row['parent'])}` "
            f"| `{base(row['magazine'])}` "
            f"| {cell(row['rpm'])} "
            f"| {cell(row['velocity'])} "
            f"| {dispersion(row)} "
            f"| {row['slots']} "
            f"| {row['warnings']} |"
        )
    return out


def common_values(rows: list[dict], key: str):
    vals = {row[key] for row in rows}
    return next(iter(vals)) if len(vals) == 1 else None


def render_index() -> str:
    return "\n".join([
        "# Weapon family comparison pages",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED SNAPSHOT NAVIGATION.** These pages compare current `catalog/weapons/*.json` data. Live addon / Workbench evidence and `reports/KNOWLEDGE_STATUS.md` remain authoritative.",
        "",
        "- [AK / RPK family](AK_FAMILY.md)",
        "- [9×39 family](CALIBER_9X39.md)",
        "- [Shotguns](SHOTGUNS.md)",
        "",
        "Regenerate all pages with `python agent/scripts/build_weapon_family_pages.py`.",
        "",
    ])


def render_ak(rows: list[dict]) -> str:
    ak = [
        row for row in rows
        if any(part in (row["prefab"] or "") for part in ("/AK74/", "/AKS74U/", "/AKM/"))
        or row["id"] == "armst_rpk74"
    ]
    return "\n".join([
        "# AK / RPK family",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED SNAPSHOT.** Missing values are unresolved/inherited in the current catalog, not zero.",
        "",
        f"Current matching catalog entries: **{len(ak)}**.",
        "",
        "The AK74/AKS74U entries in this snapshot often contain only local overrides, so handling and magazine values may remain blank at this layer. The AKM branch is more fully resolved in the current generated catalog.",
        "",
        "## Current catalog comparison",
        "",
        *table(ak),
        "",
        "## Workbench control related to this family",
        "",
        "The current AEK-971 prototype is **Workbench validated** and is based on `Rifle_AK74N_base.et`, but it is not present in the generated weapon catalog yet.",
        "",
        "- Control: [`armst_AEK971_test_v12_NAME_DESCRIPTION.et`](../samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et)",
        "- Current status: [`KNOWLEDGE_STATUS.md`](../KNOWLEDGE_STATUS.md)",
        "",
        "Do not copy unresolved AK74-family values from names or real-world memory; resolve them from the live primary addon or a refreshed canonical snapshot.",
        "",
    ])


def render_9x39(rows: list[dict]) -> str:
    family = [row for row in rows if "9x39" in (row["magazine"] or "").lower()]
    rpm = common_values(family, "rpm")
    velocity = common_values(family, "velocity")
    diameter = common_values(family, "dispersion_diameter")
    distance = common_values(family, "dispersion_range")
    moa = common_values(family, "moa")
    summary = (
        f"In the current snapshot all {len(family)} matching entries resolve to "
        f"**{rpm} RPM**, velocity coefficient **{velocity}**, dispersion "
        f"**{diameter} / {distance}** and approximately **{moa} MOA**."
        if None not in (rpm, velocity, diameter, distance, moa)
        else "The current snapshot does not resolve one common handling baseline across every 9×39 entry."
    )
    return "\n".join([
        "# 9×39 weapon family",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED SNAPSHOT.** Membership is based on explicit 9×39 magazine paths, not weapon names or folder names.",
        "",
        f"Current matching catalog entries: **{len(family)}**.",
        "",
        summary,
        "",
        "Detailed balance layer: [9×39 balance comparison](../balance/CALIBER_9X39_BALANCE.md).",
        "",
        "## Current catalog comparison",
        "",
        *table(family),
        "",
        "The current catalog shows two magazine-well families: `MagazineWell9x39` and `MagazineWell9x39_9a91`. Treat that compatibility distinction separately from shared ballistic/handling values.",
        "",
        "`Oc_Groza` is intentionally excluded because its current generated magazine path is 7.62×39, despite its location under the VAL source tree.",
        "",
    ])


def render_shotguns(rows: list[dict]) -> str:
    family = [row for row in rows if "/Shotgun/" in (row["prefab"] or "")]
    related = [
        row for row in rows
        if "12ga" in (row["magazine"] or "").lower()
        and row not in family
    ]
    lines = [
        "# Shotguns",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED SNAPSHOT.** The main family table uses the explicit `/Shotgun/` prefab path.",
        "",
        f"Current matching catalog entries: **{len(family)}**.",
        "",
        "All entries in the explicit shotgun branch currently resolve `MagazineWell12g` and the 12 ga buckshot template. A missing RPM or dispersion diameter remains unresolved rather than being treated as zero.",
        "",
        "## Current catalog comparison",
        "",
        *table(family),
    ]
    if related:
        lines.extend([
            "",
            "## Related 12 ga entries outside the shotgun prefab path",
            "",
            "These are not automatically promoted into the shotgun family because their source path does not prove the same prefab family.",
            "",
            *table(related),
        ])
    lines.append("")
    return "\n".join(lines)


def outputs(rows: list[dict]) -> dict[str, str]:
    return {
        "README.md": render_index(),
        "AK_FAMILY.md": render_ak(rows),
        "CALIBER_9X39.md": render_9x39(rows),
        "SHOTGUNS.md": render_shotguns(rows),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    expected = outputs(load_rows())
    if args.check:
        bad = []
        for name, content in expected.items():
            path = OUT_DIR / name
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != content:
                bad.append(name)
        if bad:
            print("Weapon family pages are out of date: " + ", ".join(bad))
            return 1
        print("Weapon family pages are up to date.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in expected.items():
        (OUT_DIR / name).write_text(content, encoding="utf-8")
        print(f"Wrote {OUT_DIR / name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
