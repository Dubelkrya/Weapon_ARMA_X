#!/usr/bin/env python3
"""One-command connect of the sanitized MP-133 lab insert clips (issue #27).

After the owner imports the two prepared TXA in the Workbench Animation Editor
(the only step the agent cannot do), run:

    python agent/scripts/mp133_lab_connect_anims.py \
        --w-guid <W_MP133_Lab_Inject.anm-GUID> \
        --p-guid <P_MP133_Lab_Inject.anm-GUID>

What it changes (STRICTLY inside the lab addon):
  1. `MP133_Lab_weapon.asi` / `MP133_Lab_player.asi`: the two
     `Reload.Erc/Pne.Reload_InsertMag` rows are repointed from the ORIGINAL
     inject ANM to the sanitized lab ANM.
  2. `MP133_Lab.agf`: every non-rack reload state child is redirected to
     `InsertMagAnim`, so no `RemoveMagAnim`/`MagReloadSTM` (which carry the
     stock `Weapon_MagRelease/Detach/Despawn` events) can run for the lab weapon.

It never touches the original Weapons/Core addons, worlds, layers or scripts.
It is idempotent and supports --dry-run.

NOTE: this only connects the clips. Enabling the lab insert gate
(`ARMST_MP133_Lab_Component.m_bLabInsertEnabled`) and the R handling remains a
separate step, gated on the owner's gameplay test (see the V2.3 import doc).
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DEFAULT_ADDONS = Path(
    r"C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons")

W_ANM_REL = "Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.anm"
P_ANM_REL = "Assets/Weapons_RUS/Mp_133/Workspace/LabClips/P_MP133_Lab_Inject.anm"
W_OLD_REL = "Assets/Weapons_RUS/Mp_133/Workspace/Reload/W_MP133_Reload_Inject.anm"
P_OLD_REL = "Assets/Weapons_RUS/Mp_133/Workspace/Reload/P_MP133_Reload_Inject.anm"

GUID_RE = re.compile(r"^[0-9A-Fa-f]{16}$")


def _guid(g: str) -> str:
    g = g.strip().strip("{}").upper()
    if not GUID_RE.match(g):
        raise SystemExit(f"invalid GUID: {g!r} (expected 16 hex chars)")
    return g


def repoint_inject_rows(text: str, new_guid: str, old_rel: str, new_rel: str) -> str:
    """Repoint the Reload_InsertMag rows from old_rel to {new_guid}new_rel."""
    # Replace any occurrence of the old relative path inside a Resource line.
    pattern = re.compile(
        r'(AnimSetInstanceSource_Line "Reload\.[A-Za-z]+\.Reload_InsertMag"\s*\{\s*'
        r'Resource ")(?:\{[0-9A-Fa-f]{16}\})?' + re.escape(old_rel) + r'(")')
    replaced, n = pattern.subn(lambda m: m.group(1) + "{" + new_guid + "}" + new_rel + m.group(2), text)
    if n == 0:
        # Already pointing at the new path? then it is a no-op.
        already = re.search(
            r'AnimSetInstanceSource_Line "Reload\.[A-Za-z]+\.Reload_InsertMag"\s*\{\s*'
            r'Resource "\{' + new_guid + r'\}' + re.escape(new_rel), text)
        if already:
            return text
        raise SystemExit(f"could not find Reload_InsertMag rows for {old_rel}")
    return replaced


def harden_graph(text: str) -> str:
    """Route every non-rack reload state to the sanitized insert clip."""
    if 'Child "MagReloadSTM"' not in text and 'Child "RemoveMagAnim"' not in text:
        return text  # already hardened
    text = text.replace('Child "MagReloadSTM"', 'Child "InsertMagAnim"')
    text = text.replace('Child "RemoveMagAnim"', 'Child "InsertMagAnim"')
    return text


def _lab_root(arg: str | None) -> Path:
    root = Path(arg) if arg else DEFAULT_ADDONS / "ARMST_MP133_AnimationLab"
    if not (root / "addon.gproj").is_file():
        raise SystemExit(f"lab addon not found at {root}")
    return root


def run(lab: Path, w_guid: str, p_guid: str, harden: bool, dry_run: bool) -> int:
    ws = lab / "Assets/Weapons_RUS/Mp_133/Workspace"
    jobs = [
        (ws / "MP133_Lab_weapon.asi", w_guid, W_OLD_REL, W_ANM_REL),
        (ws / "MP133_Lab_player.asi", p_guid, P_OLD_REL, P_ANM_REL),
    ]
    for path, guid, old_rel, new_rel in jobs:
        if not path.is_file():
            raise SystemExit(f"missing {path}")
        text = path.read_text(encoding="utf-8")
        new_text = repoint_inject_rows(text, guid, old_rel, new_rel)
        if new_text == text:
            print(f"[skip] {path.name}: already connected")
        else:
            print(f"[edit] {path.name}: Inject rows -> {new_rel}")
            if not dry_run:
                path.write_text(new_text, encoding="utf-8")

    agf = ws / "MP133_Lab.agf"
    if not agf.is_file():
        raise SystemExit(f"missing {agf}")
    text = agf.read_text(encoding="utf-8")
    new_text = harden_graph(text)
    if new_text == text:
        print("[skip] MP133_Lab.agf: already hardened")
    else:
        print("[edit] MP133_Lab.agf: all reload states -> InsertMagAnim")
        if not dry_run:
            agf.write_text(new_text, encoding="utf-8")

    if dry_run:
        print("dry-run: no files written")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--w-guid", required=True, help="GUID of W_MP133_Lab_Inject.anm")
    ap.add_argument("--p-guid", required=True, help="GUID of P_MP133_Lab_Inject.anm")
    ap.add_argument("--lab-root", default=None)
    ap.add_argument("--no-harden-graph", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(_lab_root(args.lab_root), _guid(args.w_guid), _guid(args.p_guid),
               not args.no_harden_graph, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())