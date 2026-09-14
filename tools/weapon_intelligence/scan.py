from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Optional

from enfusion_text import (
    Document,
    Node,
    iter_resource_refs,
    node_value,
    parent_resource,
    parse_file,
    parse_resource_ref,
    parse_guid_token,
    strip_comments,
)


RESOURCE_EXTENSIONS = {".et", ".conf", ".meta"}
SCRIPT_EXTENSION = ".c"
MAX_INHERITANCE_DEPTH = 64

CLASS_RE = re.compile(
    r"^\s*(?:(modded)\s+)?(class|interface)\s+([A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*:\s*([A-Za-z_][A-Za-z0-9_]*))?"
)
METHOD_RE = re.compile(
    r"^\s*(?:(override|static|protected|private|public|sealed|proto|native|event)\s+)*"
    r"([A-Za-z_][A-Za-z0-9_<>,\[\].:]*)\s+"
    r"([A-Za-z_][A-Za-z0-9_]*)\s*\(([^)]*)\)"
)
CONTROL_NAMES = {"if", "for", "while", "switch", "foreach", "return", "else", "catch"}


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def safe_id(text: str) -> str:
    text = text.replace("\\", "/").rsplit("/", 1)[-1]
    text = text.rsplit(".", 1)[0]
    slug = re.sub(r"[^A-Za-z0-9_]+", "_", text).strip("_").lower()
    return slug or "resource"


def atomic_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(path)


def atomic_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(text, encoding="utf-8")
    temp.replace(path)


def rel_posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def first_node(document: Document, name: str) -> Optional[Node]:
    return document.first_node(name)


def first_node_declared_as(document: Document, declared_class: str) -> Optional[Node]:
    for node in document.walk():
        if declared_class in node.header_tokens:
            return node
    return None


def first_child(node: Optional[Node], name: str) -> Optional[Node]:
    if node is None:
        return None
    for child in node.children:
        if child.name == name:
            return child
    return None


def node_header_ref(node: Optional[Node]) -> Optional[dict[str, str]]:
    if node is None:
        return None
    for token in node.header_tokens[1:]:
        ref = parse_resource_ref(token)
        if ref:
            return ref
    return None


def node_instance_guid(node: Optional[Node]) -> Optional[str]:
    if node is None:
        return None
    for token in node.header_tokens[1:]:
        guid = parse_guid_token(token)
        if guid:
            return guid
    return None


def extract_display_name(document: Document) -> Optional[str]:
    weapon = first_node(document, "WeaponComponent")
    if weapon:
        ui = first_child(weapon, "UIInfo")
        name = node_value(ui, "Name")
        if isinstance(name, str) and name:
            return name
    for node in document.walk():
        if node.name == "ItemDisplayName":
            name = node_value(node, "Name")
            if isinstance(name, str) and name:
                return name
    return None


def extract_recoil(document: Document) -> dict[str, Any]:
    recoil: dict[str, Any] = {}
    for node in document.walk():
        if node.name not in {"LinearData", "AngularData", "TurnOffsetData"}:
            continue
        if len(node.header_tokens) < 2 or node.header_tokens[1] != "RecoilData":
            continue
        magnitudes = node_value(node, "Curve Magnitudes")
        if magnitudes is not None:
            recoil[node.name] = {
                "curve_magnitudes": magnitudes if isinstance(magnitudes, list) else [magnitudes],
                "defined_line": node.line,
            }
    return recoil


def extract_fire_modes(document: Document) -> list[dict[str, Any]]:
    modes: list[dict[str, Any]] = []
    for fire_modes in document.find_nodes("FireModes"):
        for child in fire_modes.children:
            if child.name != "BaseFireMode":
                continue
            modes.append(
                {
                    "instance_guid": node_instance_guid(child),
                    "rounds_per_minute": node_value(child, "RoundsPerMinute"),
                    "max_burst": node_value(child, "MaxBurst"),
                    "ui_name": node_value(child, "UIName"),
                    "defined_line": child.line,
                }
            )
    return modes


