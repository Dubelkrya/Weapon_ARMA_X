"""Nested `.conf` hydration for resolver_v2.

Serialized weapon instances frequently reference reusable configuration blocks,
for example FireMode_Auto.conf or recoil configs. Entity inheritance alone is
therefore not enough: the referenced config must be merged first, then local
instance fields must override it.
"""

from __future__ import annotations

from collections import Counter
from typing import Optional, Tuple

from resolver_v2 import (
    RNode,
    ResourceStore,
    _clone,
    _ref_from_token,
    array_values_r,
    find_child_r,
    find_recursive_r,
    merge_pair,
    rnode_from_parsed,
    scalar_r,
)


def _norm_relpath(path: Optional[str]) -> str:
    return str(path or "").replace("\\", "/").lstrip("./").casefold()


def _field_score(node: RNode, weights: dict) -> int:
    names = {child.name for child in node.children}
    return sum(weight for name, weight in weights.items() if name in names)


def _magazine_component_score(node: RNode) -> int:
    """Prefer the functional MagazineComponent when a prefab contains several."""
    return _field_score(
        node,
        {
            "AmmoConfig": 8,
            "AmmoMapping": 4,
            "MaxAmmo": 2,
            "MagazineWell": 1,
        },
    )


def _muzzle_component_score(node: RNode) -> int:
    """Rank primary/functional muzzle instances above sparse child-only instances."""
    return _field_score(
        node,
        {
            "MagazineTemplate": 32,
            "MagazineWell": 16,
            "FireModes": 8,
            "BulletInitSpeedCoef": 4,
            "DispersionDiameter": 2,
            "DispersionRange": 2,
            "RecoilWeaponAimModifier": 1,
        },
    )


def _weapon_component_score(node: RNode) -> int:
    components = find_child_r(node, "components")
    if components is None:
        return 0
    muzzles = [child for child in components.children if child.name == "MuzzleComponent"]
    if not muzzles:
        return 0
    return 100 + max(_muzzle_component_score(muzzle) for muzzle in muzzles)


def _prefer_functional_components(node: RNode) -> RNode:
    """Stably reorder duplicate semantic component instances in resolved trees.

    Enfusion child prefabs can serialize a sparse component with a new instance
    GUID while the functional inherited component remains present separately.
    Semantic extractors historically used the first matching class, which could
    hide inherited MagazineTemplate/AmmoConfig data. Reorder only duplicate
    instances of the same semantic class; all other sibling ordering is kept.
    """
    for child in node.children:
        _prefer_functional_components(child)

    scorers = {
        "WeaponComponent": _weapon_component_score,
        "MuzzleComponent": _muzzle_component_score,
        "MagazineComponent": _magazine_component_score,
    }
    for name, scorer in scorers.items():
        positions = [index for index, child in enumerate(node.children) if child.name == name]
        if len(positions) < 2:
            continue
        ordered = sorted(
            (node.children[index] for index in positions),
            key=scorer,
            reverse=True,
        )
        for index, child in zip(positions, ordered):
            node.children[index] = child
    return node


