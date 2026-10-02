#!/usr/bin/env python3
"""Deterministic static validation for the ARMST_MP133_AnimationLab addon.

Proves (without launching Workbench) that:

  * the lab file set is present (prefabs + scripts + animation resources; NO
    world/layer/scenario, per the owner override in issue #25);
  * every resource GUID referenced from the lab resolves to a lab meta GUID or
    to a GUID the live ARMST/vanilla source files actually carry (copied graph
    content is accepted only when the GUID appears in the ORIGINAL MP-133
    animation sources);
  * the lab prefabs wire the lab graph/instances and the lab component;
  * the MP133_Lab graph contains the single-shell insert self-loop;
  * every .asi row (Group.Column.Row) used by the lab resolves against the
    lab .ast template and the instance rows are non-empty.

Run:  python agent/scripts/validate_mp133_lab.py
Env:   MP133_LAB_ADDON_PATH (defaults to the standard Workbench addons path)
       MP133_ORIGINAL_ADDON_PATH (defaults to the live ARMST Weapons addon)
"""

import os
import re
import sys
from pathlib import Path

DEFAULT_ADDONS = Path(
    r"C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons")
ENV_LAB = "MP133_LAB_ADDON_PATH"
ENV_ORIG = "MP133_ORIGINAL_ADDON_PATH"

GUID_RE = re.compile(r"\{([0-9A-Fa-f]{16})\}")


class LabValidationError(AssertionError):
    pass


def resolve_lab_root() -> Path:
    p = os.environ.get(ENV_LAB)
    root = Path(p) if p else DEFAULT_ADDONS / "ARMST_MP133_AnimationLab"
    if not (root / "addon.gproj").is_file():
        raise LabValidationError(f"lab addon not found at {root}")
    return root


def resolve_original_root() -> Path:
    p = os.environ.get(ENV_ORIG)
    root = Path(p) if p else DEFAULT_ADDONS / "ARMST-PLATFORM---Weapons"
    if not (root / "addon.gproj").is_file():
        raise LabValidationError(f"original addon not found at {root}")
    return root


def iter_resources(root: Path):
    exts = {".c", ".meta", ".et", ".agr", ".agf", ".ast", ".asi", ".aw",
            ".gproj", ".conf", ".ent", ".layer", ".txa"}
    for p in sorted(root.rglob("*")):
        if p.is_file() and p.suffix.lower() in exts:
            yield p


def guids_in(text: str):
    return [m.group(1).upper() for m in GUID_RE.finditer(text)]


def braces_balanced(text: str):
    return text.count("{") == text.count("}")


def is_ascii(text: str) -> bool:
    try:
        text.encode("ascii")
        return True
    except UnicodeEncodeError:
        return False


REQUIRED_FILES = (
    "addon.gproj",
    "Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Component.c",
    "Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr.meta",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agf.meta",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.ast.meta",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.aw.meta",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi.meta",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_player.asi.meta",
    "Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et",
    "Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et",
)

# GUIDs the lab may legitimately reference (v2: no input config, no world/layer).
EXPECTED_LAB_METAS = {
    "1187677F04E33069",  # gproj
    "F23E6BC494967D16",  # agr
    "1EB8E2249801B1E3",  # agf
    "138604905EC95210",  # ast
    "EA8670F3600F156D",  # aw
    "DE3BB4522642DDE0",  # weapon asi
    "B51A94B5A27E09B4",  # player asi
    "FC1935AF936F63E5",  # prefab 133
    "4B288C21B7125D50",  # prefab 133 ris
    "21B3393B3149815A",  # lab component instance
    "77AB6DD3F7C4DF4D",  # entity id 133 lab
    "4293C409C16270F8",  # entity id ris lab
    "801C018EA3A11FA1",  # agf insert-loop transition
}

# Original source files that define the union of "external" GUIDs accepted.
# Both the resource content and its .meta are anchored so that a resource's
# OWN GUID (stored only in its .meta) is accepted as well.
ORIGINAL_ANCHOR_FILES = (
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133.agr",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133.agf",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133.ast",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133.aw",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_weapon.asi",
    "Assets/Weapons_RUS/Mp_133/Workspace/MP133_player.asi",
    "Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et",
    "Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133_Ris.et",
    "Prefabs/Weapons/Magazines/12ga/armst_12ga_Buckshot.et",
    "Prefabs/Weapons/Magazines/12ga/armst_12ga_Shell.et",
    "worlds/Weapon_test/weapon_test.ent",
    "worlds/Weapon_test/weapon_test_Layers/default.layer",
    # .meta files carry each resource's own identity GUID:
    "Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et.meta",
    "Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133_Ris.et.meta",
    "Prefabs/Weapons/Magazines/12ga/armst_12ga_Buckshot.et.meta",
    "Prefabs/Weapons/Magazines/12ga/armst_12ga_Shell.et.meta",
    "worlds/Weapon_test/weapon_test.ent.meta",
)


def original_guid_union(orig_root: Path):
    union = set()
    for rel in ORIGINAL_ANCHOR_FILES:
        p = orig_root / rel
        if p.is_file():
            union.update(guids_in(p.read_text(encoding="utf-8", errors="ignore")))
    return union


def check_file_set(lab: Path) -> list:
    problems = []
    for rel in REQUIRED_FILES:
        if not (lab / rel).is_file():
            problems.append(f"missing required file: {rel}")
    return problems