def extract_attachment_slots(document: Document) -> list[dict[str, Any]]:
    slots: list[dict[str, Any]] = []
    for node in document.find_nodes("AttachmentSlotComponent"):
        slot = first_child(node, "AttachmentSlot")
        attachment_type = first_child(node, "AttachmentType")
        slot_name = None
        if slot and len(slot.header_tokens) >= 3:
            slot_name = slot.header_tokens[2]
        type_name = None
        if attachment_type and len(attachment_type.header_tokens) >= 2:
            type_name = attachment_type.header_tokens[1]
        slots.append(
            {
                "component_guid": node_instance_guid(node),
                "enabled": node_value(node, "Enabled"),
                "slot_name": slot_name,
                "slot_enabled": node_value(slot, "Enabled"),
                "attachment_type": type_name,
                "defined_line": node.line,
            }
        )
    return slots


def extract_weapon(document: Document, rel_path: str) -> dict[str, Any]:
    muzzle = first_node(document, "MuzzleComponent")
    phys = first_node_declared_as(document, "ItemPhysicalAttributes")
    melee = first_node(document, "SCR_MeleeWeaponProperties")
    magwell_node = first_child(muzzle, "MagazineWell") if muzzle else None
    magwell = None
    if magwell_node and len(magwell_node.header_tokens) >= 2:
        magwell = magwell_node.header_tokens[1]

    default_mag_prop = muzzle.first_property("MagazineTemplate") if muzzle else None
    default_mag = None
    if default_mag_prop and default_mag_prop.values:
        default_mag = parse_resource_ref(default_mag_prop.values[0])

    return {
        "id": safe_id(rel_path),
        "identity": {
            "name": extract_display_name(document),
            "resource": rel_path,
            "parent": parent_resource(document),
        },
        "physical": {
            "weight": node_value(phys, "Weight"),
            "volume": node_value(phys, "ItemVolume"),
            "dimensions": node_value(phys, "ItemDimensions"),
        },
        "melee": {"damage": node_value(melee, "m_fDamage")},
        "muzzle": {
            "bullet_init_speed_coef": node_value(muzzle, "BulletInitSpeedCoef"),
            "dispersion_diameter": node_value(muzzle, "DispersionDiameter"),
            "dispersion_range": node_value(muzzle, "DispersionRange"),
            "magazine_well": magwell,
            "default_magazine": default_mag,
            "fire_modes": extract_fire_modes(document),
        },
        "recoil": extract_recoil(document),
        "attachments": extract_attachment_slots(document),
        "sights": {
            "component_present": bool(document.find_nodes("SightsComponent")),
            "zeroing_modifier_present_raw": bool(document.find_nodes("ZeroingWeaponAimModifier")),
        },
    }


def extract_magazine(document: Document, rel_path: str) -> dict[str, Any]:
    component = first_node(document, "MagazineComponent")
    well_node = first_child(component, "MagazineWell") if component else None
    well = None
    if well_node and len(well_node.header_tokens) >= 2:
        well = well_node.header_tokens[1]

    ammo_prop = component.first_property("AmmoConfig") if component else None
    ammo_ref = None
    if ammo_prop and ammo_prop.values:
        ammo_ref = parse_resource_ref(ammo_prop.values[0])

    phys = first_node_declared_as(document, "ItemPhysicalAttributes")
    return {
        "id": safe_id(rel_path),
        "identity": {
            "name": extract_display_name(document),
            "resource": rel_path,
            "parent": parent_resource(document),
        },
        "magazine": {
            "max_ammo": node_value(component, "MaxAmmo"),
            "magazine_well": well,
            "ammo_config": ammo_ref,
        },
        "physical": {
            "weight": node_value(phys, "Weight"),
            "weight_per_ammo": node_value(phys, "WeightPerAmmo"),
            "volume": node_value(phys, "ItemVolume"),
        },
    }


def extract_ammunition(document: Document, rel_path: str) -> dict[str, Any]:
    shell = first_node(document, "ShellMoveComponent")
    return {
        "id": safe_id(rel_path),
        "identity": {
            "resource": rel_path,
            "parent": parent_resource(document),
        },
        "shell_move": {
            "init_speed": node_value(shell, "InitSpeed"),
            "mass": node_value(shell, "Mass"),
            "air_drag": node_value(shell, "AirDrag"),
            "velocity_variation": node_value(shell, "VelocityVariation"),
        },
    }


