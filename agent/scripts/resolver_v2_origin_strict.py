"""Production origin/dependency guard for resolver-v2 strict identity.

An explicit origin is a hard identity constraint once a concrete resource has
already been selected.  In addition, dependency traversal must respect root
precedence: a lower/read-only root may not resolve a serialized dependency to a
higher-priority editable overlay merely because that is the only copy currently
available on disk.

For the project root model this means vanilla can never silently depend upward
on ARMST, while ARMST may still reference vanilla.  The rule is expressed in
terms of root priority so the strict store remains usable with additional
read-only dependency roots.
"""

from __future__ import annotations

from typing import List, Optional

from resolver_v2 import ResourceRecord
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
            # Once origin is explicit, absence/ambiguity in that origin is a
            # miss. Never fall back to another root by priority.
            return None
        return candidates[0] if candidates else None

    def _eligible_dependency_records(
        self,
        records: List[ResourceRecord],
        origin_hint: Optional[str],
    ) -> List[ResourceRecord]:
        """Filter candidates to roots a source origin is allowed to depend on."""
        if origin_hint is None:
            return list(records)
        source_priority = self._priority_by_origin.get(origin_hint)
        if source_priority is None:
            # Unknown origins are never allowed to jump to a different root.
            return [record for record in records if record.origin == origin_hint]
        return [record for record in records if record.priority <= source_priority]

    def _index_strict_guid_evidence(self) -> None:
        """Index GUID ownership only from dependency-eligible path candidates.

        The parent implementation could incorrectly prove a vanilla GUID as
        belonging to an ARMST-only path when the vanilla copy had not yet been
        materialized.  Filtering before proving ownership prevents incomplete
        local datasets from turning upward overlay candidates into evidence.
        """
        for source in self._all_records():
            for ref in self._iter_record_refs(source):
                guid = str(ref.get("guid") or "").upper()
                path = str(ref.get("path") or "")
                if not guid or not path:
                    continue
                self._guid_observed_paths.setdefault(guid, set()).add(path.casefold())
                candidates, _mode = self._candidate_records(path)
                eligible = self._eligible_dependency_records(candidates, source.origin)
                if len(eligible) == 1:
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

        # Proven GUID ownership may resolve an alternate/short path, but only
        # inside dependency-eligible roots.
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

        blocked = [
            record
            for record in all_candidates
            if _identity(record) not in {_identity(item) for item in candidates}
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
