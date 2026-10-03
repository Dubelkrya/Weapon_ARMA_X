# MP-133 V3 — Full reload-graph read-only audit

**Status:** `T2B_PAIRED_MARKERS_CONFIRMED / INSERT_EVENT_AUDIT_DONE / RELOAD_GRAPH_READONLY_AUDIT_DONE / T3_RUNTIME_NOT_RUN`.
Strict read-only research. No addon changed (production Weapons, Core, T2A lab, frozen V2/P2),
no graph/ASI/AST/AGF/AGR/AW/ANM/TXA/prefab/script/GUID/meta edit, no Workbench/game,
`GAMEPLAY_FILES_CHANGED_BY_AUDIT=0`. Source of the task: Issue #27 comment 5970063345.

Statement labels: **SOURCE** (read from a file), **OWNER-RUNTIME** (owner log/observation),
**SCREENSHOT** (owner screenshot, not locally verifiable), **INFERENCE**, **UNRESOLVED**.

---

## 0. Authority and method

- Resolution policy (**SOURCE** `agent/scripts/addon_path.py`): order
  `ARMST_WEAPONS_ADDON_PATH` → `MOD_ROOT` → `addon_path.local.json` → `DEFAULT_ADDON_ROOT`;
  a candidate is accepted only if it has `addon.gproj` + `Prefabs/` and its gproj
  `ID` is in `EXPECTED_GPROJ_IDS = ("ARMSTPLATFORMWeapons",)`; otherwise it raises.
- Python is **not available** in this environment (only the WindowsApps `python.exe` stub),
  so the policy was applied manually (**INFERENCE**, policy-faithful): the default root
  `...\addons\ARMST-PLATFORM---Weapons` exists, has `addon.gproj` + `Prefabs/`, and its
  `ID` is `ARMSTPLATFORMWeapons`, `GUID 6A70E400C54051DC` → **resolution valid** (**SOURCE**
  `ARMST-PLATFORM---Weapons/addon.gproj`).
- HEADs (**SOURCE**): Weapons `b88bc537b8fb0b14aeecda9856b7cce1e17448d8`;
  Core `08cb1f389b16fe552c4b66caac64da2e7f4a65d6`; T2A lab has **no git repo**.
- Dirty state preserved (**SOURCE**): Weapons 29 entries, Core 4 entries (owner work; untouched).
- Lab identity (**SOURCE** `ARMSTMP133T2A_Diag/addon.gproj`): `ID ARMSTMP133T2ADiag`,
  `GUID AF1464F772CC998F`, deps `58D0FB3206B6F859` (base) + `6A70E400C54051DC` (Weapons).

---

## 1. Resource / authority map

### 1.1 Production MP-133 (**SOURCE**)
- Prefab `Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et`
  (`ID 5254ACCA959048B9`) inherits `{6C5E2009CDCD0BD3}.../core/armst_shotgun_base.et`
  (that base inherits `Rifle_M21.et`; base prefab `ID 5254ACCA959048B9`).
- `WeaponComponent {CFBAA4B706BA66E8}` → `WeaponAnimationComponent {60B4EA76EB15F6E0}`:
  - `AnimGraph {315A612FD60832E7}Mp_133/Workspace/MP133.agr`
  - `AnimInstance {CE3F8A5CEF0667C1}.../MP133_weapon.asi`
  - `AnimInjection` → same graph + `{35611B6D7707032D}.../MP133_player.asi`.
- `MuzzleComponent {CA6BE4D6B867541F}`: `MagazineWell MagazineWell12g`, `ManualAction 1`,
  `MagazineTemplate {B0DFDF7AAA9C5D39}Prefabs/Weapons/Magazines/12ga/armst_12ga_Buckshot.et`,
  `MagazinePosition InventoryStorageSlot`.

### 1.2 Graph set and GUIDs (**SOURCE**)
- `MP133.agr` `{315A612FD60832E7}` — control template (variables, commands, IK, tags), points
  to `MP133.agf` `{1E547F9548AB5BD7}` and `MP133.ast` `{23A8072FE1CDE614}`.
