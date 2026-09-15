"""Production origin-pinning guard for resolver v2 strict identity.

The base hydrated store historically falls back to the highest-priority path
candidate when an explicit ``origin`` has no matching record.  That is unsafe
once a dependency has already been resolved to a concrete origin: a later
lookup must never silently jump from read-only vanilla back into ARMST (or the
reverse).

Keep this guard isolated while PR #2 remains draft so the behavior is easy to
review and regression-test before consolidating it into the base strict store.
"""

from __future__ import annotations

from typing import Optional

from resolver_v2 import ResourceRecord
from resolver_v2_strict import StrictHydratedResourceStore


class OriginPinnedStrictHydratedResourceStore(StrictHydratedResourceStore):
    """Strict store where an explicit origin is a hard identity constraint."""

    def _record_for(
        self, relpath: str, origin: Optional[str] = None
    ) -> Optional[ResourceRecord]:
        candidates, _mode = self._candidate_records(relpath)
        if origin is not None:
            same_origin = [record for record in candidates if record.origin == origin]
            if len(same_origin) == 1:
                return same_origin[0]
            # Critical rule: once origin is explicit, absence/ambiguity in that
            # origin is a miss. Never fall back to another root by priority.
            return None
        return candidates[0] if candidates else None
