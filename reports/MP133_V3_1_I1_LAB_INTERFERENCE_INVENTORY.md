# MP-133 — V3.1: I1 lab-interference inventory + hypotheses (read-only)

**Status:** `I1_LAB_INTERFERENCE_CONFIRMED; EXACT_CAUSE_UNKNOWN;
V3_CLEAN_BASELINE_PARTIALLY_CONFIRMED`. Read-only. Old V2.x lab archived & disabled;
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
| **H1** | The global `modded HandleWeaponReloading` override prevents the native `HandleWeaponReloadingDefault` from executing for **all** weapons (calling only `super` is insufficient). | The supplied BC reference overrides `HandleWeaponFire` and explicitly calls **both** `super.HandleWeaponFire` and `HandleWeaponFireDefault` — implying `super` alone does not reach the native default in this build. The lab is the **only** addon overriding `HandleWeaponReloading`. I1 is weapon-agnostic (all pumps). | **HIGH** |
| H2 | The global `modded SCR_CharacterControllerComponent` overrides (`OnInit`/`OnControlledByPlayer`/`OnApplyControls`) interfere. | They run for every character; but they call `super` and never mutate the reload command. | MEDIUM |
| H3 | Re-registering 12 animation events in `OnInit` changes event handling. | Should be idempotent; the handler is passive. | LOW–MEDIUM |
| H4 | Lab↔production resource GUID/sub-object collisions. | Concrete: lab `MP133_Lab.agr` shares `AnimSrcGCT {6906E742614591FE}` and `Debug {6906E7426145918F}` with production `MP133.agr`; `.ast` group GUIDs `{6906E742614BA07E}/{6906E742614BA070}` and `.asi` RBF `{6906E74261498C00}` are shared; `.agf` node GUIDs copied. | LOW — `6906E742614591FE` occurs **only** in `MP133.agr` in production (checked), so it cannot explain other shotguns. |
| H5 | Input action collision on `ARMST_LIGHT_RELOAD_ACTION`. | Core + lab both listen; affects LSHIFT+R, not ordinary R. | LOW |

**Leading:** H1. The only lab code on the ordinary-R path is the global
`HandleWeaponReloading` override; removing the lab makes R work.

---

## 3. One-variable owner-only diagnostics (proposed; not implemented)

Each uses a **copy** of the archived lab, changes exactly one variable, is reversible,
and is run by the owner only (agent never launches Workbench/game). Test ordinary R on
an **original** shotgun (ideally 3× `shot → short R → shot`) with one copy enabled.

- **P1 — scripts vs resources:** copy with `Scripts/` removed (keep prefab/graph/ASI/ANM).
  If R works → culprit is scripts; if broken → resources.
- **P2 — isolate the handler:** copy with `ARMST_MP133_Lab_CommandHandler.c` removed
  (keep Character/Component). If R works → the `HandleWeaponReloading` override is the cause (H1).
- **P3 — super vs default:** if P2 is positive, a copy whose non-lab pass-through calls
  `HandleWeaponReloadingDefault` explicitly (mirroring the BC pattern). If R works →
  confirms H1's mechanism.
- **P4 — isolate the controller:** copy with `ARMST_MP133_Lab_Character.c` removed
  (keep handler). Isolates H2.
- **P5 — minimal presence:** copy with only a minimal, non-lab pass-through
  `HandleWeaponReloading` (no fields/logging). Isolates the mere presence of the override.

Do NOT patch the archived lab in place; always work on a labelled copy.

---

## 4. V3.1 binding constraints

- **No global interception** of `HandleWeaponReloading` / `HandleWeaponFire`. Use a
  weapon-scoped input adapter. If a global override is proven unavoidable, it must call
  the native `...Default` appropriately and fully pass through for non-MP133, and be
  reviewed before implementation.
- Preserve the owner's controls: **ordinary R = native manual cycle**, hold R =
  native inspection, LSHIFT+R = frozen Core action. No J handling, no V2 migration.
- Never fake chamber fill, dummy ammo, tube-magazine replacement, or native
  mag attach/detach/spawn.
- `CMD_Weapon_Reload=7` is excluded by the restored graph and is not usable.

---

## 5. Stage 1 status

Owner reports all pumps work with lab OFF, but the **exact** acceptance details
(3× `shot→short R→shot`, hold-R inspection, tube/chamber baseline) are **not yet
explicitly confirmed** → `V3_CLEAN_BASELINE_PARTIALLY_CONFIRMED`. Mark Stage 1 **PASS**
only when the owner reports those precise results.

**Next:** owner reports the exact Stage 1 result and, optionally, P1/P2 to localize the
cause. Agent performs no implementation until Stage 1 is PASS and the cause approach is
reviewed.
