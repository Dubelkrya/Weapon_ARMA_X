"""
resolver_v2.py
==============

Multi-root inheritance and ammunition resolver for Arma Reforger text resources.

Design goals
------------
* Keep raw/local data separate from resolved/effective data.
* Resolve parents by the live `{GUID}path` reference first by path, then by a
  GUID learned from live references. `.meta Name` is metadata only.
* Merge serialized instances by instance id/GUID. For nodes without ids,
  match by name + occurrence within that name, not absolute sibling position.
* Preserve per-node provenance (`defined_in`, `origin`).
* Resolve MagazineComponent.AmmoMapping against MagazineConfig.AmmoResourceArray.
* Keep projectile physics separate from AI ballistic-table configuration.
* Never infer missing values from filenames.

The module intentionally contains no ARMST- or vanilla-specific file data. Point
it at one or more Workbench resource roots at runtime.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
import argparse
import json
import os
import re
from typing import Dict, Iterator, List, Optional, Sequence, Tuple

from et_parser import GUID_REF_RE, Node, Resource, find_recursive, parse_file


TEXT_EXTENSIONS = {".et", ".conf", ".meta"}
PROJECTILE_PHYSICS_FIELDS = (
    "InitSpeed",
    "InitSpeedVariation",
    "DispersionMultiplier",
    "Mass",
    "TumblingDamageMultiplier",
    "MushroomingDamageMultiplier",
    "PenetrationDepth",
    "PenetrationSpeed",
    "PenetrationDensity",
    "AirDrag",
)
CALIBER_TOKEN_RE = re.compile(r"(?<!\d)(\d{1,3}(?:[._]\d+)?x\d{2,3}r?)(?!\d)", re.I)


def _norm_path(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _norm_key(path: str) -> str:
    return _norm_path(path).casefold()


def _ref_from_token(value: object) -> Optional[dict]:
    m = GUID_REF_RE.match(str(value))
    if not m:
        return None
    return {"guid": m.group(1).upper(), "path": _norm_path(m.group(2)), "raw": str(value)}


def iter_nodes(node: Node) -> Iterator[Node]:
    yield node
    for child in node.children:
        yield from iter_nodes(child)


@dataclass(frozen=True)
class ResourceRoot:
    label: str
    path: str
    priority: int = 0

    def normalized(self) -> "ResourceRoot":
        return ResourceRoot(self.label, os.path.abspath(self.path), self.priority)


@dataclass
class ResourceRecord:
    relpath: str
    abspath: str
    origin: str
    priority: int
    resource: Resource

    @property
    def kind(self) -> str:
        return self.resource.kind

    @property
    def parent(self) -> Optional[dict]:
        return self.resource.parent


@dataclass
class RNode:
    """Resolved node with source provenance."""

    name: str
    type: Optional[str] = None
    id: Optional[str] = None
    value: List[object] = field(default_factory=list)
    children: List["RNode"] = field(default_factory=list)
    append: bool = False
    line: int = 0
    ref: Optional[dict] = None
    defined_in: Optional[str] = None
    origin: Optional[str] = None

    def to_dict(self) -> dict:
        out = {"name": self.name}
        if self.type is not None:
            out["type"] = self.type
        if self.id is not None:
            out["id"] = self.id
        if self.value:
            out["value"] = list(self.value)
        if self.ref is not None:
            out["ref"] = dict(self.ref)
        if self.append:
            out["append"] = True
        if self.line:
            out["line"] = self.line
        if self.defined_in is not None:
            out["defined_in"] = self.defined_in
        if self.origin is not None:
            out["origin"] = self.origin
        if self.children:
            out["children"] = [c.to_dict() for c in self.children]
        return out


@dataclass
class ResolutionResult:
    resource: str
    status: str
    chain: List[dict]
    missing_parent: Optional[dict]
    raw: Optional[RNode]
    resolved: Optional[RNode]

    def to_dict(self) -> dict:
        return {
            "resource": self.resource,
            "status": self.status,
            "chain": self.chain,
            "missing_parent": self.missing_parent,
            "raw": self.raw.to_dict() if self.raw else None,
            "resolved": self.resolved.to_dict() if self.resolved else None,
        }


def _clone(node: RNode) -> RNode:
    return RNode(
        name=node.name,
        type=node.type,
        id=node.id,
        value=list(node.value),
        children=[_clone(c) for c in node.children],
        append=node.append,
        line=node.line,
        ref=dict(node.ref) if node.ref else None,
        defined_in=node.defined_in,
        origin=node.origin,
    )


def rnode_from_parsed(node: Node, relpath: str, origin: str) -> RNode:
    return RNode(
        name=node.name,
        type=node.type,
        id=node.id,
        value=list(node.value),
        children=[rnode_from_parsed(c, relpath, origin) for c in node.children],
        append=node.append,
        line=node.line,
        ref=dict(node.ref) if node.ref else None,
        defined_in=relpath,
        origin=origin,
    )


def _is_scalar_array(node: RNode) -> bool:
    return bool(node.children) and all(c.name == "__elem__" for c in node.children)


def _scope_keys(nodes: Sequence[RNode]) -> List[Tuple[str, str, object]]:
    """Stable merge keys: instance id, otherwise name + same-name occurrence."""
    occurrences: Dict[str, int] = defaultdict(int)
    keys: List[Tuple[str, str, object]] = []
    for node in nodes:
        if node.id is not None:
            keys.append((node.name, "id", node.id))
            continue
        occ = occurrences[node.name]
        occurrences[node.name] += 1
        keys.append((node.name, "occ", occ))
    return keys


def merge_scopes(parent_nodes: Sequence[RNode], child_nodes: Sequence[RNode]) -> List[RNode]:
    if not parent_nodes:
        return [_clone(c) for c in child_nodes]
    if not child_nodes:
        return [_clone(p) for p in parent_nodes]

    parent_map = dict(zip(_scope_keys(parent_nodes), parent_nodes))
    child_map = dict(zip(_scope_keys(child_nodes), child_nodes))
    out: List[RNode] = []

    for key, child in child_map.items():
        parent = parent_map.get(key)
        out.append(_clone(child) if parent is None else merge_pair(parent, child))

    for key, parent in parent_map.items():
        if key not in child_map:
            out.append(_clone(parent))
    return out


def merge_pair(parent: RNode, child: RNode) -> RNode:
    if _is_scalar_array(parent) or _is_scalar_array(child):
        if child.append and _is_scalar_array(parent):
            children = [_clone(c) for c in parent.children] + [_clone(c) for c in child.children]
            value = list(parent.value) + list(child.value)
        elif child.children or child.value:
            children = [_clone(c) for c in child.children]
            value = list(child.value)
        else:
            children = [_clone(c) for c in parent.children]
            value = list(parent.value)
        winner = child if (child.children or child.value) else parent
        return RNode(
            child.name,
            child.type or parent.type,
            child.id if child.id is not None else parent.id,
            value,
            children,
            child.append,
            child.line,
            dict(child.ref) if child.ref else (dict(parent.ref) if parent.ref else None),
            winner.defined_in,
            winner.origin,
        )

    has_child_value = bool(child.value)
    winner = child if has_child_value else parent
    return RNode(
        child.name,
        child.type or parent.type,
        child.id if child.id is not None else parent.id,
        list(child.value) if has_child_value else list(parent.value),
        merge_scopes(parent.children, child.children),
        child.append,
        child.line,
        dict(child.ref) if child.ref else (dict(parent.ref) if parent.ref else None),
        winner.defined_in,
        winner.origin,
    )


def find_child_r(node: Optional[RNode], name: str) -> Optional[RNode]:
    if node is None:
        return None
    for child in node.children:
        if child.name == name:
            return child
    return None


def find_recursive_r(node: Optional[RNode], name: str) -> List[RNode]:
    if node is None:
        return []
    out: List[RNode] = []
    for child in node.children:
        if child.name == name:
            out.append(child)
        out.extend(find_recursive_r(child, name))
    return out


def array_values_r(node: Optional[RNode]) -> List[object]:
    """Flatten serialized arrays such as AmmoMapping { 0 0 1 }."""
    if node is None:
        return []
    out = list(node.value)
    for child in node.children:
        if child.name == "__elem__":
            out.extend(child.value)
    return out


def scalar_r(node: Optional[RNode]) -> Optional[object]:
    if node is None or not node.value:
        return None
    return node.value[0]


class ResourceStore:
    """Index and resolve resources across multiple Workbench roots."""

    def __init__(self, roots: Sequence[ResourceRoot]):
        self.roots = sorted(
            (r.normalized() for r in roots), key=lambda r: r.priority, reverse=True
        )
        self.records: Dict[str, ResourceRecord] = {}
        self.records_by_key: Dict[str, ResourceRecord] = {}
        self.meta_name_guid_by_path: Dict[str, str] = {}
        self.live_guid_to_path: Dict[str, str] = {}
        self.live_guid_by_path: Dict[str, str] = {}
        self.warnings: List[dict] = []

    def scan(self) -> None:
        self.records.clear()
        self.records_by_key.clear()
        self.meta_name_guid_by_path.clear()
        self.live_guid_to_path.clear()
        self.live_guid_by_path.clear()
        self.warnings.clear()

        # Higher-priority roots win path collisions.
        for root in self.roots:
            if not os.path.isdir(root.path):
                self.warnings.append(
                    {"category": "ROOT_MISSING", "root": root.label, "path": root.path}
                )
                continue
            for dirpath, _dirs, filenames in os.walk(root.path):
                for filename in filenames:
                    ext = os.path.splitext(filename)[1].lower()
                    if ext not in TEXT_EXTENSIONS:
                        continue
                    abspath = os.path.join(dirpath, filename)
                    relpath = _norm_path(os.path.relpath(abspath, root.path))
                    key = _norm_key(relpath)
                    if key in self.records_by_key:
                        continue
                    try:
                        parsed = parse_file(abspath, root.path)
                    except Exception as exc:  # noqa: BLE001
                        self.warnings.append(
                            {
                                "category": "PARSE",
                                "resource": relpath,
                                "origin": root.label,
                                "message": str(exc),
                            }
                        )
                        continue
                    rec = ResourceRecord(relpath, abspath, root.label, root.priority, parsed)
                    self.records[relpath] = rec
                    self.records_by_key[key] = rec

        self._index_meta_names()
        self._index_live_references()

    def _index_meta_names(self) -> None:
        for record in self.records.values():
            if record.kind != "meta":
                continue
            name_nodes = find_recursive(record.resource.root, "Name")
            if not name_nodes or not name_nodes[0].value:
                continue
            ref = _ref_from_token(name_nodes[0].value[0])
            if not ref:
                continue
            actual = re.sub(r"\.meta$", "", record.relpath, flags=re.I)
            self.meta_name_guid_by_path[_norm_key(actual)] = ref["guid"]

    def _index_live_references(self) -> None:
        """Learn live GUIDs from .et/.conf references, never from .meta Name."""

        def accept(ref: Optional[dict]) -> None:
            if not ref or not ref.get("path"):
                return
            path = _norm_path(ref["path"])
            guid = ref["guid"].upper()
            self.live_guid_to_path.setdefault(guid, path)
            self.live_guid_by_path.setdefault(_norm_key(path), guid)

        for record in self.records.values():
            if record.kind not in ("et", "conf"):
                continue
            if record.kind == "et":
                accept(record.parent)
            if record.resource.root is None:
                continue
            for node in iter_nodes(record.resource.root):
                accept(node.ref)

    def get(self, relpath: str) -> Optional[ResourceRecord]:
        return self.records_by_key.get(_norm_key(relpath))

    def resolve_ref(self, guid: Optional[str], path: Optional[str]) -> dict:
        if path:
            record = self.get(path)
            if record:
                return {
                    "status": "local",
                    "resource": record.relpath,
                    "origin": record.origin,
                    "guid": guid,
                    "resolved_by": "path",
                }
        if guid:
            live_path = self.live_guid_to_path.get(guid.upper())
            if live_path:
                record = self.get(live_path)
                if record:
                    return {
                        "status": "local",
                        "resource": record.relpath,
                        "origin": record.origin,
                        "guid": guid.upper(),
                        "resolved_by": "live_guid",
                    }
        return {"status": "external", "guid": guid, "path": path}

    def build_chain(self, relpath: str, max_depth: int = 64) -> Tuple[List[dict], Optional[dict]]:
        chain: List[dict] = []
        seen = set()
        current = self.get(relpath)
        if current is None:
            return chain, {"status": "missing_resource", "path": relpath}

        while current is not None and max_depth > 0:
            max_depth -= 1
            key = _norm_key(current.relpath)
            if key in seen:
                loop = {"status": "loop", "resource": current.relpath, "origin": current.origin}
                chain.append(loop)
                return chain, loop
            seen.add(key)
            chain.append(
                {
                    "status": "local",
                    "resource": current.relpath,
                    "origin": current.origin,
                    "class": current.resource.et_class,
                    "live_guid": self.live_guid_by_path.get(key),
                    "meta_name_guid": self.meta_name_guid_by_path.get(key),
                }
            )
            parent = current.parent
            if not parent:
                return chain, None
            resolved = self.resolve_ref(parent.get("guid"), parent.get("path"))
            if resolved["status"] != "local":
                return chain, {
                    "status": "external_parent",
                    "guid": parent.get("guid"),
                    "path": parent.get("path"),
                    "defined_in": current.relpath,
                }
            current = self.get(resolved["resource"])

        if max_depth <= 0:
            return chain, {"status": "depth_limit", "path": relpath}
        return chain, None

    def resolve_entity(self, relpath: str) -> ResolutionResult:
        record = self.get(relpath)
        if record is None or record.kind != "et":
            return ResolutionResult(relpath, "missing", [], None, None, None)

        chain, missing = self.build_chain(relpath)
        local_records = [self.get(c["resource"]) for c in chain if c.get("status") == "local"]
        local_records = [r for r in local_records if r is not None]
        if not local_records:
            return ResolutionResult(relpath, "missing", chain, missing, None, None)

        raw = rnode_from_parsed(record.resource.root, record.relpath, record.origin)
        trees = [
            rnode_from_parsed(r.resource.root, r.relpath, r.origin)
            for r in local_records
        ]
        resolved = trees[-1]
        for child_tree in reversed(trees[:-1]):
            resolved = merge_pair(resolved, child_tree)

        status = "resolved" if missing is None else "partial"
        return ResolutionResult(record.relpath, status, chain, missing, raw, resolved)

    def _resolved_conf_root(self, relpath: str) -> Optional[RNode]:
        record = self.get(relpath)
        if record is None or record.kind != "conf":
            return None
        return rnode_from_parsed(record.resource.root, record.relpath, record.origin)

    def ammo_resource_array(self, conf_relpath: str) -> dict:
        root = self._resolved_conf_root(conf_relpath)
        if root is None:
            return {"status": "missing_config", "resource": conf_relpath, "projectiles": []}
        arrays = find_recursive_r(root, "AmmoResourceArray")
        if not arrays:
            return {"status": "missing_array", "resource": conf_relpath, "projectiles": []}

        projectiles = []
        for elem in arrays[0].children:
            ref = elem.ref
            if ref is None and elem.value:
                ref = _ref_from_token(elem.value[0])
            if not ref:
                continue
            resolved = self.resolve_ref(ref["guid"], ref["path"])
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
        return {"status": "resolved", "resource": conf_relpath, "projectiles": projectiles}

    def resolve_magazine_ammo(self, magazine_relpath: str) -> dict:
        entity = self.resolve_entity(magazine_relpath)
        if entity.resolved is None:
            return {"status": "missing_magazine", "resource": magazine_relpath}

        mag_nodes = find_recursive_r(entity.resolved, "MagazineComponent")
        if not mag_nodes:
            return {"status": "missing_magazine_component", "resource": magazine_relpath}
        mag = mag_nodes[0]

        max_ammo_node = find_child_r(mag, "MaxAmmo")
        max_ammo = scalar_r(max_ammo_node)
        config_node = find_child_r(mag, "AmmoConfig")
        config_ref = config_node.ref if config_node else None
        mapping_node = find_child_r(mag, "AmmoMapping")
        mapping = array_values_r(mapping_node)

        result = {
            "resource": magazine_relpath,
            "inheritance_status": entity.status,
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
            "defined_in": config_node.defined_in,
            "resolved": cfg_resolved["status"],
            "target": cfg_resolved.get("resource"),
        }
        if cfg_resolved["status"] != "local":
            result["status"] = "external_ammo_config"
            return result

        ammo_array = self.ammo_resource_array(cfg_resolved["resource"])
        projectiles = ammo_array["projectiles"]
        result["projectiles"] = projectiles

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

    def projectile_physics(self, projectile_relpath: str) -> dict:
        entity = self.resolve_entity(projectile_relpath)
        if entity.resolved is None:
            return {"status": "missing_projectile", "resource": projectile_relpath}
        shells = find_recursive_r(entity.resolved, "ShellMoveComponent")
        if not shells:
            return {"status": "missing_shell_component", "resource": projectile_relpath}
        shell = shells[0]

        physics = {}
        for name in PROJECTILE_PHYSICS_FIELDS:
            node = find_child_r(shell, name)
            physics[name] = (
                {"value": scalar_r(node), "defined_in": node.defined_in, "origin": node.origin}
                if node else None
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

        return {
            "status": entity.status,
            "resource": projectile_relpath,
            "physics": physics,
            "ai_ballistic_table": table,
            "ai_ballistic_validation": validate_aibt(projectile_relpath, table, physics),
        }


def _caliber_token(path: str) -> Optional[str]:
    text = os.path.basename(path).replace(".", "")
    m = CALIBER_TOKEN_RE.search(text)
    return m.group(1).lower().replace("_", "").replace(".", "") if m else None


def validate_aibt(projectile_path: str, table: Optional[dict], physics: dict) -> dict:
    """Keep AI ballistic-table validation separate from player projectile physics."""
    if not table:
        return {"status": "missing", "severity": "info", "note": "No AI ballistic table configured."}

    projectile_caliber = _caliber_token(projectile_path)
    table_caliber = _caliber_token(table["path"])
    fingerprint_input = {
        key: (value or {}).get("value")
        for key, value in physics.items()
        if key in PROJECTILE_PHYSICS_FIELDS
    }
    fingerprint = json.dumps(fingerprint_input, sort_keys=True, separators=(",", ":"))

    if projectile_caliber and table_caliber and projectile_caliber != table_caliber:
        return {
            "status": "suspicious_caliber_mismatch",
            "severity": "warning",
            "projectile_caliber_token": projectile_caliber,
            "table_caliber_token": table_caliber,
            "physics_fingerprint": fingerprint,
            "note": (
                "AI ballistic-table filename suggests a different caliber. Treat as an "
                "AI-aiming/table-regeneration anomaly, not as proof that player projectile "
                "physics use that table."
            ),
        }

    return {
        "status": "configured_unverified",
        "severity": "info",
        "projectile_caliber_token": projectile_caliber,
        "table_caliber_token": table_caliber,
        "physics_fingerprint": fingerprint,
        "note": "Regenerate the AI ballistic table whenever projectile physics change.",
    }


def _parse_root_arg(value: str) -> ResourceRoot:
    parts = value.split("=", 2)
    if len(parts) == 2:
        label, path = parts
        return ResourceRoot(label, path, 0)
    if len(parts) == 3:
        label, priority, path = parts
        return ResourceRoot(label, path, int(priority))
    raise argparse.ArgumentTypeError("root must be label=path or label=priority=path")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Arma Reforger multi-root resolver v2")
    parser.add_argument(
        "--root", action="append", type=_parse_root_arg, required=True,
        help="Resource root as label=path or label=priority=path; higher priority wins collisions.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--resource", help="Resolve an .et inheritance chain.")
    group.add_argument("--magazine", help="Resolve magazine AmmoConfig + AmmoMapping.")
    group.add_argument("--projectile", help="Resolve projectile physics + AI ballistic table.")
    args = parser.parse_args(argv)

    store = ResourceStore(args.root)
    store.scan()
    if args.resource:
        payload = store.resolve_entity(args.resource).to_dict()
    elif args.magazine:
        payload = store.resolve_magazine_ammo(args.magazine)
    else:
        payload = store.projectile_physics(args.projectile)
    payload["resolver_warnings"] = store.warnings
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
