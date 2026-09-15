"""Production origin/dependency guard for resolver-v2 strict identity.

An explicit origin is a hard identity constraint once a concrete resource has
already been selected. In addition, dependency traversal must respect root
precedence: a lower/read-only root may not resolve a serialized dependency to a
higher-priority editable overlay merely because that is the only copy currently
available on disk.

For the project root model this means vanilla can never silently depend upward
on ARMST, while ARMST may still reference vanilla. Live GUID evidence is learned
only from serialized `.et/.conf` data; `.meta Name` is metadata and must never
become resource-identity proof.

Materialized `.conf` files preserve an important stronger identity signal in
their root declaration, for example::

    MagazineConfig "{GUID}Configs/Weapons/Ammo/Ammo_545x39.conf" {

That left-hand ResourceName identifies the config resource itself. It is not an
instance GUID and it is not a dependency edge. When its path exactly matches the
record path, the GUID is authoritative local ownership evidence. This matters
especially when ARMST and vanilla contain the same virtual config path.

ARMST is a complete editable tree while the materialized vanilla tree is only a
partial dependency snapshot. Therefore an ARMST reference to an ARMST same-path
candidate is not, by itself, proof that the serialized GUID belongs to that
ARMST resource: the referenced vanilla resource may simply not be materialized
yet. Such references may resolve by their currently unique path, but they are
not promoted into reusable GUID ownership evidence.
"""

from __future__ import annotations

from typing import List, Optional

from resolver_v2 import ResourceRecord, _norm_key, _ref_from_token, iter_nodes
from resolver_v2_strict import StrictHydratedResourceStore, _identity


class OriginPinnedStrictHydratedResourceStore(StrictHydratedResourceStore):
    """Strict store with hard origin pinning and one-way dependency safety."""

    def __init__(self, roots):
        super().__init__(roots)
        self._priority_by_origin = {root.label: root.priority for root in self.roots}

    def _record_for(
        self, relpath: str, origin: Optional[str] = None
    ) -> Optional[ResourceRecord]:
        candidates, _mode = self._candidate_records(relpath)
        if origin is not None:
            same_origin = [record for record in candidates if record.origin == origin]
            if len(same_origin) == 1:
                return same_origin[0]
            return None
        return candidates[0] if candidates else None

    @staticmethod
    def _declared_conf_owner_ref(record: ResourceRecord) -> Optional[dict]:
        """Return a config root's serialized self ResourceName when exact."""
        if record.kind != "conf" or record.resource.root is None:
            return None
        root_node = None
        for child in record.resource.root.children:
            if child.name == "__elem__":
                continue
            root_node = child
            break
        if root_node is None or not root_node.id:
            return None
        ref = _ref_from_token(str(root_node.id))
        if not ref or not ref.get("guid") or not ref.get("path"):
            return None
        if _norm_key(ref["path"]) != _norm_key(record.relpath):
            return None
        return ref

    @classmethod
    def _iter_record_refs(cls, record: ResourceRecord):
        """Yield dependency refs, excluding config owner identity and `.meta`."""
        if record.kind not in ("et", "conf"):
            return
        if record.kind == "et" and record.parent:
            yield record.parent

        owner_ref = cls._declared_conf_owner_ref(record)
        owner_guid = str((owner_ref or {}).get("guid") or "").upper()
        owner_path = _norm_key(str((owner_ref or {}).get("path") or ""))

        root = record.resource.root
        if root is None:
            return
        for node in iter_nodes(root):
            if not node.ref:
                continue
            ref_guid = str(node.ref.get("guid") or "").upper()
            ref_path = _norm_key(str(node.ref.get("path") or ""))
            if owner_ref and ref_guid == owner_guid and ref_path == owner_path:
                continue
            yield node.ref

    def _eligible_dependency_records(
        self,
        records: List[ResourceRecord],
        origin_hint: Optional[str],
    ) -> List[ResourceRecord]:
        if origin_hint is None:
            return list(records)
        source_priority = self._priority_by_origin.get(origin_hint)
        if source_priority is None:
            return [record for record in records if record.origin == origin_hint]
        return [record for record in records if record.priority <= source_priority]

    def _reference_can_prove_guid_owner(
        self,
        source: ResourceRecord,
        target: ResourceRecord,
    ) -> bool:
        if source.priority < self._highest_priority:
            return target.priority <= source.priority
        return target.priority < source.priority

    def _index_strict_guid_evidence(self) -> None:
        """Index config owner declarations, then safe dependency evidence."""
        for record in self._all_records():
            owner = self._declared_conf_owner_ref(record)
            if not owner:
                continue
            guid = str(owner.get("guid") or "").upper()
            path = str(owner.get("path") or "")
            self._guid_observed_paths.setdefault(guid, set()).add(_norm_key(path))
            self._add_guid_target(guid, record)

        for source in self._all_records():
            for ref in self._iter_record_refs(source):
                guid = str(ref.get("guid") or "").upper()
                path = str(ref.get("path") or "")
                if not guid or not path:
                    continue
                self._guid_observed_paths.setdefault(guid, set()).add(_norm_key(path))
                candidates, _mode = self._candidate_records(path)
                eligible = self._eligible_dependency_records(candidates, source.origin)
                if (
                    len(eligible) == 1
                    and self._reference_can_prove_guid_owner(source, eligible[0])
                ):
                    self._add_guid_target(guid, eligible[0])

    def resolve_ref(
        self,
        guid: Optional[str],
        path: Optional[str],
        origin_hint: Optional[str] = None,
    ) -> dict:
        all_candidates, mode = self._candidate_records(path)
        candidates = self._eligible_dependency_records(all_candidates, origin_hint)
        all_guid_records = self._guid_records(guid)
        guid_records = self._eligible_dependency_records(all_guid_records, origin_hint)
        candidate_ids = {_identity(record) for record in candidates}
        guid_matches = [record for record in guid_records if _identity(record) in candidate_ids]

        if len(guid_matches) == 1:
            return self._resolved_ref(guid_matches[0], guid, f"guid+{mode}", candidates)
        if len(guid_matches) > 1:
            return self._ambiguous_ref(
                guid, path, candidates, "guid_matches_multiple_records", guid_matches
            )

        if all_guid_records and not guid_records:
            return {
                "status": "external",
                "reason": "guid_target_not_dependency_eligible",
                "guid": str(guid).upper() if guid else None,
                "path": path,
                "candidates": self._candidate_payload(candidates),
                "guid_candidates": self._candidate_payload(all_guid_records),
            }

        if not candidates and len(guid_records) == 1:
            return self._resolved_ref(guid_records[0], guid, "guid_evidence", guid_records)

        if len(candidates) == 1:
            if guid_records and all(
                _identity(record) != _identity(candidates[0]) for record in guid_records
            ):
                return self._ambiguous_ref(
                    guid, path, candidates, "guid_path_conflict", guid_records
                )
            return self._resolved_ref(candidates[0], guid, mode, candidates)

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

        candidate_ids = {_identity(item) for item in candidates}
        blocked = [
            record for record in all_candidates if _identity(record) not in candidate_ids
        ]
        result = {
            "status": "external",
            "guid": str(guid).upper() if guid else None,
            "path": path,
        }
        if blocked:
            result["reason"] = "upward_dependency_blocked"
            result["candidates"] = self._candidate_payload(blocked)
        return result
