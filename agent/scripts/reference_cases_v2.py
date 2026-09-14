"""Build a compact human-review report for known ARMST weapon families.

The full resolver-v2 catalog is intentionally verbose.  This script extracts a
small set of reference cases that we have manually inspected during resolver
development so a real Workbench scan can be checked quickly before v2 replaces
the legacy catalog.

It reads only generated semantic JSON from `agent/v2_output/catalog`; no raw
vanilla resources are copied or emitted.
"""

from __future__ import annotations

import argparse
import json
import os
from typing import Dict, Iterable, List, Optional, Sequence


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


DEFAULT_CASES = (
    "armst_ak74",
    "armst_ak105",
    "armst_ak74n",
    "armst_ak74m",
    "armst_aks74u",
    "armst_aks74un",
    "rifle_vss",
    "rifle_val",
    "rifle_vsk94",
    "rifle_9a91",
    "armst_svd",
    "armst_vz58p",
    "armst_vz58v",
    "armst_pkm",
    "armst_rpk74",
    "rifle_m16a2",
    "rifle_m16a2_carbine",
    "shotgun_base",
)


def _value(value):
    return value.get("value") if isinstance(value, dict) and "value" in value else value


def _source(value):
    if not isinstance(value, dict):
        return None
    return value.get("defined_in")


def _load_documents(catalog_root: str) -> Dict[str, dict]:
    docs: Dict[str, dict] = {}
    if not os.path.isdir(catalog_root):
        return docs
    for dirpath, _dirs, filenames in os.walk(catalog_root):
        for filename in filenames:
            if not filename.lower().endswith(".json"):
                continue
            path = os.path.join(dirpath, filename)
            try:
                with open(path, "r", encoding="utf-8") as handle:
                    doc = json.load(handle)
            except (OSError, json.JSONDecodeError):
                continue
            entity_id = doc.get("id")
            if entity_id:
                docs[str(entity_id)] = doc
    return docs


def _fire_modes(doc: dict) -> List[dict]:
    modes = ((doc.get("resolved") or {}).get("fire_modes") or [])
    out = []
    for mode in modes:
        out.append(
            {
                "mode_id": mode.get("mode_id"),
                "name": _value(mode.get("ui_name")),
                "rpm": _value(mode.get("rounds_per_minute")),
                "max_burst": _value(mode.get("max_burst")),
                "defined_in": mode.get("defined_in"),
            }
        )
    return out


def _recoil_summary(doc: dict) -> dict:
    recoil = ((doc.get("resolved") or {}).get("recoil") or {})
    out = {}
    for key in ("linear", "angular", "turn_offset"):
        data = recoil.get(key) or {}
        if not data:
            continue
        out[key] = {
            "magnitudes": _value(data.get("curve_magnitudes")),
            "mins": _value(data.get("curve_mins")),
            "maxs": _value(data.get("curve_maxs")),
            "time_scale": _value(data.get("curve_time_scale")),
            "base_scale": _value(data.get("base_recoil_scale")),
            "defined_in": data.get("defined_in"),
        }
    return out


def summarize(doc: dict) -> dict:
    resolved = doc.get("resolved") or {}
    physical = resolved.get("physical") or {}
    ballistics = resolved.get("ballistics") or {}
    magazine = resolved.get("magazine") or {}
    ammo_resolution = doc.get("ammo_resolution") or {}
    mag_resolution = ammo_resolution.get("magazine") or {}
    derived = doc.get("derived") or {}
    resolution = doc.get("resolution") or {}

    chain = [
        {
            "resource": row.get("resource"),
            "origin": row.get("origin"),
            "live_guid": row.get("live_guid"),
        }
        for row in resolution.get("chain") or []
    ]

    velocities = []
    for row in derived.get("effective_muzzle_velocities") or []:
        velocities.append(
            {
                "projectile": row.get("projectile"),
                "count": row.get("count"),
                "ammo_index": row.get("ammo_index"),
                "init_speed": row.get("ammo_init_speed"),
                "coefficient": row.get("bullet_init_speed_coef"),
                "effective_muzzle_velocity": row.get("effective_muzzle_velocity"),
                "aibt_status": (row.get("ai_ballistic_validation") or {}).get("status"),
            }
        )

    template = magazine.get("magazine_template") or {}
    return {
        "id": doc.get("id"),
        "resource": (doc.get("source") or {}).get("resource"),
        "status": resolution.get("status"),
        "missing_parent": resolution.get("missing_parent"),
        "chain": chain,
        "weight": _value(physical.get("Weight")),
        "weight_defined_in": _source(physical.get("Weight")),
        "volume": _value(physical.get("ItemVolume")),
        "volume_defined_in": _source(physical.get("ItemVolume")),
        "melee_damage": _value(physical.get("MeleeDamage")),
        "melee_defined_in": _source(physical.get("MeleeDamage")),
        "fire_modes": _fire_modes(doc),
        "bullet_init_speed_coef": _value(ballistics.get("bullet_init_speed_coef")),
        "bullet_init_speed_coef_defined_in": _source(ballistics.get("bullet_init_speed_coef")),
        "dispersion_diameter": _value(ballistics.get("dispersion_diameter")),
        "dispersion_range": _value(ballistics.get("dispersion_range")),
        "approx_moa": derived.get("approx_moa"),
        "magazine_template": template.get("path"),
        "magazine_template_defined_in": template.get("defined_in"),
        "magazine_status": mag_resolution.get("status") or ammo_resolution.get("status"),
        "magazine_capacity": _value(mag_resolution.get("max_ammo")),
        "ammo_composition": mag_resolution.get("counts") or [],
        "effective_muzzle_velocities": velocities,
        "recoil": _recoil_summary(doc),
        "warnings": doc.get("warnings") or [],
    }


