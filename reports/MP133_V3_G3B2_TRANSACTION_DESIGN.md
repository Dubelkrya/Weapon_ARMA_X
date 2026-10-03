# MP-133 V3 — G3-B2: one donor round → SAME installed magazine — transaction design (DESIGN ONLY)

**Status:** `G3B1_RUNTIME_PASS / G3B2_DESIGN_AUTHORIZED / G3B2_IMPLEMENTATION_NOT_YET_AUTHORIZED / ASTRA_INDEPENDENT`.

**This document is read-only design.** It authorizes nothing at runtime. No executable G3-B2
source, Workbench item, gameplay/animation/R/input integration, MP replication or production
change is included. Implementation starts only after a **separate code-level task** is approved
following independent design review of this document.

**Authority:** Issue #34 comment
[5973625747](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5973625747)
(G3-B2 design-only task). Baseline resolves fresh `origin/t4b/installed-mag-probe` at
`d31df071d97ce5336f6794b6402e69e23a51e83c`.

Labels used throughout: **SOURCE** (installed SDK / existing project source), **INFERENCE**
(reasoned from SOURCE, not proven), **UNRESOLVED** (not established; do not assume).

---

## 0. Scope, baseline and non-goals

**In scope (design):** one manual, lab-only, no-R, server-authoritative operation that moves exactly
one round from one genuine carried donor magazine into the **same** already-installed MP-133 lab
magazine, with a one-shot transaction state machine, quarantined partial-failure handling, correlated
telemetry, and an acceptance/negative matrix.

**Out of scope (this document and the next task unless separately approved):**

