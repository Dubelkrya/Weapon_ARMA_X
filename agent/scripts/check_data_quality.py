#!/usr/bin/env python3
"""Read-only data-quality checks for Weapon_ARMA_X weapon catalogs.

The checker reports contradictions and coverage gaps without inventing missing
gameplay values. By default findings do not fail CI; use --fail-on when a clean
baseline exists and new findings should become blocking.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MAGAZINES = ROOT / "catalog" / "magazines"
AMMUNITION = ROOT / "catalog" / "ammunition"
WEAPONS = ROOT / "catalog" / "weapons"
AMMO_CONFIG_INDEX = ROOT / "indexes" / "config_reference" / "ammo_configs.json"

CALIBER_MARKERS = (
    "145x114",
    "127x108",
    "127x99",
    "25x137",
    "762x54",
    "762x51",
    "762x39",
    "763x25",
    "556x45",
    "545x39",
    "9x39",
    "9x19",
    "9x18",
    "12ga",
)

SEVERITY_ORDER = {"error": 0, "warning": 1, "info": 2}


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    detail: str


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def field_value(field):
    return field.get("value") if isinstance(field, dict) else None


def caliber_token(value: str | None) -> str | None:
    text = (value or "").lower().replace("×", "x")
    for marker in CALIBER_MARKERS:
        if marker in text:
            return marker
    return None


def expected_capacity(resource: str | None) -> int | None:
    match = re.search(r"_(\d+)rnd(?:_|\.|$)", resource or "", flags=re.IGNORECASE)
    return int(match.group(1)) if match else None


def load_resource_map(directory: Path) -> dict[str, Path]:
    result = {}
    for path in directory.glob("*.json"):
        doc = load(path)
        resource = (doc.get("source") or {}).get("resource")
        if resource:
            result[resource] = path
    return result


def scan_magazines(findings: list[Finding]) -> None:
    indexed_configs = (load(AMMO_CONFIG_INDEX).get("data") or {}) if AMMO_CONFIG_INDEX.exists() else {}

    for path in sorted(MAGAZINES.glob("*.json")):
        doc = load(path)
        data = doc.get("data") or {}
        resource = (doc.get("source") or {}).get("resource")
        relative = path.relative_to(ROOT).as_posix()

        resource_caliber = caliber_token(resource)
        caliber_id = field_value(data.get("caliber_id"))
        id_caliber = caliber_token(caliber_id)
        if resource_caliber and id_caliber and resource_caliber != id_caliber:
            findings.append(Finding(
                "error",
                "MAG_CALIBER_ID_MISMATCH",
                relative,
                f"resource indicates {resource_caliber}, but caliber_id indicates {id_caliber}: {caliber_id}",
            ))

        capacity = field_value(data.get("max_ammo"))
        if capacity is None:
            capacity = (doc.get("derived") or {}).get("capacity")
        named_capacity = expected_capacity(resource)
        if named_capacity is not None and capacity is None:
            findings.append(Finding(
                "warning",
                "MAG_CAPACITY_UNRESOLVED",
                relative,
                f"resource name contains {named_capacity}rnd, but max_ammo / derived capacity is unresolved",
            ))
        elif named_capacity is not None and capacity is not None and named_capacity != capacity:
            findings.append(Finding(
                "error",
                "MAG_CAPACITY_MISMATCH",
                relative,
                f"resource name contains {named_capacity}rnd, but resolved capacity is {capacity}",
            ))

        ammo_config = (data.get("ammo_config") or {}).get("path")
        if ammo_config and ammo_config not in indexed_configs:
            findings.append(Finding(
                "warning",
                "AMMO_CONFIG_NOT_INDEXED",
                relative,
                f"{ammo_config} is referenced by the magazine but absent from indexes/config_reference/ammo_configs.json",
            ))

        mapping = data.get("ammo_mapping") or []
        if capacity is not None and not mapping:
            findings.append(Finding(
                "info",
                "AMMO_MAPPING_EMPTY",
                relative,
                f"resolved capacity is {capacity}, but serialized ammo_mapping is empty; loaded projectile cannot be proven from this snapshot",
            ))


def scan_ammunition(findings: list[Finding]) -> None:
    for path in sorted(AMMUNITION.glob("*.json")):
        doc = load(path)
        data = doc.get("data") or {}
        shell = data.get("shell") or {}
        resource = (doc.get("source") or {}).get("resource")
        relative = path.relative_to(ROOT).as_posix()
        projectile_caliber = caliber_token(resource)

        ballistic_table = (shell.get("ballistic_table") or {}).get("path")
        table_caliber = caliber_token(ballistic_table)
        if projectile_caliber and table_caliber and projectile_caliber != table_caliber:
            findings.append(Finding(
                "info",
                "CROSS_CALIBER_BALLISTIC_TABLE",
                relative,
                f"projectile indicates {projectile_caliber}, while ballistic table indicates {table_caliber}: {ballistic_table}",
            ))

        parents = (doc.get("inheritance") or {}).get("external_parents") or []
        if parents:
            parent = parents[0].get("path")
            parent_caliber = caliber_token(parent)
            if projectile_caliber and parent_caliber and projectile_caliber != parent_caliber:
                findings.append(Finding(
                    "info",
                    "CROSS_CALIBER_PARENT",
                    relative,
                    f"projectile indicates {projectile_caliber}, while external parent indicates {parent_caliber}: {parent}",
                ))

        for effect in data.get("effects") or []:
            if effect.get("type") == "ProjectileDamage" and effect.get("DamageValue") is None:
                findings.append(Finding(
                    "warning",
                    "PROJECTILE_DAMAGE_UNRESOLVED",
                    relative,
                    "ProjectileDamage exists, but DamageValue is unresolved in the current catalog snapshot",
                ))
                break


def scan_weapon_links(findings: list[Finding]) -> None:
    magazine_resources = load_resource_map(MAGAZINES)
    for path in sorted(WEAPONS.glob("*.json")):
        doc = load(path)
        magazine = (((doc.get("data") or {}).get("magazine") or {}).get("magazine_template") or {}).get("path")
        if magazine and magazine not in magazine_resources:
            findings.append(Finding(
                "warning",
                "WEAPON_MAGAZINE_NOT_CATALOGED",
                path.relative_to(ROOT).as_posix(),
                f"linked magazine is not present in catalog/magazines: {magazine}",
            ))


def collect() -> list[Finding]:
    findings: list[Finding] = []
    scan_magazines(findings)
    scan_ammunition(findings)
    scan_weapon_links(findings)
    return sorted(
        findings,
        key=lambda item: (SEVERITY_ORDER[item.severity], item.code, item.path, item.detail),
    )


def render_text(findings: list[Finding]) -> str:
    counts = Counter(item.severity for item in findings)
    lines = [
        f"Data-quality scan: {counts['error']} error(s), {counts['warning']} warning(s), {counts['info']} info finding(s)."
    ]
    for item in findings:
        lines.append(
            f"[{item.severity.upper()}] {item.code} :: {item.path} :: {item.detail}"
        )
    return "\n".join(lines)


def render_markdown(findings: list[Finding]) -> str:
    counts = Counter(item.severity for item in findings)
    lines = [
        "## Weapon catalog data-quality scan",
        "",
        f"**{counts['error']} errors · {counts['warning']} warnings · {counts['info']} informational findings**",
        "",
        "The scan is evidence-preserving: filenames can trigger a consistency check, but never supply a missing gameplay value.",
        "",
    ]
    for severity in ("error", "warning", "info"):
        subset = [item for item in findings if item.severity == severity]
        lines.extend([f"### {severity.title()} ({len(subset)})", ""])
        if not subset:
            lines.extend(["None.", ""])
            continue
        for item in subset:
            lines.append(
                f"- **{item.code}** — `{item.path}` — {item.detail}"
            )
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--markdown", action="store_true")
    parser.add_argument(
        "--fail-on",
        choices=("none", "error", "warning"),
        default="none",
        help="Optional blocking threshold. CI currently uses none until a clean baseline exists.",
    )
    args = parser.parse_args()

    findings = collect()
    print(render_markdown(findings) if args.markdown else render_text(findings))

    if args.fail_on == "error" and any(item.severity == "error" for item in findings):
        return 1
    if args.fail_on == "warning" and any(item.severity in {"error", "warning"} for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
