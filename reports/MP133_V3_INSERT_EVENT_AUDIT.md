# MP-133 V3 — Insert-animation event audit (read-only)

**Status:** `INSERT_EVENT_AUDIT_DONE; ONE_MINIMAL_TEST_PROPOSED; NOT_RUN`.
Analysis only. No production Weapons / Core / lab / animation edits; no Workbench/game by
the agent. Source: Issue #27 owner task. Bridge stays PAUSED; V2 frozen.

---

## 1. What was inspected (evidence)

- Clips: production `P_/W_MP133_Reload_Inject.txa`, `P_/W_MP133_Reload_Rem.txa`,
  `P_/W_MP133_Reload_Bolt.txa` (`ARMST-PLATFORM---Weapons/.../Mp_133/Workspace/Reload/`).
- ASI/workspace: `MP133_player.asi`, `MP133_weapon.asi`, `MP133.ast`, `MP133.agr`,
  `MP133.agf`, `MP133.aw` (production) and the lab copies `MP133_T2A.*` (T2A Diag).
- Prefab: `Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et` +
  `Western/Shotgun/core/armst_shotgun_base.et`; magazine `12ga_Buckshot_base.et` /
  `armst_12ga_Shell.et` (`MagazineWell12g`, `MaxAmmo 10`, `Ammo_12g`).
- Prior evidence: `MP133_V3_2_ANIM_EVENT_FINDING.md`, `MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md`,
  `MP133_ANIMATION_LAB_V27_C2_TRACE_AND_CORE_ISOLATION.md`, `MP133_INDEX.md`, the V2 lab
  script `ARMST_MP133_AnimationLab/.../ARMST_MP133_Lab_Character.c`.
- Official Bohemia docs: `CMD_Weapon_Reload` table, `WeaponAnimationComponent` API,
  `Reload_InsertMag` descriptor.

---

## 2. Confirmed facts

### 2.1 Commands (`CMD_Weapon_Reload`, official)
| Int | Float | Meaning |
|---|---|---|
| 1 | 0.0 | rack bolt |
| 2 | — | attach the magazine, no rack |
| 3 | 0.0 | attach the magazine, then rack |
| 4 | — | detach + attach the magazine |
| 5 | 0.0 | detach + attach the magazine, then rack |
| 6 | — | detach the magazine |
| **7** | — | **insert a single projectile (UGL)** |
| 8 | — | remove a single projectile (UGL) |
| 9 | — | remove all projectiles and reinsert (UGL) |
| 10 | — | skip animations and reload |

### 2.2 Graph routing (`MP133.agf`, `WeaponReloadSTM`) — identical in production and T2A lab
- `== 1 && F==0.0` → **ReloadActionBolt** → `ReloadActionBolt` clip (bolt; `Weapon_EnableFire`,
  `Weapon_Rack_Bolt`).
- `== 2` / `== 3 && F==0.0` → **InsertMagAnim** = `Reload.Reload_InsertMag` (the inject clip).
- `== 4` / `== 5 && F==0.0` → **MagReloadSTM** (RemoveMag → InsertMag) = remove + inject clips.
- `== 6` → **RemoveMagAnim** = `Reload_RemoveMag`.
- The `IdleReloadSTM` entry condition is
  `IsCommand(CMD_Weapon_Reload) && !inRange(GetCommandI(...), 7, 9) && != -2`.
  **Commands 7/8/9 are excluded and have no state** — the MP-133 graph does not implement
  the engine's "single projectile" path.
- `MagReloadSTM` transition RemoveMag→InsertMag uses `IsEvent("BlendOut")`, i.e. the graph
  timing does **not** depend on the magazine events.

### 2.3 Insert / remove clip events (exact)
`P_/W_MP133_Reload_Inject` — **107 frames @30 fps**:
| Frame | time | Event |
|---|---|---|
| 1 | 0.033 | BlendIn |
| **10** | **0.333** | **Weapon_SpawnMagazine** |
| **43** | **1.433** | **Weapon_AttachMagazine** |
| **64** | **2.133** | **Weapon_MagRelease** |
| 100 | 3.333 | BlendOut |

