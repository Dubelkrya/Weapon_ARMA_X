"""Probe the v2 resolver against real Workbench resource roots.

This is a non-destructive bridge between resolver_v2 and the legacy
scan_build.py exporter. It prints/writes derived JSON only; it does not copy or
commit vanilla source files.

Example (PowerShell):

  python agent/scripts/scan_v2_probe.py `
    --armst-root "C:\...\ARMST-PLATFORM---Weapons" `
    --root "vanilla=10=C:\...\MaterializedVanilla" `
    --resource "Prefabs/Weapons/Rifles/armst_SVD.et" `
    --resource "Prefabs/Weapons/Magazines/Magazine_762x54_SVD_10rnd_Sniper.et"
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
import os
from typing import Optional, Sequence

from resolver_v2 import (
    RNode,
    ResourceRoot,
    array_values_r,
    find_child_r,
    find_recursive_r,
    scalar_r,
)
from resolver_v2_configs import HydratedResourceStore


def _pval(node: Optional[RNode]):
    if node is None:
        return None
    return {
        "value": scalar_r(node),
        "defined_in": node.defined_in,
        "origin": node.origin,
    }


def _pref(node: Optional[RNode]):
    if node is None or node.ref is None:
        return None
    return {
        "guid": node.ref.get("guid"),
        "path": node.ref.get("path"),
        "defined_in": node.defined_in,
        "origin": node.origin,
    }


def _first(root: Optional[RNode], name: str) -> Optional[RNode]:
    nodes = find_recursive_r(root, name)
    return nodes[0] if nodes else None


def _physical(root: RNode) -> dict:
    attrs = _first(root, "ItemPhysAttributes")
    fields = {}
    if attrs is not None:
        owner = attrs
        # Older parser/extractor assumptions expected an extra wrapper. Real
        # vanilla resources frequently place Weight/ItemVolume directly under
        # ItemPhysAttributes, so direct children are preferred.
        if not any(find_child_r(owner, key) is not None for key in ("Weight", "ItemVolume")):
            if owner.children:
                owner = owner.children[0]
        for key in ("Weight", "ItemVolume", "ItemDimensions", "DimensionScaler"):
            node = find_child_r(owner, key)
            if node is not None:
                if len(node.value) > 1:
                    fields[key] = {
                        "value": list(node.value),
                        "defined_in": node.defined_in,
                        "origin": node.origin,
                    }
                else:
                    fields[key] = _pval(node)

    melee = _first(root, "SCR_MeleeWeaponProperties")
    if melee is not None:
        fields["MeleeDamage"] = _pval(find_child_r(melee, "m_fDamage"))
    return fields


def _fire_modes(root: RNode) -> list:
    block = _first(root, "FireModes")
    if block is None:
        return []
    out = []
    for mode in block.children:
        if mode.name != "BaseFireMode":
            continue
        out.append(
            {
                "instance_id": mode.id,
                "template": _pref(mode),
                "ui_name": _pval(find_child_r(mode, "UIName")),
                "rounds_per_minute": _pval(find_child_r(mode, "RoundsPerMinute")),
                "max_burst": _pval(find_child_r(mode, "MaxBurst")),
                "max_salvo": _pval(find_child_r(mode, "MaxSalvo")),
                "defined_in": mode.defined_in,
                "origin": mode.origin,
            }
        )
    return out


def _recoil(root: RNode):
    recoil = _first(root, "RecoilWeaponAimModifier")
    if recoil is None:
        return None
    out = {
        "template": _pref(recoil),
        "defined_in": recoil.defined_in,
        "origin": recoil.origin,
    }
    for section in ("LinearData", "AngularData", "TurnOffsetData"):
        data = find_child_r(recoil, section)
        if data is None:
            out[section] = None
            continue
        values = {}
        for key in (
            "Curve Magnitudes",
            "Curve Mins",
            "Curve Maxs",
            "Curve Time Scale",
            "Base Recoil Scale",
            "Deployment Multiplier",
            "Bipod Deployment Multiplier",
        ):
            node = find_child_r(data, key)
            if node is not None:
                values[key] = {
                    "value": list(node.value),
                    "defined_in": node.defined_in,
                    "origin": node.origin,
                }
        out[section] = values
    return out


def _weapon_summary(store: HydratedResourceStore, relpath: str, root: RNode) -> dict:
    muzzle = _first(root, "MuzzleComponent")
    mag_well = find_child_r(muzzle, "MagazineWell") if muzzle else None
    mag_template = find_child_r(muzzle, "MagazineTemplate") if muzzle else None
    return {
        "kind": "weapon",
        "physical": _physical(root),
        "fire_modes": _fire_modes(root),
        "muzzle": {
            "bullet_init_speed_coef": _pval(find_child_r(muzzle, "BulletInitSpeedCoef")) if muzzle else None,
            "dispersion_diameter": _pval(find_child_r(muzzle, "DispersionDiameter")) if muzzle else None,
            "dispersion_range": _pval(find_child_r(muzzle, "DispersionRange")) if muzzle else None,
            "magazine_well": {
                "class": mag_well.type,
                "instance_id": mag_well.id,
                "defined_in": mag_well.defined_in,
                "origin": mag_well.origin,
            } if mag_well else None,
            "magazine_template": _pref(mag_template),
        },
        "recoil": _recoil(root),
    }


def _kind(root: RNode) -> str:
    if find_recursive_r(root, "WeaponComponent"):
        return "weapon"
    if find_recursive_r(root, "MagazineComponent"):
        return "magazine"
    if find_recursive_r(root, "ShellMoveComponent"):
        return "projectile"
    return "entity"


def summarize(store: HydratedResourceStore, relpath: str) -> dict:
    resolved = store.resolve_entity(relpath)
    out = {
        "resource": relpath,
        "resolution_status": resolved.status,
        "chain": resolved.chain,
        "missing_parent": resolved.missing_parent,
    }
    if resolved.resolved is None:
        return out

    kind = _kind(resolved.resolved)
    if kind == "weapon":
        out["data"] = _weapon_summary(store, relpath, resolved.resolved)
    elif kind == "magazine":
        out["data"] = {
            "kind": "magazine",
            "ammo": store.resolve_magazine_ammo(relpath),
        }
    elif kind == "projectile":
        out["data"] = {
            "kind": "projectile",
            "ballistics": store.projectile_physics(relpath),
        }
    else:
        out["data"] = {"kind": kind}
    return out


def _root_arg(value: str) -> ResourceRoot:
    parts = value.split("=", 2)
    if len(parts) == 2:
        return ResourceRoot(parts[0], parts[1], 0)
    if len(parts) == 3:
        return ResourceRoot(parts[0], parts[2], int(parts[1]))
    raise argparse.ArgumentTypeError("--root expects label=path or label=priority=path")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Probe resolver v2 on real Workbench resources")
    parser.add_argument("--armst-root", required=True)
    parser.add_argument("--root", action="append", type=_root_arg, default=[])
    parser.add_argument("--resource", action="append", default=[])
    parser.add_argument("--all-armst", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args(argv)

    roots = [ResourceRoot("armst", args.armst_root, 100)] + list(args.root)
    store = HydratedResourceStore(roots)
    store.scan()

    requested = list(dict.fromkeys(args.resource))
    if args.all_armst:
        requested.extend(
            rec.relpath
            for rec in store.records.values()
            if rec.origin == "armst" and rec.kind == "et"
        )
        requested = list(dict.fromkeys(requested))
    if not requested:
        parser.error("provide --resource or --all-armst")

    rows = [summarize(store, relpath) for relpath in requested]
    statuses = Counter(row["resolution_status"] for row in rows)
    kinds = Counter((row.get("data") or {}).get("kind", "unknown") for row in rows)
    payload = {
        "schema": "resolver-v2-probe/1",
        "roots": [
            {"label": root.label, "path": root.path, "priority": root.priority}
            for root in roots
        ],
        "summary": {
            "resources": len(rows),
            "resolution_status": dict(statuses),
            "kinds": dict(kinds),
            "resolver_warnings": len(store.warnings),
        },
        "warnings": store.warnings,
        "resources": rows,
    }

    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if args.output:
        output = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(output) or ".", exist_ok=True)
        with open(output, "w", encoding="utf-8") as handle:
            handle.write(text + "\n")
        print(output)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
