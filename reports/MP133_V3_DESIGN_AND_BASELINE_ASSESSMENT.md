# MP-133 — V3 design, native-R assessment, baseline checklist (read-only)

**Status:** `V3_DESIGN_APPROVED; CLEAN_BASELINE_RUNTIME_GATE_PENDING` →
**`BASELINE_RUNTIME_REQUIRED`** (Stage 1 not yet proven). **No implementation.**
Source: Issue #27 comment 5966570978. Nothing outside the knowledge repo changed;
V2.x lab stays frozen/historical; both `m_bLabInsertEnabled` gates OFF.

---

## 0. Restored baseline inventory (source-backed)

- Production weapon: `{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et`
  (also RIS `{9F8CA2FE5A3540DC}`); chain → `armst_shotgun_base.et` →
  `Rifle_M21.et`. Muzzle `{CA6BE4D6B867541F}`, `BaseFireMode {B80A64F4A8EF8333}`
  `ManualAction 1` (Single). `MagazineTemplate armst_12ga_Buckshot.et`
  `{B0DFDF7AAA9C5D39}` (capacity 10).
- Restored `Assets/Weapons_RUS/Mp_133/Workspace/MP133.agf`: **no `InsertSingleProjectile`**;
  `Idle→Buffer3` / `WeaponInspection→Buffer3` condition is
  `!inRange(GetCommandI(CMD_Weapon_Reload), 7, 9)` → **command 7/8 are excluded** from
  the reload state machine in the working baseline. ⇒ `CMD_Weapon_Reload=7` is **not
  usable** for shell insert without graph edits (not authorized).
- Rack path: `ReloadActionBolt` (cmd 1) → `RackBoltAnim` →
  `{45B1772B8AFEAE46}Reload/W_MP133_Reload_Bolt.anm`, events `BlendIn`(5),
  `Weapon_EnableFire`(10), `Weapon_Rack_Bolt`(14). ASI `MP133_weapon.asi`
  `Reload.Erc/Pne.ReloadActionBolt` → same clip.
- Git (post-restore): Weapons `main` `b88bc537…` (dirty: SPAS-12 anims + MP-133 `.meta`);
  Core `main` `08cb1f38…` (dirty: weather/rdb); knowledge `main` (see repo).