- `MP133.agf` — graph logic (1066 lines), group selects, STMs.
- `MP133.ast` — source template: group `Inspection`, group `Reload` with animations
  `BoltPose, Finger_trigger_in/out, Fire, Idle, Idle_finger, IKOffset, Reload_InsertMag,
  Reload_RemoveMag, ReloadActionBolt, Safety, Sight, Switch_Mode_*, Trigger`; columns
  `Erc, Pne`.
- `MP133.aw` — workspace referencing `MP133.agr` + both ASIs.

### 1.3 T2A lab clone (**SOURCE**)
- `Prefabs/Weapons/MP133_T2A/armst_Shotgun_mp_133_T2A.et` (`ID 7FD677C018140DBC`) inherits
  production `{63FF6FDCA4E7E735}armst_Shotgun_mp_133.et`; replaces the weapon animation
  component with `ARMST_T2A_WeaponAnimationComponent {60B4EA76EB15F6E0}`:
  - `AnimGraph {F579D9BAB4D1AE9C}.../T2A/MP133_T2A.agr`
  - `AnimInstance {99E82B778E3C48A7}.../T2A/MP133_T2A_weapon.asi`
  - `AnimInjection` → T2A graph + `{1BCB6E5A1AB12EB6}.../T2A/MP133_T2A_player.asi`.

### 1.4 Clone vs production — proven, not assumed (**SOURCE**)
Normalizing all `{GUID}` tokens and trimming:
| Pair | Result |
|---|---|
| `MP133.agf` vs `MP133_T2A.agf` | **line-identical, 1066 lines** (only GUID values differ; prod uses CRLF, lab LF) |
| `MP133.agr` vs `MP133_T2A.agr` | identical except the asset-path strings (`Mp_133/Workspace/…` vs `Assets/Weapons_RUS/Mp_133/T2A/…`) |
| `MP133.ast` vs `MP133_T2A.ast` | **identical (51 lines)** |
| `MP133.aw` vs `MP133_T2A.aw` | identical except path references |
| `MP133_player.asi` vs T2A | differs only: `Template` path, and **both `ReloadActionBolt` rows** → `{3581B839F53FC345}…/P_MP133_T2A_Bolt.anm` |
| `MP133_weapon.asi` vs T2A | differs only: `Template` path, and **both `ReloadActionBolt` rows** → `{0C775A2108B6D5AD}…/W_MP133_T2B_Bolt.anm` |

**Conclusion:** the T2A graph logic is a faithful clone of production; the only functional
difference is the two `ReloadActionBolt` clips (the marker experiment). `Reload_InsertMag` /
`Reload_RemoveMag` still resolve to the **production** clips in the lab.

Hashes for all files are in §8.

---

## 2. Complete reload state map (**SOURCE**, `MP133.agf`, node/line references)

Reload is reached from `MasterControl → IdleReloadSTM.Reload → Blend T 1 →
WeaponReloadStanceSTM → WeaponReloadSTM → MagReloadSTM`.

