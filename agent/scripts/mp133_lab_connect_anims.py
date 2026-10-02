#!/usr/bin/env python3
"""One-command connect of the sanitized MP-133 lab insert clips (issue #27).

After the owner imports the two prepared TXA in the Workbench Animation Editor
(the only step the agent cannot do), run:

    python agent/scripts/mp133_lab_connect_anims.py \
        --w-guid <W_MP133_Lab_Inject.anm-GUID> \
        --p-guid <P_MP133_Lab_Inject.anm-GUID>

Design (reviewed against issue #27 comment):
  * PREFLIGHT before any write: the referenced `.anm` files must exist and their
    `.anm.meta` must declare the SAME GUID and the SAME resource path; both ASIs
    must contain exactly the expected `Reload.Erc/Pne.Reload_InsertMag` rows;
    the AGF `WeaponReloadSTM` must match the expected structure.
  * ASI: repoint EXACTLY the two rows per instance (Erc + Pne); a partial edit is
    a failure.
  * AGF hardening is OPT-IN (`--harden-graph`, default OFF) and STRUCTURED: only
    states inside `WeaponReloadSTM` whose child is `MagReloadSTM`/`RemoveMagAnim`
    are redirected to `InsertMagAnim`, removing the stock swap events from the
    lab reload paths. The nested `MagReloadSTM`, transitions, `RackBoltAnim` and
    every unrelated node are left untouched; an unexpected structure aborts.
  * Atomic-ish write: all files are validated first, then written via a temp
    file + os.replace with rollback of already-written files on failure.
  * Idempotent: a lab already connected to the same GUID/path is a no-op.

It never touches the original Weapons/Core addons, worlds, layers or scripts.
"""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

DEFAULT_ADDONS = Path(
    r"C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons")

W_ANM_REL = "Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.anm"
P_ANM_REL = "Assets/Weapons_RUS/Mp_133/Workspace/LabClips/P_MP133_Lab_Inject.anm"
W_OLD_REL = "Assets/Weapons_RUS/Mp_133/Workspace/Reload/W_MP133_Reload_Inject.anm"
P_OLD_REL = "Assets/Weapons_RUS/Mp_133/Workspace/Reload/P_MP133_Reload_Inject.anm"
W_OLD_GUID = "45B1772B8AFEAE47"
P_OLD_GUID = "2E4A565E1D442CEA"

EXPECTED_ROWS = ("Reload.Erc.Reload_InsertMag", "Reload.Pne.Reload_InsertMag")
AGF_STM_MARKER = "AnimSrcNodeStateMachine WeaponReloadSTM {"
EXPECTED_MAGRELOAD_CHILDREN = 2   # MagReload + MagNoBulletReload
EXPECTED_REMOVEMAG_CHILDREN = 1   # RemoveMag state

GUID_RE = re.compile(r"^[0-9A-Fa-f]{16}$")
NAME_GUID_RE = re.compile(r'Name\s+"\{([0-9A-Fa-f]{16})\}([^"]+)"')


class ConnectorError(SystemExit):
    pass


def _guid(g: str) -> str:
    g = g.strip().strip("{}").upper()
    if not GUID_RE.match(g):
        raise ConnectorError(f"invalid GUID: {g!r} (expected 16 hex chars)")
    return g


def _norm(p: str) -> str:
    return p.replace("\\", "/").lstrip("./").casefold()


# ---------------------------------------------------------------------------
# Preflight helpers (pure where possible)
# ---------------------------------------------------------------------------
def verify_anm(lab: Path, rel_anm: str, expected_guid: str) -> list:
    """The .anm must exist and its .meta must declare the same GUID and path."""
    problems = []
    anm = lab / rel_anm
    meta = lab / (rel_anm + ".meta")
    if not anm.is_file():
        problems.append(f"missing ANM: {rel_anm}")
    if not meta.is_file():
        problems.append(f"missing ANM meta: {rel_anm}.meta")
        return problems
    text = meta.read_text(encoding="utf-8", errors="ignore")
    m = NAME_GUID_RE.search(text)
    if not m:
        problems.append(f"{rel_anm}.meta: no Name GUID found")
        return problems
    guid, declared = m.group(1).upper(), m.group(2)
    if guid != expected_guid.upper():
        problems.append(f"{rel_anm}.meta: GUID {guid} != requested {expected_guid.upper()}")
    if _norm(declared) != _norm(rel_anm):
        problems.append(f"{rel_anm}.meta: declared path {declared!r} != {rel_anm!r}")
    return problems


