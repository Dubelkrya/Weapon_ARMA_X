# MP-133 G4-A — native magazine swap route audit + lab-only design (READ-ONLY)

**Status:** `G4A_AUDIT_STATUS: COMPLETE / REV2_P0_CORRECTIONS_APPLIED`. Read-only engineering audit and
design. **No gameplay implementation in this task.** No game/animation/prefab/script/Core/production
edit, no new branch/addon, no Workbench/game run by the agent.

**Authority:** Issue #34 comment `5975411582` (G4-A task) + REV2 comment `5979175085`; independent P0
review `5979146603`. Checkpoint at task creation `4807dfd7244c27a263b83e10f8f5ade07f1f87ae`; audit
published at `ad89a18195c669b060d0707750ef73615b15e8e0`; REV2 resolved HEAD
`dd215e1545279bd3485bbd9daf24716250dc0673` (branch advanced with research-only docs `ea2fff7`,
`23fb09a`, `dd215e1`; both incoming commits do not touch this report). Working tree clean except
owner-untracked `reports/CORE_ARMST_READONLY_AUDIT.md`.

_labels._ **REV2 note:** the earlier §1/§4/§5/§7/§8 wording that implied sanitizing the **inject** clip
alone is sufficient was **over-confident and is corrected in §0 (REV2 / P0 correction) below**; the
remove path (`Reload_RemoveMag`: `Weapon_MagRelease`/`Weapon_DetachMagazine`/`Weapon_DespawnMagazine`)
must be accounted for too.

`READONLY_GAMEPLAY_FILES_CHANGED=0` (this task writes one report; REV2 touches this file only).

---

## 0. REV2 / P0 correction (Issue #34 comment 5979175085; review 5979146603)

The first revision proposed sanitizing only the **inject** clip. Independent review is correct: this
is **UNSAFE**, because the removal path is a separate clip with its own native events. Both paths must
be accounted for.

### 0.1 Full command → state → source → clip route matrix (**SOURCE**, `MP133.agf`)

Graph is line-identical in production and the T2A/lab clone (`MP133_V3_RELOAD_GRAPH_AUDIT.md` §1.4).
`WeaponReloadStanceSTM` selects column `Erc`/`Cro` (`Stance == 0 || Stance == 1`) or `Pne`
(`Stance == 2`); both columns resolve the same state names through the P and W ASIs. `IdleReloadSTM`
entry gate rejects 7/8/9 (`!inRange(GetCommandI(CMD_Weapon_Reload), 7, 9)`).

| `GetCommandI(CMD_Weapon_Reload)` | Graph state | Child source | Removal events | Insertion events |
|---|---|---|---|---|
| `1 && F==0.0` | `ReloadActionBolt` | `Reload.ReloadActionBolt` (bolt) | none | none (`Weapon_EnableFire` f10, `Weapon_Rack_Bolt` f14) |
| `2` | `NoMagReload` | `Reload.Reload_InsertMag` (inject) | **none** (inject only) | `Weapon_SpawnMagazine` f10, `Weapon_AttachMagazine` f43, `Weapon_MagRelease` f64 |
| `3 && F==0.0` | `NoMagNoBulletReload` → `ReloadActionBolt` on `RemainingTimeLess(0.1)` | inject, then bolt | none | inject events + bolt events |
| `4` | `MagReload` → `MagReloadSTM` | `Reload_RemoveMag` **then** `Reload_InsertMag` | **`Weapon_MagRelease` f6, `Weapon_DetachMagazine` f10, `Weapon_DespawnMagazine` f15** | inject events |
| `5 && F==0.0` | `MagNoBulletReload` → `MagReloadSTM` → `ReloadActionBolt` | remove, inject, bolt | **detach/despawn as cmd4** | inject events + bolt events |
| `6` | `RemoveMag` | `Reload.Reload_RemoveMag` | **`Weapon_MagRelease` f6, `Weapon_DetachMagazine` f10, `Weapon_DespawnMagazine` f15** | none |
| `7/8/9` | — (vetoed at `IdleReloadSTM` entry; no state) | — | — | — |
| `10` | — (passes entry, no state in `WeaponReloadSTM`) | — | — | — |