- V2.x lab: historical only, backed up at
  `C:\Users\yshky\Documents\MP133_Lab_Backups\MP133_Lab_Backup_20261003-002026\`.

---

## 1. Native R interception / tap-vs-hold — source-backed assessment

**What is provable from project sources / SDK:**
- The only project-defined weapon input action is `ARMST_LIGHT_RELOAD_ACTION` =
  **keyboard R + LSHIFT** (Core `Configs/System/chimeraInputCommon.conf:113-125`) —
  i.e. LSHIFT+R (frozen Core behavior).
- The **vanilla R reload action name is NOT present in project configs** (base-game
  input config lives in the game paks). It is **unresolved** and must be obtained from
  the base input config / owner keybindings / API before a weapon-scoped listener can
  target it.
- `CharacterInputContext` exposes reload **state**, not key edges: `GetWeaponReloadType()`,
  `WeaponIsStartReloading()`, `WeaponIsRaised()`, `WeaponIsPullingTrigger()`,
  `SetReloadWeapon(int)`. There is **no** `IsRKeyDown`/edge query.
- `scripts/Game/.../MP133_LoadController` cannot read raw R edges from the input
  context; a listener or a handler override is required.

**Options (ranked):**
1. **Weapon-scoped input listener (preferred, if the vanilla action name is resolved):**
   `InputManager.AddActionListener("<vanilla reload action>", EActionTrigger.DOWN/UP, …)`
   guarded by “current weapon is this MP-133 instance”. Character-scoped registration,
   behavior weapon-scoped. No global handler override.
2. **Global `HandleWeaponReloading` override with full non-MP133 pass-through** (the
   V2.x approach) — allowed only if option 1 is demonstrated impossible; must be
   reviewed as a global interception before implementation.

**Tap vs hold:** DOWN cannot distinguish a tap from a hold. Discrimination must use
DOWN/UP edges + a threshold (≤250 ms, owner-tunable), and **native R must not run in
parallel with scripted loading**. On the intended flow, a **short R** must first request
the **native pump**; only after a **confirmed native completion** may scripted loading
begin. Hold R must keep the **native inspection**.

**Native pump completion signal (unproven — Stage 3 gate):** candidates are
`Weapon_Rack_Bolt`, `Weapon_EnableFire`, `GetWeaponReloadType()` returning to 0,
`IsReloading()` clearing, or the graph `TagRackBolt`. **None is proven**; receiving
`reloadType=1` does **not** mean the rack executed (E0). If no reliable signal exists,
**STOP** and report evidence/options.

---

## 2. V3 architecture (weapon-scoped)

`MP133_LoadController` (ScriptComponent on the MP-133 instance, new lab clone with
distinct GUIDs) — finite-state machine:

```
IDLE --shortR--> WAIT_NATIVE_PUMP --pumpComplete--> INSERTING
INSERTING --cycleStarted--> COMMITTING --commitConfirmed--> INSERTING | autoFinish(END)
any --shortR while active--> STOP_REQUESTED (stop scheduling new cycles)
WAIT_NATIVE_PUMP/INSERTING/COMMITTING --fullTube|noRealShells|weaponLost--> END
```

- **Unique insertion sequence ID** per cycle; the authoritative server applies each
  animation commit **at most once** (`seq` guard + terminal recycle).
- Sample **current tube count/capacity and real inventory ammunition every cycle**
  (no virtual reserve, no hardcoded 3).
- Lab owns only input orchestration + one-shell insertion into the **same** physical
  magazine instance; native handles fire/manual bolt/chamber. **Never** fake chamber
  fill, never replace/dummy the tube magazine, never reintroduce native mag
  attach/detach/spawn.
- Interrupt: `STOP_REQUESTED` stops scheduling; a shell already past the one-time
  authoritative commit is kept; otherwise cancelled/refunded with no phantom round.
- Empty chamber + empty tube: do **not** claim an empty pump can chamber — define an
  explicit verified transition (load first, then native chamber) after a bounded test.

---

## 3. Baseline owner checklist (Stage 1 — MUST pass first)

On the **freshly restored original** MP-133 (no lab addon), Single + `ManualAction`:
1. baseline `tube`/`chamber`;
2. **3×** `shot → short R pump → shot` (each short R actually chambers and the next
   shot fires);
3. **hold R** → native inspection (no pump/load);
4. record tube/chamber transitions; if diagnostics are available, the reload command/
   `Weapon_Rack_Bolt`.
If this cannot be demonstrated: report **`BASELINE_RUNTIME_REQUIRED`** and STOP —
do not implement.

---

## 4. Exact one-variable first implementation diff (Stage 2, ONLY after Stage 1)

**Do not apply yet.** Scope: brand-new isolated reversible lab clone (distinct GUIDs,
backup + SHA manifest), implementing **only R tap-vs-hold + state-transition logging**:

- new prefab(s) inheriting the restored MP-133, new addon ID/GUIDs;
- `MP133_LoadController` skeleton with the FSM states above, transition logging
  (tagged, rate-limited) and **no** ammo/ASI/AGF/ANM/Core changes;
- minimal input adapter (option 1 if the action name is resolved, else option 2 with
  pass-through) selecting the **single variable**: R tap vs hold edges;
- proof that other weapons are unaffected (owner test).

No insertion, no commit, no tube/inventory change in this first diff.

---

## 5. STOP / blockers

- **BLOCKER (gate):** Stage 1 clean native baseline is not yet proven →
  `BASELINE_RUNTIME_REQUIRED`.
- **Open (Stage 1/3):** vanilla R action name unresolved; native pump completion
  signal unproven.
- Do not: patch production/Core, reinstall V2.x, use `CMD_Weapon_Reload=7`, fake
  chamber, dummy ammo, or reload native mag events. E1–E4 discontinued.