def plan_asi(text: str, new_guid: str, old_guid: str, old_rel: str, new_rel: str) -> dict:
    """Return {ok, problems, new_text, changed_rows}. Exactly one Erc + one Pne row,
    each replaced independently (never a global text replace)."""
    problems = []
    changed = []
    new_text = text
    old_res = f"{{{old_guid}}}{old_rel}"
    new_res = f"{{{new_guid}}}{new_rel}"

    for row in EXPECTED_ROWS:
        row_re = re.compile(
            r'(AnimSetInstanceSource_Line "' + re.escape(row) + r'"\s*\{\s*Resource ")([^"]+)(")')
        matches = row_re.findall(new_text)
        if len(matches) != 1:
            problems.append(f"expected exactly one '{row}' row, found {len(matches)}")
            continue
        res = matches[0][1]
        if res not in (old_res, new_res):
            problems.append(f"'{row}' resource is neither original nor lab path: {res}")
            continue
        if res == old_res:
            m = row_re.search(new_text)
            new_text = new_text[:m.start(2)] + new_res + new_text[m.end(2):]
            changed.append(row)

    if problems:
        return {"ok": False, "problems": problems, "new_text": text, "changed_rows": []}
    return {"ok": True, "problems": [], "new_text": new_text, "changed_rows": changed}


def _extract_braced_block(text: str, marker: str) -> tuple[int, int] | None:
    """Return (start, end) index range of the block whose header contains marker."""
    i = text.find(marker)
    if i < 0:
        return None
    b = text.find("{", i + len(marker) - 1)
    if b < 0:
        return None
    depth = 0
    for j in range(b, len(text)):
        if text[j] == "{":
            depth += 1
        elif text[j] == "}":
            depth -= 1
            if depth == 0:
                return (i, j + 1)
    return None


def _validate_transitions(seg: str) -> list:
    """Every non-empty transition endpoint must be a state defined in the STM."""
    problems = []
    states = set(m.group(2) for m in re.finditer(r'AnimSrcNodeState\s+("?)([\w]+)\1\s*\{', seg))
    for m in re.finditer(r'(FromState|ToState)\s+"([^"]*)"', seg):
        endpoint = m.group(2)
        if endpoint and endpoint not in states:
            problems.append(f"transition {m.group(1)} {endpoint!r} references an unknown state")
    return problems


def plan_graph_hardening(text: str) -> dict:
    """Structured, scoped redirect inside WeaponReloadSTM only."""
    problems = []
    block = _extract_braced_block(text, AGF_STM_MARKER)
    if not block:
        return {"ok": False, "problems": ["WeaponReloadSTM block not found"], "new_text": text, "states": []}
    start, end = block
    seg = text[start:end]

    problems += _validate_transitions(seg)
    if problems:
        return {"ok": False, "problems": problems, "new_text": text, "states": []}

    n_mag = seg.count('Child "MagReloadSTM"')
    n_rem = seg.count('Child "RemoveMagAnim"')

    if n_mag == 0 and n_rem == 0:
        return {"ok": True, "problems": [], "new_text": text, "states": []}  # already hardened
    if n_mag != EXPECTED_MAGRELOAD_CHILDREN or n_rem != EXPECTED_REMOVEMAG_CHILDREN:
        problems.append(
            "unexpected WeaponReloadSTM structure: "
            f"MagReloadSTM children={n_mag} (expected {EXPECTED_MAGRELOAD_CHILDREN}), "
            f"RemoveMagAnim children={n_rem} (expected {EXPECTED_REMOVEMAG_CHILDREN})")
        return {"ok": False, "problems": problems, "new_text": text, "states": []}

    new_seg = seg.replace('Child "MagReloadSTM"', 'Child "InsertMagAnim"')
    new_seg = new_seg.replace('Child "RemoveMagAnim"', 'Child "InsertMagAnim"')
    states = _state_names_with_child(seg, ("MagReloadSTM", "RemoveMagAnim"))
    return {
        "ok": True,
        "problems": [],
        "new_text": text[:start] + new_seg + text[end:],
        "states": states,
    }


def _state_names_with_child(seg: str, children: tuple) -> list:
    names = []
    for m in re.finditer(r'AnimSrcNodeState\s+("?)([\w]+)\1\s*\{', seg):
        name = m.group(2)
        tail = seg[m.end(): m.end() + 400]
        close = tail.find("}")
        body = tail if close < 0 else tail[:close]
        for c in children:
            if f'Child "{c}"' in body:
                names.append(name)
                break
    return names