### 2.1 `IdleReloadSTM` (line 20) — entry/exit + inspection
States: `Idle` (child `Queue 1`), `Reload` (child `Blend T 1`, `TagWeaponReload`, IsExit 1),
`Buffer1..4` (child `Buffer Use 1`), `WeaponInspection` (child `Blend 2`, IsExit 1).
Transitions:
| From → To | Dur | Condition (exact) | Notes |
|---|---|---|---|
| Idle → Buffer3 | 0.3 | `IsCommand(CMD_Weapon_Reload) && !inRange(GetCommandI(CMD_Weapon_Reload), 7, 9) && GetCommandI(CMD_Weapon_Reload) != -2` | **commands 7/8/9 vetoed** |
| Buffer3 → Reload | 0.3 | `true` | |
| Reload → Buffer4 | 0.3 | `(RemainingTimeLess(0.01) || GetCommandI(CMD_Weapon_Reload) == -2) && WeaponInspectionState == 0` | PostEval 1 |
| Reload → Buffer4 | 0.3 | `(RemainingTimeLess(0.5) || GetCommandI(CMD_Weapon_Reload) == -2) && WeaponInspectionState != 0` | PostEval 1 |
| Buffer4 → Idle | 0.3 | `true` | |
| Idle → Buffer2 | 0.3 | `WeaponInspectionState != 0 && WeaponInspectionState != -2` | |
| Buffer2 → WeaponInspection | 0.5 | `true` | |
| WeaponInspection → Buffer1 | 0.8 | `RemainingTimeLess(0.5) || WeaponInspectionState == -3` | PostEval 1 |
| WeaponInspection → Buffer3 | 0.3 | `IsCommand(CMD_Weapon_Reload) && !inRange(GetCommandI(CMD_Weapon_Reload), 7, 9) && GetCommandI(CMD_Weapon_Reload) != -2` | |
| Buffer1 → Idle | 0.5 | `true` | |
| Buffer4 → WeaponInspection | 0.3 | `WeaponInspectionState != 0 && WeaponInspectionState != -2` | |

### 2.2 `WeaponReloadStanceSTM` (line 288)
`Erc_Cro` (`Stance == 0 || Stance == 1`) → `ReloadErcCroG` (Group `Reload`, Column `Erc`);
`Pne` (`Stance == 2`) → `ReloadPneG` (Column `Pne`); both children = `WeaponReloadSTM`.

### 2.3 `WeaponReloadSTM` (line 214, `TagWeaponReload`)
| State | Child | StartCondition (exact) | TimeStorage | IsExit |
|---|---|---|---|---|
| NoMagReload | `InsertMagAnim` | `GetCommandI(CMD_Weapon_Reload) == 2` | Real Time | 1 |
| NoMagNoBulletReload | `InsertMagAnim` | `GetCommandI(CMD_Weapon_Reload) == 3 && GetCommandF(CMD_Weapon_Reload) == 0.0` | Real Time | 0 |
| MagReload | `MagReloadSTM` | `GetCommandI(CMD_Weapon_Reload) == 4` | Inherit | 1 |
| MagNoBulletReload | `MagReloadSTM` | `GetCommandI(CMD_Weapon_Reload) == 5 && GetCommandF(CMD_Weapon_Reload) == 0.0` | Inherit | 0 |
| ReloadActionBolt | `RackBoltAnim` | `GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(CMD_Weapon_Reload) == 0.0` | Real Time | 1 |
| RemoveMag | `RemoveMagAnim` | `GetCommandI(CMD_Weapon_Reload) == 6` | (default) | 1 |

Transitions:
| From → To | Dur | Condition | Notes |
|---|---|---|---|
| NoMagNoBulletReload → ReloadActionBolt | 0.3 | `RemainingTimeLess(0.1)` | PostEval 1, MotionVecBlend 0x33 0 |
| MagNoBulletReload → ReloadActionBolt | 0.3 | `RemainingTimeLess(0.1)` | PostEval 1, MotionVecBlend 0x33 0 |

**There is no state for `CMD_Weapon_Reload` 7, 8, 9, 10** — they are excluded at the
`IdleReloadSTM` entry and have no target state.

### 2.4 `MagReloadSTM` (line 158)
| State | Child | StartCondition | IsExit |
|---|---|---|---|
| InsertMag | `InsertMagAnim` | `""` | 1 |
| RemoveMag | `RemoveMagAnim` | `True` | 0 |

Transition: `RemoveMag → InsertMag`, Dur 0.3,
`StartTime GetEventTime(anim.Reload.Erc.Reload_InsertMag, "BlendIn")`,
`Condition IsEvent("BlendOut")`, PostEval 1, MotionVecBlend 0x33 0.
`IsEvent("BlendOut")` is a **graph event read from the played source**, not proof of ammo
transfer (**SOURCE** node / **INFERENCE**).