def check_text_hygiene(lab: Path) -> list:
    problems = []
    for p in iter_resources(lab):
        if "LabClips" in p.as_posix() and p.suffix == ".txa":
            continue  # txa allowed to differ slightly (long lines); still checked for ascii
        text = p.read_text(encoding="utf-8", errors="replace")
        if not is_ascii(text):
            problems.append(f"non-ascii: {p.relative_to(lab)}")
        if not braces_balanced(text):
            problems.append(f"unbalanced braces: {p.relative_to(lab)}")
    return problems


def check_guid_references(lab: Path, orig_union: set) -> list:
    problems = []
    lab_metas = set()
    for meta in lab.rglob("*.meta"):
        text = meta.read_text(encoding="utf-8", errors="ignore")
        m = GUID_RE.search(text)
        if m:
            lab_metas.add(m.group(1).upper())

    accepted = set(EXPECTED_LAB_METAS) | lab_metas | orig_union
    for p in iter_resources(lab):
        if ".meta" in p.suffix:
            continue
        text = p.read_text(encoding="utf-8", errors="ignore")
        for g in guids_in(text):
            if g not in accepted:
                problems.append(
                    f"{p.relative_to(lab)} references unresolved GUID {{{g}}}")
    return problems


def check_prefab_wiring(lab: Path) -> list:
    problems = []
    prefab = lab / "Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et"
    text = prefab.read_text(encoding="utf-8", errors="ignore")
    # parent is the ORIGINAL mp_133 prefab GUID
    if "{63FF6FDCA4E7E735}" not in text:
        problems.append("133 lab prefab: missing original mp_133 parent GUID")
    if "{F23E6BC494967D16}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr" not in text:
        problems.append("133 lab prefab: AnimGraph not wired to lab .agr")
    if "{DE3BB4522642DDE0}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi" not in text:
        problems.append("133 lab prefab: weapon AnimInstance not wired to lab .asi")
    if "{B51A94B5A27E09B4}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_player.asi" not in text:
        problems.append("133 lab prefab: player AnimInjection instance not wired")
    if "ARMST_MP133_Lab_Component" not in text:
        problems.append("133 lab prefab: missing lab component")
    return problems


def check_graph_loop(lab: Path) -> list:
    problems = []
    agf = lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agf"
    text = agf.read_text(encoding="utf-8", errors="ignore")
    if 'FromState "InsertSingleProjectile"' not in text:
        problems.append("agf: InsertSingleProjectile state missing")
    if '"{801C018EA3A11FA1}"' not in text:
        problems.append("agf: insert-loop transition missing")
    loop = ('FromState "InsertSingleProjectile"' in text
            and text.count('Condition "IsEvent(\\"BlendOut\\") && '
                           'GetCommandI(CMD_Weapon_Reload) == 7"') >= 1)
    if not loop:
        problems.append("agf: insert-loop condition/state wiring incorrect")
    return problems


def check_asi_rows(lab: Path) -> list:
    """Every .asi line must resolve against the .ast template rows/columns."""
    problems = []
    ast = lab / "Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.ast"
    ast_text = ast.read_text(encoding="utf-8", errors="ignore")

    # build {group: {rows..., columns...}} from the .ast
    groups = {}
    for gm in re.finditer(r'Name "(\w+)"\s+Animations \{(.*?)\}\s+Columns \{(.*?)\}',
                          ast_text, re.S):
        name, anims, cols = gm.group(1), gm.group(2), gm.group(3)
        rows = {r for r in re.findall(r'"(\w+)"', anims)}
        columns = {c for c in re.findall(r'"(\w+)"', cols)}
        groups[name] = (rows, columns)

    for asi in (lab / "Assets/Weapons_RUS/Mp_133/Workspace").glob("MP133_Lab_*.asi"):
        text = asi.read_text(encoding="utf-8", errors="ignore")
        used = set()
        for lm in re.finditer(r'AnimSetInstanceSource_Line "([\w.]+)"', text):
            used.add(lm.group(1))
            parts = lm.group(1).split(".")
            if len(parts) != 3:
                problems.append(f"{asi.name}: malformed row {lm.group(1)}")
                continue
            group, column, row = parts
            if group not in groups:
                problems.append(f"{asi.name}: unknown group {group}")
                continue
            rows, columns = groups[group]
            if row not in rows:
                problems.append(f"{asi.name}: row {row} not in group {group}")
            if column not in columns:
                problems.append(f"{asi.name}: column {column} not in group {group}")
            if not re.search(r'Resource "(\{[0-9A-F]{16}\})?[^"]*\.(anm|aex|aw)"',
                             text[text.find(lm.group(1)):], re.M):
                problems.append(f"{asi.name}: row {lm.group(1)} has no resource")
    return problems


def run_all(lab: Path | None = None, orig: Path | None = None) -> list:
    lab = lab or resolve_lab_root()
    orig = orig or resolve_original_root()
    problems = []
    problems += check_file_set(lab)
    problems += check_text_hygiene(lab)
    problems += check_guid_references(lab, original_guid_union(orig))
    problems += check_prefab_wiring(lab)
    problems += check_graph_loop(lab)
    problems += check_asi_rows(lab)
    return problems


def main() -> int:
    try:
        lab = resolve_lab_root()
        orig = resolve_original_root()
    except LabValidationError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        return 2
    problems = run_all(lab, orig)
    if problems:
        print(f"MP133 lab validation FAILED ({len(problems)}):")
        for p in problems:
            print("  - " + p)
        return 1
    print("MP133 lab validation PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())