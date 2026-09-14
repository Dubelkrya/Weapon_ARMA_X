"""Resolver-v2 catalog pipeline.

This is the integration bridge between resolver_v2 and the existing catalog.
It deliberately writes to a separate output directory until v1/v2 comparison is
clean enough to replace scan_build.py.

No vanilla source trees are exported.  Only semantic resolved values,
provenance, ammo composition, derived metrics, and anomaly summaries are
written.

Example (Windows):

  python agent/scripts/scan_build_v2.py ^
    --armst-root "C:\\...\\ARMST-PLATFORM---Weapons" ^
    --vanilla-root "base=C:\\...\\MaterializedVanilla" ^
    --repo-root .

Environment fallbacks:
  MOD_ROOT           ARMST root
  VANILLA_ROOTS      os.pathsep-separated vanilla/materialized roots
  REPO_ROOT          repository root
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
import re
import shutil
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from resolver_v2 import ResourceRoot
from resolver_v2_configs import HydratedResourceStore
from resolver_v2_extract import classify, extract_semantic


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REPO_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
DEFAULT_MOD_ROOT = (
    r"C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench"
    r"\addons\ARMST-PLATFORM---Weapons"
)


def slugify(relpath: str) -> str:
    stem = re.sub(r"\.et$", "", os.path.basename(relpath), flags=re.I)
    return re.sub(r"[^A-Za-z0-9]+", "_", stem).strip("_").lower() or "entity"


def _path_key(path: str) -> str:
    return path.replace("\\", "/").lstrip("./").casefold()


def _value(obj):
    if isinstance(obj, dict) and "value" in obj:
        return obj.get("value")
    return obj


def _root_spec(raw: str, index: int) -> Tuple[str, str]:
    if "=" in raw:
        label, path = raw.split("=", 1)
        return label.strip() or f"vanilla{index}", path
    return f"vanilla{index}", raw


def roots_from_args(armst_root: str, vanilla_roots: Sequence[str]) -> List[ResourceRoot]:
    roots = [ResourceRoot("armst", armst_root, 100)]
    priority = 50
    for idx, raw in enumerate(vanilla_roots, 1):
        label, path = _root_spec(raw, idx)
        roots.append(ResourceRoot(label, path, priority))
        priority -= 1
    return roots


def build_store(armst_root: str, vanilla_roots: Sequence[str]) -> HydratedResourceStore:
    store = HydratedResourceStore(roots_from_args(armst_root, vanilla_roots))
    store.scan()
    return store


def _fire_mode_snapshot(modes: Iterable[dict]) -> List[dict]:
    out = []
    for mode in modes or []:
        out.append(
            {
                "mode_id": mode.get("mode_id"),
                "ui_name": _value(mode.get("ui_name")),
                "rpm": _value(mode.get("rounds_per_minute")),
                "max_burst": _value(mode.get("max_burst")),
                "max_salvo": _value(mode.get("max_salvo")),
            }
        )
    return out


def _weapon_derived(resolved: dict, ammo: dict) -> dict:
    modes = resolved.get("fire_modes") or []
    rpms = [
        _value(mode.get("rounds_per_minute"))
        for mode in modes
        if isinstance(_value(mode.get("rounds_per_minute")), (int, float))
    ]
    out = {}
    if rpms:
        out["max_rpm"] = max(rpms)
        out["max_rounds_per_second"] = round(max(rpms) / 60.0, 3)

    ballistics = resolved.get("ballistics") or {}
    dd = _value(ballistics.get("dispersion_diameter"))
    dr = _value(ballistics.get("dispersion_range"))
    if isinstance(dd, (int, float)) and isinstance(dr, (int, float)) and dr:
        out["approx_moa"] = round((dd / dr) * 3437.74677, 3)
        out["dispersion_m_per_km"] = round((dd / dr) * 1000.0, 4)

    velocities = ammo.get("effective_muzzle_velocities") if ammo else None
    if velocities:
        out["effective_muzzle_velocities"] = velocities
    return out


def _projectile_velocity(store: HydratedResourceStore, projectile: str, coef) -> dict:
    result = store.projectile_physics(projectile)
    init = (result.get("physics") or {}).get("InitSpeed")
    init_value = _value(init)
    effective = None
    if isinstance(init_value, (int, float)) and isinstance(coef, (int, float)):
        effective = round(init_value * coef, 3)
    return {
        "projectile": projectile,
        "status": result.get("status"),
        "ammo_init_speed": init_value,
        "bullet_init_speed_coef": coef,
        "effective_muzzle_velocity": effective,
        "ai_ballistic_table": result.get("ai_ballistic_table"),
        "ai_ballistic_validation": result.get("ai_ballistic_validation"),
    }


def resolve_weapon_ammo(store: HydratedResourceStore, resolved: dict) -> dict:
    magazine = resolved.get("magazine") or {}
    template = magazine.get("magazine_template")
    if not template:
        return {"status": "missing_magazine_template"}

    ref = store.resolve_ref(template.get("guid"), template.get("path"))
    result = {
        "status": ref.get("status"),
        "magazine_template": template,
        "magazine_target": ref.get("resource"),
    }
    if ref.get("status") != "local" or not ref.get("resource"):
        result["status"] = "external_magazine_template"
        return result

    mag = store.resolve_magazine_ammo(ref["resource"])
    result["magazine"] = mag
    result["status"] = mag.get("status")

    coef = _value((resolved.get("ballistics") or {}).get("bullet_init_speed_coef"))
    velocities = []
    seen = set()
    for row in mag.get("counts") or []:
        projectile = row.get("projectile")
        if not projectile or projectile in seen:
            continue
        seen.add(projectile)
        item = _projectile_velocity(store, projectile, coef)
        item["count"] = row.get("count")
        item["ammo_index"] = row.get("ammo_index")
        velocities.append(item)
    result["effective_muzzle_velocities"] = velocities
    return result


def _entry(store: HydratedResourceStore, relpath: str) -> dict:
    record = store.get(relpath)
    resolution = store.resolve_entity(relpath)
    resolved_tree = resolution.resolved
    classification = classify(resolved_tree, relpath, record.resource.et_class)
    kind = classification["kind"]

    local = extract_semantic(resolution.raw, relpath, record.resource.et_class, kind)
    resolved = extract_semantic(resolved_tree, relpath, record.resource.et_class, kind)
    path_key = _path_key(relpath)

    doc = {
        "schema_version": 2,
        "id": slugify(relpath),
        "source": {
            "resource": relpath,
            "origin": record.origin,
            "class": record.resource.et_class,
            "resource_guid": store.live_guid_by_path.get(path_key),
            "meta_name_guid": store.meta_name_guid_by_path.get(path_key),
        },
        "classification": classification,
        "resolution": {
            "status": resolution.status,
            "chain": resolution.chain,
            "missing_parent": resolution.missing_parent,
        },
        "local": local,
        "resolved": resolved,
        "derived": {},
        "warnings": [],
    }

    if kind == "weapon":
        ammo = resolve_weapon_ammo(store, resolved)
        doc["ammo_resolution"] = ammo
        doc["derived"] = _weapon_derived(resolved, ammo)
    elif kind == "magazine":
        ammo = store.resolve_magazine_ammo(relpath)
        doc["ammo_resolution"] = ammo
        capacity = _value(resolved.get("max_ammo"))
        doc["derived"] = {
            "capacity": capacity,
            "ammo_composition": ammo.get("counts") or [],
        }
        doc["warnings"].extend(ammo.get("warnings") or [])
    elif kind == "ammunition":
        projectile = store.projectile_physics(relpath)
        doc["projectile_resolution"] = projectile
        validation = projectile.get("ai_ballistic_validation") or {}
        if validation.get("severity") == "warning":
            doc["warnings"].append(
                {"category": "AI_BALLISTIC_TABLE", **validation}
            )
    return doc


def build_documents(store: HydratedResourceStore, origin: str = "armst") -> Dict[str, dict]:
    docs = {}
    for record in sorted(store.records.values(), key=lambda r: r.relpath.lower()):
        if record.origin != origin or record.kind != "et":
            continue
        docs[record.relpath] = _entry(store, record.relpath)

    # Role is computed only among exported ARMST entities.  Vanilla resources
    # participate in resolution but are not mirrored into the public catalog.
    used_as_base = Counter()
    for doc in docs.values():
        for node in (doc.get("resolution") or {}).get("chain", [])[1:]:
            resource = node.get("resource")
            if resource in docs:
                used_as_base[resource] += 1
    for relpath, doc in docs.items():
        doc["role"] = "base" if used_as_base[relpath] else "leaf"
    return docs


def _plural(kind: str) -> str:
    return {
        "weapon": "weapons",
        "magazine": "magazines",
        "ammunition": "ammunition",
        "optic": "optics",
        "attachment": "attachments",
        "grenade": "grenades",
        "core": "core",
    }.get(kind, "misc")


def _provenance_free(value):
    if isinstance(value, list):
        return [_provenance_free(v) for v in value]
    if not isinstance(value, dict):
        return value
    if "value" in value and set(value).intersection({"defined_in", "origin", "inherited"}):
        return _provenance_free(value.get("value"))
    return {
        key: _provenance_free(val)
        for key, val in value.items()
        if key not in {"defined_in", "origin", "inherited", "status"}
    }


def _v2_snapshot(doc: dict) -> dict:
    kind = (doc.get("classification") or {}).get("kind")
    resolved = doc.get("resolved") or {}
    if kind == "weapon":
        return _provenance_free(
            {
                "physical": resolved.get("physical"),
                "fire_modes": _fire_mode_snapshot(resolved.get("fire_modes") or []),
                "magazine": resolved.get("magazine"),
                "ballistics": resolved.get("ballistics"),
                "recoil": resolved.get("recoil"),
            }
        )
    if kind == "magazine":
        return _provenance_free(
            {
                "magazine_well": resolved.get("magazine_well"),
                "max_ammo": resolved.get("max_ammo"),
                "ammo_config": resolved.get("ammo_config"),
                "ammo_mapping": resolved.get("ammo_mapping"),
                "physical": resolved.get("physical"),
                "weight_per_ammo": resolved.get("weight_per_ammo"),
            }
        )
    if kind == "ammunition":
        return _provenance_free(
            {
                "physics": resolved.get("physics"),
                "ai_ballistic_table": resolved.get("ai_ballistic_table"),
                "damage_effects": resolved.get("damage_effects"),
            }
        )
    return {}


def _v1_snapshot(doc: dict) -> dict:
    kind = (doc.get("classification") or {}).get("kind")
    data = doc.get("data") or {}
    if kind == "weapon":
        return _provenance_free(
            {
                "physical": data.get("physical"),
                "fire_modes": _fire_mode_snapshot(data.get("fire_modes") or []),
                "magazine": data.get("magazine"),
                "ballistics": data.get("ballistics"),
                "recoil": (data.get("aim") or {}).get("recoil"),
            }
        )
    if kind == "magazine":
        return _provenance_free(
            {
                "magazine_well": data.get("magazine_well"),
                "max_ammo": data.get("max_ammo"),
                "ammo_config": data.get("ammo_config"),
                "ammo_mapping": data.get("ammo_mapping"),
                "physical": {"Weight": data.get("weight")},
            }
        )
    if kind == "ammunition":
        shell = data.get("shell") or {}
        physics = {
            key: shell.get(key)
            for key in (
                "InitSpeed", "InitSpeedVariation", "DispersionMultiplier", "Mass",
                "TumblingDamageMultiplier", "MushroomingDamageMultiplier",
                "PenetrationDepth", "PenetrationSpeed", "PenetrationDensity", "AirDrag",
            )
        }
        return _provenance_free(
            {
                "physics": physics,
                "ai_ballistic_table": shell.get("ballistic_table"),
                "damage_effects": data.get("effects"),
            }
        )
    return {}


def _flatten(value, prefix="") -> dict:
    out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            next_prefix = f"{prefix}.{key}" if prefix else str(key)
            out.update(_flatten(item, next_prefix))
    elif isinstance(value, list):
        for idx, item in enumerate(value):
            out.update(_flatten(item, f"{prefix}[{idx}]"))
        if not value:
            out[prefix] = []
    else:
        out[prefix] = value
    return out


def compare_with_v1(repo_root: str, docs: Dict[str, dict]) -> dict:
    rows = []
    compared = 0
    for relpath, doc in docs.items():
        kind = (doc.get("classification") or {}).get("kind")
        old_path = os.path.join(repo_root, "catalog", _plural(kind), slugify(relpath) + ".json")
        if not os.path.isfile(old_path):
            continue
        try:
            with open(old_path, "r", encoding="utf-8") as handle:
                old = json.load(handle)
        except Exception as exc:  # noqa: BLE001
            rows.append({"resource": relpath, "category": "V1_READ", "message": str(exc)})
            continue
        compared += 1
        before = _flatten(_v1_snapshot(old))
        after = _flatten(_v2_snapshot(doc))
        for path in sorted(set(before) | set(after)):
            if before.get(path) == after.get(path):
                continue
            rows.append(
                {
                    "resource": relpath,
                    "kind": kind,
                    "path": path,
                    "v1": before.get(path),
                    "v2": after.get(path),
                }
            )
    return {"compared_entities": compared, "difference_count": len(rows), "differences": rows}


def collect_anomalies(store: HydratedResourceStore, docs: Dict[str, dict]) -> List[dict]:
    out = list(store.warnings)
    for relpath, doc in docs.items():
        for warning in doc.get("warnings") or []:
            out.append({"resource": relpath, **warning})
    return out


def write_outputs(repo_root: str, output_root: str, docs: Dict[str, dict], store: HydratedResourceStore) -> dict:
    if os.path.isdir(output_root):
        shutil.rmtree(output_root)
    os.makedirs(output_root, exist_ok=True)

    catalog_root = os.path.join(output_root, "catalog")
    index_root = os.path.join(output_root, "indexes")
    report_root = os.path.join(output_root, "reports")
    os.makedirs(index_root, exist_ok=True)
    os.makedirs(report_root, exist_ok=True)

    indexes: Dict[str, List[dict]] = {}
    for relpath, doc in docs.items():
        plural = _plural((doc.get("classification") or {}).get("kind"))
        directory = os.path.join(catalog_root, plural)
        os.makedirs(directory, exist_ok=True)
        with open(os.path.join(directory, slugify(relpath) + ".json"), "w", encoding="utf-8") as handle:
            json.dump(doc, handle, indent=2, ensure_ascii=False)
        indexes.setdefault(plural, []).append(
            {
                "id": doc["id"],
                "resource": relpath,
                "class": (doc.get("source") or {}).get("class"),
                "role": doc.get("role"),
                "resolution_status": (doc.get("resolution") or {}).get("status"),
            }
        )

    for name, rows in indexes.items():
        with open(os.path.join(index_root, name + ".json"), "w", encoding="utf-8") as handle:
            json.dump(rows, handle, indent=2, ensure_ascii=False)

    diff = compare_with_v1(repo_root, docs)
    anomalies = collect_anomalies(store, docs)
    counts = Counter((doc.get("classification") or {}).get("kind") for doc in docs.values())
    statuses = Counter((doc.get("resolution") or {}).get("status") for doc in docs.values())
    summary = {
        "schema_version": 2,
        "entities": len(docs),
        "counts_by_kind": dict(counts),
        "resolution_status": dict(statuses),
        "resolver_warnings": len(store.warnings),
        "anomalies": len(anomalies),
        "v1_v2_compared_entities": diff["compared_entities"],
        "v1_v2_difference_count": diff["difference_count"],
    }

    for filename, payload in (
        ("scan_summary_v2.json", summary),
        ("resolver_v2_diff.json", diff),
        ("anomalies_v2.json", anomalies),
    ):
        with open(os.path.join(report_root, filename), "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, ensure_ascii=False)

    with open(os.path.join(report_root, "scan_summary_v2.md"), "w", encoding="utf-8") as handle:
        handle.write("# Resolver v2 scan summary\n\n")
        handle.write(f"- Entities: {summary['entities']}\n")
        handle.write(f"- Resolution: `{summary['resolution_status']}`\n")
        handle.write(f"- Resolver warnings: {summary['resolver_warnings']}\n")
        handle.write(f"- Anomalies: {summary['anomalies']}\n")
        handle.write(f"- Compared with v1: {summary['v1_v2_compared_entities']} entities\n")
        handle.write(f"- v1/v2 differing fields: {summary['v1_v2_difference_count']}\n")

    with open(os.path.join(report_root, "resolver_v2_diff.md"), "w", encoding="utf-8") as handle:
        handle.write("# Resolver v1 → v2 differences\n\n")
        handle.write(f"Compared entities: {diff['compared_entities']}\n\n")
        handle.write(f"Differing fields: {diff['difference_count']}\n\n")
        for row in diff["differences"][:500]:
            handle.write(
                f"- `{row.get('resource')}` `{row.get('path')}`: "
                f"v1=`{row.get('v1')}` → v2=`{row.get('v2')}`\n"
            )
        if diff["difference_count"] > 500:
            handle.write("\nFull diff is in `resolver_v2_diff.json`.\n")

    return summary


def _env_vanilla_roots() -> List[str]:
    raw = os.environ.get("VANILLA_ROOTS", "")
    return [item for item in raw.split(os.pathsep) if item]


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build ARMST catalog with resolver v2")
    parser.add_argument("--armst-root", default=os.environ.get("MOD_ROOT", DEFAULT_MOD_ROOT))
    parser.add_argument(
        "--vanilla-root",
        action="append",
        default=None,
        help="Materialized/base resource root, optionally label=path. Repeatable.",
    )
    parser.add_argument("--repo-root", default=os.environ.get("REPO_ROOT", DEFAULT_REPO_ROOT))
    parser.add_argument("--output-root", default=None)
    args = parser.parse_args(argv)

    repo_root = os.path.abspath(args.repo_root)
    vanilla_roots = args.vanilla_root if args.vanilla_root is not None else _env_vanilla_roots()
    output_root = os.path.abspath(
        args.output_root or os.path.join(repo_root, "agent", "v2_output")
    )

    store = build_store(os.path.abspath(args.armst_root), vanilla_roots)
    docs = build_documents(store)
    summary = write_outputs(repo_root, output_root, docs, store)

    print(json.dumps({"output_root": output_root, **summary}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
