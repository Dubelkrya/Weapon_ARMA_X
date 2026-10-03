# MP-133 — V3.1: I1 lab-interference inventory + hypotheses (read-only)

**Status:** `P2_R_RESTORED / LEGACY_HANDLER_IMPLICATED / V3_STAGE1_PENDING`
(owner P2 runtime, comment 5966964438). Read-only. Old V2.x lab archived & disabled;
no code migration, no Workbench/game by agent; production/Core/graph/ASI/ANM untouched.
Source: Issue #27 comment 5966704171.

Owner A/B: **all pump-action shotguns fail ordinary R while the old lab addon is
enabled; disabling the lab restores R.** Exact component/method/collision unknown.

---

## 1. Actually loaded lab artifacts (inventoried from the archived copy)

Global `modded` classes (loaded whenever the addon is enabled, regardless of weapon):

- `modded SCR_CharacterControllerComponent` — `ARMST_MP133_Lab_Character.c`:
  - `override void OnInit(...)` → `GetAnimationComponent()`,
    `BindCommand("CMD_Weapon_Reload")`, `LabRegisterKnownEvents()` =
    `GameAnimationUtils.RegisterAnimationEvent(...)` ×12
    (`BlendIn/BlendOut/Weapon_Rack_Bolt/Weapon_EnableFire/Weapon_SpawnMagazine/
    Weapon_AttachMagazine/Weapon_MagRelease/Weapon_DetachMagazine/
    Weapon_DespawnMagazine/ARMST_Lab_Shell_Commit/Spawn/Release`),
    `GetOnAnimationEvent().Insert(OnLabAnimationEvent)`.
  - `override protected void OnControlledByPlayer(...)` →
    `AddActionListener("ARMST_LIGHT_RELOAD_ACTION", DOWN, OnLabPumpDown)` /
    `RemoveActionListener(...)`, watcher/diag timers.
  - `override protected void OnApplyControls(...)` → `super` + trace.
- `modded SCR_CharacterCommandHandlerComponent` — `ARMST_MP133_Lab_CommandHandler.c`:
  - `override bool HandleWeaponReloading(CharacterInputContext, float, int)` for
    **every weapon**; for non-lab it returns `super.HandleWeaponReloading(...)`
    (no explicit `HandleWeaponReloadingDefault` call).
- `ARMST_MP133_Lab_Component` (ScriptComponent) — attached only to lab prefabs; not global.

Resources loaded globally: `MP133_Lab.agr/.agf/.ast/.asi/.aw`,
`LabClips/*.anm|.txa`, lab prefab + 3-round mag, metas. No input config in this version.

Core (for contrast) does **not** override `HandleWeaponReloading`/`...Default`; it only
mutates the reload command inside `OnRackBoltMDown` (LSHIFT+R).

---

## 2. Hypothesis / evidence table

| # | Hypothesis | Evidence | Likelihood |
|---|---|---|---|
| **H1** | The global `modded HandleWeaponReloading` override prevents the native reload path from executing for all weapons. | **UNCONFIRMED.** The BC reference calls both `super.HandleWeaponFire` and `HandleWeaponFireDefault`, but that does **not** prove `super.HandleWeaponReloading` bypasses the native default. Bohemia Enforce docs state `super` calls the prior implementation in the modded-class chain. Adding `...Default()` unverified risks a **double run**. | **UNCONFIRMED** (candidate, not leading) |
| H2 | The global `modded SCR_CharacterControllerComponent` overrides (`OnInit`/`OnControlledByPlayer`/`OnApplyControls`) interfere. | They run for every character; but they call `super` and never mutate the reload command. | MEDIUM |
| H3 | Re-registering 12 animation events in `OnInit` changes event handling. | Should be idempotent; the handler is passive. | LOW–MEDIUM |
| H4 | Lab↔production resource GUID/sub-object collisions. | Concrete: lab `MP133_Lab.agr` shares `AnimSrcGCT {6906E742614591FE}` and `Debug {6906E7426145918F}` with production `MP133.agr`; `.ast` group GUIDs `{6906E742614BA07E}/{6906E742614BA070}` and `.asi` RBF `{6906E74261498C00}` are shared; `.agf` node GUIDs copied. | UNPROVEN — `6906E742614591FE` occurs only in `MP133.agr` in a scoped code-search, which hints but does not prove MP-133-scope; other interactions elsewhere cannot be categorically ruled out. |
| H5 | Input action collision on `ARMST_LIGHT_RELOAD_ACTION`. | Core + lab both listen; affects LSHIFT+R, not ordinary R. | LOW |

