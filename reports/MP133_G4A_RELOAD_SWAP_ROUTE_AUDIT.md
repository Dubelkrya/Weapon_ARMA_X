# MP-133 G4-A — native magazine swap route audit + lab-only design (READ-ONLY)

**Status:** `G4A_AUDIT_STATUS: COMPLETE`. Read-only engineering audit and design. **No gameplay
implementation in this task.** No game/animation/prefab/script/Core/production edit, no new
branch/addon, no Workbench/game run by the agent.

**Authority:** Issue #34 comment `5975411582` (G4-A task). Checkpoint at task creation
`4807dfd7244c27a263b83e10f8f5ade07f1f87ae`; resolved HEAD (this audit)
`4807dfd7244c27a263b83e10f8f5ade07f1f87ae`, `origin/t4b/installed-mag-probe` identical, working tree
clean except owner-untracked `reports/CORE_ARMST_READONLY_AUDIT.md`.

Labels: **SOURCE** (file read), **OWNER-RUNTIME** (owner log/observation), **INFERENCE**,
**UNRESOLVED**.

`READONLY_GAMEPLAY_FILES_CHANGED=0` (this task writes one report + sync/index only).

---

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
- **OWNER-RUNTIME (confirmed):** with the tube emptied, a **single R** replaces the installed 3-round
  tube with a carried 10-cap magazine (op21 log; target became 10-cap; G3B2 then rejects
  `target-capacity-mismatch`). This is a **whole-magazine** route: the graph reaches
  `MagReload`/`MagNoBulletReload` (cmd 4/5 → `MagReloadSTM`: Remove then Insert), whose **inject clip
  carries native magazine lifecycle events**.
- **Exact command integer for the empty-tube case: UNRESOLVED without one passive trace.** The
  routing (cmd 4/5 vs 2/3) selects whether `Reload_RemoveMag` also plays; both end in the inject clip
  that performs the attach. `MP133_V3_RELOAD_GRAPH_AUDIT.md` §6 already specifies the one safe passive
  experiment (`OnCharacterCommand(commandID, intValue, floatValue)`) to confirm the actual integer.
- **INFERENCE:** the "reload type" is chosen by the input/command handler from the magazine/chamber
  state (empty tube ⇒ magazine reload), matching `MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md` §0
  (`reloadType=1` for the post-shot bolt case).

### 1.3 TRIGGER_DOUBLE_R
- **OWNER-RUNTIME (confirmed):** two rapid R presses (not limited to an empty tube) also replace the
  tube. The second command re-enters the reload path; because the inject clip of the **first**
  magazine-reload still carries `Weapon_AttachMagazine`, the native attach completes and installs a
  carried 10-cap magazine.
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
| **1 (preferred)** | **Lab-owned animation graph + ASI with a sanitized inject clip** (the V2 lab pattern) | A lab-only `WeaponAnimationComponent` on the two active G3-B2 fixtures points at a lab-owned `MP133_G4A.agr`/`_weapon.asi`/`_player.asi` whose `Reload.*.Reload_InsertMag` resolves to a **sanitized clip** (native `Weapon_SpawnMagazine/AttachMagazine/MagRelease` replaced by inert custom events, same 107 frames) and whose whole-magazine states (cmd 2–5/6) are routed to that inert clip or a bolt-only clip | (a) Physically **never attaches/replaces** the tube; the installed entity stays the same; (b) short-R bolt (cmd 1), chambering, fire and hold-R inspection are untouched (they use other states/clips); (c) fully isolated to the two lab weapons, other shotguns/weapons unaffected; (d) reversible | Requires a lab animation graph/ASI + one sanitized clip; the native per-shell ammo still comes from **G3B2** (already proven). Removing the events means a stock full-mag seek would no longer visually "load" a magazine — acceptable for the lab |
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

- `G4A_AUDIT_STATUS: COMPLETE`
- `SOURCE_HEAD: 4807dfd7244c27a263b83e10f8f5ade07f1f87ae`
- `READONLY_GAMEPLAY_FILES_CHANGED=0`
- `TRIGGER_EMPTY_R`: OWNER-RUNTIME confirmed swap; route = whole-magazine reload → inject clip native
  `Weapon_AttachMagazine`; exact integer UNRESOLVED.
- `TRIGGER_DOUBLE_R`: OWNER-RUNTIME confirmed swap; same native inject-clip attach; exact integers
  UNRESOLVED.
- `STOCK_MAG_SWAP_ROOT`: PROVEN = engine whole-magazine attach on `Weapon_AttachMagazine` (not a
  G3B2/donor/conservation issue).
- `CORE_FINDING`: read-only; legacy SHIFT+R experiment non-functional; no magazine-preserving insert.
- `CHUNGUS_FINDING`: reference only for G4-B; unsafe to copy (mag spawn/attach, dummy +1, duplicate
  feed).
- `OPTIONS_RANKED`: (1) lab-owned sanitized-clip graph/ASI [preferred]; (2) magwell/resource gate
  [no proven field]; (3) input interception [global-hook risk].
- `PREFERRED_LAB_ONLY_FIX` + allowlist: Option 1 (§5).
- `OWNER_TEST_MATRIX`: §6.
- `RISKS`: §5. `UNRESOLVED`: §7.
- `STOP_FOR_OWNER_REVIEW`.

**Not authorized here:** any graph/ASI/ANM/TXA/prefab/script/Core/production change, input config,
magazine donor/capacity relaxation, G4-B animation, G5/MP, or Workbench/game run. One new report plus
sync/index pointers are the only published changes.