# ---------------------------------------------------------------------------
# Orchestration
# ---------------------------------------------------------------------------
def _lab_root(arg: str | None) -> Path:
    root = Path(arg) if arg else DEFAULT_ADDONS / "ARMST_MP133_AnimationLab"
    if not (root / "addon.gproj").is_file():
        raise ConnectorError(f"lab addon not found at {root}")
    return root


def plan(lab: Path, w_guid: str, p_guid: str, harden: bool) -> dict:
    """Validate everything and return planned writes. No file is modified."""
    problems = []
    ws = lab / "Assets/Weapons_RUS/Mp_133/Workspace"

    problems += verify_anm(lab, W_ANM_REL, w_guid)
    problems += verify_anm(lab, P_ANM_REL, p_guid)

    plans = {}
    for name, guid, old_guid, old_rel, new_rel in (
        ("MP133_Lab_weapon.asi", w_guid, W_OLD_GUID, W_OLD_REL, W_ANM_REL),
        ("MP133_Lab_player.asi", p_guid, P_OLD_GUID, P_OLD_REL, P_ANM_REL),
    ):
        p = ws / name
        if not p.is_file():
            problems.append(f"missing {name}")
            continue
        r = plan_asi(p.read_text(encoding="utf-8"), guid, old_guid, old_rel, new_rel)
        if not r["ok"]:
            problems += [f"{name}: {x}" for x in r["problems"]]
        plans[name] = r

    agf = ws / "MP133_Lab.agf"
    if not agf.is_file():
        problems.append("missing MP133_Lab.agf")
        graph = {"ok": False, "problems": [], "new_text": "", "states": []}
    elif harden:
        graph = plan_graph_hardening(agf.read_text(encoding="utf-8"))
        if not graph["ok"]:
            problems += [f"MP133_Lab.agf: {x}" for x in graph["problems"]]
    else:
        graph = {"ok": True, "problems": [], "new_text": None, "states": []}

    return {"ok": not problems, "problems": problems, "ws": ws, "plans": plans, "graph": graph}


def run(lab: Path, w_guid: str, p_guid: str, harden: bool, dry_run: bool) -> int:
    result = plan(lab, w_guid, p_guid, harden)
    if not result["ok"]:
        print("PREFLIGHT FAILED (no files written):")
        for p in result["problems"]:
            print("  - " + p)
        return 1

    plan_data = result["plans"]
    graph = result["graph"]

    if dry_run:
        print("-- dry-run --")
        for name, r in plan_data.items():
            if r["changed_rows"]:
                for row in r["changed_rows"]:
                    print(f"[edit] {name}: {row} -> connected")
            else:
                print(f"[skip] {name}: already connected")
        if harden:
            if graph["states"]:
                print(f"[edit] MP133_Lab.agf: redirect states {graph['states']}")
            else:
                print("[skip] MP133_Lab.agf: already hardened")
        else:
            print("[skip] MP133_Lab.agf: hardening disabled (--harden-graph off)")
        print("dry-run: no files written")
        return 0

    writes = []
    for name, r in plan_data.items():
        if r["changed_rows"]:
            writes.append((result["ws"] / name, r["new_text"]))
    if harden and graph["states"]:
        writes.append((result["ws"] / "MP133_Lab.agf", graph["new_text"]))

    if not writes:
        print("already connected: nothing to do")
        return 0

    backups = {p: p.read_bytes() for p, _ in writes}
    done = []
    try:
        for p, text in writes:
            tmp = p.with_suffix(p.suffix + ".tmp")
            tmp.write_text(text, encoding="utf-8")
            os.replace(tmp, p)
            done.append(p)
            print(f"[write] {p.name}")
    except Exception as exc:  # noqa: BLE001
        for p in done:
            p.write_bytes(backups[p])
        raise ConnectorError(f"write failed, rolled back: {exc}")
    print(f"connected: {len(writes)} file(s) updated")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--w-guid", required=True)
    ap.add_argument("--p-guid", required=True)
    ap.add_argument("--lab-root", default=None)
    ap.add_argument("--harden-graph", dest="harden", action="store_true",
                    help="also redirect WeaponReloadSTM swap states (default off)")
    ap.add_argument("--no-harden-graph", dest="harden", action="store_false")
    ap.set_defaults(harden=False)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    return run(_lab_root(args.lab_root), _guid(args.w_guid), _guid(args.p_guid),
               args.harden, args.dry_run)


if __name__ == "__main__":
    sys.exit(main())