#!/usr/bin/env python3
"""Index materialized vanilla resources exported from Workbench.

The Weapon_ARMA_X repository can contain parser-readable copies of mounted
Arma Reforger resources. Their adjacent .meta files use identities like:

    {LOCAL_IMPORT_GUID}Imported/VanillaSources/Prefabs/Weapons/...

The GUID belongs to the local materialization and must not be equated with a
live/base-game GUID referenced by ARMST. Cross-layer identity is therefore
resolved by the declared original resource path after Imported/VanillaSources/.

This module is read-only. It never writes, registers, moves, or mutates a
resource.
"""

from __future__ import annotations

import os

from et_parser import GUID_REF_RE, find_recursive, parse_file

IMPORTED_PREFIX = "Imported/VanillaSources/"
SNAPSHOT_KEY_PREFIX = "base_game_snapshot:"


def normalize_resource_path(path: str | None) -> str | None:
    if not path:
        return None
    return path.replace("\\", "/").lstrip("./").casefold()


def snapshot_key(original_path: str) -> str:
    return SNAPSHOT_KEY_PREFIX + original_path.replace("\\", "/").lstrip("./")


def _meta_identity(meta_resource) -> dict | None:
    if not meta_resource or meta_resource.kind != "meta":
        return None
    for node in find_recursive(meta_resource.root, "Name"):
        if not node.value:
            continue
        raw = str(node.value[0])
        match = GUID_REF_RE.match(raw)
        if not match:
            continue
        declared = match.group(2).replace("\\", "/")
        if not declared.startswith(IMPORTED_PREFIX):
            return None
        original = declared[len(IMPORTED_PREFIX):]
        if not original:
            return None
        return {
            "import_guid": match.group(1).upper(),
            "declared_name": declared,
            "original_path": original,
        }
    return None


def build_snapshot_index(root: str | None) -> dict:
    """Build a path-keyed read-only index of materialized vanilla resources.

    Returns a dictionary with:
      by_path   normalized original ResourceName -> record
      resources synthetic snapshot key -> parsed Resource
      metadata  synthetic snapshot key -> record
      issues    deterministic indexing/parse issues

    Duplicate original resource identities are rejected from by_path rather
    than guessed.
    """
    result = {
        "root": os.path.abspath(root) if root else None,
        "by_path": {},
        "resources": {},
        "metadata": {},
        "issues": [],
        "meta_count": 0,
        "resource_count": 0,
    }
    if not root or not os.path.isdir(root):
        return result

    candidates = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name for name in dirnames
            if name not in (".git", "__pycache__", ".venv", "venv")
        ]
        for filename in filenames:
            if not filename.lower().endswith(".meta"):
                continue
            candidates.append(os.path.join(dirpath, filename))

    for meta_path in sorted(candidates, key=lambda p: p.casefold()):
        result["meta_count"] += 1
        try:
            meta_resource = parse_file(meta_path, root)
        except Exception as exc:  # noqa: BLE001
            rel = os.path.relpath(meta_path, root).replace("\\", "/")
            result["issues"].append({
                "code": "SNAPSHOT_META_PARSE_FAILED",
                "path": rel,
                "detail": str(exc),
            })
            continue

        identity = _meta_identity(meta_resource)
        if not identity:
            continue

        physical_path = meta_path[:-5]  # remove trailing ".meta"
        ext = os.path.splitext(physical_path)[1].lower()
        if ext not in (".et", ".conf"):
            continue
        if not os.path.isfile(physical_path):
            rel = os.path.relpath(meta_path, root).replace("\\", "/")
            result["issues"].append({
                "code": "SNAPSHOT_RESOURCE_MISSING",
                "path": rel,
                "original_path": identity["original_path"],
            })
            continue

        norm = normalize_resource_path(identity["original_path"])
        key = snapshot_key(identity["original_path"])
        if norm in result["by_path"]:
            prior = result["by_path"][norm]
            result["issues"].append({
                "code": "SNAPSHOT_IDENTITY_AMBIGUOUS",
                "original_path": identity["original_path"],
                "paths": [
                    prior["physical_rel"],
                    os.path.relpath(physical_path, root).replace("\\", "/"),
                ],
            })
            # Remove the ambiguous identity from automatic resolution.
            result["by_path"][norm] = None
            continue

        try:
            parsed = parse_file(physical_path, root)
        except Exception as exc:  # noqa: BLE001
            rel = os.path.relpath(physical_path, root).replace("\\", "/")
            result["issues"].append({
                "code": "SNAPSHOT_RESOURCE_PARSE_FAILED",
                "path": rel,
                "original_path": identity["original_path"],
                "detail": str(exc),
            })
            continue

        record = {
            "key": key,
            "original_path": identity["original_path"],
            "declared_name": identity["declared_name"],
            "import_guid": identity["import_guid"],
            "physical_rel": os.path.relpath(
                physical_path, root
            ).replace("\\", "/"),
            "meta_rel": os.path.relpath(meta_path, root).replace("\\", "/"),
            "kind": parsed.kind,
            "class": parsed.et_class,
        }
        result["by_path"][norm] = record
        result["resources"][key] = parsed
        result["metadata"][key] = record
        result["resource_count"] += 1

    # Ambiguous identities are stored as None and intentionally unresolved.
    return result


def lookup_snapshot(snapshot: dict | None, resource_path: str | None) -> dict | None:
    if not snapshot:
        return None
    norm = normalize_resource_path(resource_path)
    if not norm:
        return None
    return snapshot.get("by_path", {}).get(norm)