def build_report(catalog_root: str, cases: Iterable[str]) -> dict:
    docs = _load_documents(catalog_root)
    requested = list(cases)
    found = []
    missing = []
    for entity_id in requested:
        doc = docs.get(entity_id)
        if doc is None:
            missing.append(entity_id)
        else:
            found.append(summarize(doc))
    return {
        "requested": len(requested),
        "found": len(found),
        "missing": missing,
        "cases": found,
    }


def _fmt(value) -> str:
    if value is None:
        return "—"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def write_report(report: dict, report_root: str) -> None:
    os.makedirs(report_root, exist_ok=True)
    json_path = os.path.join(report_root, "reference_cases_v2.json")
    md_path = os.path.join(report_root, "reference_cases_v2.md")
    with open(json_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)

    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write("# Resolver v2 reference cases\n\n")
        handle.write(f"- Requested: {report['requested']}\n")
        handle.write(f"- Found: {report['found']}\n")
        if report["missing"]:
            handle.write("- Missing IDs: " + ", ".join(f"`{x}`" for x in report["missing"]) + "\n")
        handle.write("\n")
        for case in report["cases"]:
            handle.write(f"## {case['id']}\n\n")
            handle.write(f"- Resource: `{case['resource']}`\n")
            handle.write(f"- Resolution: `{case['status']}`\n")
            handle.write(f"- Weight / volume / melee: `{_fmt(case['weight'])}` / `{_fmt(case['volume'])}` / `{_fmt(case['melee_damage'])}`\n")
            handle.write(f"- Fire modes: `{_fmt(case['fire_modes'])}`\n")
            handle.write(f"- BulletInitSpeedCoef: `{_fmt(case['bullet_init_speed_coef'])}`\n")
            handle.write(f"- Dispersion: `{_fmt(case['dispersion_diameter'])}` @ `{_fmt(case['dispersion_range'])}`; MOA `{_fmt(case['approx_moa'])}`\n")
            handle.write(f"- Magazine: `{_fmt(case['magazine_template'])}`; capacity `{_fmt(case['magazine_capacity'])}`; status `{_fmt(case['magazine_status'])}`\n")
            handle.write(f"- Ammo composition: `{_fmt(case['ammo_composition'])}`\n")
            handle.write(f"- Muzzle velocity: `{_fmt(case['effective_muzzle_velocities'])}`\n")
            handle.write(f"- Recoil: `{_fmt(case['recoil'])}`\n")
            if case["missing_parent"]:
                handle.write(f"- Missing parent: `{_fmt(case['missing_parent'])}`\n")
            if case["warnings"]:
                handle.write(f"- Warnings: `{_fmt(case['warnings'])}`\n")
            handle.write("\n")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build compact resolver-v2 reference-case report")
    parser.add_argument("--output-root", default=os.path.join(os.path.dirname(SCRIPT_DIR), "v2_output"))
    parser.add_argument("--case", action="append", default=None, help="Entity id to include. Repeatable.")
    args = parser.parse_args(argv)

    output_root = os.path.abspath(args.output_root)
    catalog_root = os.path.join(output_root, "catalog")
    report_root = os.path.join(output_root, "reports")
    report = build_report(catalog_root, args.case or DEFAULT_CASES)
    write_report(report, report_root)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["found"] else 2


if __name__ == "__main__":
    raise SystemExit(main())