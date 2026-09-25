#!/usr/bin/env python3
"""Build evidence-preserving balance comparison pages for Weapon_ARMA_X.

The generator never infers gameplay values from weapon/ammo filenames. It joins
records only through explicit source.resource paths or catalog fields.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WEAPONS = ROOT / "catalog" / "weapons"
MAGAZINES = ROOT / "catalog" / "magazines"
AMMUNITION = ROOT / "catalog" / "ammunition"
OUT_DIR = ROOT / "reports" / "balance"


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def field_value(value):
    return value.get("value") if isinstance(value, dict) else None


def basename(value: str | None) -> str:
    return Path(value).name if value else "—"


def load_by_resource(directory: Path) -> dict[str, dict]:
    result = {}
    for path in directory.glob("*.json"):
        doc = read_json(path)
        resource = (doc.get("source") or {}).get("resource")
        if resource:
            result[resource] = {"doc": doc, "path": path}
    return result


def max_rpm(data: dict):
    values = []
    for mode in data.get("fire_modes") or []:
        rpm = field_value(mode.get("rounds_per_minute"))
        if isinstance(rpm, (int, float)):
            values.append(rpm)
    return max(values) if values else None


def weapon_rows() -> list[dict]:
    magazines = load_by_resource(MAGAZINES)
    rows = []
    for path in sorted(WEAPONS.glob("*.json")):
        doc = read_json(path)
        data = doc.get("data") or {}
        mag_field = ((data.get("magazine") or {}).get("magazine_template") or {})
        mag_resource = mag_field.get("path")
        if "9x39" not in (mag_resource or "").lower():
            continue

        mag_entry = magazines.get(mag_resource)
        mag_doc = mag_entry["doc"] if mag_entry else {}
        mag_data = mag_doc.get("data") or {}
        capacity = field_value(mag_data.get("max_ammo"))
        if capacity is None:
            capacity = (mag_doc.get("derived") or {}).get("capacity")

        ballistics = data.get("ballistics") or {}
        rows.append(
            {
                "id": doc.get("id") or path.stem,
                "path": path.relative_to(ROOT).as_posix(),
                "role": doc.get("role") or "unknown",
                "magazine": mag_resource,
                "capacity": capacity,
                "magwell": ((data.get("magazine") or {}).get("magazine_well") or {}).get("class"),
                "rpm": max_rpm(data),
                "velocity_coef": field_value(ballistics.get("bullet_init_speed_coef")),
                "dispersion_diameter": field_value(ballistics.get("dispersion_diameter")),
                "dispersion_range": field_value(ballistics.get("dispersion_range")),
                "moa": ((doc.get("derived") or {}).get("approx_moa") or {}).get("value"),
                "warnings": len(doc.get("warnings") or []),
            }
        )
    return rows


def projectile_rows() -> list[dict]:
    rows = []
    for path in sorted(AMMUNITION.glob("*.json")):
        doc = read_json(path)
        resource = (doc.get("source") or {}).get("resource") or ""
        if "ammo_9x39_" not in resource.lower():
            continue
        data = doc.get("data") or {}
        shell = data.get("shell") or {}
        damage = None
        for effect in data.get("effects") or []:
            if effect.get("type") == "ProjectileDamage":
                damage = field_value(effect.get("DamageValue"))
                break
        rows.append(
            {
                "id": doc.get("id") or path.stem,
                "path": path.relative_to(ROOT).as_posix(),
                "resource": resource,
                "init_speed": field_value(shell.get("InitSpeed")),
                "mass": field_value(shell.get("Mass")),
                "air_drag": field_value(shell.get("AirDrag")),
                "dispersion_multiplier": field_value(shell.get("DispersionMultiplier")),
                "damage": damage,
                "penetration_depth": field_value(shell.get("PenetrationDepth")),
                "penetration_speed": field_value(shell.get("PenetrationSpeed")),
                "ballistic_table": (shell.get("ballistic_table") or {}).get("path"),
                "warnings": len(doc.get("warnings") or []),
            }
        )
    return rows


def magazine_rows() -> list[dict]:
    rows = []
    for path in sorted(MAGAZINES.glob("*.json")):
        doc = read_json(path)
        resource = (doc.get("source") or {}).get("resource") or ""
        if "9x39" not in resource.lower():
            continue
        data = doc.get("data") or {}
        capacity = field_value(data.get("max_ammo"))
        if capacity is None:
            capacity = (doc.get("derived") or {}).get("capacity")
        rows.append(
            {
                "id": doc.get("id") or path.stem,
                "path": path.relative_to(ROOT).as_posix(),
                "resource": resource,
                "capacity": capacity,
                "magwell": (data.get("magazine_well") or {}).get("class"),
                "ammo_config": (data.get("ammo_config") or {}).get("path"),
                "mapping_count": len(data.get("ammo_mapping") or []),
                "caliber_id": field_value(data.get("caliber_id")),
                "warnings": len(doc.get("warnings") or []),
            }
        )
    return rows


def text(value) -> str:
    return "—" if value is None else str(value)


def render_readme() -> str:
    return "\n".join([
        "# Balance comparison reports",
        "",
        "> [!NOTE]",
        "> **Status: GENERATED ANALYSIS.** These reports compare repository snapshot values; they do not change gameplay balance and do not replace Workbench/runtime validation.",
        "",
        "- [9×39 balance comparison](CALIBER_9X39_BALANCE.md)",
        "- [Catalog data-quality findings](../DATA_QUALITY.md)",
        "",
        "Regenerate with `python agent/scripts/build_balance_pages.py`.",
        "",
    ])


def render_9x39() -> str:
    weapons = weapon_rows()
    projectiles = projectile_rows()
    mags = magazine_rows()

    lines = [
        "# 9×39 balance comparison",
        "",
        "> [!IMPORTANT]",
        "> **Status: GENERATED ANALYSIS / NOT A BALANCE POLICY.** Values come from the current checked-in catalog. Unknown values remain unknown. No projectile is assigned to a magazine from its filename.",
        "",
        "This report keeps three evidence layers separate: weapon handling, magazine capacity/compatibility, and projectile lethality/penetration.",
        "",
        "## Weapon handling",
        "",
        "| Weapon entry | Role | Magazine | Capacity | Mag well | RPM | Velocity coef | Dispersion | Warnings |",
        "|---|---|---|---:|---|---:|---:|---|---:|",
    ]

    for row in sorted(weapons, key=lambda x: x["id"]):
        disp = "—"
        if row["dispersion_diameter"] is not None or row["dispersion_range"] is not None:
            parts = []
            if row["dispersion_diameter"] is not None:
                parts.append(f"D={row['dispersion_diameter']}")
            if row["dispersion_range"] is not None:
                parts.append(f"R={row['dispersion_range']}")
            if row["moa"] is not None:
                parts.append(f"{row['moa']} MOA")
            disp = ", ".join(parts)
        lines.append(
            f"| [`{row['id']}`](../../{row['path']}) | {row['role']} "
            f"| `{basename(row['magazine'])}` | {text(row['capacity'])} "
            f"| `{text(row['magwell'])}` | {text(row['rpm'])} "
            f"| {text(row['velocity_coef'])} | {disp} | {row['warnings']} |"
        )

    lines.extend([
        "",
        "### Handling snapshot",
        "",
        "The handling rows above are generated from the current catalog. Capacity is shown only when the linked magazine catalog resolves it; RPM, velocity coefficient and dispersion remain per-entry evidence rather than family-wide assumptions.",
        "",
        "## Magazine layer",
        "",
        "| Magazine | Capacity | Mag well | AmmoConfig | AmmoMapping entries | Caliber ID | Warnings |",
        "|---|---:|---|---|---:|---|---:|",
    ])
    for row in sorted(mags, key=lambda x: x["id"]):
        lines.append(
            f"| [`{basename(row['resource'])}`](../../{row['path']}) "
            f"| {text(row['capacity'])} | `{text(row['magwell'])}` "
            f"| `{basename(row['ammo_config'])}` | {row['mapping_count']} "
            f"| `{text(row['caliber_id'])}` | {row['warnings']} |"
        )

    lines.extend([
        "",
        "> [!NOTE]",
        "> AmmoMapping entry counts and capacities above come from the current catalog. The generator does not infer projectile identity or capacity from magazine filenames; caliber IDs are shown verbatim from resolved source evidence.",
        "",
        "> [!NOTE]",
        "> A derived capacity is shown only when the catalog has source-backed evidence (for example, serialized AmmoMapping length when MaxAmmo is absent). Mapping indices must be interpreted through the resolved AmmoConfig resource list.",
        "",
        "## Projectile layer",
        "",
        "| Projectile | Init speed | Mass | Damage | Penetration depth | Penetration speed | Air drag | Dispersion mult | Ballistic table | Warnings |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|---:|",
    ])
    for row in sorted(projectiles, key=lambda x: x["id"]):
        lines.append(
            f"| [`{basename(row['resource'])}`](../../{row['path']}) "
            f"| {text(row['init_speed'])} | {text(row['mass'])} "
            f"| {text(row['damage'])} | {text(row['penetration_depth'])} "
            f"| {text(row['penetration_speed'])} | {text(row['air_drag'])} "
            f"| {text(row['dispersion_multiplier'])} "
            f"| `{basename(row['ballistic_table'])}` | {row['warnings']} |"
        )

    lines.extend([
        "",
        "### What the current projectile snapshot actually proves",
        "",
    ])
    for row in sorted(projectiles, key=lambda x: x["id"]):
        lines.append(
            f"- `{basename(row['resource'])}`: InitSpeed={text(row['init_speed'])}, "
            f"Mass={text(row['mass'])}, Damage={text(row['damage'])}, "
            f"PenetrationDepth={text(row['penetration_depth'])}, "
            f"PenetrationSpeed={text(row['penetration_speed'])}, "
            f"AirDrag={text(row['air_drag'])}, "
            f"BallisticTable=`{basename(row['ballistic_table'])}`."
        )

    lines.extend([
        "",
        "## Authority boundary",
        "",
        "The older `indexes/ammunition_reference/part-06.json` contains different 9×39 SP5/SP6 resources from `Weapons.zip` (`Ammo_9x39_Ball_SP5.et` / `Ammo_9x39_AP_SP6.et`) with different penetration values. Those older reference rows are useful historical/source evidence but must not be merged into the current ARMST projectile rows as if they were the same resources.",
        "",
        "Before making balance changes, use the current generated AmmoConfig resource list together with serialized magazine AmmoMapping evidence, then validate one projectile/magazine family at a time in Workbench.",
        "",
    ])
    return "\n".join(lines)


def outputs() -> dict[str, str]:
    return {
        "README.md": render_readme(),
        "CALIBER_9X39_BALANCE.md": render_9x39(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    expected = outputs()

    if args.check:
        stale = []
        for name, content in expected.items():
            path = OUT_DIR / name
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != content:
                stale.append(name)
        if stale:
            print("Balance pages are out of date: " + ", ".join(stale))
            return 1
        print("Balance pages are up to date.")
        return 0

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    for name, content in expected.items():
        path = OUT_DIR / name
        path.write_text(content, encoding="utf-8")
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