- Native reload / `CMD_Weapon_Reload` / short-R / `Weapon_Rack_Bolt` / pump / fire (G4).
- Astra animation lab (#35), graph/ASI/ANM edits, input handling.
- Production `ARMST-PLATFORM---Weapons`, Core, frozen V2/P2, original T2a/T4a, worlds/layers.
- MP replication guarantees and dedicated-server testing (future; this first B2 experiment is one
  isolated offline run).
- Replacing the verified G3-B1 action/script or the original T4b fixture.
- Rollback / compensation / auto-retry / speculative re-issue.

**Baseline proven offline (owner runtime, cited as evidence, not re-derived here):**

- T4b single installed-magazine `SetAmmoCount(t+1)` persists on the **same** installed component.
- G3-B1 independent real 12ga donor `SetAmmoCount(d-1)` persisted at +250 ms/+1 s with the same
  actor/inventory/component/slot, installed target excluded; duplicate invocation rejects.
- These were **independent** operations in **different** tests. No atomic two-sided transaction and
  no MP guarantee has been proved. (**SOURCE**: owner evidence
  [5973576236](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5973576236).)

**Owned reference (not to be changed by G3-B2):** owner-saved T4b prefab
`29C70A78B7CBA7678B84A57A29EBF32127A1ED2575742270D9CFACAB78F2AE83`; T4b script
`D581B9C9EE270725FFEC94C7685CBBCB2AB41DBA717F2B4FBCF8C4AC8DDCBEB1`; G3B1 script
`A7CE4FE399A9789CFCDA475D477EC9E1BB4AE942C3DF040AE0F3B04B264620DA`; G3B1 child weapon
`0C03C3662F567E342B0BEAD059151B1299BDE48BC6C37C22D18FB7A010F7733B`; donor mag
`437D75E3545400A31663F78DBD08E7898BEDE69BA758FC76935ABAA8D1FE0761`; `addon.gproj`
`200E3156DED0C793CFA6FCF94767A4DC265FF28760307A158BCD4DF9696608A6`.

**Installed SDK inspected (**SOURCE**):** `Arma Reforger Tools` buildid `24870687`; script API HTML
at `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic\html`
(version string previously recorded as Enfusion `1.8.0.13`; not re-derived here).

---

## 1. Eligibility / prewrite checks

All checks run **server-side only** (`Replication.IsServer()`), on the **action-owner** child lab
weapon and the **acting user**. Any failure here is a **no-write** `REJECTED`.

### 1.1 Actor / weapon context

| # | Check | Source |
|---|---|---|
| 1 | `Replication.IsServer()` true; non-server call `REJECTED` | **SOURCE** `Replication.IsServer` (offline `true` is **not** MP proof — **UNRESOLVED**) |
| 2 | Acting user entity present; `user.FindComponent(SCR_CharacterControllerComponent)` present | **SOURCE** (T4b/G3B1 pattern) |
| 3 | Action owner == current equipped weapon: `CharacterControllerComponent.GetWeaponManagerComponent().GetCurrentWeapon()` returns the `BaseWeaponComponent` whose `GetOwner()` == action-owner entity | **SOURCE** `BaseWeaponManagerComponent.GetCurrentWeapon()`; T4b/G3B1 pattern |
| 4 | `BaseWeaponComponent` is on the child lab weapon entity (action owner) | **SOURCE** pattern |
| 5 | T4b baseline ready and the **same installed magazine** is present (`wpn.GetCurrentMagazine()` non-null) | **SOURCE** `BaseWeaponComponent.GetCurrentMagazine()`; T4b probe `IsBaselineDone()` |

### 1.2 Target (installed magazine) prewrite

| # | Check | Source |
|---|---|---|
| 6 | Target magazine component captured (`targetMag`), its owning entity `targetEnt == targetMag.GetOwner()` | **SOURCE** `BaseMagazineComponent.GetOwner()` |
| 7 | `0 <= targetCount <= targetMax-1` (must have room for exactly +1; full → `REJECTED`) | **SOURCE** `GetAmmoCount`/`GetMaxAmmoCount` |
| 8 | `targetAmmoType = targetMag.GetAmmoType(0)` non-empty | **SOURCE** `GetAmmoType(int idx=0)` |
| 9 | Same installed target across pre→commit: captured `targetMag` reference **and** its `targetEnt` **and** `MP133-WeaponComponent` **and** owning weapon entity are re-read and must be identical | **SOURCE** getters; **INFERENCE** the getters are stable across the two synchronous setters in one frame |
| 10 | Chamber/barrel snapshot captured: `muzzle.GetAmmoCount()`, `muzzle.IsCurrentBarrelChambered()`, `muzzle.GetCurrentBarrelIndex()`, `muzzle.GetBarrelsCount()` | **SOURCE** `BaseMuzzleComponent` |
| 11 | The installed target must be **excluded** as a donor by **component and entity identity**, not by prefab GUID | **SOURCE** (G3-B1 pattern; identity ≠ resource) |

### 1.3 Donor discovery / eligibility

Reuse the **tested** G3-B1 nested enumeration (**SOURCE**, owner-runtime PASS):
`GetAllRootItems` **plus** `GetStorages(EStoragePurpose.PURPOSE_ANY)` and
`SCR_InventoryStorageManagerComponent.GetAllItems(items, storage)` per storage, deduplicated by
reference. Re-verify each gate immediately before the write.

| # | Check | Source |
|---|---|---|
| 12 | Donor magazine resolver: `BaseMagazineComponent.Cast(item.FindComponent(MagazineComponent))` (fallback `BaseMagazineComponent`); `donorMag.GetOwner() == donorItem` | **SOURCE** |
| 13 | Donor is genuinely carried: `SCR_InventoryStorageManagerComponent.Contains(donorItem)`; `InventoryItemComponent.GetParentSlot()` resolves; `slot.GetStorage()` recorded | **SOURCE** `Contains`, `GetParentSlot()`, `InventoryStorageSlot.GetStorage()` |
| 14 | Exactly **one** independent compatible donor. `donorMag != targetMag` **and** `donorItem != targetEnt` (physical identity). `0` compatible → `no-donor`; `>1` → `ambiguous-donor` | **SOURCE** (G3-B1 pattern) |
| 15 | Donor count `1 <= donorCount <= donorMax` (`0` → `zero-ammo`) | **SOURCE** |
| 16 | Strict ammo compatibility: `donorMag.GetAmmoType(0)` non-empty **and** strictly equal to the target reference type. Identical prefab GUID is **not** treated as sufficient | **SOURCE** getter; **INFERENCE** strict equality is the safe first rule; cross-prefab 12ga interchangeability **UNRESOLVED** |
| 17 | Donor slot/membership retained and re-verified between the two writes; donor item not moved/replaced/removed | **SOURCE** getters; invalidation semantics **UNRESOLVED** |
| 18 | No native `CMD_Weapon_Reload` / `/full` / magazine swap / rack / fire was observed in the transaction window | **INFERENCE** (window is synchronous; native command observation is **UNRESOLVED** in-game) |
| 19 | No B2 operation already in progress or quarantined (`state == IDLE`); no other B2 action instance is mid-transaction | **SOURCE** lab-controlled |

**Fail-closed rule:** any uncertainty in 1–19 → `REJECTED`, no writes. Once the first setter is
called, the operation can no longer return `REJECTED` (§2).

---

## 2. One-shot transaction state machine

```
                 invoke (server)
    IDLE ───────────────────────────────▶ PREFLIGHT
     ▲                                        │
     │ any prewrite check 1..19 fails         │ all pass
     │ (no writes)                            ▼
   REJECTED                               (latch set)  ── first setter called ──▶ never REJECTED again
     ●  terminal                                │
                                                │ donor.SetAmmoCount(d-1)
                                                │ + immediate donor readback + target/chamber recheck
                                                ▼
                                          DONOR_WRITTEN
                                                │ target.SetAmmoCount(t+1)
                                                │ + immediate target readback + identity checks
                                                ▼
                                          TARGET_WRITTEN
                                                │ commit criteria §4
                                                ▼
                                           COMMITTED ●  terminal

    any identity mismatch / setter or readback failure / observation uncertainty
    at or after the first setter  ─────────▶  INDETERMINATE ──▶ QUARANTINED ●  terminal
```

**Rules (binding on the future implementation):**

- **Latch before first setter.** A per-action boolean (and an incrementing `opId`) is set/assigned
  **before** `donor.SetAmmoCount(...)`. A second invocation during or after the operation must not
  reach either setter. The latch is **not** released automatically.
- **No second call between the two writes.** The two setters execute in one synchronous
  `PerformAction` body with no `CallLater`/await between them, so no other B2 invocation can
  interleave. (**INFERENCE**: single-threaded script execution within the frame; verified by
  construction during implementation.)
- **`REJECTED` means nothing written.** It is only reachable from `PREFLIGHT`.
- **Any failure at/after the first setter → `INDETERMINATE` → `QUARANTINED`.** Never relabelled
  `REJECTED`; never auto-retried; never speculatively rolled back; no "success" claim.
- **Permanent quarantine.** Once `QUARANTINED`, further B2 invocations log `quarantined` and do
  nothing until the owner resets the lab weapon (re-equip / re-spawn) — no automated recovery.
- **Do not reuse G3-B1's permanent one-shot guard as the final design.** G3-B1's `m_bUsed` is an
  intentional lab one-shot; the eventual *repeated shell reload* needs a **per-insertion-cycle
  token** advanced only when a validated cycle completes. **For this first B2 experiment one shot is
  enough**; the per-insertion token is **documented here, not implemented**, and repeated
  animation/input callbacks are strictly prevented (by not implementing the callback path at all).

**State/output mapping:** `REJECTED` (no write) / `COMMITTED` (both writes validated, §4) /
`INDETERMINATE` then `QUARANTINED` (partial or uncertain → STOP/log, no repeat).

---

## 3. Order and risk (explicit)

**Proposed order for the first controlled experiment: donor-first.**

1. `d → d-1` on the donor.
2. **Immediate** readback of the **same** donor component/entity/location.
3. Re-check the **same** still-installed target, its pre-count, and the chamber snapshot.
4. `t → t+1` on the target.
5. **Immediate** target readback.

**Tradeoff (accepted, not hidden):**

- **donor-first:** if the second write fails, one real round is **lost** (counts sum to
  `d+t-1`). Chosen because a lost-but-accounted round is preferable to a duplicated round, and the
  loss is fully observable in telemetry.
- **target-first:** if the donor write fails, one round is **duplicated** (counts sum to `d+t+1`) and
  the weapon is silently over-supplied.

**Neither order is safe under arbitrary failures** — there is **no proven atomic SDK one-round
transfer API** (**SOURCE**: only `BaseMagazineComponent.SetAmmoCount(int)` exists as a magazine-ammo
writer; no round-level consume/transfer API was found on the installed SDK). A post-first-write
uncertainty must **STOP and quarantine**, never be relabelled `REJECTED` or auto-compensated.
**Rollback is explicitly not guaranteed** and must not be claimed. Any proposal of another order must
be substantiated with installed-SDK/engine evidence and submitted for review.

---

## 4. Commit criteria

`COMMITTED` requires **all** of the following, using values captured before each write:

| Criterion | Assertion |
|---|---|
| Donor count | `donorAfter == donorBefore - 1` |
| Target count | `targetAfter == targetBefore + 1` |
| Donor identity | same `BaseMagazineComponent` reference, same owning entity, `donorMag.GetOwner()==donorItem` |
| Target identity | same `BaseMagazineComponent` reference **and** same owning entity; target still installed on the equipped child (`wpn.GetCurrentMagazine()==targetMag`) |
| Donor storage | donor still `inv.Contains(donorItem)`; same `InventoryItemComponent.GetParentSlot()`/storage recorded |
| Ammo type | donor and target `GetAmmoType(0)` unchanged |
| Chamber/barrel | muzzle `GetAmmoCount()`, `IsCurrentBarrelChambered()`, `GetCurrentBarrelIndex()` unchanged |
| Conservation | `donorBefore + targetBefore == donorAfter + targetAfter` |
| Ammo supply / muzzle | captured **separately** and allowed to change when the installed target increases (do **not** fold into the conservation assertion) |

- `COMMITTED` is declared **only** with all immediate checks passing.
- At **+250 ms** and **+1 s** the operation re-reads both magazines **without re-issuing setters** and
  reports persistence. **Any mismatch is `LATE_INDETERMINATE` → `QUARANTINE`**, never a retroactive
  full proof.
- The **donor is never deleted** when it reaches 0; no loose-shell spawn, no UI mutation, no eject.

---

## 5. Telemetry (log only)

Single correlated `opId` per operation; JSON-like `key=value` lines, bounded. Each record carries:

- `opId`, sequence stage: `validate` / `pre` / `donor-post` / `target-post` / `commit` /
  `delayed+250ms` / `delayed+1000ms` / `reject` / `indeterminate` / `quarantine`.
- **Donor actual entity and component identity**: lab tag `I<n>` for the entity reference and `M<n>`
  for the component reference (tags are correlation aids, **not** identity), plus prefab GUID/path,
  source storage slot + storage owner, membership.
- **Target actual entity and component identity**: same scheme; current installed target and the
  equipped child weapon entity; action-owner.
- Actor entity; `srv`; baseline donor/target/chamber/muzzle values; total before/after.
- `state` and `reason` (`no-donor`, `zero-ammo`, `incompatible-ammo`, `ambiguous-donor`,
  `target-full`, `donor-is-target`, `wrong-weapon-context`, `not-owned`, `no-slot`,
  `donor-changed`, `target-changed`, `chamber-changed`, `donor-readback-mismatch`,
  `target-readback-mismatch`, `late-persistence-mismatch`, `quarantined`, …).
- Logging only: **no** donor presentation change, **no** exhausted-magazine deletion, **no** fake
  loose shells, **no** auto-eject, **no** input injection.

---

## 6. Acceptance / negative matrix

**Positive (one owner offline run):** one unique carried 12ga donor with count ∈ [1,max], target
installed and not full, compatible type, chamber snapshot; one invocation → donor `d→d-1`, target
`t→t+1`, identities/storage/chamber unchanged, `d+t` conserved, persistence at +250 ms/+1 s.

| Case | Trigger class | Expected | How tested |
|---|---|---|---|
| Zero-count donor | negative | `REJECTED zero-ammo` (no write) | owner offline |
| Target full (`== max`) | negative | `REJECTED target-full` | owner offline |
| Incompatible ammo type | negative | `REJECTED incompatible-ammo` | owner offline |
| Two compatible donors | negative | `REJECTED ambiguous-donor` | owner offline |
| Donor is the installed target | negative | `REJECTED donor-is-target` (excluded by identity) | owner offline |
| Missing / moved donor / slot | negative | `REJECTED donor-changed`/`not-owned` | owner offline (donor moved before call where safe) |
| Missing donor magazine | negative | `REJECTED no-donor-magazine` | owner offline |
| Changed equipped weapon / installed target | negative | `REJECTED wrong-weapon-context`/`target-changed` | owner offline |
| Client-authority call | negative | `REJECTED not-server` | static/log (offline `srv` != MP proof) |
| Duplicate action / callback | negative | `already-used` / `quarantined` (no second write) | owner offline (second invocation) |
| Chamber changed pre→post | commit | `INDETERMINATE`/`QUARANTINE` | **mock/read-only** (do not force) |
| Donor readback mismatch after first setter | commit | `INDETERMINATE`/`QUARANTINE`, no retry | **mock/read-only test** (unit-style in lab script, no destructive forced failure) |
| Target readback / identity failure after donor write | commit | `INDETERMINATE`/`QUARANTINE`, no rollback claim | **mock/read-only** |
| Transient entity loss between setters | commit | `INDETERMINATE`/`QUARANTINE` | **mock/read-only** |
| Delayed persistence mismatch (+250 ms/+1 s) | commit | `LATE_INDETERMINATE`/`QUARANTINE` | owner offline observation; not forced |
| Interruption / magazine swap mid-window | commit | fail-closed `REJECTED` (pre) or `INDETERMINATE` (post-first-write) | design; not forced |

Rules for the matrix:

- **Do not destructively force failures in the owner Workbench.** Cases that cannot be triggered
  safely use **mock/read-only** unit-style exercises (e.g. feed the state machine a synthetic
  capture where the readback differs) or are recorded as reasoned design behaviour.
- **STOP criteria:** any `INDETERMINATE`/`QUARANTINE`, any chamber change, any identity change, or
  any non-conservation → the owner reports and the operation is quarantined; no retry.
- **Validation classes:** (a) *SDK static tests* — API/AST/compile and mock state-machine tests;
  (b) *single owner offline test* — the positive run and the safely triggerable negatives;
  (c) *future dedicated server test* — MP authority/replication (out of scope here).

---

## 7. Packaging and owner procedure (after **separate** approval)

- **Fixture:** a new **B2-only child of the currently verified G3B1 child weapon**, i.e.
  `Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et` inheriting
  `{9A8B7C6D5E4F3021}Prefabs/Test/ARMST_T4B_G3B1_TestWeapon.et`, adding **only** a new B2 action to
  the inherited `ActionsManagerComponent {A29AE67FF4D82B0F}`. It must **not** replace or edit the
  G3B1 action instance, the G3B1 child, or the original T4b fixture.
- **New source script (additive):** `Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c`, a new
  `ScriptedUserAction` class; it must **not** modify or subclass-override the G3B1 script or T4b
  probe beyond adding its own logic. New lab GUIDs (meta + instance + action + UIInfo) are assigned
  at implementation time and recorded in the manifest; they must be unique and lab-scoped.
- **Write disabled by default:** the B2 action carries an explicit gate attribute (e.g.
  `m_bG3B2WriteEnabled`, default `false`). The first owner run is a **read-only dry-run** that
  resolves the donor/target/chamber snapshot and logs the preflight verdict with **no setters**.
- **Independent source review** is required before any write-enabled run.
- **Owner alone** later compiles and runs: expendable target e.g. `2/10`, donor `10/10` in a known
  vest slot, chamber snapshot recorded; read-only dry-run first, then the single isolated offline
  transfer only if explicitly authorized.
- **No** R / `ShellReloadSTM` / TXA/ANM / Core hooks / production change; no Astra.

---

## 8. Source / uncertainty matrix

| Item | Label | Note |
|---|---|---|
| `BaseMagazineComponent.GetAmmoCount/GetAmmoType/GetMaxAmmoCount/GetMagazineWell/GetOwner/IsUsed/SetAmmoCount` | **SOURCE** | installed SDK; only ammo writer is `SetAmmoCount` |
| `BaseWeaponComponent.GetCurrentMagazine/GetCurrentMuzzle/GetMuzzlesList/GetOwner/IsChamberingNecessary/IsChamberingPossible` | **SOURCE** | installed SDK |
| `BaseMuzzleComponent.GetAmmoCount/GetMaxAmmoCount/GetBarrelsCount/GetCurrentBarrelIndex/GetMagazine/GetMagazineWell/IsCurrentBarrelChambered/IsBarrelChambered` | **SOURCE** | chamber/barrel snapshot; `ClearChamber` exists but is a writer and is **not** used |
| `BaseWeaponManagerComponent.GetCurrentWeapon/GetCurrent/GetCurrentSlot/GetWeapons/GetWeaponsList` | **SOURCE** | equipped-weapon context |
| `SCR_InventoryStorageManagerComponent.GetAllRootItems/GetAllItems/Contains/GetStorages/GetCharacterStorage` | **SOURCE** | nested discovery (G3-B1 pattern) |
| `InventoryStorageManagerComponent.GetItems/GetStorages/FindItemsWithComponents` | **SOURCE** | enumeration |
| `BaseInventoryStorageComponent.GetAll/GetOwnedItems/Contains/FindItemSlot` | **SOURCE** | storage contents |
| `InventoryItemComponent.GetParentSlot` → `InventoryStorageSlot.GetStorage/GetID/IsLocked` | **SOURCE** | ownership/slot provenance |
| `SCR_InventoryStorageManagerComponent.ResupplyMagazines/GetValidResupplyItemsAndCount/CanResupplyItem/CanResupplyMuzzle/IsResupplyMagazinesAvailable/EndResupplyMagazines` | **SOURCE** API, **UNRESOLVED** semantics | may create/replace magazines (arsenal-style); **not** usable until proven to preserve target identity and deduct exactly one real source round |
| No atomic one-round transfer / round-consume API | **SOURCE** (absence) | matches T4/G3-A audits |
| Donor presentation / inventory-count update after setter | **INFERENCE** (owner-runtime PASS for decrement) | authorization/serialization **UNRESOLVED** |
| `SetAmmoCount` authorization/replication; `Replication.IsServer()==true` offline == MP authority | **UNRESOLVED** | offline `srv` is not MP proof |
| Exact invalidation semantics when a donor/target entity is moved/replaced mid-window | **UNRESOLVED** | mitigated by re-check + quarantine |
| Cross-prefab 12ga `GetAmmoType(0)` equality | **UNRESOLVED** | first transfer requires strict non-empty equality |
| Nested-container donor coverage | **SOURCE** API; **owner-runtime PASS** (G3-B1) | raw classification log not stored in-repo |
| Rollback / compensation guarantee | **UNRESOLVED** | must not be claimed |
| MP authority / dedicated-server behaviour | **UNRESOLVED** | out of scope this task |

---

## 9. Proposed implementation allowlist (future, NOT done now)

**Will be added (new files only; no edits to verified fixtures):**

- `labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c` (new).
- `labs/ARMSTMP133T4B_InstalledMagProbe/Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et` (+`.meta`, new;
  child of the G3B1 child).
- `labs/ARMSTMP133T4B_InstalledMagProbe/MANIFEST.sha256` (append new files; existing hashes kept).

**Will be edited (docs only):**

- `reports/MP133_V3_G3B2_TRANSACTION_DESIGN.md` (this document).
- `reports/MP133_V3_T4B_INSTALLED_MAG_PROBE.md` (evidence section, when runs exist).
- `docs/sync/CURRENT_AI_SYNC.md`.

**Explicitly preserved / untouched:**

- T4b script `D581B9C9…`, T4b prefab `29C70A78…`, G3-B1 script `A7CE4FE3…`, G3-B1 child
  `0C03C366…`, donor mag `437D75E3…`, historical `G3B1_DonorDevice`, `addon.gproj` `200E3156…`.
- Production `ARMST-PLATFORM---Weapons`, Core, frozen V2/P2, original T2a/T4a, Astra/worlds/layers,
  `.meta`/GUID identity.
- Untracked owner file `reports/CORE_ARMST_READONLY_AUDIT.md`.

`GAMEPLAY_FILES_CHANGED_BY_DESIGN = 0` (this task writes documentation only).

---

## 10. Gate output

```
G3B2_DESIGN_RESULT:
BRANCH: t4b/installed-mag-probe
BRANCH_HEAD_AT_TASK: d31df071d97ce5336f6794b6402e69e23a51e83c
SDK: Arma Reforger Tools buildid 24870687; ArmaReforgerScriptAPIPublic html (version label 1.8.0.13 per prior record)
VERIFIED_APIS: BaseMagazineComponent{GetAmmoCount,GetAmmoType,GetMaxAmmoCount,GetMagazineWell,GetOwner,IsUsed,SetAmmoCount}; BaseWeaponComponent{GetCurrentMagazine,GetCurrentMuzzle,GetMuzzlesList,GetOwner,IsChamberingNecessary,IsChamberingPossible}; BaseMuzzleComponent{GetAmmoCount,GetMaxAmmoCount,GetBarrelsCount,GetCurrentBarrelIndex,GetMagazine,GetMagazineWell,IsCurrentBarrelChambered,IsBarrelChambered}; BaseWeaponManagerComponent{GetCurrentWeapon,GetCurrent,GetCurrentSlot,GetWeapons,GetWeaponsList}; SCR_InventoryStorageManagerComponent{GetAllRootItems,GetAllItems,Contains,GetStorages,GetCharacterStorage,ResupplyMagazines*,GetValidResupplyItemsAndCount*,CanResupplyItem*,CanResupplyMuzzle*,IsResupplyMagazinesAvailable*,EndResupplyMagazines*}; InventoryStorageManagerComponent{GetItems,GetStorages,FindItemsWithComponents}; BaseInventoryStorageComponent{GetAll,GetOwnedItems,Contains,FindItemSlot}; InventoryItemComponent.GetParentSlot; InventoryStorageSlot{GetStorage,GetID,IsLocked}
STATE_MACHINE: IDLE -> PREFLIGHT -> (REJECTED | DONOR_WRITTEN -> TARGET_WRITTEN -> COMMITTED) ; any uncertainty at/after first setter -> INDETERMINATE -> QUARANTINED
ORDER: donor-first (d -> d-1, then t -> t+1); tradeoff = possible lost round if 2nd write fails (vs duplication if target-first)
COMMIT: donor==d-1, target==t+1, same entity+component identities, donor storage/membership/slot retained, target still installed, ammo type unchanged, chamber/barrel unchanged, d+t conserved; +250ms/+1s persistence; mismatch -> LATE_INDETERMINATE/QUARANTINE
IMPLEMENTATION_ALLOWLIST: new labs/.../ARMST_T4B_G3B2_Transfer.c ; new labs/.../Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et(+.meta) ; labs/.../MANIFEST.sha256 ; docs (this report, T4B report, sync)
GAMEPLAY_FILES_CHANGED_BY_DESIGN: 0
ASTRA: INDEPENDENT (not touched)
STATUS: G3B1_RUNTIME_PASS / G3B2_DESIGN_AUTHORIZED / G3B2_IMPLEMENTATION_NOT_YET_AUTHORIZED
NEXT_GATE: STOP_FOR_INDEPENDENT_DESIGN_REVIEW
```

`*` = API confirmed to exist, semantics **UNRESOLVED** and not used by the proposed implementation.
