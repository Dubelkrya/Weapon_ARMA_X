# MP-133 Lab — RESTORE INSTRUCTIONS (pre-restore backup)

**Purpose:** restore the V2.x `ARMST_MP133_AnimationLab` exactly as it was before the
main-mod restore, if needed. The V2.x lab is **historical material only** — the
approved path is V3 (`V3_DESIGN_APPROVED`); do **not** integrate V2.x into production.

**Backup location (outside the restored tree):**
`C:\Users\yshky\Documents\MP133_Lab_Backups\MP133_Lab_Backup_20261003-002026\`

Contents:
- `lab_addon\` — full byte copy of `ARMST_MP133_AnimationLab` (30 files).
- `lab_related_outside\knowledge_artifacts\MP133_Lab\` — git-ignored lab backups
  (prefab backups, v27 script backups).
- `lab_related_outside\knowledge_lab_files\` — copies of committed lab knowledge files.
- `MANIFEST.sha256` — 52 files, `<sha256>\t<size>\t<relpath>`; verified 0 mismatches.
- `BACKUP_INFO.txt` — provenance, Git snapshot, GUIDs, not-saved list.

## Restore steps

1. If `...\addons\ARMST_MP133_AnimationLab` exists, **move it aside** (do not delete in
   place); the backup must not be overwritten.
2. Copy `lab_addon\*` → `...\addons\ARMST_MP133_AnimationLab` (preserve structure).
3. Verify integrity: recompute SHA-256 for every file and compare against
   `MANIFEST.sha256` (expect 0 mismatches).
4. (Optional) Restore git-ignored scratch:
   `lab_related_outside\knowledge_artifacts\MP133_Lab\*` →
   `...\addons\Weapon_ARMA_X\artifacts\MP133_Lab\`.
   The `knowledge_lab_files\*` are already tracked in the knowledge repo via Git; only
   copy them if the repo is missing them.
5. Static check only (no Workbench/game):
   `python agent/scripts/validate_mp133_lab.py` and
   `agent/tests/test_mp133_lab_validation.py` (expect PASSED / 14 OK).
6. **Gates:** both `m_bLabInsertEnabled` must remain **OFF** (they are OFF in the backup).

## Warnings

- Do **not** push local lab sources to GitHub (repository rules).
- Do **not** modify production/Core/worlds/original animations.
- Do **not** re-enable the V2.x insert gate, J-held loading, E1–E4, Core suppression, or
  native mag-swap events. Those are discontinued; follow V3.
- The dirty production `MP133.agf` prototype from the pre-restore tree is preserved
  indirectly by `lab_addon\...\MP133_Lab.agf` (byte copy + documented hardening) and the
  captured diff/hash in this backup's `BACKUP_INFO.txt`.