`P_/W_MP133_Reload_Rem` — **20 frames @30 fps**:
| Frame | time | Event |
|---|---|---|
| 5 | 0.167 | BlendIn |
| 6 | 0.200 | Weapon_MagRelease |
| 10 | 0.333 | Weapon_DetachMagazine |
| 15 | 0.500 | Weapon_DespawnMagazine |
| 19 | 0.633 | BlendOut |

All `MainPathOnly 0`.

### 2.4 Weapon / magazine
- `armst_Shotgun_mp_133.et` (`WeaponAnimationComponent {60B4EA76EB15F6E0}`):
  `AnimGraph MP133.agr`, weapon `AnimInstance MP133_weapon.asi`, `AnimInjection` → same graph +
  **player** `MP133_player.asi` (root binding `Weapon`).
- `MuzzleComponent` carries `MagazineWell MagazineWell12g` and
  `MagazineTemplate armst_12ga_Buckshot.et`; `ManualAction 1`.
- The ARMST MP-133 "tube" is a **detachable 10-round magazine** (`armst_12ga_Buckshot`:
  `MagazineComponent.MaxAmmo 10`, 12g). It is not a fixed tube.
- `Reload_InsertMag` is officially defined as "Animation of **inserting magazine** into the
  weapon"; `722_Weapon_MagRelease profile` is the animated magazine-release.

---

## 3. Answer: which event is a shell insert vs a stock magazine operation

**None of the three events is a per-shell insert.** They are the engine's stock
**whole-magazine lifecycle**:

| Event | What the engine does | Role |
|---|---|---|
| `Weapon_SpawnMagazine` (f10) | spawns/shows the **magazine** object | stock mag create |
| `Weapon_AttachMagazine` (f43) | **attaches a whole magazine** to the magazine well (becomes the ammo source) | stock mag **insert** (whole mag) |
| `Weapon_MagRelease` (f64) | magazine-release / catch animation | stock mag latch/release |

- The visible "insert" moment is `Weapon_AttachMagazine` (f43), but it inserts **one whole
  magazine**, not one shell.
- The engine's genuine single-projectile concept is `CMD_Weapon_Reload` **7**, which the
  MP-133 graph **excludes (7–9) and does not implement**. There is therefore **no native
  per-shell insert event** for this weapon.
- `Weapon_MagRelease`(+`Weapon_DetachMagazine`/`Weapon_DespawnMagazine` on remove) is the
  catch/release path; it is a magazine operation, not a shell insert.
- The only "per shell" semantics in the project are the **custom** lab events
  `ARMST_Lab_Shell_Spawn/Commit/Release` (V2), which the engine does not understand and
  which are handled only by project script.

**Receivers:** these vanilla events are consumed by the **engine** (native weapon/magazine/
animation system). Project code: Core reacts only to `Weapon_Rack_Bolt`; the V2 lab
registers the mag events but acts **only** on `ARMST_Lab_Shell_Commit` and `Weapon_Rack_Bolt`.
No project handler performs a per-shell insert.

---

## 4. Why restoring the native events "made the animation work" but left the magazine/ammo question

- With the **custom** `ARMST_Lab_Shell_*` events the engine's magazine system receives
  nothing → no magazine spawn/attach → the insert visually does not happen (and no ammo
  moves except via the lab script). This is why the sanitized V2 experiment needed a
  scripted `tube+1`.
- With the **native** events the engine runs its full stock path: spawn magazine (f10) →
  **attach a whole magazine** (f43) → release/catch (f64). The insert therefore *appears*
  to work — because the engine physically spawns and attaches a real, full magazine.