### 2.5 Source nodes present (line references)
`InsertMagAnim` (153, `Source "Reload.Reload_InsertMag"`, No Loop), `RackBoltAnim` (189,
`Source "Reload.ReloadActionBolt"`, No Loop, `BonesInterpolatedInModelSpace {RightHandProp}`),
`RemoveMagAnim` (209, `Source "Reload.Reload_RemoveMag"`, No Loop). Non-reload STMs present
but ammo-neutral: `SafetySTM`, `FingerOnTrigger`, `ModesSTM`, `WeaponInspectionSTM`,
`WeaponInspectionStance`.

---

## 3. Animation / event mapping

### 3.1 Which source each state drives; which clip each ASI resolves (**SOURCE**)
| Command | State | Graph source | Player ASI (`MP133_player.asi`) | Weapon ASI (`MP133_weapon.asi`) |
|---|---|---|---|---|
| 1 | ReloadActionBolt | `Reload.ReloadActionBolt` | `{2E4A565E1D442CE9}P_MP133_Reload_Bolt.anm` | `{45B1772B8AFEAE46}W_MP133_Reload_Bolt.anm` |
| 2 / 3 | NoMagReload / NoMagNoBulletReload | `Reload.Reload_InsertMag` | `{2E4A565E1D442CEA}P_MP133_Reload_Inject.anm` | `{45B1772B8AFEAE47}W_MP133_Reload_Inject.anm` |
| 4 / 5 | MagReload / MagNoBulletReload → `MagReloadSTM` | `Reload_RemoveMag` then `Reload_InsertMag` | `{1A0174AF80728E7E}P_MP133_Reload_Rem.anm` + Inject | `{FBC8FA7934FA4394}W_MP133_Reload_Rem.anm` + Inject |
| 6 | RemoveMag → `RemoveMagAnim` | `Reload.Reload_RemoveMag` | `{1A0174AF80728E7E}P_MP133_Reload_Rem.anm` | `{FBC8FA7934FA4394}W_MP133_Reload_Rem.anm` |
| 7–9 | — (no state) | — | — | — |

**T2A lab override (**SOURCE**):** `ReloadActionBolt` → player
`{3581B839F53FC345}P_MP133_T2A_Bolt.anm`, weapon `{0C775A2108B6D5AD}W_MP133_T2B_Bolt.anm`;
`Inject`/`Remove` unchanged (production).

### 3.2 Clip lengths/fps and authored events (**SOURCE**, `.txa`; `.anm` binary)
- `Reload_Inject` 107f@30: `BlendIn`(1), **`Weapon_SpawnMagazine`(10)**, **`Weapon_AttachMagazine`(43)**,
  **`Weapon_MagRelease`(64)**, `BlendOut`(100). `MainPathOnly 0`.
- `Reload_RemoveMag` 20f@30: `BlendIn`(5), `Weapon_MagRelease`(6), `Weapon_DetachMagazine`(10),
  `Weapon_DespawnMagazine`(15), `BlendOut`(19).
- `ReloadActionBolt` 20f@30: `BlendIn`(5), `Weapon_EnableFire`(10), `Weapon_Rack_Bolt`(14).
  (T2B lab weapon copy adds `ARMST_T2B_WM_6E28B9A4`(12); player T2A copy adds
  `ARMST_T2A_PM_C41F7A29`(12).)

### 3.3 Three distinct event categories (do not conflate)
1. **Graph `IsEvent(...)` condition** — `MagReloadSTM` reads `BlendOut` of the remove source;
   it is a graph transition condition, **not** an ammo commit (**SOURCE**).
2. **Clip-authored events** — `Weapon_SpawnMagazine/AttachMagazine/MagRelease/Detach/Despawn/
   EnableFire/Rack_Bolt` authored in the `.anm`/`.txa` (**SOURCE**).