**No hypothesis is confirmed.** The owner A/B proves the legacy addon *contributes*
(addon ON → all pumps fail; OFF → work), not the offending method. The only authorized
follow-up to localize it is **P2** (below).

### 2.1 P2 owner runtime result (reported observation)

`P2_R_RESTORED; GLOBAL_COMMAND_HANDLER_INVOLVEMENT_SUPPORTED`: with the P2 copy enabled
(the ONLY source change from legacy V2 = excluding
`Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_CommandHandler.c`), the **original
pump-action shotguns again respond to ordinary R**. Contrast: legacy V2 enabled → all
pump R broken; lab OFF → R works.

**Bounded to** the presence/behavior of the global `modded
SCR_CharacterCommandHandlerComponent` / its interaction in the legacy lab. **Do NOT**
assert `super.HandleWeaponReloading` vs `HandleWeaponReloadingDefault` as causal: P2 does
not distinguish callback order, other modded-chain interactions, logging side effects, or
a compile/load interaction. No P3/P4/P5 required; the legacy root mechanism may remain
unresolved.

**Evidence separation:** this is the owner's reported observation. The **Workbench script
compilation / fresh resource-rebuild proof** and the **exact successful cases** (one cycle
vs 3× `shot → short R → shot`, hold-R inspection) are not yet provided → strict Stage 1
acceptance stays PENDING. Record them when the owner supplies them; do not invent tests.

---

## 3. Diagnostics (corrected per owner review) — P2 only

Owner corrections: **P1** (removing all `Scripts/`) can orphan component classes
referenced by lab prefabs → not an interpretable scripts-vs-resources A/B; **P4**
(removing the Character file) can remove methods invoked by the retained handler →
compile failure; **P5** must be specified as a buildable standalone minimal test, not
assumed safe; **P3** (`HandleWeaponReloadingDefault`) **NOT APPROVED** — Enforce `super`
already chains the prior implementation, so an extra `Default` call may double-run reload.

**Only authorized optional follow-up — P2** (owner-run; agent never launches the game):
1. Make a separately labeled, reversible **copy** of the archived V2 lab (do not edit the
   frozen archive).
2. Exclude only `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_CommandHandler.c`.
3. Static dependency/compilation review (done here, §3.1).
4. Owner: enable the P2 copy, verify startup compiled cleanly and that the old handler is
   genuinely absent, test an **original** pump shotgun ordinary R (3× `shot → R → shot`),
   then restore lab OFF.
5. If R recovers → handler involvement is supported (exact reason still unknown). If
   startup fails → P2 **BLOCKED**, no causal diagnosis.

### 3.0 P2 copy prepared (this session; owner review 5966846052)

- Path: `C:\Users\yshky\Documents\MP133_Lab_Backups\P2_no_handler\ARMST_MP133_AnimationLab`
- **Source change (exactly one):** removed
  `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_CommandHandler.c`. Everything else
  byte-identical to the archive (same GUIDs).
- **Generated-cache change (recorded separately, not a source mutation):** deleted the
  stale generated `resourceDatabase.rdb` (it still listed the removed source) so
  Workbench performs a clean rescan/regeneration.
- `MANIFEST_P2.sha256` (29 entries) verified 0 mismatches; `P2_README.md` has the steps.
- Static verification: 0 remaining `.c` references to the removed handler symbols.
- **Owner precondition:** fresh Workbench resource scan / script compilation; verify the
  old handler is not loaded/compiled. If unverifiable or compile fails → `P2_BLOCKED`, no
  causal conclusion.
