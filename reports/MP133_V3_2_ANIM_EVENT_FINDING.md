# MP-133 — V3.2: native-event finding (read-only)

**Status:** `ANIM_EVENT_FINDING_RECORDED; WORKING_EDIT_SCOPE_UNVERIFIED`.
Read-only, knowledge repo only. No Workbench/game by agent; no graph/ASI/ANM/Core/prod
changes. Old V2.x lab frozen/disabled; P2 stays OFF. Source: Issue #27 comment 5967161341.

---

## 1. What the owner modified (recorded precisely)

**Files (on disk, lab addon):**
- `Assets/Weapons_RUS/Mp_133/Workspace/LabClips/P_MP133_Lab_Inject.anm` — re-imported
  2026-10-02 20:34, size **11865** (original V2.x import was 11857).
  SHA-256 `04FD8664C66958366C09D4D7B6E575595B6249BC78761FB5A58135D4E3A3A12C`.
- `Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.anm` — re-imported
  same time, size **2047** (original 2039).
  SHA-256 `D8044DA04CF1BC6843DFFF705DAABB51EEE1454D68A32AC06E7ACAD9D382622D`.
- `.txa` sources (`P/W_MP133_Lab_Inject.txa`) are **stale**: they still declare
  `ARMST_Lab_Shell_Spawn/Commit/Release` at frames 10/43/64. The event rename was done in
  the Workbench Animation Editor on the `.anm` (the editor did not rewrite the `.txa`).

**Owner-reported new events in the revised P clip (frames):**
`BlendIn`(1), **`Weapon_SpawnMagazine`**(10), **`Weapon_AttachMagazine`**(43),
**`Weapon_MagRelease`**(64), `BlendOut`(100) — replacing
`ARMST_Lab_Shell_Spawn/Commit/Release` at the same frames.
The production `Reload/P_MP133_Reload_Inject.anm` (11857 B, SHA
`2F876E731CC91208…`, `.txa` readable) carries **exactly the same** vanilla events/frames.

**ASI:** the current lab `MP133_Lab_player.asi`
(SHA `DDE9C574CA3C1F7B5EC04906FDE0EB53195DB1A6F3B1050765711ACE00BA8BAD`) maps
`Reload.Erc/Pne.Reload_InsertMag` → `{FE510A1EC49563F1}LabClips/P_MP133_Lab_Inject.anm`
(**lab clip**). The owner's description said it maps to
`Reload/P_MP133_Reload_Inject.anm` (**production clip**). **Discrepancy to confirm** —
which ASI/clip was active in the working test.

**Working edit already frozen:** the freeze backup
(`...\MP133_Lab_Backups\MP133_Lab_Backup_20261003-002026\lab_addon`) contains these exact
files (live==archive for the `.anm`/`.asi`/`.agf`; full SHAs in `MANIFEST.sha256`). The
only live-vs-archive diffs are the two prefabs (`Enabled 1` + coords re-save; **no
`m_bLabInsertEnabled`** → gate OFF).

---

## 2. Legacy vs now-working

| | Legacy V2.x (original import) | Now-working (owner edit) |
|---|---|---|
| P/W insert-clip events | `ARMST_Lab_Shell_Spawn/Commit/Release` (10/43/64) | `Weapon_SpawnMagazine/AttachMagazine/MagRelease` (10/43/64) |
| Event receiver | **lab script only** (`OnLabAnimationEvent`) | **engine native** weapon/animation handling |
| Lab scripted commit | `LabServerCommitInsert` fires → `tube+1` | does **not** fire (no `ARMST_Lab_Shell_Commit`) |
| Owner-observed | insert/chamber not fed | insert/chamber "began working" |

**Two independent findings must be preserved separately** (owner instruction):
1. **P2:** removing the global `modded SCR_CharacterCommandHandlerComponent` file restored
   ordinary **R** on all pumps.
2. **Event rename:** reportedly restored the **insert/chamber** behavior.
The animation edit cannot be attributed to P2's single-variable experiment.

---

## 3. Event receivers (code/SDK)

- Vanilla `Weapon_SpawnMagazine / Weapon_AttachMagazine / Weapon_MagRelease /
  Weapon_DetachMagazine / Weapon_DespawnMagazine / Weapon_EnableFire / Weapon_Rack_Bolt`
  are consumed by the **engine** (native weapon/magazine/animation system). Project code:
  Core reacts only to `Weapon_Rack_Bolt`; the lab registers these but acts only on
  `ARMST_Lab_Shell_Commit` and `Weapon_Rack_Bolt`.
- Custom `ARMST_Lab_Shell_*` are seen **only** by the lab's `OnLabAnimationEvent`.
- Consequence: with **vanilla** events, the engine performs the attach/chamber and the
  lab's scripted `tube+1` never runs; with **custom** events, only the lab script runs and
  the engine does nothing for the insert.
- `Weapon_AttachMagazine` is a **signal**, not proof that a physical magazine swap is
  desired. Whether it attaches a real magazine entity and whether ammo is conserved must
  be verified (mag entity identity, tube/chamber counts).

---

## 4. Required verification (owner) before any conclusion / Stage 1

- Which ASI/clip was active and whether the **lab handler** was present or the P2 copy
  (two independent variables).
- Exact counts: tube/chamber before/after, reserve/ammo conservation, **magazine entity
  identity** (same physical mag?), no phantom shell, no `10/10`.
- Workbench compile / fresh resource-rebuild proof.
- Controlled ≥3× `shot → ordinary short R → shot`, hold-R inspection, tube/chamber,
  mag continuity → then Stage 1.

---

## 5. Minimal validated design proposal (V3; NOT implemented)

- Do **not** copy the old global command handler. Keep archived V2 frozen.
- Make the **event strategy explicit**:
  - **Option A — native events (owner's current working direction):** rely on the engine's
    handling of `Weapon_*Magazine`. V3 then only orchestrates input + shell accounting and
    must **prove no physical mag swap and no phantom/lost ammo**. Simplest if it holds.
  - **Option B — custom events + scripted commit:** keep `ARMST_Lab_Shell_*` with a
    weapon-scoped receiver and an at-most-once authoritative commit. Note: there is **no
    public API to set the chamber** (V2.6), so custom events cannot chamber natively —
    Option B only manages the **tube**.
- Do **not** add `Weapon_Rack_Bolt` to the insert clip (owner correction); investigate
  `ReloadActionBolt` separately only if the pump remains faulty.
- Input research stays: weapon-scoped R arbitration + a proven native pump-completion
  signal. No global reload override.

---

## 6. Authorization

No V3 implementation, no graph/ASI/ANM edits, no global reload override. Stage 1 remains
`PENDING`. The animation edit is recorded as an **owner-observed** result pending the
verification in §4.
