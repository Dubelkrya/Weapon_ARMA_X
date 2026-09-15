"""Strict production entrypoint for the resolver-v2 catalog pipeline.

The original ``scan_build_v2`` remains intact as a comparison baseline while
PR #2 is still draft.  This entrypoint installs the conservative identity store
and origin-preserving weapon->magazine->ammo->projectile traversal, then reuses
the existing output/report code.
"""

from __future__ import annotations

from typing import Sequence

import scan_build_v2 as pipeline
from resolver_v2_strict import StrictHydratedResourceStore


def build_store(armst_root: str, vanilla_roots: Sequence[str]) -> StrictHydratedResourceStore:
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