- The archive and the live addon were **not** modified. Only one lab addon (same addon
  ID/GUID) may be enabled at a time. P2 is a **diagnostics-only, optional A/B** — not a
  V3 gate.
- **Result (owner runtime):** `P2_R_RESTORED` — ordinary R works on original pump
  shotguns with the handler excluded (see §2.1). P2 is complete; the owner turns P2 OFF
  for the clean baseline. Further P3/P4/P5 are not required.

### 3.1 P2 static dependency / compilation review (read-only, this session)

- `ARMST_MP133_Lab_CommandHandler.c` defines only the `modded
  SCR_CharacterCommandHandlerComponent` override plus its own fields
  (`m_iLabDbgLastCmdId`, `m_fLabDbgAccum`) and a private helper (`LabDiagReloadCmd`).
  Nothing outside this file references them.
- It **calls** `ctrl.LabInsertEnabledOnCurrentWeapon()` and
  `ctrl.LabRequestInsertFromHandler(...)`, both defined in
  `ARMST_MP133_Lab_Character.c`; removing the handler leaves those Character methods
  simply unused (no dangling reference).
- No prefab/`.et`/`.meta`/graph/ASI references the handler file or its symbols.
- Conclusion: excluding the handler file should compile cleanly and leave the Character
  and Component files valid. Static assessment only — real compilation is `OWNER TEST`.

Do NOT patch the archived lab in place; always work on a labelled copy. No other
diagnostic (P1/P3/P4/P5) is authorized.

---

## 4. V3.1 binding constraints

- **No global interception** of `HandleWeaponReloading` / `HandleWeaponFire` — **NOT
  AUTHORIZED for V3**. Use a weapon-scoped input adapter. If a global override were ever
  proven unavoidable, it must **preserve verified native semantics with a tested single
  call path and pass-through, without assuming an extra `...Default` is required**, and
  be reviewed before implementation. Do not call `...Default` speculatively (may
  double-run native reload).
- Preserve the owner's controls: **ordinary R = native manual cycle**, hold R =
  native inspection, LSHIFT+R = frozen Core action. No J handling, no V2 migration.
- Never fake chamber fill, dummy ammo, tube-magazine replacement, or native
  mag attach/detach/spawn.
- `CMD_Weapon_Reload=7` is excluded by the restored graph and is not usable.

---

## 5. Stage 1 status and V3 priority

**Stage 1 = PENDING.** P2 is complete and stays **OFF** for the clean baseline. Owner
reports all pumps work with lab OFF, but the exact acceptance details
(3× `shot → ordinary short R → shot`, hold-R inspection, tube/chamber baseline, no
magazine replacement) are **not yet reported** → `V3_STAGE1_PENDING`. Mark Stage 1 PASS
only on the owner's precise result (and, for the strict record, the Workbench
compile/rebuild proof).

**V3 priority (no V2 salvage cycles):** keep the old addon OFF; capture the clean
original baseline; after Stage 1 PASS, research (read-only) and propose:
1. **Safe R input arbitration** — a weapon-scoped way to get R DOWN/UP edges without a
   global `HandleWeaponReloading` override (resolve the vanilla reload action name, or a
   guarded input listener / weapon component). Must keep tap=native pump, hold=native
   inspection, and never run native R in parallel with scripting.
2. **Native pump-completion signal** — prove a reliable completion signal
   (`Weapon_Rack_Bolt`/`Weapon_EnableFire`/reload type clearing/`IsReloading`) before any
   insert scheduling; `reloadType=1` alone is not proof.
3. Then a **new isolated weapon-scoped V3 lab** (distinct GUIDs, backup + SHA manifest),
   changing one variable at a time.

**Nothing in I1 authorizes V3 code changes or a global `HandleWeaponReloading` override.**
No implementation by the agent until Stage 1 is PASS and the approach is reviewed.
