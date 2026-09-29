#!/usr/bin/env python3
"""Resolve the live ARMST weapons addon root, safely.

Weapon_ARMA_X is a *tools* repository. It never contains gameplay resources.
Every script that needs to read the live addon resolves it through this module
so there is exactly one resolution policy and one place to change it.

Resolution order
----------------
1. ``ARMST_WEAPONS_ADDON_PATH`` environment variable (preferred, explicit).
2. ``MOD_ROOT`` environment variable (legacy name used by ``scan_build.py``).
3. A ``addon_path.local.json`` marker at the repository root, if present.
4. ``DEFAULT_ADDON_ROOT`` below, used only when it actually validates.

Validation
----------
A candidate is accepted only when it looks like an Enfusion weapons addon:

* the directory exists,
* ``addon.gproj`` is present,
* ``Prefabs/`` is a directory.

Anything else raises :class:`AddonPathError`. This deliberately refuses to
return a plausible-looking but wrong path: pointing a scanner at
``Weapon_ARMA_X`` itself, at the parent ``addons/`` directory, or at the
``Armst_Work`` sandbox must fail loudly rather than produce an empty or
misleading catalog.

Usage
-----
::

    from addon_path import resolve_addon_root

    root = resolve_addon_root()          # raises on any problem
    root = resolve_addon_root(strict=False)   # returns None instead
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

__all__ = [
    "AddonPathError",
    "ENV_PRIMARY",
    "ENV_LEGACY",
    "MARKER_FILENAME",
    "DEFAULT_ADDON_ROOT",
    "validate_addon_root",
    "resolve_addon_root",
    "describe_resolution",
]

ENV_PRIMARY = "ARMST_WEAPONS_ADDON_PATH"
ENV_LEGACY = "MOD_ROOT"
ENV_ALLOW_ANY = "ARMST_WEAPONS_ALLOW_ANY_ADDON"
MARKER_FILENAME = "addon_path.local.json"

#: Kept for the common local layout only. Always validated before use.
DEFAULT_ADDON_ROOT = Path(
    r"C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench"
    r"\addons\ARMST-PLATFORM---Weapons"
)

#: Directories that must never be treated as the addon root.
FORBIDDEN_SUBSTRINGS = ("Weapon_ARMA_X", "Armst_Work", "addons\\addons")

REQUIRED_FILE = "addon.gproj"
REQUIRED_DIRS = ("Prefabs",)

#: ``ID "..."`` values inside addon.gproj that identify the ARMST weapons addon.
#: Several sibling addons satisfy the structural checks above, so identity is
#: checked separately. A fork with a different ID can be accepted by setting
#: ``ARMST_WEAPONS_ALLOW_ANY_ADDON=1``.
EXPECTED_GPROJ_IDS = ("ARMSTPLATFORMWeapons",)
GPROJ_ID_RE = re.compile(r'^\s*ID\s+"([^"]*)"', re.M)


class AddonPathError(RuntimeError):
    """Raised when no valid live addon root can be resolved."""


def validate_addon_root(candidate: os.PathLike | str) -> list[str]:
    """Return a list of problems with *candidate*. Empty list means valid."""
    problems: list[str] = []

    try:
        root = Path(candidate).expanduser()
    except (TypeError, ValueError) as exc:
        return [f"not a usable path: {candidate!r} ({exc})"]

    raw = str(candidate)
    if not raw.strip():
        return [f"{ENV_PRIMARY} is set but empty"]

    if not root.exists():
        return [f"does not exist: {root}"]
    if not root.is_dir():
        return [f"is not a directory: {root}"]

    for bad in FORBIDDEN_SUBSTRINGS:
        if bad.lower() in raw.lower():
            problems.append(
                f"refusing to use a tools/sandbox path as the addon root: {root}"
            )

    if not (root / REQUIRED_FILE).is_file():
        problems.append(f"missing {REQUIRED_FILE}: {root}")

    for name in REQUIRED_DIRS:
        if not (root / name).is_dir():
            problems.append(f"missing directory {name}/: {root}")

    # Structural checks alone do not identify the addon: several sibling addons
    # also contain addon.gproj + Prefabs/. Check addon.gproj's own ID so a
    # scanner cannot silently analyse the wrong project.
    gproj = root / REQUIRED_FILE
    if gproj.is_file() and not _allow_any_addon():
        try:
            text = gproj.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            problems.append(f"cannot read {REQUIRED_FILE}: {exc}")
        else:
            m = GPROJ_ID_RE.search(text)
            if m and m.group(1) not in EXPECTED_GPROJ_IDS:
                problems.append(
                    f"addon.gproj ID {m.group(1)!r} is not the ARMST weapons "
                    f"addon (expected one of: {', '.join(EXPECTED_GPROJ_IDS)}); "
                    f"set ${ENV_ALLOW_ANY}=1 if this really is a fork"
                )

    return problems


def _allow_any_addon() -> bool:
    return os.environ.get(ENV_ALLOW_ANY, "").strip().lower() in ("1", "true", "yes")


def _candidates() -> list[tuple[str, os.PathLike | str, bool]]:
    """Ordered (source, value, explicit) candidate triples to try.

    ``explicit=True`` means the operator deliberately pointed at this path.
    An explicit candidate that fails validation is a hard error: silently
    scanning a different addon than the one that was asked for is the exact
    failure mode this module exists to prevent.
    """
    out: list[tuple[str, os.PathLike | str, bool]] = []

    for env in (ENV_PRIMARY, ENV_LEGACY):
        value = os.environ.get(env)
        if value is not None:
            out.append((f"${env}", value, True))

    marker = Path(__file__).resolve().parents[2] / MARKER_FILENAME
    if marker.is_file():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
        except Exception:
            data = None
        if isinstance(data, dict):
            value = data.get("addon_root")
            if isinstance(value, str) and value.strip():
                out.append((MARKER_FILENAME, value, True))

    out.append(("DEFAULT_ADDON_ROOT", DEFAULT_ADDON_ROOT, False))
    return out


def resolve_addon_root(strict: bool = True) -> Path | None:
    """Resolve and validate the live addon root.

    With ``strict=True`` (default) a :class:`AddonPathError` is raised that
    explains every candidate that was tried and why it was rejected. With
    ``strict=False`` the same information is printed to stderr and ``None`` is
    returned.
    """
    attempts: list[str] = []

    for source, value, explicit in _candidates():
        problems = validate_addon_root(value)
        if problems:
            line = (f"  {source} = {value}\n      rejected: " +
                    "; ".join(problems))
            attempts.append(line)
            if explicit:
                # A path the operator chose explicitly is never silently
                # replaced by another addon. Fail now.
                detail = (
                    "an explicitly configured ARMST weapons addon root is "
                    "invalid; refusing to fall back to a different addon.\n"
                    "Rejected:\n" + line
                )
                detail += _usage_hint()
                if strict:
                    raise AddonPathError(detail)
                print(detail, file=sys.stderr)
                return None
            continue
        return Path(value).expanduser().resolve()

    detail = ("no valid ARMST weapons addon root found.\n"
              "Tried:\n" + "\n".join(attempts)) + _usage_hint()
    if strict:
        raise AddonPathError(detail)
    print(detail, file=sys.stderr)
    return None


def _usage_hint() -> str:
    return (
        f"\n\nSet {ENV_PRIMARY} to the addon root, for example:\n"
        f'  set {ENV_PRIMARY}="C:\\...\\addons\\ARMST-PLATFORM---Weapons"\n'
        f"or create {MARKER_FILENAME} at the repository root containing\n"
        f'  {{"addon_root": "C:\\\\...\\\\addons\\\\ARMST-PLATFORM---Weapons"}}\n'
        f"The directory must contain {REQUIRED_FILE} and Prefabs/."
    )
    detail += (
        f"\n\nSet {ENV_PRIMARY} to the addon root, for example:\n"
        f'  set {ENV_PRIMARY}="C:\\...\\addons\\ARMST-PLATFORM---Weapons"\n'
        f"or create {MARKER_FILENAME} at the repository root containing\n"
        f'  {{"addon_root": "C:\\\\...\\\\addons\\\\ARMST-PLATFORM---Weapons"}}\n'
        f"The directory must contain {REQUIRED_FILE} and Prefabs/."
    )

    if strict:
        raise AddonPathError(detail)

    print(detail, file=sys.stderr)
    return None


def describe_resolution() -> str:
    """Human-readable one-liner used in tool banners and reports."""
    try:
        return f"{resolve_addon_root()}  (validated)"
    except AddonPathError as exc:
        return f"UNRESOLVED: {str(exc).splitlines()[0]}"


if __name__ == "__main__":
    try:
        print(f"{resolve_addon_root()}  (validated)")
    except AddonPathError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1)