def extract_ammo_config(document: Document, rel_path: str) -> dict[str, Any]:
    resources: list[dict[str, str]] = []
    for ref in iter_resource_refs(document.path.read_text(encoding="utf-8", errors="replace")):
        resources.append({"guid": str(ref["guid"]), "path": str(ref["path"])})
    return {
        "id": safe_id(rel_path),
        "identity": {"resource": rel_path, "parent": parent_resource(document)},
        "ammo_resources": resources,
    }


def classify_document(document: Document) -> set[str]:
    names = {node.name for node in document.walk()}
    kinds: set[str] = set()
    if "WeaponComponent" in names:
        kinds.add("weapon")
    if "MagazineComponent" in names:
        kinds.add("magazine")
    if "ShellMoveComponent" in names or any(
        node.name in {"Projectile", "Bullet"} for node in document.root.children
    ):
        kinds.add("ammunition")
    if any(node.name == "MagazineConfig" for node in document.root.children):
        kinds.add("ammo_config")
    if "AttachmentSlotComponent" in names and "WeaponComponent" not in names:
        kinds.add("attachment")
    return kinds


def parse_scripts(script_paths: list[Path], root: Path) -> dict[str, Any]:
    files: list[dict[str, Any]] = []
    symbols: list[dict[str, Any]] = []
    methods: list[dict[str, Any]] = []

    for path in script_paths:
        rel = rel_posix(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        in_block = False
        current_owner: Optional[str] = None
        brace_depth = 0
        owner_depth: Optional[int] = None
        method_count = 0
        symbol_count = 0

        for lineno, raw in enumerate(text.splitlines(), start=1):
            line, in_block = strip_comments(raw, in_block)
            code = re.sub(r'"(?:\\.|[^"\\])*"', '""', line)
            class_match = CLASS_RE.match(code)
            if class_match:
                modded, kind, name, base = class_match.groups()
                symbols.append(
                    {
                        "kind": kind,
                        "name": name,
                        "base": base,
                        "modded": bool(modded),
                        "path": rel,
                        "line": lineno,
                    }
                )
                current_owner = name
                owner_depth = brace_depth + code.count("{") - code.count("}")
                symbol_count += 1

            method_match = METHOD_RE.match(code)
            if method_match and current_owner:
                _, return_type, name, params = method_match.groups()
                if name not in CONTROL_NAMES:
                    param_text = params.strip()
                    arity = 0 if not param_text else len([p for p in param_text.split(",") if p.strip()])
                    methods.append(
                        {
                            "owner": current_owner,
                            "return_type": return_type,
                            "name": name,
                            "arity": arity,
                            "path": rel,
                            "line": lineno,
                        }
                    )
                    method_count += 1

            brace_depth += code.count("{") - code.count("}")
            if current_owner and owner_depth is not None and brace_depth < owner_depth:
                current_owner = None
                owner_depth = None

        files.append(
            {
                "path": rel,
                "lines": len(text.splitlines()),
                "symbols": symbol_count,
                "methods": method_count,
                "sha256": sha256_file(path),
            }
        )

    return {"files": files, "symbols": symbols, "methods": methods}


def resolve_path(target_path: str, path_index: dict[str, str]) -> Optional[str]:
    norm = target_path.replace("\\", "/").lstrip("/")
    if norm in path_index:
        return path_index[norm]
    lowered = norm.lower()
    candidates = [rel for key, rel in path_index.items() if key.lower() == lowered]
    if len(candidates) == 1:
        return candidates[0]
    return None


def build_inheritance(
    resource_records: dict[str, dict[str, Any]],
    path_index: dict[str, str],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    graph: dict[str, Any] = {}
    issues: list[dict[str, Any]] = []

    for rel, record in resource_records.items():
        parent = record.get("parent")
        if not parent:
            graph[rel] = {"parent": None, "resolved_parent": None, "chain": [], "status": "root_or_unknown"}
            continue

        parent_path = str(parent.get("path", ""))
        resolved = resolve_path(parent_path, path_index)
        chain: list[str] = []
        visited = {rel}
        cursor = resolved
        status = "resolved_local" if resolved else "external_or_missing"

        if not resolved:
            issues.append(
                {
                    "type": "unresolved_parent",
                    "source": rel,
                    "target": parent_path,
                    "guid": parent.get("guid"),
                }
            )
        else:
            for _ in range(MAX_INHERITANCE_DEPTH):
                if cursor is None:
                    break
                if cursor in visited:
                    status = "cycle"
                    issues.append({"type": "inheritance_cycle", "source": rel, "at": cursor})
                    break
                visited.add(cursor)
                chain.append(cursor)
                next_parent = resource_records.get(cursor, {}).get("parent")
                if not next_parent:
                    break
                next_path = str(next_parent.get("path", ""))
                next_cursor = resolve_path(next_path, path_index)
                if next_cursor is None:
                    status = "partially_resolved_external"
                    issues.append(
                        {
                            "type": "unresolved_parent",
                            "source": cursor,
                            "target": next_path,
                            "guid": next_parent.get("guid"),
                        }
                    )
                    break
                cursor = next_cursor
            else:
                status = "depth_limit"
                issues.append({"type": "inheritance_depth_limit", "source": rel})

        graph[rel] = {
            "parent": parent,
            "resolved_parent": resolved,
            "chain": chain,
            "status": status,
        }
    return graph, issues


def scan(root: Path, out: Path) -> dict[str, Any]:
    root = root.resolve()
    out = out.resolve()

    if not root.exists() or not root.is_dir():
        raise SystemExit(f"scan root does not exist or is not a directory: {root}")

    resource_paths: list[Path] = []
    script_paths: list[Path] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        suffix = path.suffix.lower()
        if suffix in RESOURCE_EXTENSIONS:
            resource_paths.append(path)
        elif suffix == SCRIPT_EXTENSION:
            script_paths.append(path)

    path_index = {rel_posix(path, root): rel_posix(path, root) for path in resource_paths}
    resources: dict[str, dict[str, Any]] = {}
    refs: list[dict[str, Any]] = []
    parse_warnings: list[dict[str, Any]] = []
    catalog: dict[str, list[dict[str, Any]]] = {
        "weapons": [],
        "magazines": [],
        "ammunition": [],
        "ammo_configs": [],
        "attachments": [],
    }

    for path in resource_paths:
        rel = rel_posix(path, root)
        text = path.read_text(encoding="utf-8", errors="replace")
        try:
            document = parse_file(path)
        except Exception as exc:
            parse_warnings.append({"path": rel, "warning": f"parse_exception: {exc}"})
            continue

        for warning in document.parse_warnings:
            parse_warnings.append({"path": rel, "warning": warning})

        parent = parent_resource(document)
        kinds = sorted(classify_document(document))
        resources[rel] = {
            "path": rel,
            "sha256": sha256_file(path),
            "size": path.stat().st_size,
            "kinds": kinds,
            "parent": parent,
        }

        for ref in iter_resource_refs(text):
            target = str(ref["path"])
            refs.append(
                {
                    "source": rel,
                    "line": ref["line"],
                    "guid": ref["guid"],
                    "target": target,
                    "resolved_local": resolve_path(target, path_index),
                }
            )

        if "weapon" in kinds:
            catalog["weapons"].append(extract_weapon(document, rel))
        if "magazine" in kinds:
            catalog["magazines"].append(extract_magazine(document, rel))
        if "ammunition" in kinds:
            catalog["ammunition"].append(extract_ammunition(document, rel))
        if "ammo_config" in kinds:
            catalog["ammo_configs"].append(extract_ammo_config(document, rel))
        if "attachment" in kinds:
            catalog["attachments"].append(
                {
                    "id": safe_id(rel),
                    "identity": {"resource": rel, "parent": parent},
                    "attachment_slots": extract_attachment_slots(document),
                }
            )

    inheritance, inheritance_issues = build_inheritance(resources, path_index)
    unresolved_refs = [ref for ref in refs if ref["resolved_local"] is None]
    scripts = parse_scripts(script_paths, root)

    for kind, records in catalog.items():
        target_dir = out / "catalog" / kind
        target_dir.mkdir(parents=True, exist_ok=True)
        for record in records:
            resource = record["identity"]["resource"]
            record["inheritance"] = inheritance.get(resource, {})
            record["provenance"] = {
                "scan_mode": "read_only",
                "source_sha256": resources.get(resource, {}).get("sha256"),
                "source_resource": resource,
            }
            atomic_json(target_dir / f"{record['id']}.json", record)

    atomic_json(out / "indexes" / "resources.json", sorted(resources.values(), key=lambda x: x["path"]))
    atomic_json(out / "indexes" / "references.json", refs)
    atomic_json(out / "indexes" / "inheritance.json", inheritance)
    atomic_json(out / "indexes" / "scripts.json", scripts)

    atomic_json(
        out / "agent" / "scan_state.json",
        {
            "schema": "WEAPON_ARMA_X_SCAN_STATE_V1",
            "generated_at": now_iso(),
            "source_root_name": root.name,
            "read_only": True,
            "counts": {
                "resource_files": len(resource_paths),
                "script_files": len(script_paths),
                "weapons": len(catalog["weapons"]),
                "magazines": len(catalog["magazines"]),
                "ammunition": len(catalog["ammunition"]),
                "ammo_configs": len(catalog["ammo_configs"]),
                "attachments": len(catalog["attachments"]),
                "references": len(refs),
                "unresolved_references": len(unresolved_refs),
                "parse_warnings": len(parse_warnings),
                "inheritance_issues": len(inheritance_issues),
            },
        },
    )

    summary = f"""# Weapon Intelligence scan summary

Generated: `{now_iso()}`

Source root: `{root.name}`

## Counts

- Resource files (`.et/.conf/.meta`): **{len(resource_paths)}**
- Enforce scripts (`.c`): **{len(script_paths)}**
- Weapons: **{len(catalog['weapons'])}**
- Magazines: **{len(catalog['magazines'])}**
- Ammunition/projectiles: **{len(catalog['ammunition'])}**
- Ammo configs: **{len(catalog['ammo_configs'])}**
- Attachments: **{len(catalog['attachments'])}**
- Resource references: **{len(refs)}**
- References not resolved inside this addon: **{len(unresolved_refs)}**
- Parser warnings: **{len(parse_warnings)}**
- Inheritance issues: **{len(inheritance_issues)}**

## Safety boundary

This scan is read-only. It does not modify source `.et`, `.conf`, `.meta`, or `.c` files.
A missing local target is recorded as unresolved/external and is not guessed.

## Resolution boundary

V1 records declared resource data, reference edges, and inheritance chains.
It does **not** claim a full Enfusion-effective merge of component arrays or GUID-based overrides.
That step requires a separately validated merge model before any automatic balance edit is allowed.
"""
    atomic_text(out / "reports" / "scan_summary.md", summary)

    unresolved_lines = ["# Unresolved/external resource references", ""]
    for item in unresolved_refs:
        unresolved_lines.append(
            f"- `{item['source']}:{item['line']}` → `{{{item['guid']}}}{item['target']}`"
        )
    if len(unresolved_lines) == 2:
        unresolved_lines.append("None.")
    atomic_text(out / "reports" / "unresolved_references.md", "\n".join(unresolved_lines) + "\n")

    issue_lines = ["# Inheritance issues", ""]
    for issue in inheritance_issues:
        issue_lines.append(f"- `{issue['type']}`: `{json.dumps(issue, ensure_ascii=False)}`")
    if len(issue_lines) == 2:
        issue_lines.append("None.")
    atomic_text(out / "reports" / "inheritance_issues.md", "\n".join(issue_lines) + "\n")

    if parse_warnings:
        atomic_json(out / "reports" / "parse_warnings.json", parse_warnings)

    return {
        "weapons": len(catalog["weapons"]),
        "magazines": len(catalog["magazines"]),
        "ammunition": len(catalog["ammunition"]),
        "scripts": len(script_paths),
        "unresolved_references": len(unresolved_refs),
        "inheritance_issues": len(inheritance_issues),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Read-only ARMST weapon/resource intelligence scanner."
    )
    parser.add_argument("--root", required=True, type=Path, help="Local addon root to scan.")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("."),
        help="Output repository root (default: current directory).",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    result = scan(args.root, args.out)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