class HydratedResourceStore(ResourceStore):
    """ResourceStore that resolves nested `.conf` templates in entity trees."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reported_config_loops = set()

    def scan(self) -> None:
        super().scan()
        self._reported_config_loops.clear()

    def _config_template_node(self, conf_relpath: str) -> Optional[RNode]:
        record = self.get(conf_relpath)
        if record is None or record.kind != "conf":
            return None
        root = rnode_from_parsed(
            record.resource.root, record.relpath, record.origin
        )
        for child in root.children:
            if child.name != "__elem__":
                return child
        return None

    def _report_config_loop(self, target: str, stack: Tuple[str, ...]) -> None:
        target_key = _norm_relpath(target)
        stack_keys = [_norm_relpath(item) for item in stack]
        try:
            first = stack_keys.index(target_key)
            cycle = list(stack[first:])
        except ValueError:
            cycle = list(stack) + [target]

        # The same directed cycle can be reached from many entities. Canonicalize
        # by rotation so A->B->A and B->A->B produce one diagnostic.
        cycle_keys = [_norm_relpath(item) for item in cycle]
        if cycle_keys:
            rotations = [
                tuple(cycle_keys[index:] + cycle_keys[:index])
                for index in range(len(cycle_keys))
            ]
            key = min(rotations)
        else:
            key = (target_key,)

        if key in self._reported_config_loops:
            return
        self._reported_config_loops.add(key)
        self.warnings.append(
            {
                "category": "CONFIG_REF_LOOP",
                "resource": target,
                "stack": cycle + [target],
            }
        )

    def _hydrate_config_refs(
        self, node: RNode, stack: Optional[Tuple[str, ...]] = None
    ) -> RNode:
        stack = stack or ()
        current = _clone(node)

        # Hydrate only the local subtree before merging a referenced template.
        # Re-walking merged template children caused the same config chain to be
        # expanded repeatedly and multiplied loop diagnostics.
        current.children = [
            self._hydrate_config_refs(child, stack) for child in current.children
        ]

        if current.ref and str(current.ref.get("path", "")).lower().endswith(".conf"):
            resolved = self.resolve_ref(
                current.ref.get("guid"), current.ref.get("path")
            )
            target = resolved.get("resource")
            if resolved.get("status") == "local" and target:
                target_key = _norm_relpath(target)
                stack_keys = tuple(_norm_relpath(item) for item in stack)
                if target_key in stack_keys:
                    # BaseContainerTools.SaveContainer can serialize the root
                    # object of a materialized config with a reference back to
                    # that same config. That is an ownership/self reference,
                    # not an inheritance cycle, and there is nothing to hydrate.
                    if target_key == _norm_relpath(current.defined_in):
                        return current
                    self._report_config_loop(target, stack)
                    return current

                template = self._config_template_node(target)
                if template is not None:
                    template = self._hydrate_config_refs(
                        template, stack + (target,)
                    )
                    current = merge_pair(template, current)

        return current

    def resolve_entity(self, relpath: str):
        result = super().resolve_entity(relpath)
        if result.resolved is not None:
            hydrated = self._hydrate_config_refs(result.resolved)
            result.resolved = _prefer_functional_components(hydrated)
        return result

    def resolve_magazine_ammo(self, magazine_relpath: str) -> dict:
        """Resolve the functional magazine instance instead of blindly taking the first."""
        entity = self.resolve_entity(magazine_relpath)
        if entity.resolved is None:
            return {"status": "missing_magazine", "resource": magazine_relpath}

        mag_nodes = find_recursive_r(entity.resolved, "MagazineComponent")
        if not mag_nodes:
            return {"status": "missing_magazine_component", "resource": magazine_relpath}
        mag = max(mag_nodes, key=_magazine_component_score)

        max_ammo_node = find_child_r(mag, "MaxAmmo")
        max_ammo = scalar_r(max_ammo_node)
        config_node = find_child_r(mag, "AmmoConfig")
        config_ref = config_node.ref if config_node else None
        if config_ref is None and config_node and config_node.value:
            config_ref = _ref_from_token(config_node.value[0])
        mapping_node = find_child_r(mag, "AmmoMapping")
        mapping = array_values_r(mapping_node)

        result = {
            "resource": magazine_relpath,
            "inheritance_status": entity.status,
            "magazine_component": {
                "id": mag.id,
                "defined_in": mag.defined_in,
                "candidate_count": len(mag_nodes),
                "score": _magazine_component_score(mag),
            },
            "max_ammo": {
                "value": max_ammo,
                "defined_in": max_ammo_node.defined_in if max_ammo_node else None,
            },
            "ammo_config": None,
            "mapping": mapping,
            "mapping_defined_in": mapping_node.defined_in if mapping_node else None,
            "rounds": [],
            "counts": [],
            "warnings": [],
        }

        if not config_ref:
            result["status"] = "missing_ammo_config"
            return result

        cfg_resolved = self.resolve_ref(config_ref["guid"], config_ref["path"])
        result["ammo_config"] = {
            "guid": config_ref["guid"],
            "path": config_ref["path"],
            "defined_in": config_node.defined_in if config_node else None,
            "resolved": cfg_resolved["status"],
            "target": cfg_resolved.get("resource"),
        }
        if cfg_resolved["status"] != "local":
            result["status"] = "external_ammo_config"
            return result

        ammo_array = self.ammo_resource_array(cfg_resolved["resource"])
        projectiles = ammo_array.get("projectiles") or []
        result["projectiles"] = projectiles
        if ammo_array.get("status") != "resolved":
            result["status"] = ammo_array.get("status") or "missing_ammo_array"
            return result

        if not mapping:
            result["status"] = "missing_ammo_mapping"
            return result

        if isinstance(max_ammo, (int, float)) and int(max_ammo) != len(mapping):
            result["warnings"].append(
                {
                    "category": "AMMO_MAPPING_LENGTH",
                    "max_ammo": int(max_ammo),
                    "mapping_length": len(mapping),
                }
            )

        counts: Counter = Counter()
        for position, raw_index in enumerate(mapping):
            if not isinstance(raw_index, int):
                result["warnings"].append(
                    {"category": "AMMO_MAPPING_NON_INTEGER", "position": position, "value": raw_index}
                )
                continue
            if raw_index < 0 or raw_index >= len(projectiles):
                result["warnings"].append(
                    {
                        "category": "AMMO_MAPPING_OUT_OF_RANGE",
                        "position": position,
                        "index": raw_index,
                        "ammo_resource_count": len(projectiles),
                    }
                )
                continue
            projectile = projectiles[raw_index]
            counts[raw_index] += 1
            result["rounds"].append(
                {
                    "position": position,
                    "ammo_index": raw_index,
                    "projectile": projectile["target"] or projectile["path"],
                    "status": projectile["resolved"],
                }
            )

        result["counts"] = [
            {
                "ammo_index": index,
                "count": count,
                "projectile": projectiles[index]["target"] or projectiles[index]["path"],
            }
            for index, count in sorted(counts.items())
        ]
        result["status"] = "resolved" if not result["warnings"] else "resolved_with_warnings"
        return result