- Consequence: it is a **whole-magazine replace**, not a per-shell load. V2 recorded
  `reloadType=5 → 3/3 → 10/10` (the real 3-round lab tube replaced by a full stock
  magazine). So the physical magazine is **not** preserved and ammo is not conserved — the
  exact open question. `Weapon_AttachMagazine` is therefore unsafe as a per-shell commit
  trigger (V2.3 had already switched the commit to the custom event).
- Additional caution: `armst_12ga_Shell.et` holds 10 rounds with a mixed `AmmoMapping`;
  artificial mag `+1`/dummy-ammo tricks risk entity deletion/duplication (per the earlier
  design note, do not touch ammo without proof).

---

## 5. Facts / hypotheses / unknowns

- **Facts:** clip frames/events; graph command routing (Reload_InsertMag only for 2/3/4/5;
  cmd 1 → bolt; 7–9 excluded); prefab graph/ASI/magazine wiring; magazine is a 10-round
  detachable `MagazineWell12g`; `Reload_InsertMag` = magazine insert (official);
  `Weapon_SpawnMagazine/AttachMagazine/MagRelease` consumed by the engine; no project
  per-shell native handler.
- **Hypotheses (need the test):** that `Weapon_AttachMagazine`(f43) is the exact moment the
  physical magazine identity changes and ammo resets; that `Weapon_SpawnMagazine`/
  `Weapon_MagRelease` do not change identity/ammo; whether these events are observable on a
  project callback vs engine-internal only.
- **Unknowns:** physical magazine *entity* identity before/after a stock insert (never
  instrumented); whether a sanitized (custom-event) clip still plays the full insert visual
  while leaving the magazine untouched (Option B, V2); MP authority.

---

## 6. Proposed ONE minimal diagnostic test (T3 — logging-only, not implemented)

**Goal:** attribute the magazine/ammo change to a specific event, and measure whether the
physical magazine survives a stock insert — without changing any mechanics.

- **Venue:** existing `ARMSTMP133T2A_Diag` lab (no new addon; prod/Core/V2 untouched).
- **Change (passive only):** in the T2A diagnostic, additionally register
  `Weapon_SpawnMagazine`, `Weapon_AttachMagazine`, `Weapon_MagRelease`,
  `Weapon_DetachMagazine`, `Weapon_DespawnMagazine` and, on each such event (plus
  BlendIn/BlendOut), log: event name, `timeFromStart`, the current magazine prefab name, a
  **physical identity tag** (component-reference comparison, per the V2 trace method) and
  `GetAmmoCount()/GetMaxAmmoCount()`; log both the weapon-side callback and the character
  invoker (whichever actually receives them). No `SetAmmoCount`, no command changes, no
  suppression.
- **Owner run:** equip the lab MP-133 and perform **one stock magazine insert** (the command
  that reaches `Reload_InsertMag`: cmd 2, or the empty-mag reload), and optionally **one
  remove** (cmd 6). Capture `console.log`/`script.log`.
- **Read-out:** after which event the magazine identity tag flips and ammo changes
  (expected: at `Weapon_AttachMagazine`, f43); whether `Weapon_SpawnMagazine`/
  `Weapon_MagRelease` leave identity/ammo unchanged; whether the events are observable at
  all on a project callback; remove-path control.
- **STOP:** no mechanics edits; if the log shows a full 10/10 after the insert that is the
  expected swap confirmation, not a fault. Do not proceed to sanitized-clip A/B or per-shell
  work before this read-out and owner review.

**Note:** this probe cannot *create* a shell insert — it establishes that the native path is
a whole-mag swap. If confirmed, the next (separately authorized) step is the sanitized-clip
A/B (custom events, same frames) to verify the magazine is preserved while the animation
still plays; that is **not** part of this test.

---

## 7. Authorization

Analysis only. No production Weapons/Core/lab/animation edits; no Workbench/game; no ammo,
no reload hook, no graph/ASI/ANM changes. Bridge stays paused. Await owner review before any
T3 implementation.
