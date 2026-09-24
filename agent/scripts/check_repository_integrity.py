#!/usr/bin/env python3
"""Read-only repository integrity checks for Weapon_ARMA_X."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXPECTED_PRIMARY = "ARMST-PLATFORM---Weapons"
JSON_ROOTS = ("agent", "catalog", "indexes", "reports", "schema")
MD_LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
STALE_ARMST_WORK_PATH = "addons\\Armst_Work"


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def check_json(errors: list[str]) -> None:
    for root_name in JSON_ROOTS:
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in root.rglob("*.json"):
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except Exception as exc:
                fail(f"Invalid JSON: {path.relative_to(ROOT)}: {exc}", errors)


def check_schemas(errors: list[str]) -> None:
    try:
        import jsonschema
    except ImportError:
        fail("jsonschema is not installed; CI should install it before this check.", errors)
        return

    for path in sorted((ROOT / "schema").glob("*.json")):
        try:
            schema = json.loads(path.read_text(encoding="utf-8"))
            validator = jsonschema.validators.validator_for(schema)
            validator.check_schema(schema)
        except Exception as exc:
            fail(f"Invalid JSON Schema: {path.relative_to(ROOT)}: {exc}", errors)


def check_markdown_links(errors: list[str]) -> None:
    for path in ROOT.rglob("*.md"):
        text = path.read_text(encoding="utf-8")
        for raw_target in MD_LINK_RE.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            if "*" in target:
                continue
            resolved = (path.parent / target).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                continue
            if not resolved.exists():
                fail(
                    f"Broken Markdown link: {path.relative_to(ROOT)} -> {raw_target}",
                    errors,
                )


def check_primary_root_policy(errors: list[str]) -> None:
    canonical_files = [
        ROOT / "README.md",
        ROOT / "reports" / "KNOWLEDGE_STATUS.md",
        ROOT / "agent" / "PRIMARY_MOD_POLICY.md",
    ]
    for path in canonical_files:
        text = path.read_text(encoding="utf-8")
        if EXPECTED_PRIMARY not in text:
            fail(
                f"Primary addon marker missing from {path.relative_to(ROOT)}",
                errors,
            )

    for relative in ("reports/scan_summary.md", "reports/anomalies.md"):
        path = ROOT / relative
        if STALE_ARMST_WORK_PATH in path.read_text(encoding="utf-8"):
            fail(
                f"Historical scanner report still points at Armst_Work as a refresh path: {relative}",
                errors,
            )


def main() -> int:
    errors: list[str] = []
    check_json(errors)
    check_schemas(errors)
    check_markdown_links(errors)
    check_primary_root_policy(errors)

    if errors:
        print("Repository integrity checks failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Repository integrity checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