`MagReloadSTM` (`RemoveMag` IsExit 0 → `InsertMag` IsExit 1) transitions on `IsEvent("BlendOut")` with
`StartTime GetEventTime(anim.Reload.Erc.Reload_InsertMag, "BlendIn")` — the graph **depends on the
`BlendIn`/`BlendOut` markers**, so a sanitized clip must keep those markers.

**P0 statement:** a sanitized **inject**-only design is insufficient. Commands **4/5/6** execute
`Reload_RemoveMag` first (`Weapon_MagRelease`/`Weapon_DetachMagazine`/`Weapon_DespawnMagazine`), which
can **detach/despawn the only installed physical `Tube3Mag` before** any inert inject clip, leaving
G3-B2 with no target. Cmd 6 (remove-only) must likewise not destroy it. Removing *authored* events does
**not** by itself prove the engine cannot detach/attach in every state (**UNVERIFIED** engine-internal
side effects).

**Double-R (INFERENCE, per review):** the exact per-press integer sequence is **UNRESOLVED**. A rapid
second R re-enters the reload path while the first whole-mag route is in progress; whichever integer
each press carries, it lands on a route in the matrix above, so covering **all** whole-mag routes
(2–6, both columns, P/W clips) also covers double-R.

### 0.2 Target-already-missing state (fail-closed)
If the tube was already removed/swapped by an earlier native action or manual removal, the design must
**STOP**, not create/fallback: **no** default-mag spawn, **no** invisible re-attach, **no** counterfeit
tube, **no** capacity-guard bypass. A magazine already **detached mid-animation** has an
**UNRESOLVED** engine state; treat it as missing and fail closed. This preserves G3-B2's existing
`target-capacity-mismatch` / no-target rejections.

### 0.3 Preserving the physical tube — corrected design options

- **Option A (preferred, lab-only redirection/suppression of ALL whole-mag branches):** the lab-owned
  graph routes commands **2/3/4/5/6** so they never enter the stock `RemoveMag`/`InsertMag` clips
  (e.g. to the bolt-only `ReloadActionBolt` **only if** chamber/rack preservation is justified by
  evidence, otherwise to an inert lab-only clip that keeps `BlendIn`/`BlendOut`), while **cmd 1** keeps
  the native bolt/rack. This requires a **demonstrated graph transition and safe completion** and a
  proof that the shell still racks/chambers/fires. Removing authored events in one clip is **not**
  enough; the *route* must not select a clip carrying native magazine lifecycle events.
- **Option B (preferred-equivalent, sanitized BOTH clips):** lab-only sanitized **`Reload_RemoveMag`**
  **and** **`Reload_InsertMag`** clips (native `Weapon_Spawn/Attach/MagRelease/Detach/Despawn` →
  inert events, **keeping** `BlendIn`/`BlendOut`), correctly mapped to **both** P and W ASIs
  (`Reload.Erc.*` and `Reload.Pne.*`) and every reachable path. Engine-internal non-clip side effects
  remain **UNVERIFIED**.
- **Rejected:** "inject-only sanitization" (P0); blanket R disable / global `HandleWeaponReloading`
  override (global-hook risk, other weapons); `MaxAmmo`/script-cap as a non-removability mechanism
  (does not change native removal).

### 0.4 Proposed EXACT future lab-only file allowlist (NOT created; G4-A implementation needs separate approval)
- Lab-owned graph set: `…/ARMSTMP133T4B_InstalledMagProbe/Assets/…/MP133_G4A.agr` + `.agf` (copy of the
  production graph with the whole-mag commands 2–6 routed off the stock remove/insert clips), `.ast`,
  `.aw`.
- Lab-owned ASIs: `MP133_G4A_weapon.asi`, `MP133_G4A_player.asi` with `Reload.Erc.Reload_RemoveMag` and
  `Reload.Erc.Reload_InsertMag` (**and** the `Pne` columns) → sanitized clips; **cmd-1 bolt, chamber,
  fire, inspection clips unchanged**.
- Sanitized clips: `W_`/`P_MP133_G4A_Rem.anm`(+`.txa`) and `W_`/`P_MP133_G4A_Inject.anm`(+`.txa`) —
  inert magazine events, `BlendIn`/`BlendOut` kept. **ANM must be owner-imported/compiled; text editing
  cannot produce a compiled `.anm`** (do not guess GUIDs).
