"""Semantic extraction for resolver_v2 resolved resource trees.

The legacy scanner mixed parsing, inheritance, and field interpretation.  This
module keeps interpretation separate and consumes RNode trees that are already
resolved by resolver_v2 / resolver_v2_configs.

Important rules:
* `local` means explicitly serialized in the leaf resource.
* `resolved` means effective value after inheritance/config hydration.
* every scalar/vector keeps `defined_in`, `origin`, and `inherited`.
* ItemPhysAttributes is read directly; there is no extra wrapper node.
* recoil curves are retained, not reduced to only magnitudes.
* magazine AmmoMapping is flattened from its serialized block.
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from resolver_v2 import (
    PROJECTILE_PHYSICS_FIELDS,
    RNode,
    array_values_r,
    find_child_r,
    find_recursive_r,
    scalar_r,
)


def _pval(node: Optional[RNode], leaf: str) -> Optional[dict]:
    if node is None:
        return None
    return {
        "value": scalar_r(node),
        "defined_in": node.defined_in,
        "origin": node.origin,
        "inherited": bool(node.defined_in and node.defined_in != leaf),
    }


def _pvec(node: Optional[RNode], leaf: str) -> Optional[dict]:
    if node is None:
        return None
    values = array_values_r(node) if node.children else list(node.value)
    return {
        "value": values,
        "defined_in": node.defined_in,
        "origin": node.origin,
        "inherited": bool(node.defined_in and node.defined_in != leaf),
    }


def _pref(node: Optional[RNode], leaf: str) -> Optional[dict]:
    if node is None or not node.ref:
        return None
    return {
        "guid": node.ref.get("guid"),
        "path": node.ref.get("path"),
        "defined_in": node.defined_in,
        "origin": node.origin,
        "inherited": bool(node.defined_in and node.defined_in != leaf),
    }


def _first(root: Optional[RNode], name: str) -> Optional[RNode]:
    nodes = find_recursive_r(root, name)
    return nodes[0] if nodes else None


def _nested_components(owner: Optional[RNode]) -> List[RNode]:
    block = find_child_r(owner, "components")
    return list(block.children) if block else []


def _component(root: Optional[RNode], name: str) -> Optional[RNode]:
    return _first(root, name)


def _item_physical(attributes: Optional[RNode], leaf: str) -> dict:
    item = find_child_r(attributes, "ItemPhysAttributes") if attributes else None
    if item is None:
        return {}
    out = {}
    for field in (
        "Weight",
        "ItemVolume",
        "ItemDimensions",
        "DimensionScaler",
        "SizeSetupStrategy",
    ):
        node = find_child_r(item, field)
        if node is None:
            continue
        out[field] = _pvec(node, leaf) if len(node.value) > 1 else _pval(node, leaf)
    out["defined_in"] = item.defined_in
    out["origin"] = item.origin
    return out


def _curve(block: Optional[RNode], name: str) -> Optional[dict]:
    node = find_child_r(block, name) if block else None
    if node is None:
        return None
    return {
        "points": array_values_r(node),
        "defined_in": node.defined_in,
        "origin": node.origin,
    }


def _recoil_data(node: Optional[RNode], leaf: str) -> Optional[dict]:
    if node is None:
        return None
    out = {
        "defined_in": node.defined_in,
        "origin": node.origin,
        "inherited": bool(node.defined_in and node.defined_in != leaf),
    }
    for name, key in (
        ("Curve Magnitudes", "curve_magnitudes"),
        ("Curve Mins", "curve_mins"),
        ("Curve Maxs", "curve_maxs"),
        ("Curve Time Scale", "curve_time_scale"),
        ("Base Recoil Scale", "base_recoil_scale"),
        ("Deployment Multiplier", "deployment_multiplier"),
        ("Bipod Deployment Multiplier", "bipod_deployment_multiplier"),
    ):
        field = find_child_r(node, name)
        if field is not None:
            out[key] = _pvec(field, leaf) if len(field.value) > 1 else _pval(field, leaf)
    out["curve_x"] = _curve(node, "Curve X")
    out["curve_y"] = _curve(node, "Curve Y")
    out["curve_z"] = _curve(node, "Curve Z")
    return out


def _recoil(root: Optional[RNode], leaf: str) -> Optional[dict]:
    recoil = _first(root, "RecoilWeaponAimModifier")
    if recoil is None:
        return None
    return {
        "defined_in": recoil.defined_in,
        "origin": recoil.origin,
        "linear": _recoil_data(find_child_r(recoil, "LinearData"), leaf),
        "angular": _recoil_data(find_child_r(recoil, "AngularData"), leaf),
        "turn_offset": _recoil_data(find_child_r(recoil, "TurnOffsetData"), leaf),
    }


def _sway(root: Optional[RNode], leaf: str) -> Optional[dict]:
    sway = _first(root, "SwayWeaponAimModifier")
    if sway is None:
        return None
    return {
        "defined_in": sway.defined_in,
        "origin": sway.origin,
        "lower_translation": _pvec(find_child_r(sway, "Lower Translation"), leaf),
        "lower_rotation": _pvec(find_child_r(sway, "Lower Rotation"), leaf),
    }


def _fire_modes(muzzle: Optional[RNode], leaf: str) -> List[dict]:
    modes = []
    block = find_child_r(muzzle, "FireModes") if muzzle else None
    if block is None:
        return modes
    for mode in block.children:
        if mode.name != "BaseFireMode":
            continue
        modes.append(
            {
                "mode_id": mode.id,
                "config": _pref(mode, leaf),
                "ui_name": _pval(find_child_r(mode, "UIName"), leaf),
                "rounds_per_minute": _pval(find_child_r(mode, "RoundsPerMinute"), leaf),
                "max_burst": _pval(find_child_r(mode, "MaxBurst"), leaf),
                "max_salvo": _pval(find_child_r(mode, "MaxSalvo"), leaf),
                "defined_in": mode.defined_in,
                "origin": mode.origin,
                "inherited": bool(mode.defined_in and mode.defined_in != leaf),
            }
        )
    return modes


def _sights(root: Optional[RNode], leaf: str) -> Optional[dict]:
    sights = _first(root, "SightsComponent")
    if sights is None:
        return None
    ranges = []
    ranges_block = find_child_r(sights, "SightsRanges")
    if ranges_block:
        for entry in ranges_block.children:
            rng = find_child_r(entry, "Range")
            if rng is not None:
                ranges.append(_pvec(rng, leaf))
    return {
        "defined_in": sights.defined_in,
        "origin": sights.origin,
        "switch_skip": _pval(find_child_r(sights, "SightsSwitchSkip"), leaf),
        "ranges": ranges,
    }


def _attachment_slots(weapon: Optional[RNode], leaf: str) -> List[dict]:
    slots = []
    if weapon is None:
        return slots
    for node in _nested_components(weapon):
        if node.name != "AttachmentSlotComponent":
            continue
        slot = find_child_r(node, "AttachmentSlot")
        attachment_types = []
        for child in node.children:
            if child.name == "AttachmentType":
                attachment_types.append(child.type or child.id or scalar_r(child))
        slots.append(
            {
                "instance_id": node.id,
                "slot": scalar_r(slot),
                "slot_class": slot.type if slot else None,
                "enabled": _pval(find_child_r(node, "Enabled"), leaf),
                "attachment_types": attachment_types,
                "defined_in": node.defined_in,
                "origin": node.origin,
                "inherited": bool(node.defined_in and node.defined_in != leaf),
            }
        )
    return slots


def extract_weapon(root: Optional[RNode], leaf: str) -> dict:
    weapon = _component(root, "WeaponComponent")
    if weapon is None:
        return {"status": "no_weapon_component"}
    muzzle = None
    animation = None
    for node in _nested_components(weapon):
        if node.name == "MuzzleComponent" and muzzle is None:
            muzzle = node
        elif node.name == "WeaponAnimationComponent" and animation is None:
            animation = node

    storage = _component(root, "SCR_WeaponAttachmentsStorageComponent")
    attrs = find_child_r(storage, "Attributes") if storage else None
    melee = _component(root, "SCR_MeleeWeaponProperties")

    physical = _item_physical(attrs, leaf)
    if melee is not None:
        physical["MeleeDamage"] = _pval(find_child_r(melee, "m_fDamage"), leaf)

    mag_well = find_child_r(muzzle, "MagazineWell") if muzzle else None
    mag_template = find_child_r(muzzle, "MagazineTemplate") if muzzle else None

    return {
        "status": "ok",
        "physical": physical,
        "fire_modes": _fire_modes(muzzle, leaf),
        "magazine": {
            "magazine_well": {
                "name": mag_well.name,
                "class": mag_well.type,
                "defined_in": mag_well.defined_in,
                "origin": mag_well.origin,
                "inherited": bool(mag_well.defined_in and mag_well.defined_in != leaf),
            } if mag_well else None,
            "magazine_template": _pref(mag_template, leaf),
        },
        "ballistics": {
            "bullet_init_speed_coef": _pval(find_child_r(muzzle, "BulletInitSpeedCoef"), leaf) if muzzle else None,
            "dispersion_diameter": _pval(find_child_r(muzzle, "DispersionDiameter"), leaf) if muzzle else None,
            "dispersion_range": _pval(find_child_r(muzzle, "DispersionRange"), leaf) if muzzle else None,
        },
        "recoil": _recoil(muzzle or weapon, leaf),
        "sway": _sway(muzzle or weapon, leaf),
        "sights": _sights(weapon, leaf),
        "attachment_slots": _attachment_slots(weapon, leaf),
        "animation": {
            "anim_graph": _pref(find_child_r(animation, "AnimGraph"), leaf) if animation else None,
            "anim_instance": _pref(find_child_r(animation, "AnimInstance"), leaf) if animation else None,
        },
    }


def extract_magazine(root: Optional[RNode], leaf: str) -> dict:
    mag = _component(root, "MagazineComponent")
    if mag is None:
        return {"status": "no_magazine_component"}
    inv = _component(root, "InventoryMagazineComponent")
    attrs = find_child_r(inv, "Attributes") if inv else None
    well = find_child_r(mag, "MagazineWell")
    ammo_config = find_child_r(mag, "AmmoConfig")
    mapping = find_child_r(mag, "AmmoMapping")
    ui = find_child_r(mag, "UIInfo")

    return {
        "status": "ok",
        "magazine_well": {
            "name": well.name,
            "class": well.type,
            "defined_in": well.defined_in,
            "origin": well.origin,
            "inherited": bool(well.defined_in and well.defined_in != leaf),
        } if well else None,
        "max_ammo": _pval(find_child_r(mag, "MaxAmmo"), leaf),
        "ammo_config": _pref(ammo_config, leaf),
        "ammo_mapping": {
            "value": array_values_r(mapping),
            "defined_in": mapping.defined_in,
            "origin": mapping.origin,
            "inherited": bool(mapping.defined_in and mapping.defined_in != leaf),
        } if mapping else None,
        "caliber_id": _pval(find_child_r(ui, "m_sAmmoCaliber"), leaf) if ui else None,
        "physical": _item_physical(attrs, leaf),
        "weight_per_ammo": _pval(find_child_r(inv, "WeightPerAmmo"), leaf) if inv else None,
    }


def _damage_effects(root: Optional[RNode], leaf: str) -> List[dict]:
    out = []
    for effect in find_recursive_r(root, "ProjectileDamage"):
        row = {
            "type": "ProjectileDamage",
            "instance_id": effect.id,
            "defined_in": effect.defined_in,
            "origin": effect.origin,
            "inherited": bool(effect.defined_in and effect.defined_in != leaf),
        }
        for name in ("DamageValue", "DamageType", "MinimumDamage"):
            row[name] = _pval(find_child_r(effect, name), leaf)
        out.append(row)
    return out


def extract_projectile(root: Optional[RNode], leaf: str) -> dict:
    shell = _component(root, "ShellMoveComponent")
    if shell is None:
        return {"status": "no_shell_move_component"}
    physics = {}
    for name in PROJECTILE_PHYSICS_FIELDS:
        physics[name] = _pval(find_child_r(shell, name), leaf)
    return {
        "status": "ok",
        "physics": physics,
        "ai_ballistic_table": _pref(find_child_r(shell, "BallisticTableConfig"), leaf),
        "damage_effects": _damage_effects(shell, leaf),
    }


def classify(root: Optional[RNode], relpath: str, et_class: Optional[str]) -> dict:
    low = relpath.lower()
    if et_class == "Projectile":
        return {"kind": "ammunition", "confidence": "class"}
    if _component(root, "WeaponComponent") is not None:
        return {"kind": "weapon", "confidence": "components"}
    if _component(root, "MagazineComponent") is not None:
        return {"kind": "magazine", "confidence": "components"}
    if "/attachments/" in low:
        kind = "optic" if "/optics/" in low else "attachment"
        return {"kind": kind, "confidence": "folder"}
    if "/grenades/" in low:
        return {"kind": "grenade", "confidence": "folder"}
    if "/ammo/" in low:
        return {"kind": "ammunition", "confidence": "folder"}
    if "/magazines/" in low:
        return {"kind": "magazine", "confidence": "folder"}
    if any(token in low for token in ("/rifles/", "/handguns/", "/machineguns/", "/shotguns/")):
        return {"kind": "weapon", "confidence": "folder"}
    if "/core/" in low:
        return {"kind": "core", "confidence": "folder"}
    return {"kind": "misc", "confidence": "unknown"}


def extract_semantic(root: Optional[RNode], relpath: str, et_class: Optional[str], kind: Optional[str] = None) -> dict:
    actual_kind = kind or classify(root, relpath, et_class)["kind"]
    if actual_kind == "weapon":
        return extract_weapon(root, relpath)
    if actual_kind == "magazine":
        return extract_magazine(root, relpath)
    if actual_kind == "ammunition":
        return extract_projectile(root, relpath)
    return {"status": "not_balance_entity"}
