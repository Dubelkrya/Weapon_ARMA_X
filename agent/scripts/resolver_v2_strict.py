"""Strict identity/provenance layer for resolver v2.

This module intentionally sits on top of ``resolver_v2_configs`` while the
existing real-data pipeline is still a draft.  The older store remains useful
for comparison, but production scans should use ``StrictHydratedResourceStore``.

The strict rules are deliberately conservative:

* path collisions are not silently resolved to the highest-priority root;
* a proven GUID target wins over path/origin heuristics;
* lower/read-only roots may resolve a collision to their own origin because
  base-game data cannot depend upward on the editable ARMST root;
* ARMST collisions stay ambiguous unless GUID evidence proves the target;
* once a concrete origin is selected it is carried through magazine/config/
  projectile resolution;
* config loop identity is ``(origin, path)``, never path alone.

The point is correctness and provenance, not maximizing ``resolved`` counts.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, Iterable, List, Optional, Tuple

from resolver_v2 import (
    PROJECTILE_PHYSICS_FIELDS,
    RNode,
    ResolutionResult,
    ResourceRecord,
    ResourceRoot,
    _clone,
    _norm_key,
    _ref_from_token,
    array_values_r,
    find_child_r,
    find_recursive_r,
    iter_nodes,
    merge_pair,
    rnode_from_parsed,
    scalar_r,
    validate_aibt,
)
from resolver_v2_configs import (
    HydratedResourceStore,
    _magazine_component_score,
    _prefer_functional_components,
)


Identity = Tuple[str, str]


def _identity(record: ResourceRecord) -> Identity:
    return (record.origin, _norm_key(record.relpath))


def _node_identity(node: RNode) -> Identity:
    return (str(node.origin or ""), _norm_key(str(node.defined_in or "")))


class StrictHydratedResourceStore(HydratedResourceStore):
    """Hydrated resolver with conservative cross-root resource identity."""

    def __init__(self, roots: Iterable[ResourceRoot]):
        super().__init__(roots)
        self._guid_targets: Dict[str, List[ResourceRecord]] = {}
        self._guids_by_identity: Dict[Identity, List[str]] = {}
        self._guid_observed_paths: Dict[str, set[str]] = {}

    def scan(self) -> None:
        super().scan()
        self._guid_targets.clear()
        self._guids_by_identity.clear()
        self._guid_observed_paths.clear()
        self._index_strict_guid_evidence()
        self._publish_safe_legacy_guid_indexes()

    def _all_records(self) -> List[ResourceRecord]:
        out: List[ResourceRecord] = []
        seen = set()
        for records in self._records_by_path_key.values():
            for record in records:
                key = _identity(record)
                if key in seen:
                    continue
                seen.add(key)
                out.append(record)
        return out

    @staticmethod
    def _iter_record_refs(record: ResourceRecord):
        if record.kind == "et" and record.parent:
            yield record.parent
        root = record.resource.root
        if root is None:
            return
        for node in iter_nodes(root):
            if node.ref:
                yield node.ref

    def _add_guid_target(self, guid: str, record: ResourceRecord) -> None:
        guid = guid.upper()
        targets = self._guid_targets.setdefault(guid, [])
        record_id = _identity(record)
        if all(_identity(item) != record_id for item in targets):
            targets.append(record)
        reverse = self._guids_by_identity.setdefault(record_id, [])
        if guid not in reverse:
            reverse.append(guid)

    def _index_strict_guid_evidence(self) -> None:
        """Build only GUID ownership evidence that can be justified locally.

        A reference to a path with exactly one available record proves that
        GUID->record relation.  For a lower/read-only source, an exact/suffix
        collision may also be assigned to its same-origin candidate: vanilla
        data cannot depend upward on ARMST.  We deliberately do *not* apply the
        inverse assumption to ARMST references.
        """
        for source in self._all_records():
            for ref in self._iter_record_refs(source):
                guid = str(ref.get("guid") or "").upper()
                path = str(ref.get("path") or "")
                if not guid or not path:
                    continue
                self._guid_observed_paths.setdefault(guid, set()).add(_norm_key(path))
                candidates, _mode = self._candidate_records(path)
                if len(candidates) == 1:
                    self._add_guid_target(guid, candidates[0])
                    continue

                if source.priority >= self._highest_priority:
                    continue
                same_origin = [c for c in candidates if c.origin == source.origin]
                if len(same_origin) == 1:
                    self._add_guid_target(guid, same_origin[0])

    def _publish_safe_legacy_guid_indexes(self) -> None:
        """Replace path-only legacy maps with unambiguous strict evidence.

        Callers still reading ``live_guid_by_path`` get a value only when one
        path identifies one record and that record has exactly one proven GUID.
        Collided paths are omitted rather than mislabeled.
        """
        self.live_guid_to_path = {}
        self.live_guid_by_path = {}

        for guid, targets in self._guid_targets.items():
            if len(targets) == 1:
                self.live_guid_to_path[guid] = targets[0].relpath

        for path_key, records in self._records_by_path_key.items():
            if len(records) != 1:
                continue
            guids = self._guids_by_identity.get(_identity(records[0]), [])
            if len(guids) == 1:
                self.live_guid_by_path[path_key] = guids[0]

    def _guid_records(self, guid: Optional[str]) -> List[ResourceRecord]:
        if not guid:
            return []
        return list(self._guid_targets.get(str(guid).upper(), []))

    @staticmethod
    def _candidate_payload(records: List[ResourceRecord]) -> List[dict]:
        return [
            {
                "resource": record.relpath,
                "origin": record.origin,
                "priority": record.priority,
            }
            for record in records
        ]

    def _ambiguous_ref(
        self,
        guid: Optional[str],
        path: Optional[str],
        candidates: List[ResourceRecord],
        reason: str,
        guid_records: Optional[List[ResourceRecord]] = None,
    ) -> dict:
        return {
            "status": "ambiguous",
            "reason": reason,
            "guid": str(guid).upper() if guid else None,
            "path": path,
            "candidates": self._candidate_payload(candidates),
            "guid_candidates": self._candidate_payload(guid_records or []),
        }

    def resolve_ref(
        self,
        guid: Optional[str],
        path: Optional[str],
        origin_hint: Optional[str] = None,
    ) -> dict:
        candidates, mode = self._candidate_records(path)
        guid_records = self._guid_records(guid)
        candidate_ids = {_identity(record) for record in candidates}
        guid_matches = [record for record in guid_records if _identity(record) in candidate_ids]

        # Strongest evidence: the serialized GUID is already proven to identify
        # exactly one of the path candidates.
        if len(guid_matches) == 1:
            return self._resolved_ref(
                guid_matches[0], guid, f"guid+{mode}", candidates
            )
        if len(guid_matches) > 1:
            return self._ambiguous_ref(
                guid, path, candidates, "guid_matches_multiple_records", guid_matches
            )

        # A GUID proven elsewhere can resolve a short/alternate serialized path.
        if not candidates and len(guid_records) == 1:
            return self._resolved_ref(
                guid_records[0], guid, "guid_evidence", guid_records
            )

        if len(candidates) == 1:
            if guid_records and all(
                _identity(record) != _identity(candidates[0]) for record in guid_records
            ):
                return self._ambiguous_ref(
                    guid, path, candidates, "guid_path_conflict", guid_records
                )
            return self._resolved_ref(candidates[0], guid, mode, candidates)

        if candidates and origin_hint:
            same_origin = [record for record in candidates if record.origin == origin_hint]
            # Safe one-way fallback: read-only/base resources cannot depend on
            # the higher-priority editable ARMST root.  Do not make this
            # assumption for an ARMST source.
            if len(same_origin) == 1 and same_origin[0].priority < self._highest_priority:
                if not guid_records or any(
                    _identity(record) == _identity(same_origin[0])
                    for record in guid_records
                ):
                    return self._resolved_ref(
                        same_origin[0], guid, f"{mode}+base_origin", candidates
                    )

        if candidates:
            return self._ambiguous_ref(
                guid,
                path,
                candidates,
                "path_collision_without_proven_guid_owner",
                guid_records,
            )

        if len(guid_records) > 1:
            return self._ambiguous_ref(
                guid, path, [], "guid_maps_multiple_records", guid_records
            )

        return {
            "status": "external",
            "guid": str(guid).upper() if guid else None,
            "path": path,
        }

    def build_chain(
        self,
        relpath: str,
        max_depth: int = 64,
        origin: Optional[str] = None,
    ) -> Tuple[List[dict], Optional[dict]]:
        chain: List[dict] = []
        seen = set()
        current = self._record_for(relpath, origin)
        if current is None:
            return chain, {
                "status": "missing_resource",
                "path": relpath,
                "origin": origin,
            }

        while current is not None and max_depth > 0:
            max_depth -= 1
            current_id = _identity(current)
            if current_id in seen:
                loop = {
                    "status": "loop",
                    "resource": current.relpath,
                    "origin": current.origin,
                }
                chain.append(loop)
                return chain, loop
            seen.add(current_id)

            candidates, _mode = self._candidate_records(current.relpath)
            guids = self._guids_by_identity.get(current_id, [])
            chain.append(
                {
                    "status": "local",
                    "resource": current.relpath,
                    "origin": current.origin,
                    "class": current.resource.et_class,
                    "live_guid": guids[0] if len(guids) == 1 else None,
                    "live_guid_candidates": sorted(guids),
                    "meta_name_guid": (
                        self.meta_name_guid_by_path.get(_norm_key(current.relpath))
                        if len(candidates) == 1
                        else None
                    ),
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
                    "reason": resolved.get("reason"),
                    "candidates": resolved.get("candidates") or [],
                    "guid_candidates": resolved.get("guid_candidates") or [],
                }

            current = self._record_for(
                resolved["resource"], resolved.get("origin")
            )

        if max_depth <= 0:
            return chain, {"status": "depth_limit", "path": relpath, "origin": origin}
        return chain, None

    @staticmethod
    def _config_id(origin: Optional[str], resource: Optional[str]) -> Identity:
        return (str(origin or ""), _norm_key(str(resource or "")))

    @staticmethod
    def _config_stack_paths(stack: Tuple[Identity, ...]) -> List[str]:
        return [resource for _origin, resource in stack]

    def _report_config_loop(
        self,
        target: Identity,
        stack: Tuple[Identity, ...],
    ) -> None:
        try:
            first = stack.index(target)
            cycle = list(stack[first:])
        except ValueError:
            cycle = list(stack) + [target]

        if cycle:
            rotations = [
                tuple(cycle[index:] + cycle[:index]) for index in range(len(cycle))
            ]
            key = min(rotations)
        else:
            key = (target,)

        if key in self._reported_config_loops:
            return
        self._reported_config_loops.add(key)
        display = cycle + [target]
        self.warnings.append(
            {
                "category": "CONFIG_REF_LOOP",
                "resource": target[1],
                "origin": target[0],
                # Preserve the old path-only shape for existing reports/tests.
                "stack": [resource for _origin, resource in display],
                "identity_stack": [
                    {"origin": origin, "resource": resource}
                    for origin, resource in display
                ],
            }
        )

    def _resolved_conf_root(
        self, relpath: str, origin: Optional[str] = None
    ) -> Optional[RNode]:
        record = self._record_for(relpath, origin)
        if record is None or record.kind != "conf":
            return None
        root = rnode_from_parsed(record.resource.root, record.relpath, record.origin)
        return self._hydrate_config_refs(
            root,
            (self._config_id(record.origin, record.relpath),),
        )

    def _hydrate_config_refs(
        self,
        node: RNode,
        stack: Optional[Tuple[Identity, ...]] = None,
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
            target_path = resolved.get("resource")
            target_origin = resolved.get("origin")
            if resolved.get("status") == "local" and target_path:
                target_id = self._config_id(target_origin, target_path)
                current_id = self._config_id(current.origin, current.defined_in)
                if target_id in stack:
                    # BaseContainerTools can serialize a config as inheriting
                    # from itself.  It is an ownership/self-reference, not a
                    # semantic cycle.
                    if target_id == current_id:
                        return current
                    self._report_config_loop(target_id, stack)
                    return current

                template = self._config_template_node(target_path, target_origin)
                if template is not None:
                    template = self._hydrate_config_refs(
                        template,
                        stack + (target_id,),
                    )
                    current = merge_pair(template, current)

        return current

    def resolve_entity(
        self,
        relpath: str,
        origin: Optional[str] = None,
    ) -> ResolutionResult:
        record = self._record_for(relpath, origin)
        if record is None or record.kind != "et":
            return ResolutionResult(relpath, "missing", [], None, None, None)

        chain, missing = self.build_chain(relpath, origin=record.origin)
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
        resolved_tree = trees[-1]
        for child_tree in reversed(trees[:-1]):
            resolved_tree = merge_pair(resolved_tree, child_tree)

        status = "resolved" if missing is None else "partial"
        hydrated = self._hydrate_config_refs(resolved_tree)
        hydrated = _prefer_functional_components(hydrated)
        return ResolutionResult(
            record.relpath,
            status,
            chain,
            missing,
            raw,
            hydrated,
        )

    def resolve_magazine_ammo(
        self,
        magazine_relpath: str,
        origin: Optional[str] = None,
    ) -> dict:
        """Resolve a magazine while preserving the selected resource origin."""
        entity = self.resolve_entity(magazine_relpath, origin)
        if entity.resolved is None:
            return {
                "status": "missing_magazine",
                "resource": magazine_relpath,
                "origin": origin,
            }

        mag_nodes = find_recursive_r(entity.resolved, "MagazineComponent")
        if not mag_nodes:
            return {
                "status": "missing_magazine_component",
                "resource": magazine_relpath,
                "origin": origin,
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
            "origin": origin or (entity.chain[0].get("origin") if entity.chain else None),
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
                "origin": max_ammo_node.origin if max_ammo_node else None,
            },
            "ammo_config": None,
            "mapping": mapping,
            "mapping_defined_in": mapping_node.defined_in if mapping_node else None,
            "mapping_origin": mapping_node.origin if mapping_node else None,
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
            "reason": cfg_resolved.get("reason"),
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
                    "projectile_origin": projectile.get("origin"),
                    "status": projectile["resolved"],
                }
            )

        result["counts"] = [
            {
                "ammo_index": index,
                "count": count,
                "projectile": projectiles[index]["target"]
                or projectiles[index]["path"],
                "projectile_origin": projectiles[index].get("origin"),
            }
            for index, count in sorted(counts.items())
        ]
        result["status"] = (
            "resolved" if not result["warnings"] else "resolved_with_warnings"
        )
        return result

    def projectile_physics(
        self,
        projectile_relpath: str,
        origin: Optional[str] = None,
    ) -> dict:
        """Resolve projectile physics at the already-selected origin."""
        entity = self.resolve_entity(projectile_relpath, origin)
        if entity.resolved is None:
            return {
                "status": "missing_projectile",
                "resource": projectile_relpath,
                "origin": origin,
            }
        shells = find_recursive_r(entity.resolved, "ShellMoveComponent")
        if not shells:
            return {
                "status": "missing_shell_component",
                "resource": projectile_relpath,
                "origin": origin,
            }
        shell = shells[0]

        physics = {}
        for name in PROJECTILE_PHYSICS_FIELDS:
            node = find_child_r(shell, name)
            physics[name] = (
                {
                    "value": scalar_r(node),
                    "defined_in": node.defined_in,
                    "origin": node.origin,
                }
                if node
                else None
            )

        table_node = find_child_r(shell, "BallisticTableConfig")
        table = None
        if table_node and table_node.ref:
            table = {
                "guid": table_node.ref["guid"],
                "path": table_node.ref["path"],
                "defined_in": table_node.defined_in,
                "origin": table_node.origin,
            }

        selected_origin = origin or (entity.chain[0].get("origin") if entity.chain else None)
        return {
            "status": entity.status,
            "resource": projectile_relpath,
            "origin": selected_origin,
            "physics": physics,
            "ai_ballistic_table": table,
            "ai_ballistic_validation": validate_aibt(
                projectile_relpath,
                table,
                physics,
            ),
        }
