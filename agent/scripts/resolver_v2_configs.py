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


def _norm_relpath(path: Optional[str]) -> str:
    return str(path or "").replace("\\", "/").lstrip("./").casefold()


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
            result.resolved = self._hydrate_config_refs(result.resolved)
        return result
