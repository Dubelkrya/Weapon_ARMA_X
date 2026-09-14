"""Nested `.conf` hydration for resolver_v2.

Serialized weapon instances frequently reference reusable configuration blocks,
for example FireMode_Auto.conf or recoil configs. Entity inheritance alone is
therefore not enough: the referenced config must be merged first, then local
instance fields must override it.
"""

from __future__ import annotations

from typing import Optional, Tuple

from resolver_v2 import (
    RNode,
    ResourceStore,
    _clone,
    merge_pair,
    rnode_from_parsed,
)


class HydratedResourceStore(ResourceStore):
    """ResourceStore that resolves nested `.conf` templates in entity trees."""

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

    def _hydrate_config_refs(
        self, node: RNode, stack: Optional[Tuple[str, ...]] = None
    ) -> RNode:
        stack = stack or ()
        current = _clone(node)

        if current.ref and str(current.ref.get("path", "")).lower().endswith(".conf"):
            resolved = self.resolve_ref(
                current.ref.get("guid"), current.ref.get("path")
            )
            target = resolved.get("resource")
            if resolved.get("status") == "local" and target:
                if target in stack:
                    self.warnings.append(
                        {
                            "category": "CONFIG_REF_LOOP",
                            "resource": target,
                            "stack": list(stack),
                        }
                    )
                else:
                    template = self._config_template_node(target)
                    if template is not None:
                        template = self._hydrate_config_refs(
                            template, stack + (target,)
                        )
                        current = merge_pair(template, current)

        current.children = [
            self._hydrate_config_refs(child, stack) for child in current.children
        ]
        return current

    def resolve_entity(self, relpath: str):
        result = super().resolve_entity(relpath)
        if result.resolved is not None:
            result.resolved = self._hydrate_config_refs(result.resolved)
        return result