3. **Native engine side effects** — the engine consumes the `Weapon_*` events and performs
   the magazine operations (spawn/attach/release). **OWNER-RUNTIME** V2 evidence:
   `reloadType=5 → 3/3 → 10/10` (whole-magazine attach). `Weapon_AttachMagazine` is the
   magazine insert; **none of the three is a per-shell insert** (see
   `MP133_V3_INSERT_EVENT_AUDIT.md`). The engine's single-projectile command 7 is excluded
   by this graph (**SOURCE**).

---

## 4. Lifecycle / interrupt / replay (**SOURCE** unless labelled)

- **Normal end (cmd 1):** `ReloadActionBolt` IsExit 1; returns via `IdleReloadSTM`.
- **Normal end (cmd 2/6):** `NoMagReload`/`RemoveMag` IsExit 1.
- **Combined (cmd 3/5):** `NoMagNoBulletReload`/`MagNoBulletReload` (IsExit 0) →
  `ReloadActionBolt` on `RemainingTimeLess(0.1)`.
- **cmd 4/5:** `MagReloadSTM` `RemoveMag`(IsExit 0) → `InsertMag`(IsExit 1) on
  `IsEvent("BlendOut")` with `StartTime GetEventTime(...,"BlendIn")`.
- **Interrupt before/after the insert marker:** there is **no source-level interrupt node**
  inside the reload STMs (the `FireAnim`/`FireEmptyAnim` queue lives under `Idle`, not under
  `Reload`). Whether an actual animation can be cut mid-insert is **UNRESOLVED** (runtime).
- **Repeated short R:** cmd 1 re-enters `ReloadActionBolt` (each request re-evaluates the
  STM). Actual repeat behaviour (queue/cooldown) is **UNRESOLVED** (runtime).
- **Trigger / fire during reload:** not routed by these STMs (**SOURCE**); runtime unknown.
- **Weapon switch:** handled by instance sync, not by this graph (**UNRESOLVED** here).
- **Missing magazine / full / empty:** the reload STMs read only `CMD_Weapon_Reload` and
  `WeaponInspectionState`; `Empty`/`Cocked`/`LastBullet` variables exist in `MP133.agr` but
  are used under `FingerOnTrigger`/`Queue 1`, **not** by the reload STMs (**SOURCE**).
- **Nested STM exit:** `WeaponReloadSTM` is the child of `WeaponReloadStanceSTM`; `MagReloadSTM`
  is the child of `MagReload`/`MagNoBulletReload`. Exits are the `IsExit` flags above.
- **No current route** for a per-shell command: 7–9 excluded; no state.

---

## 5. Design feasibility — per-shell loop (NO implementation)

Available mod-facing pattern: a dedicated `WeaponReloadSTM` state keyed on a distinct
`CMD_Weapon_Reload` value with a **self-transition** on the insert clip's `BlendOut`, so the
clip replays per shell while the command persists. The **frozen V2 lab already built exactly
that** (**SOURCE** `ARMST_MP133_AnimationLab/.../MP133_Lab.agf`): a state
`InsertSingleProjectile { Child "InsertMagAnim"; StartCondition "GetCommandI(CMD_Weapon_Reload) == 7" }`
plus `InsertSingleProjectile → InsertSingleProjectile, Condition IsEvent("BlendOut") && GetCommandI(CMD_Weapon_Reload) == 7`. The active production/T2A graph has **no such state**.

| Option | Pros | Constraints (factual) |
|---|---|---|
| **A. New dedicated STM/state on a distinct command** (V2 cmd-7 pattern) | Isolates per-shell from remove/insert; the self-loop gives a natural per-shell cadence; no change to the native short-R path | Needs a **graph edit**; must pick a command not colliding with 1–6; cmd 7 is the engine "single projectile" and may have native side effects (**UNRESOLVED**); needs an explicit exit/safe-stop; the clip still carries native `Weapon_*Magazine` events unless a sanitized clip is used |
| **B. Extend existing `MagReloadSTM`** (`RemoveMag`→`InsertMag`) | Smallest graph change; reuses the existing insert state | This path is the **whole-magazine** remove→insert; the clip fires native `Spawn/Attach/MagRelease`; cannot express repeated single shells without a loop; touches physical magazine identity |
| **C. Alternative route** (reuse cmd 1 `ReloadActionBolt`, or a new graph source) | No new state | Cmd 1 is the **native manual pump** (control says keep it); overloading it conflicts with the native short-R; a new source needs a new clip source (`.ast`/ASI) and owner import |