- The **two** active G3-B2 weapon `.et` files (add a lab `WeaponAnimationComponent` override to the G4A
  graph/ASIs; keep GUIDs/instances/actions/write settings).
- Lab `MANIFEST.sha256`; this report; index/sync **only if separately authorized** (PR #31 overlap).
- **Rollback:** revert the two `.et` `WeaponAnimationComponent` overrides and remove the new lab assets;
  production graph/prefabs and `.meta`/instance IDs never touched; owner dirty files preserved.

### 0.5 Passive two-trigger diagnostic (DESIGN ONLY — not implemented, not run)
One narrowly bounded, **getter/log-only**, owner-run trace; implementation needs separate approval.

- **Hooks (project-verified APIs only):** `ARMST_T2A_WeaponAnimationComponent.OnCharacterCommand(int
  commandID, int intValue, float floatValue)` (proven in `MP133_V3_T2C_COMMAND_TRACE.md`) and the
  existing passive `OnAnimationEvent(...)`. **No** global `HandleWeaponReloading` override, **no** input
  binding change, **no** forced animation command.
- **Per action record:** time + op correlation; `CharacterInputContext.GetWeaponReloadType` **if
  accessible**; `OnCharacterCommand` int/float; active state/clip **only if an existing supported
  observer exposes it**; P/W `Weapon_Spawn/Attach/MagRelease/Detach/Despawn` and `Weapon_Rack_Bolt`
  markers; installed magazine **entity ref/tag + component ref/tag**, ResourceName/GUID, count/max;
  chamber/barrel; donor identity/storage/count before/after each press. No persisted raw pointers beyond
  safe scope.
- **Scenarios:** (i) empty tube + single R; (ii) nonempty tube (1/3 or 2/3) + rapid double-R;
  (iii) nonempty tube + empty chamber + one normal short R (bolt control). Separate first/second
  double-R presses by correlation marker **if** the instrumentation supports it; otherwise mark
  uncertainty. Optional one passive comparison with another pump **only if** no new global hook is
  needed.
- **Labels:** keep `OWNER-RUNTIME` (a swap occurs — fact), `PROJECT-SOURCE` (graph route/clip events),
  `INFERENCE` (which command/clip ran per repro) strictly separate; no guessed integer or ordering in
  conclusions. Absence of an observed clip event does **not** prove the engine cannot swap.
## 1. Trigger paths — empty-R and rapid double-R

### 1.1 What the graph receives (**SOURCE**, `MP133.agf`)
The reload STM path is identical in production and the T2A/lab clone
(`MP133_V3_RELOAD_GRAPH_AUDIT.md` §1.4, §2):
`MasterControl → IdleReloadSTM → WeaponReloadStanceSTM → WeaponReloadSTM → MagReloadSTM`.

`IdleReloadSTM` entry gate (line ~20):
`IsCommand(CMD_Weapon_Reload) && !inRange(GetCommandI(CMD_Weapon_Reload), 7, 9) && GetCommandI(CMD_Weapon_Reload) != -2`.

`WeaponReloadSTM` (line ~214) states:

| `GetCommandI(CMD_Weapon_Reload)` | State | Child source |
|---|---|---|
| `== 1 && F==0.0` | ReloadActionBolt | `Reload.ReloadActionBolt` (bolt; native pump for this weapon) |
| `== 2` / `== 3 && F==0.0` | NoMagReload / NoMagNoBulletReload | `Reload.Reload_InsertMag` (inject clip) |
| `== 4` / `== 5 && F==0.0` | MagReload / MagNoBulletReload | `MagReloadSTM` → `Reload_RemoveMag` then `Reload_InsertMag` |
| `== 6` | RemoveMag | `Reload.Reload_RemoveMag` |

`MagReloadSTM` (line ~158): `RemoveMag` (IsExit 0) → `InsertMag` (IsExit 1), condition
`IsEvent("BlendOut")`, `StartTime GetEventTime(anim.Reload.Erc.Reload_InsertMag, "BlendIn")`.

### 1.2 TRIGGER_EMPTY_R
**Qualifier (REV2): the exact command integer and clip sequence below are `INFERENCE / UNRESOLVED`
until observed by the passive trace (§9); only "a swap occurs" is `OWNER-RUNTIME` fact.**
- **OWNER-RUNTIME (confirmed):** with the tube emptied, a **single R** replaces the installed 3-round
  tube with a carried 10-cap magazine (op21 log; target became 10-cap; G3B2 then rejects
  `target-capacity-mismatch`). This is a **whole-magazine** route: the graph reaches
  `MagReload`/`MagNoBulletReload` (cmd 4/5 → `MagReloadSTM`: Remove then Insert), whose **inject clip
  carries native magazine lifecycle events**. *(Route label: INFERENCE.)*
- **Exact command integer for the empty-tube case: UNRESOLVED without one passive trace.** The
  routing (cmd 4/5 vs 2/3) selects whether `Reload_RemoveMag` also plays; both end in the inject clip
  that performs the attach. `MP133_V3_RELOAD_GRAPH_AUDIT.md` §6 already specifies the one safe passive
  experiment (`OnCharacterCommand(commandID, intValue, floatValue)`) to confirm the actual integer.
- **INFERENCE:** the "reload type" is chosen by the input/command handler from the magazine/chamber
  state (empty tube ⇒ magazine reload), matching `MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md` §0
  (`reloadType=1` for the post-shot bolt case).

### 1.3 TRIGGER_DOUBLE_R
**Qualifier (REV2): exact per-press command integers/order and clip sequence are `INFERENCE /
UNRESOLVED` until observed by the passive trace (§9).**
- **OWNER-RUNTIME (confirmed):** two rapid R presses (not limited to an empty tube) also replace the
  tube. The second command re-enters the reload path; because the inject clip of the **first**
  magazine-reload still carries `Weapon_AttachMagazine`, the native attach completes and installs a
  carried 10-cap magazine. *(Mechanism label: INFERENCE.)*
- **Exact command values / debounce behaviour of the two rapid presses: UNRESOLVED** (runtime);
  however the *mechanism* is the same native inject-clip attach, so the fix that removes the whole-mag
  route neutralizes both triggers without needing the exact per-press integer.

### 1.4 Whole-magazine commands vs bolt; command 7–9 exclusion (**SOURCE**)
- Commands **2–5** (and 6 = remove) are the **whole-magazine** routes; command **1** is the manual
  bolt (`ReloadActionBolt` / `RackBoltAnim`, events `Weapon_EnableFire` + `Weapon_Rack_Bolt`).
- Commands **7/8/9** are **vetoed at the `IdleReloadSTM` entry** (`!inRange(7,9)`) and have no state
  in `WeaponReloadSTM`; command 10 passes the entry but has no state. The MP-133 graph does **not**
  implement the engine's single-projectile (UGL) path.

---

## 2. Which native events cause the swap (**SOURCE**, `.txa`)

Clip-authored events (`MP133_V3_INSERT_EVENT_AUDIT.md` §2.3):

| Clip | Frames@30 | Native events |
|---|---|---|
| `P_/W_MP133_Reload_Inject` | 107 | BlendIn(1), **Weapon_SpawnMagazine(10)**, **Weapon_AttachMagazine(43)**, **Weapon_MagRelease(64)**, BlendOut(100) |
| `P_/W_MP133_Reload_Rem` | 20 | BlendIn(5), **Weapon_MagRelease(6)**, **Weapon_DetachMagazine(10)**, **Weapon_DespawnMagazine(15)**, BlendOut(19) |
| `P_/W_MP133_Reload_Bolt` | 20 | BlendIn(5), **Weapon_EnableFire(10)**, **Weapon_Rack_Bolt(14)** |

- **STOCK_MAG_SWAP_ROOT (proven):** the engine consumes `Weapon_AttachMagazine` (inject clip frame 43)
  and **attaches a whole magazine** as the new ammo source; `Weapon_SpawnMagazine` creates/shows it and
  `Weapon_MagRelease` is the catch animation. Combined with the **empty-tube** route's
  `Weapon_DetachMagazine`/`Weapon_DespawnMagazine` (remove clip), the engine replaces the installed
  tube with a carried magazine. `MP133_V3_INSERT_EVENT_AUDIT.md` §4 and the earlier V2 record
  `reloadType=5 → 3/3 → 10/10` corroborate the whole-mag replace. This is the **physical identity
  change**, not a G3B2 issue, and it is why B2 correctly rejects afterwards.
- **Vanilla `MagazineWell12g`** (inherited `MuzzleComponent {CA6BE4D6B867541F}` → `MagazineWell
  MagazineWell12g`) accepts `armst_12ga_Buckshot` (10-cap) and the lab `Tube3Mag` (3-cap) as valid
  magazines; it does not by itself forbid the swap.

---

## 3. Chungus / BC-Ithaca reference finding (**SOURCE: historical excerpts only**)

The raw BC-Ithaca sources (`BC_PumpShotgunComponent`, `SCR_IthacaAnimationComponent`,
`bc_ithaca_m37_player.asi`) are **not available locally as files** ⇒ **SOURCE_UNAVAILABLE** for the
originals. From the documented excerpts (`MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md` §1–§2, §7):

- Chungus implements its own per-shell flow via **pump-side graph sources** (`Reload_PumpAction`,
  `Reload_GrabShell`, `Reload_InsertShell`, `Reload_OpenAction`, `Reload_CloseAction`) and a
  `BC_PumpActionForward` busy-reset event — **none of these exist in the MP-133 graph/ASI/AST**.
- Its `TryRackBolt` runs off the **trigger-pull edge** (`WeaponIsPullingTrigger`), not R, and calls
  `weaponAnim.CallCommand(...)`, `charAnim.CallCommand(...)` **and** `controller.ReloadWeapon()`.
- `SCR_IthacaAnimationComponent` may **spawn/attach a default magazine when none is present** ⇒ copying
  it risks exactly the magazine replacement/duplication we are diagnosing.

**CORE_FINDING:** `ARMST-PLATFORM---Core` (read-only) only reacts to `Weapon_Rack_Bolt`; its legacy
`ARMST_LIGHT_RELOAD_ACTION` / `OnRackBoltMDown` SHIFT+R path is a **failed experiment**, not a working
reload, and it does not implement a magazine-preserving insert. Core is **not** the fix.

**CHUNGUS_FINDING:** usable only as a **pattern reference for LATER G4-B** (staged
prepare/grab/insert/continue/stop, per-shell cadence). It must **not** be copied (dummy +1, magazine
spawning, duplicate chamber/feed, `ReloadWeapon()` semantics are unproven for preserving the tube).

---

## 4. Options, ranked (lab-only)

| Rank | Option | What it does | Pros | Cons / constraints |
|---|---|---|---|---|
| **1 (preferred, see §0.3/§0.4)** | **Lab-owned animation graph + ASI that routes ALL whole-mag commands off the stock remove/insert clips** (V2 lab pattern extended to the remove path) | A lab-only `WeaponAnimationComponent` on the two active G3-B2 fixtures points at a lab-owned `MP133_G4A.agr`/`_weapon.asi`/`_player.asi` whose whole-magazine states (cmd 2–6) are routed to inert lab clips / a non-mag route so **neither** `Reload_RemoveMag` **nor** `Reload_InsertMag` native events (`Weapon_Spawn/Attach/MagRelease/Detach/Despawn`) can run; `BlendIn`/`BlendOut` are preserved for graph transitions | (a) The installed tube entity stays the same **only if all remove AND insert routes are covered** (§0.1); (b) short-R bolt (cmd 1), chambering, fire and hold-R inspection are untouched (they use other states/clips); (c) fully isolated to the two lab weapons, other shotguns/weapons unaffected; (d) reversible | Requires a lab animation graph/ASI + sanitized **remove and insert** clips (owner-imported ANM); native per-shell ammo still comes from **G3B2**; engine-internal non-clip side effects **UNVERIFIED**. Removing events from one clip is insufficient (§P0) |
| 2 | **Magwell/config gate** (make the well accept only the 3-cap magazine) | Restrict accepted magazine resource per magwell | No graph change if the engine supports it | No proven prefab field was found that filters magazines by resource at the magwell for a `MagazineWell` in this project; risk of guessing a field (**UNRESOLVED**); magwell is inherited from the base, so this would touch the production chain unless overridden lab-locally. Not chosen |
| 3 | **Weapon-gated input interception** (`HandleWeaponReloading`) | Suppress/remap whole-mag commands only for the lab weapon | No graph assets | `HandleWeaponReloading` is a global handler override; proving it cannot affect other weapons requires a per-weapon guard and a global hook — fails the "prove safe for all other weapons" bar in this bounded task; risks duplicating native routes. Not chosen |

**Why the events cannot simply be "unregistered":** the `Weapon_*Magazine` events are **authored in
the clip** and consumed by the **engine** (native), not by project script; a project listener cannot
suppress them (`MP133_V3_INSERT_EVENT_AUDIT.md` §2.4, §4). The only way to stop the native attach is
to **not play a clip that carries `Weapon_AttachMagazine`** on the whole-magazine routes — i.e. the
sanitized-clip + lab-graph route (Option 1). Changing `MaxAmmo` does **not** make a magazine
non-removable.

---

## 5. Preferred lab-only fix + exact future allowlist (for a SEPARATE G4-A implementation task)

**Superseded by §0.3.** The original §5 text below described an **inject-only** sanitization; that is
**insufficient and rejected** (P0, §0.1). The corrected fix routes **ALL** whole-magazine commands
(2–6) off the stock remove **and** insert clips (Option A graph redirection, or Option B sanitized
**both** remove+insert clips), preserving `BlendIn`/`BlendOut` and the cmd-1 bolt/chamber/fire. See
§0.3 (design) and §0.4 (exact allowlist + rollback). The text below is retained as the historical
inject-only draft and must not be implemented as written.

### 5.0 (historical, superseded) inject-only draft

**Change (one minimal, reversible, lab-only):** add a lab-owned animation graph/ASIs derived from the
existing AnimationLab V2 pattern and point the two active G3-B2 fixtures' `WeaponAnimationComponent`
at it, with the inject clip sanitized (native `Weapon_*Magazine` events → inert custom events) so the
whole-magazine routes cannot attach/replace the tube. Bind the physical 3-round `Tube3Mag` is already
done (G3-B2 physical-tube task).

**Proposed future file allowlist (NOT created now):**
- `ARMSTMP133T4B_InstalledMagProbe/Assets/.../MP133_G4A.agr` (+ `.agf` copy of the production graph
  with the reload states routing the whole-mag commands to the inert clip / bolt), `.ast`, `.aw`.
- `ARMSTMP133T4B_InstalledMagProbe/Assets/.../MP133_G4A_weapon.asi` /
  `MP133_G4A_player.asi` (lab-owned copies; `Reload.Erc/Pne.Reload_InsertMag` → sanitized clip;
  **short-R bolt, chambering, fire, inspection clips unchanged**).
- `ARMSTMP133T4B_InstalledMagProbe/Assets/.../LabClips/W_/P_MP133_G4A_Inject.anm` (+ `.txa`) — the
  sanitized inject clip (native magazine events replaced by inert ones).
- The **two** active G3-B2 weapon `.et` files (add a lab `WeaponAnimationComponent` override pointing
  at the G4A graph/ASI; keep their existing GUIDs/instances/actions/write settings).
- Lab `MANIFEST.sha256`; G3-B2/G4-A design report; MP133 index; sync.

**Rollback:** revert the two `.et` `WeaponAnimationComponent` overrides (the production graph remains
untouched) and remove the new lab assets; the lab weapons immediately return to the stock behaviour.

**Risks to weigh (design):**
- **Short-R bolt (cmd 1):** must keep `ReloadActionBolt`/`RackBoltAnim` and its
  `Weapon_EnableFire`/`Weapon_Rack_Bolt` events untouched — chambering and firing rely on them.
- **Rapid double-R:** neutralized only if the whole-mag commands (2–5/6) resolve to the inert clip;
  if the engine still reaches a native attach via another clip, the swap can persist ⇒ report.
- **Hold-R inspection:** uses `WeaponInspectionSTM`/`WeaponInspectionState`, independent of the reload
  clips ⇒ expected unaffected; verify.
- **Network / chamber / other shotguns:** lab-only assets + two lab prefabs only; no production chain
  change; MP remains UNVERIFIED.

**Stop criteria:** if a lab graph/ASI cannot be shown to keep the tube's **same physical entity** on
empty-R and double-R without breaking short-R bolt/chamber/fire, or if any change would touch the
production graph/prefab chain or other weapons ⇒ **STOP** and report `NO_SAFE_LAB_SOLUTION`.

---

## 6. Owner acceptance matrix (design only; DO NOT claim PASS)

- Equipped WRITE-ON lab fixture with physical 3/3 `Tube3Mag` GUID **and the same runtime entity/mag
  component identity** throughout.
- Empty tube + single R: **no** remove/replace/attach; carried donor unaffected.
- Tube 1/3 or 2/3 + rapid double-R: **no** mag replacement; donor unaffected.
- Tube >0, chamber empty + normal short R: valid native bolt/feed; no unwanted shell loss.
- G3B2 action + eligible carried donor: `0→1→2→3` on the SAME target, donor −1 each; busy/full guards
  and both delayed samples intact.
- Fire, dry/last shell, hold-R inspection, weapon switch; no regression on an unrelated pump shotgun;
  multiplayer separately UNVERIFIED.
- **STOP** on: changed target identity, capacity 10, phantom/double count, donor loss, broken
  bolt/chamber, or any reload change affecting other weapons.

---

## 7. Facts / hypotheses / unresolved

| Statement | Label |
|---|---|
| Whole-mag commands 2–5/6 route to inject/remove clips carrying native `Weapon_Spawn/Attach/MagRelease`; cmd 1 is the bolt; 7–9 vetoed | **SOURCE** |
| The engine attaches a whole magazine on `Weapon_AttachMagazine` ⇒ tube replaced | **SOURCE** (+ OWNER-RUNTIME V2 `3/3→10/10`) |
| Empty-tube R and rapid double-R both reach a magazine-reload route that attaches a carried mag | **OWNER-RUNTIME** (confirmed bug), **mechanism SOURCE** |
| Exact command integer for empty-R and the two rapid presses | **UNRESOLVED** (one passive trace, graph audit §6) |
| Chungus originals available locally | **SOURCE_UNAVAILABLE** (excerpts only) |
| A prefab/magwell field that filters accepted magazine resource | **UNRESOLVED** (no proven field) |
| Sanitized-clip + lab-graph keeps the tube entity while preserving bolt/fire | **INFERENCE** (V2 built the pattern; runtime UNVERIFIED) |
| MP authority/replication of the fix | **UNRESOLVED** |

---

## 8. Required response summary

- `G4A_REV2_STATUS: COMPLETE`
- `SOURCE_HEAD: dd215e1545279bd3485bbd9daf24716250dc0673` (audit base `ad89a18`)
- `READONLY_GAMEPLAY_FILES_CHANGED=0` (this report + prior docs only)
- `REMOVE_PATH_ACCOUNTED_FOR: YES` — cmds 4/5/6 → `Reload_RemoveMag` (`Weapon_MagRelease` f6,
  `Weapon_DetachMagazine` f10, `Weapon_DespawnMagazine` f15); inject-only sanitization rejected as
  unsafe (§0.1).
- `ALL_COMMAND_ROUTES_MAPPED_OR_UNRESOLVED`: 1/2/3/4/5/6 mapped (SOURCE); per-press integer for empty-R
  and double-R **UNRESOLVED**; engine-internal non-clip side effects **UNVERIFIED**.
- `R_DIAGNOSTIC_DESIGNED_NOT_RUN` (§0.5).
- `PREFERRED_MINIMAL_LAB_FIX`: route **all** whole-mag commands (2–6, Erc/Pne, P/W) off the stock
  remove/insert clips — Option A (graph redirection) or Option B (sanitized **both** remove+insert
  clips, `BlendIn`/`BlendOut` kept); cmd 1 bolt/chamber/fire untouched (§0.3, §0.4 allowlist).
- `UNRESOLVED`: exact command integers per repro; engine-internal magazine side effects outside clips;
  behavior of a magazine detached mid-animation; `WeaponAnimationComponent`/both ASI binding for the
  two fixtures at runtime; ANM compile/import validity.
- `GAMEPLAY_FILES_CHANGED=0`
- `STOP_FOR_INDEPENDENT_REVIEW`

**Not authorized here:** any graph/ASI/ANM/TXA/prefab/script/Core/production change, input config,
magazine donor/capacity relaxation, the passive diagnostic implementation, G4-B animation, G5/MP, or
Workbench/game run. This REV2 changes this report only.

---

## 9. PASSIVE-R-TRACE V1 (source prepared, not run) — Issue #34 comment 5979262345

**What it is:** reuse of the **already-published** T4b diagnostic on the **current G3-B2 WRITE-ON**
fixture, instead of writing a new handler. The lab script `ARMST_T4B_InstalledMagProbe.c` already
implements (SOURCE, verified):
- `ARMST_T4B_WeaponAnimationComponent.OnCharacterCommand(int,int,float)` → `super` + `[ARMST_T4B-CMD]`;
- `OnAnimationEvent(...)` → pre/post-super `[ARMST_T4B-EVT]` for `Weapon_SpawnMagazine`,
  `Weapon_AttachMagazine`, `Weapon_MagRelease`, `Weapon_DetachMagazine`, `Weapon_DespawnMagazine`,
  `Weapon_Rack_Bolt`, `Weapon_EnableFire`, `BlendIn/Out`;
- `ARMST_T4B_WeaponProbe` → `[ARMST_T4B-INSTALLED]` snapshot with **entity-reference** `magTag=M#`,
  mag prefab, ammo/max, chamber/barrel, plus a post-`BlendOut` +250 ms snapshot.

**Source-prepared change (this V1, lab-only, one prefab):** in
`labs/ARMSTMP133T4B_InstalledMagProbe/Prefabs/Test/ARMST_T4B_G3B2_InventoryWide_WriteOn_TestWeapon.et`,
inside the existing inherited `WeaponComponent {CFBAA4B706BA66E8} → components`, the inherited
weapon-animation instance `{60B4EA76EB15F6E0}` is now overridden by
`ARMST_T4B_WeaponAnimationComponent {60B4EA76EB15F6E0}` (the proven `ARMST_T4B_TestWeapon.et` pattern:
**same instance, subtype substitution, no second component, no graph/ASI override**). Retained:
`MuzzleComponent.MagazineTemplate = Tube3Mag`, prefab `ID 899AABBCDDEEFF00`, the
`ARMST_T4B_WeaponProbe` baseline `2`, and the WRITE-ON `TransferAction` (`writeEnabled 1`,
`inventoryWide 1`, unchanged UI). The **OFF** fixture and `ARMST_T4B_TestWeapon.et` are unchanged.

**Output markers (for the owner log):** `[ARMST_T4B-CMD]` (commandID/intValue/floatValue),
`[ARMST_T4B-EVT]` (pre/post-super animation events), `[ARMST_T4B-INSTALLED]` (`magTag` entity ref,
mag prefab, ammo/max, chamber/barrel). `[ARMST_T4B-CMD]` has a per-instance cap of 400 — respawn
rather than change the log limit.

**Limitations (do not overstate):** the probe identifies the installed mag by **owning-entity
reference tags**, not a standalone component-reference tag; it does **not** capture all carried donor
inventory counts; the **exact command integers remain UNRESOLVED** until the owner run; and a static
pass is **not** proof of Workbench/compile/runtime success. The existing T4b baseline init
`SetAmmoCount(m_iT4BStartAmmo=2)` is a **pre-existing setup write**; this V1 adds **zero** new writers
and does not touch G3-B2's setters or `m_iG3B2RequiredTargetMax=3`.

**Owner-only later scenarios (design/checklist; NOT run here):** each starts with a fresh disposable
WRITE-ON fixture after owner sync/recompile, installed real `Tube3Mag` (`2/3`, `baselineDone=1`), a
separately identified 10-cap donor in the vest, and full `console.log`/`script.log` timestamps. **Do
not invoke the G3-B2 action during the R trace.**
- **A. Bolt control:** nonempty tube + empty chamber, one ordinary short R.
- **B. Empty tube:** deplete the tube by permitted gameplay (do not manually install the donor), one
  short R; capture remove/inject events, swapped/lost magazine and donor count.
- **C. Double-R:** fresh fixture, nonempty tube (1/3 or 2/3), two rapid R presses; record the
  chronological command/event sequence, `magTag`/prefab/capacity and chamber transitions.
For B/C an observed changed `magTag`/10-cap target is the **expected bug evidence**, not a probe fault.
STOP each scenario on unexpected ammo loss, duplicate chamber manipulation, compile errors or loss of
unrelated weapon reload.

`PASSIVE_R_TRACE_V1_SOURCE_STATUS: PREPARED` (lab prefab + manifest + this report only).
