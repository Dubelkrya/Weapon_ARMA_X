"""Strict production entrypoint for the resolver-v2 catalog pipeline.

The original ``scan_build_v2`` remains intact as a comparison baseline while
PR #2 is still draft. This entrypoint installs the conservative identity store
and origin-preserving weapon->magazine->ammo->projectile traversal, then reuses
the existing output/report code.

When a materialization manifest exists, the strict pipeline also refuses to
scan stale/unlisted ``.et/.conf/.meta`` files left from an older Workbench run.
A failed export must never become successful resolver evidence merely because a
previous copy still exists on disk.
"""

from __future__ import annotations

import os
from typing import Sequence

import scan_build_v2 as pipeline
from resolver_v2_strict import StrictHydratedResourceStore


MATERIALIZATION_MANIFEST = "_wax_materialization.tsv"
RESOLVER_EXTENSIONS = {".et", ".conf", ".meta"}


def _norm_rel(path: str) -> str:
    return str(path or "").replace("\\", "/").lstrip("./")


def validate_materialized_root(root: str) -> dict:
    """Validate a Workbench materialized root against its latest manifest.

    Roots without a manifest are accepted for tests/manual fixtures. If a
    manifest is present it becomes authoritative for resolver-readable files.
    """
    root = os.path.abspath(root)
    manifest_path = os.path.join(root, MATERIALIZATION_MANIFEST)
    if not os.path.isfile(manifest_path):
        return {"status": "manifest_absent", "root": root}

    with open(manifest_path, "r", encoding="utf-8-sig", errors="replace") as handle:
        lines = [line.rstrip("\r\n") for line in handle if line.strip()]
    if not lines:
        raise RuntimeError(f"materialization manifest is empty: {manifest_path}")

    header = lines[0].split("\t")
    required = {"destination_relative", "status"}
    if not required.issubset(header):
        raise RuntimeError(
            f"materialization manifest missing columns {sorted(required - set(header))}: "
            f"{manifest_path}"
        )
    columns = {name: index for index, name in enumerate(header)}

    ok_paths = set()
    failed_paths = set()
    for raw in lines[1:]:
        parts = raw.split("\t")
        if len(parts) < len(header):
            parts.extend([""] * (len(header) - len(parts)))
        rel = _norm_rel(parts[columns["destination_relative"]])
        status = parts[columns["status"]].strip().lower()
        if not rel:
            continue
        ext = os.path.splitext(rel)[1].lower()
        if ext not in RESOLVER_EXTENSIONS:
            continue
        if status == "ok":
            ok_paths.add(rel.casefold())
        else:
            failed_paths.add(rel.casefold())

    actual_paths = set()
    actual_display = {}
    for dirpath, _dirs, filenames in os.walk(root):
        for filename in filenames:
            if os.path.splitext(filename)[1].lower() not in RESOLVER_EXTENSIONS:
                continue
            rel = _norm_rel(os.path.relpath(os.path.join(dirpath, filename), root))
            key = rel.casefold()
            actual_paths.add(key)
            actual_display[key] = rel

    unlisted = sorted(actual_paths - ok_paths)
    missing = sorted(ok_paths - actual_paths)
    failed_present = sorted(actual_paths & failed_paths)
    if unlisted or missing or failed_present:
        def sample(items):
            return [actual_display.get(item, item) for item in items[:8]]

        raise RuntimeError(
            "materialized vanilla root does not match latest manifest: "
            f"unlisted={len(unlisted)} missing_ok={len(missing)} "
            f"failed_but_present={len(failed_present)}; "
            f"unlisted_sample={sample(unlisted)} "
            f"missing_sample={sample(missing)} "
            f"failed_sample={sample(failed_present)}"
        )

    return {
        "status": "ok",
        "root": root,
        "manifest": manifest_path,
        "ok_resolver_files": len(ok_paths),
    }


def _vanilla_root_path(raw: str, index: int) -> str:
    if "=" in raw:
        _label, path = raw.split("=", 1)
        return os.path.abspath(path)
    return os.path.abspath(raw)


def build_store(armst_root: str, vanilla_roots: Sequence[str]) -> StrictHydratedResourceStore:
    for index, raw in enumerate(vanilla_roots, 1):
        validate_materialized_root(_vanilla_root_path(raw, index))

    store = StrictHydratedResourceStore(
        pipeline.roots_from_args(armst_root, vanilla_roots)
    )
    store.scan()
    return store


def _value(obj):
    if isinstance(obj, dict) and "value" in obj:
        return obj.get("value")
    return obj


def _projectile_velocity(
    store: StrictHydratedResourceStore,
    projectile: str,
    projectile_origin: str | None,
    coef,
) -> dict:
    result = store.projectile_physics(projectile, projectile_origin)
    init = (result.get("physics") or {}).get("InitSpeed")
    init_value = _value(init)
    effective = None
    if isinstance(init_value, (int, float)) and isinstance(coef, (int, float)):
        effective = round(init_value * coef, 3)
    return {
        "projectile": projectile,
        "origin": result.get("origin") or projectile_origin,
        "status": result.get("status"),
        "ammo_init_speed": init_value,
        "bullet_init_speed_coef": coef,
        "effective_muzzle_velocity": effective,
        "ai_ballistic_table": result.get("ai_ballistic_table"),
        "ai_ballistic_validation": result.get("ai_ballistic_validation"),
    }


def resolve_weapon_ammo(store: StrictHydratedResourceStore, resolved: dict) -> dict:
    magazine = resolved.get("magazine") or {}
    template = magazine.get("magazine_template")
    if not template:
        return {"status": "missing_magazine_template"}

    ref = store.resolve_ref(
        template.get("guid"),
        template.get("path"),
        origin_hint=template.get("origin"),
    )
    result = {
        "status": ref.get("status"),
        "magazine_template": template,
        "magazine_target": ref.get("resource"),
        "magazine_target_origin": ref.get("origin"),
        "identity_resolution": {
            "resolved_by": ref.get("resolved_by"),
            "reason": ref.get("reason"),
            "candidates": ref.get("candidates") or [],
            "guid_candidates": ref.get("guid_candidates") or [],
        },
    }
    if ref.get("status") != "local" or not ref.get("resource"):
        result["status"] = (
            "ambiguous_magazine_template"
            if ref.get("status") == "ambiguous"
            else "external_magazine_template"
        )
        return result

    mag = store.resolve_magazine_ammo(
        ref["resource"],
        ref.get("origin"),
    )
    result["magazine"] = mag
    result["status"] = mag.get("status")

    coef = _value((resolved.get("ballistics") or {}).get("bullet_init_speed_coef"))
    velocities = []
    seen = set()
    for row in mag.get("counts") or []:
        projectile = row.get("projectile")
        projectile_origin = row.get("projectile_origin")
        identity = (projectile_origin, projectile)
        if not projectile or identity in seen:
            continue
        seen.add(identity)
        item = _projectile_velocity(
            store,
            projectile,
            projectile_origin,
            coef,
        )
        item["count"] = row.get("count")
        item["ammo_index"] = row.get("ammo_index")
        velocities.append(item)
    result["effective_muzzle_velocities"] = velocities
    return result


def install_strict_pipeline() -> None:
    # scan_build_v2.main() resolves these names from its own module globals.
    # Replacing just the two identity-sensitive hooks lets us reuse its stable
    # catalog/report writer without duplicating a large file during validation.
    pipeline.build_store = build_store
    pipeline.resolve_weapon_ammo = resolve_weapon_ammo


def main(argv=None) -> int:
    install_strict_pipeline()
    return pipeline.main(argv)


if __name__ == "__main__":
    raise SystemExit(main())