**Conflicts to hold in view:** native whole-magazine
`Weapon_SpawnMagazine/AttachMagazine/MagRelease`; physical magazine identity
(`MagazineWell12g` + `armst_12ga_Buckshot`, MaxAmmo 10) — a real mag swap replaces the
entity; native short-R = cmd 1; hold-R = `WeaponInspectionState` routed through
`IdleReloadSTM`. **Animation events alone do not guarantee ammo transfer** (V2 showed the
engine attaches a full magazine; the lab's scripted commit is the only per-shell accounting).

---

## 6. Minimal next gate (ONE experiment; NOT implemented / NOT run)

**Goal:** resolve the most important graph uncertainty — **which `CMD_Weapon_Reload`
integer/float the active graph actually receives** for (a) an ordinary short R and (b) a
stock magazine reload, and whether 7–9 ever occur.

**Method (passive, lab-only, no graph/ASI/clip edits):** add a passive override of the
documented animation-command callback
`WeaponAnimationComponent.OnCharacterCommand(int commandID, int intValue, float floatValue)`
(**SOURCE** official API) to the **already present** lab subclass
`ARMST_T2A_WeaponAnimationComponent`, logging `commandID/intValue/floatValue` (+ `isServer`).
Owner equips `MP-133 [T2A-DIAG]`, performs one ordinary short R and one stock magazine
reload (and, if safe, one remove), and returns the log.

**Read-out:** the actual command ids per action (e.g. short R = 1? stock reload = 2/4? ever
7?), which decides whether a per-shell route could piggyback on an existing command or needs
a new one. This is **one** experiment, separately approvable.

**Explicitly not in this task:** T3 magazine-identity diagnostics (preserved as approved
idea), sanitized-ANM A/B, T1/T2c, event bridge, RPC, per-shell implementation.

---

## 7. Facts / hypotheses / unresolved

| Statement | Label |
|---|---|
| Active production and T2A graphs: `Reload_InsertMag` only for cmd 2/3/4/5; cmd 1 → bolt; 7–9 excluded | **SOURCE** |
| T2A `.agf` logic == production `.agf` (1066 lines, GUID-normalized); `.ast` identical; ASIs differ only in `ReloadActionBolt` | **SOURCE** |
| V2 lab added `InsertSingleProjectile` (cmd 7) with a `BlendOut` self-loop (historical) | **SOURCE** |
| Engine performs whole-magazine attach on the native events; `reloadType=5 → 3/3→10/10` | **OWNER-RUNTIME** |
| Whether the engine can cut a reload mid-insert; replay/cooldown; weapon-switch | **UNRESOLVED** |
| Which command id ordinary short R gives the graph (cmd 1 vs other) | **UNRESOLVED** (gate §6) |
| Cmd 7 native side effects (if a per-shell state were added) | **UNRESOLVED** |
| Physical magazine identity across a stock insert | **UNRESOLVED** (T3) |

---

## 8. Hash manifest (read-only; pre == post) and integrity

All consumed gameplay files were read only. SHA-256 (**SOURCE**):

```
094ECCA3431706A9C5E6D6AACF15EBD85A8F60A648D0696B713241956485A939  ...\Weapons\...\Mp_133\Workspace\MP133.agr
7F19A71D7C0786C83124C2ED5EFEBA902AC14A6D1DCCB54D45163F775BC2A062  ...\Mp_133\Workspace\MP133.agf
4C44B016C83C5F0765B9D2118E7F903A6727D91BF91C66D99F9E3382518E47F7  ...\Mp_133\Workspace\MP133.ast
DBCE94CA3138819457009473167E73398BEC73E86BC7FA54B19A5D9E71A5E7BB  ...\Mp_133\Workspace\MP133.aw
9A78CE05E43F9CDDE720E91160BB2199DEFBC951E27740039481F7EC80038E57  ...\Mp_133\Workspace\MP133_weapon.asi
D5676BA2C9C4DBF2FBE5EEC3E568746272CD0BD7A9654D7FEE61BD762ACB97C0  ...\Mp_133\Workspace\MP133_player.asi
2F876E731CC91208CDC309558ADDC302DC3996907060EFB3DBE5444FD79EECEC  ...\Workspace\Reload\P_MP133_Reload_Inject.anm
1579846A9CE2D0631E864862A350AC4624B747B9425E17B27F8A5236C4FAF802  ...\Reload\W_MP133_Reload_Inject.anm
B53325B7932DF2D64726988D7271CA956CBAC572FB1FECEAEB55544E6F1D4327  ...\Reload\P_MP133_Reload_Rem.anm
F92AA408892012DDF20C84CB2FF9AA10F8F24E55957EED8D417E404A4453B243  ...\Reload\W_MP133_Reload_Rem.anm
A992E47AEFECA7E5C1757AEF52675112C6E39770BDABE587FD4EDF3C726F91E4  ...\Reload\P_MP133_Reload_Bolt.anm
F3E8F47B22AA7DD8A45699D954A93287A670D24622D5955099D95E36EB2BD903  ...\Reload\W_MP133_Reload_Bolt.anm
463EFB0C9BDBB107BB29098050E970D09347ADBFCD90365404B58309A9CECA49  ...\Prefabs\Weapons\Russian\Shotgun\armst_Shotgun_mp_133.et
49D6D3534996A0303BEEC4E25F3E4CFF1F45F806674C8972596CAABFA3CA05AB  ...\core\armst_shotgun_base.et
DFD6B4DD375BF79E3E96BA39695A599945C7CEAA928BA900F1D69EBB589E30D1  ...\Magazines\12ga\12ga_Buckshot_base.et
266D86496ECB1A9E431E2E277BB9341D4BEC37CE2AE08C4B6BE517FCCBAA8847  ...\Magazines\12ga\armst_12ga_Shell.et
90865DEF3CB02ECA7A9F31630E0E9C52A0C5E25CA7B87F368652B02FC792D4C5  ...\T2A\MP133_T2A.agr
7D7176C9E3B0B4C5E6C36DA71D3B10B12EEADEA541BAF4FEA62B714F1552B062  ...\T2A\MP133_T2A.agf
53F33E08C5824FB485EA7ACB0F77D8EBD5889A5FFFED5593EAA1F8696FB90AED  ...\T2A\MP133_T2A.ast
E24249536E74379D1794B117DE3694ED78834C854697404A591899F9BC7417E6  ...\T2A\MP133_T2A.aw
3B79041F1FABD9D077BFD964F849598B455346758E48AFE5663992D762D60DB8  ...\T2A\MP133_T2A_weapon.asi
563170F1AF237A0EC2F14C701B0AB3677BC1C63FB84C9E218A5BF55F527262A0  ...\T2A\MP133_T2A_player.asi
A7DFB94D1CB3B2F2A88AF5C7C92F86D97875C200FF92B29665FD5AC6692C4906  ...\Prefabs\Weapons\MP133_T2A\armst_Shotgun_mp_133_T2A.et
```

**Integrity:** the audit performed reads only; no gameplay file was written.
`GAMEPLAY_FILES_CHANGED_BY_AUDIT=0`. Weapons dirty = 29, Core dirty = 4 (unchanged, owner
work preserved). Report + minimal sync/index pointers are the only published changes (knowledge repo).

## 9. Authorization

Read-only; STOP for owner review. No graph/ASI/clip/prefab/script edits, no game/Workbench,
no T3/A-B/bridge/RPC/per-shell work.
