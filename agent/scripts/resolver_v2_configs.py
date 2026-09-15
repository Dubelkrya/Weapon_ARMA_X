"""Nested `.conf` hydration plus origin-aware resource identity for resolver_v2.

Serialized weapon instances frequently reference reusable configuration blocks,
for example FireMode_Auto.conf or recoil configs. Entity inheritance alone is
therefore not enough: the referenced config must be merged first, then local
instance fields must override it.

This store also preserves duplicate virtual paths across roots. That matters
when ARMST overrides a vanilla resource at the same path: a vanilla child must
still be able to inherit from the vanilla parent instead of silently switching
to the higher-priority ARMST record.
"""

from __future__ import annotations

from collections import Counter
import os
from typing import Dict, List, Optional, Tuple

from et_parser import parse_file
from resolver_v2 import (
    RNode,
    ResolutionResult,
    ResourceRecord,
    ResourceStore,
    TEXT_EXTENSIONS,
    _clone,
    _norm_key,
    _norm_path,
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
    """ResourceStore with config hydration and origin-aware duplicate-path handling."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._reported_config_loops = set()
        self._records_by_origin_key: Dict[Tuple[str, str], ResourceRecord] = {}
        self._records_by_path_key: Dict[str, List[ResourceRecord]] = {}
        self._highest_priority = max((root.priority for root in self.roots), default=0)

    def scan(self) -> None:
        # Keep the legacy/high-priority index for compatibility and GUID/meta
        # bookkeeping, then build a second identity index that does NOT discard
        # lower-priority records sharing the same virtual path.
        super().scan()
        self._reported_config_loops.clear()
        self._records_by_origin_key.clear()
        self._records_by_path_key.clear()

        for root in self.roots:
            if not os.path.isdir(root.path):
                continue
            for dirpath, _dirs, filenames in os.walk(root.path):
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in TEXT_EXTENSIONS:
                        continue
                    abspath = os.path.join(dirpath, filename)
                    relpath = _norm_path(os.path.relpath(abspath, root.path))
                    try:
                        parsed = parse_file(abspath, root.path)
                    except Exception:
                        # super().scan() already reports parse errors for the
                        # active/high-priority view. Do not duplicate warnings.
                        continue
                    record = ResourceRecord(
                        relpath, abspath, root.label, root.priority, parsed
                    )
                    key = _norm_key(relpath)
                    self._records_by_origin_key[(root.label, key)] = record
                    self._records_by_path_key.setdefault(key, []).append(record)

        for records in self._records_by_path_key.values():
            records.sort(key=lambda item: item.priority, reverse=True)

    def _candidate_records(self, relpath: Optional[str]) -> Tuple[List[ResourceRecord], str]:
        """Return exact candidates, otherwise a unique/safe suffix candidate set.

        ARMST contains serialized links like `Rifles/AK74/armst_AK74.et` while
        the checkout path is `Prefabs/Weapons/Rifles/AK74/armst_AK74.et`.
        Suffix matching is used only as a fallback and ambiguity is preserved.
        """
        key = _norm_key(str(relpath or ""))
        if not key:
            return [], "none"

        exact = list(self._records_by_path_key.get(key, []))
        if exact:
            return exact, "path"

        suffix = "/" + key
        matches: List[ResourceRecord] = []
        for candidate_key, records in self._records_by_path_key.items():
            if candidate_key.endswith(suffix):
                matches.extend(records)
        matches.sort(key=lambda item: item.priority, reverse=True)
        return matches, "suffix" if matches else "none"

    def _record_for(
        self, relpath: str, origin: Optional[str] = None
    ) -> Optional[ResourceRecord]:
        candidates, _mode = self._candidate_records(relpath)
        if origin is not None:
            same_origin = [record for record in candidates if record.origin == origin]
            if len(same_origin) == 1:
                return same_origin[0]
        return candidates[0] if candidates else None

    @staticmethod
    def _resolved_ref(
        record: ResourceRecord,
        guid: Optional[str],
        resolved_by: str,
        candidates: List[ResourceRecord],
    ) -> dict:
        return {
            "status": "local",
            "resource": record.relpath,
            "origin": record.origin,
            "guid": guid.upper() if guid else None,
            "resolved_by": resolved_by,
            "candidate_count": len(candidates),
        }

    def resolve_ref(
        self,
        guid: Optional[str],
        path: Optional[str],
        origin_hint: Optional[str] = None,
    ) -> dict:
        candidates, mode = self._candidate_records(path)

        if len(candidates) == 1:
            return self._resolved_ref(candidates[0], guid, mode, candidates)

        if candidates and origin_hint:
            same_origin = [record for record in candidates if record.origin == origin_hint]
            if len(same_origin) == 1:
                return self._resolved_ref(
                    same_origin[0],
                    guid,
                    f"{mode}+origin",
                    candidates,
                )

        # Live GUID references can provide an alternate canonical path. Re-run
        # the same candidate logic there, but never collapse an unresolved
        # duplicate to the higher-priority path just because it was scanned first.
        if guid:
            live_path = self.live_guid_to_path.get(guid.upper())
            if live_path and _norm_key(live_path) != _norm_key(str(path or "")):
                live_candidates, live_mode = self._candidate_records(live_path)
                if len(live_candidates) == 1:
                    return self._resolved_ref(
                        live_candidates[0], guid, f"live_guid:{live_mode}", live_candidates
                    )
                if live_candidates and origin_hint:
                    same_origin = [
                        record for record in live_candidates if record.origin == origin_hint
                    ]
                    if len(same_origin) == 1:
                        return self._resolved_ref(
                            same_origin[0],
                            guid,
                            f"live_guid:{live_mode}+origin",
                            live_candidates,
                        )

        if candidates:
            return {
                "status": "ambiguous",
                "guid": guid.upper() if guid else None,
                "path": path,
                "candidates": [
                    {
                        "resource": record.relpath,
                        "origin": record.origin,
                        "priority": record.priority,
                    }
                    for record in candidates
                ],
            }

        return {
            "status": "external",
            "guid": guid.upper() if guid else None,
            "path": path,
        }

    def build_chain(
        self, relpath: str, max_depth: int = 64
    ) -> Tuple[List[dict], Optional[dict]]:
        chain: List[dict] = []
        seen = set()
        current = self._record_for(relpath)
        if current is None:
            return chain, {"status": "missing_resource", "path": relpath}

        while current is not None and max_depth > 0:
            max_depth -= 1
            key = _norm_key(current.relpath)
            seen_key = (current.origin, key)
            if seen_key in seen:
                loop = {
                    "status": "loop",
                    "resource": current.relpath,
                    "origin": current.origin,
                }
                chain.append(loop)
                return chain, loop
            seen.add(seen_key)

            path_candidates, _mode = self._candidate_records(current.relpath)
            live_guid = (
                self.live_guid_by_path.get(key) if len(path_candidates) == 1 else None
            )
            chain.append(
                {
                    "status": "local",
                    "resource": current.relpath,
                    "origin": current.origin,
                    "class": current.resource.et_class,
                    "live_guid": live_guid,
                    "meta_name_guid": self.meta_name_guid_by_path.get(key),
                }
            )

            parent = current.parent
            if not parent:
                return chain, None

            resolved = self.resolve_ref(
                parent.get("guid"),
                parent.get("path"),
                origin_hint=current.origin,
            )
            if resolved.get("status") != "local":
                return chain, {
                    "status": (
                        "ambiguous_parent"
                        if resolved.get("status") == "ambiguous"
                        else "external_parent"
                    ),
                    "guid": parent.get("guid"),
                    "path": parent.get("path"),
                    "defined_in": current.relpath,
                    "origin": current.origin,
                    "candidates": resolved.get("candidates") or [],
                }

            current = self._record_for(
                resolved["resource"], resolved.get("origin")
            )

        if max_depth <= 0:
            return chain, {"status": "depth_limit", "path": relpath}
        return chain, None

    def _config_template_node(
        self, conf_relpath: str, origin: Optional[str] = None
    ) -> Optional[RNode]:
        record = self._record_for(conf_relpath, origin)
        if record is None or record.kind != "conf":
            return None
        root = rnode_from_parsed(
            record.resource.root, record.relpath, record.origin
        )
        for child in root.children:
            if child.name != "__elem__":
                return child
        return None

    def _resolved_conf_root(
        self, relpath: str, origin: Optional[str] = None
    ) -> Optional[RNode]:
        """Return a config root with nested config inheritance already hydrated."""
        record = self._record_for(relpath, origin)
        if record is None or record.kind != "conf":
            return None
        root = rnode_from_parsed(record.resource.root, record.relpath, record.origin)
        return self._hydrate_config_refs(root, (record.relpath,))

    def _report_config_loop(self, target: str, stack: Tuple[str, ...]) -> None:
        target_key = _norm_relpath(target)
        stack_keys = [_norm_relpath(item) for item in stack]
        try:
            first = stack_keys.index(target_key)
            cycle = list(stack[first:])
        except ValueError:
            cycle = list(stack) + [target]

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

        current.children = [
            self._hydrate_config_refs(child, stack) for child in current.children
        ]

        if current.ref and str(current.ref.get("path", "")).lower().endswith(".conf"):
            resolved = self.resolve_ref(
                current.ref.get("guid"),
                current.ref.get("path"),
                origin_hint=current.origin,
            )
            target = resolved.get("resource")
            if resolved.get("status") == "local" and target:
                target_key = _norm_relpath(target)
                stack_keys = tuple(_norm_relpath(item) for item in stack)
                if target_key in stack_keys:
                    if target_key == _norm_relpath(current.defined_in):
                        return current
                    self._report_config_loop(target, stack)
                    return current

                template = self._config_template_node(
                    target, resolved.get("origin")
                )
                if template is not None:
                    template = self._hydrate_config_refs(
                        template, stack + (target,)
                    )
                    current = merge_pair(template, current)

        return current

    def resolve_entity(self, relpath: str) -> ResolutionResult:
        record = self._record_for(relpath)
        if record is None or record.kind != "et":
            return ResolutionResult(relpath, "missing", [], None, None, None)

        chain, missing = self.build_chain(relpath)
        local_records = [
            self._record_for(row["resource"], row.get("origin"))
            for row in chain
            if row.get("status") == "local"
        ]
        local_records = [item for item in local_records if item is not None]
        if not local_records:
            return ResolutionResult(relpath, "missing", chain, missing, None, None)

        raw = rnode_from_parsed(record.resource.root, record.relpath, record.origin)
        trees = [
            rnode_from_parsed(item.resource.root, item.relpath, item.origin)
            for item in local_records
        ]
        resolved = trees[-1]
        for child_tree in reversed(trees[:-1]):
            resolved = merge_pair(resolved, child_tree)

        status = "resolved" if missing is None else "partial"
        hydrated = self._hydrate_config_refs(resolved)
        hydrated = _prefer_functional_components(hydrated)
        return ResolutionResult(
            record.relpath, status, chain, missing, raw, hydrated
        )

    def ammo_resource_array(
        self, conf_relpath: str, origin_hint: Optional[str] = None
    ) -> dict:
        root = self._resolved_conf_root(conf_relpath, origin_hint)
        if root is None:
            return {
                "status": "missing_config",
                "resource": conf_relpath,
                "projectiles": [],
            }
        arrays = find_recursive_r(root, "AmmoResourceArray")
        if not arrays:
            return {
                "status": "missing_array",
                "resource": conf_relpath,
                "projectiles": [],
            }

        projectiles = []
        array_origin = arrays[0].origin or origin_hint
        for elem in arrays[0].children:
            ref = elem.ref
            if ref is None and elem.value:
                ref = _ref_from_token(elem.value[0])
            if not ref:
                continue
            resolved = self.resolve_ref(
                ref["guid"], ref["path"], origin_hint=array_origin
            )
            projectiles.append(
                {
                    "index": len(projectiles),
                    "guid": ref["guid"],
                    "path": ref["path"],
                    "resolved": resolved["status"],
                    "target": resolved.get("resource"),
                    "origin": resolved.get("origin"),
                }
            )
        return {
            "status": "resolved",
            "resource": conf_relpath,
            "origin": origin_hint,
            "projectiles": projectiles,
        }

    def resolve_magazine_ammo(self, magazine_relpath: str) -> dict:
        """Resolve the functional magazine instance and its exact ammo mapping."""
        entity = self.resolve_entity(magazine_relpath)
        if entity.resolved is None:
            return {"status": "missing_magazine", "resource": magazine_relpath}

        mag_nodes = find_recursive_r(entity.resolved, "MagazineComponent")
        if not mag_nodes:
            return {
                "status": "missing_magazine_component",
                "resource": magazine_relpath,
            }
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
                "origin": mag.origin,
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

        cfg_resolved = self.resolve_ref(
            config_ref["guid"],
            config_ref["path"],
            origin_hint=config_node.origin if config_node else mag.origin,
        )
        result["ammo_config"] = {
            "guid": config_ref["guid"],
            "path": config_ref["path"],
            "defined_in": config_node.defined_in if config_node else None,
            "origin": config_node.origin if config_node else None,
            "resolved": cfg_resolved["status"],
            "target": cfg_resolved.get("resource"),
            "target_origin": cfg_resolved.get("origin"),
        }
        if cfg_resolved["status"] != "local":
            result["status"] = (
                "ambiguous_ammo_config"
                if cfg_resolved["status"] == "ambiguous"
                else "external_ammo_config"
            )
            return result

        ammo_array = self.ammo_resource_array(
            cfg_resolved["resource"], cfg_resolved.get("origin")
        )
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
                    {
                        "category": "AMMO_MAPPING_NON_INTEGER",
                        "position": position,
                        "value": raw_index,
                    }
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
                "projectile": projectiles[index]["target"]
                or projectiles[index]["path"],
            }
            for index, count in sorted(counts.items())
        ]
        result["status"] = (
            "resolved" if not result["warnings"] else "resolved_with_warnings"
        )
        return result
