# MP-133 V3 — G3-B2: one donor round → SAME installed magazine — transaction design (DESIGN ONLY)

**Revision 2 — corrections after independent design review**
[Issue #34 comment 5973710199](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5973710199).

**Status:** `G3B1_PASS / G3B2_DESIGN_CORRECTIONS_REQUIRED / IMPLEMENTATION_NOT_AUTHORIZED`.

**This document is read-only design.** It authorizes nothing at runtime. No executable G3-B2
source, Workbench item, gameplay/animation/R/input integration, MP replication or production
change is included. Implementation starts only after a **separate code-level task** is approved
following independent design review of this revision.

**Authority:** Issue #34 comment
[5973625747](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5973625747)
(G3-B2 design-only task) plus the review corrections in comment
[5973710199](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5973710199).
Reviewed baseline `0a4cc959c350b4b2a2f70ec5416a9d010cbf285d`; baseline task HEAD
`d31df071d97ce5336f6794b6402e69e23a51e83c`.

Labels: **SOURCE** (installed SDK / existing project source), **INFERENCE** (reasoned from SOURCE),
**UNRESOLVED** (not established; never assumed).

---

## 0. Revision-2 change log (how each blocker was resolved)

1. **Muzzle-count commit gate (blocker) — RESOLVED.** The chamber/barrel invariant no longer uses
   `muzzle.GetAmmoCount()`. It now uses `muzzle.IsCurrentBarrelChambered()` + `muzzle.GetCurrentBarrelIndex()`
   (+ stable `GetBarrelsCount()`); `muzzle.GetAmmoCount()`/`GetMaxAmmoCount()` are **supply telemetry**
   only and are **not** required to stay equal. Verified evidence: during a correct T4b
   same-installed-magazine `+1`, `[ARMST_T4B-INSTALLED] phase=post-detail` recorded
   `muzzleSupplyBefore=6 muzzleSupplyAfter=7 muzzleSupplySame=0 ... chamberUnchanged=1`. Applied to
   §§1.2, 4, 5, 6 and the result block.
2. **Inherited live write actions (blocker) — RESOLVED BY ALTERNATIVE INHERITANCE PATH.** Child-local
   suppression of inherited actions is **not proven** (see §1.4): the installed SDK exposes no
   per-action disable/remove setter and the `.et` format shows only `{ }` (declare) and `+{ }` (append)
   — no removal operator was found in the installed SDK or the project corpus. Therefore the B2
   fixture does **not** descend from the G3B1 child / T4b weapon; it is a **fresh thin child of the
   production MP-133** that carries the T4b probe and adds **only** the B2 action, so the B1/T4b
   mutating actions do not exist in the B2 fixture at all (§7).
3. **Donor scope includes other weapons' installed magazines (blocker) — RESOLVED.** Donor discovery
   now rejects any candidate installed in a weapon: (a) the installed-magazine set of **all** weapons
   reachable from the actor's weapon manager, and (b) any item whose storage owner carries a
   `BaseWeaponComponent`. The first B2 run additionally uses a **fail-closed donor-storage whitelist**
   so only a proven carry container is accepted (§1.3).

**Editorial corrections also applied:** state-machine diagram/`REJECTED` lifetime and quarantine
reset clarified (§2); `donor-is-target` vs `no-donor` clarified (§6); "no atomic API" qualified to
absence-in-inspected-scope (§8/§10); mock tests are pure transition logic with **no setters** (§6);
`CURRENT_AI_SYNC.md` top-of-file state rewritten (§ sync commit).

---

## 1. Eligibility / prewrite checks

All checks run **server-side only** (`Replication.IsServer()`) on the **action-owner** B2 lab weapon
and the **acting user**. Any failure here is a **no-write** `REJECTED`.

### 1.1 Actor / weapon context

| # | Check | Source |
|---|---|---|
| 1 | `Replication.IsServer()` true; non-server call `REJECTED` | **SOURCE** `Replication.IsServer` (offline `true` is **not** MP proof — **UNRESOLVED**) |
| 2 | Acting user entity present; `user.FindComponent(SCR_CharacterControllerComponent)` present | **SOURCE** (T4b/G3B1 pattern) |
| 3 | Action owner == current equipped weapon: `CharacterControllerComponent.GetWeaponManagerComponent().GetCurrentWeapon()` returns the `BaseWeaponComponent` whose `GetOwner()` == action-owner entity | **SOURCE** `BaseWeaponManagerComponent.GetCurrentWeapon()` |
| 4 | `BaseWeaponComponent` is on the B2 lab weapon entity (action owner) | **SOURCE** pattern |
| 5 | Baseline ready and the **same installed magazine** present (`wpn.GetCurrentMagazine()` non-null); B2 baseline captured before the first setter | **SOURCE** `BaseWeaponComponent.GetCurrentMagazine()` |

### 1.2 Target (installed magazine) prewrite

| # | Check | Source |
|---|---|---|
| 6 | Target magazine component captured (`targetMag`), owning entity `targetEnt == targetMag.GetOwner()` | **SOURCE** `BaseMagazineComponent.GetOwner()` |
| 7 | `0 <= targetCount <= targetMax-1` (room for exactly +1; full → `REJECTED`) | **SOURCE** `GetAmmoCount`/`GetMaxAmmoCount` |
| 8 | `targetAmmoType = targetMag.GetAmmoType(0)` non-empty | **SOURCE** `GetAmmoType(int idx=0)` |
| 9 | Same installed target across pre→commit: `targetMag` reference, `targetEnt`, owning weapon entity, and `wpn.GetCurrentMagazine()` all re-read and identical | **SOURCE** getters; **INFERENCE** stable across the two synchronous setters in one frame |
| 10 | **Chamber/barrel invariant (not muzzle ammo):** `muzzle.IsCurrentBarrelChambered()` and `muzzle.GetCurrentBarrelIndex()` (and `GetBarrelsCount()` stable). `muzzle.GetAmmoCount()`/`GetMaxAmmoCount()` are captured **separately as supply telemetry** and are **not** an unchanged predicate | **SOURCE** `BaseMuzzleComponent`; T4b evidence `muzzleSupply 6→7`, `chamberUnchanged=1` |
| 11 | Installed target excluded as donor by **component and entity identity** (not prefab GUID) | **SOURCE** (G3-B1 pattern) |

### 1.3 Donor discovery / eligibility

Enumeration (tested in G3-B1, owner-runtime PASS): `GetAllRootItems` **plus**
`GetStorages(EStoragePurpose.PURPOSE_ANY)` and
`SCR_InventoryStorageManagerComponent.GetAllItems(items, storage)` per storage, deduplicated by
reference. Re-verify each gate immediately before the write.

| # | Check | Source |
|---|---|---|
| 12 | Resolve `BaseMagazineComponent.Cast(item.FindComponent(MagazineComponent))` (fallback `BaseMagazineComponent`); `donorMag.GetOwner() == donorItem` | **SOURCE** |
| 13 | Donor genuinely carried: `inv.Contains(donorItem)`; `InventoryItemComponent.GetParentSlot()` resolves; `slot.GetStorage()` recorded | **SOURCE** `Contains`, `GetParentSlot()`, `InventoryStorageSlot.GetStorage()` |
| 13a | **Not installed in ANY weapon (new):** build `installedSet` from the actor's weapon manager — `ctrl.GetWeaponManagerComponent().GetWeapons(out array<BaseWeaponComponent>)`, and for each `w` add `w.GetCurrentMagazine()` and `w.GetCurrentMagazine().GetOwner()`. Reject a candidate whose magazine or entity is in `installedSet`. | **SOURCE** `GetWeapons`, `GetCurrentMagazine`, `GetOwner` |
| 13b | **Not stored inside a weapon (new):** reject if `slot.GetStorage().GetOwner()` carries a `BaseWeaponComponent` (item inside a weapon/attachment storage, e.g. the M16 STANAG that B1 logs enumerated as `member=1, storage=M16/slot0`). | **SOURCE** `GetStorage().GetOwner()`, weapon component lookup |
| 13c | **Fail-closed donor-storage whitelist (first B2 run, new):** accept a donor only if its storage-owner prefab path is in an explicit action attribute whitelist (default **empty** → reject everything). The owner supplies the exact permitted carry-container prefab (e.g. the vest used in the B1 log) and slot. Anything else → `REJECTED no-permitted-storage`. | **INFERENCE** (whitelist is intent-proven, not a guessed API); storage-owner *type* classification is **UNRESOLVED** |
| 14 | Exactly **one** independent compatible donor. `donorMag != targetMag` **and** `donorItem != targetEnt`. `0` compatible → `no-donor`; `>1` → `ambiguous-donor` | **SOURCE** (G3-B1 pattern) |
| 15 | Donor count `1 <= donorCount <= donorMax` (`0` → `zero-ammo`) | **SOURCE** |
| 16 | Strict ammo compatibility: `donorMag.GetAmmoType(0)` non-empty **and** strictly equal to the target reference type. Identical prefab GUID is **not** sufficient | **SOURCE** getter; **INFERENCE** strict equality is the safe first rule; cross-prefab 12ga interchangeability **UNRESOLVED** |
| 17 | Donor slot/membership retained and re-verified between the two writes | **SOURCE** getters; invalidation semantics **UNRESOLVED** |
| 18 | No native `CMD_Weapon_Reload` / `/full` / magazine swap / rack / fire observed in the window | **INFERENCE** (synchronous window); in-game native observation **UNRESOLVED** |
| 19 | No B2 operation already in progress or quarantined (`state == IDLE`) | **SOURCE** lab-controlled |

### 1.4 Child-local action suppression — investigated, UNRESOLVED

**SOURCE (absence observed in inspected scope):** the installed SDK's `BaseActionsManagerComponent`
(`ActionsManagerComponent` derived) exposes only `GetActionsList/FindAction/GetActionsCount/
GetContext/GetContextList/IsEnabled/AddUserActionEventListener/RemoveUserActionEventListener` — **no
per-action enable/disable/remove setter**. `BaseUserAction` has `WasDisabledByServer()` (read-only),
`GetVisibilityRange()`, `SetSendActionDataFlag()` — **no public disable**. The `.et` format uses
`property { }` (declare/override) and `property +{ }` (append); **no element-removal operator was
found** in the installed corpus or the SDK docs. Prefab-level class replacement of an inherited action
instance, or reparenting it to a non-existent `ParentContextList`, is **not proven**.

**Resolution:** do not rely on suppression. Use the alternative inheritance path (§7) that **does not
contain** the mutating actions. If a future task still requires suppression on a G3B1-child path, it
is a **pre-implementation gate** and must be proven in Workbench first.

**Fail-closed rule:** any uncertainty in 1–19 → `REJECTED`, no writes. Once the first setter is called,
the operation can no longer return `REJECTED` (§2).

---

## 2. One-shot transaction state machine

```
                 invoke (server)
    IDLE ───────────────────────────────▶ PREFLIGHT
     ▲                                        │
     │ any prewrite check 1..19 fails         │ all pass
     │ (no writes, latch NOT set,             ▼
     │  REJECTED is repeatable)          (latch + opId set)
     ●  REJECTED (repeatable)                 │
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

- **Latch before first setter.** A per-instance boolean `m_b2Latch` and an increasing `opId` are set
  **immediately before** `donor.SetAmmoCount(...)`. A second invocation during/after the operation
  can never reach either setter.
- **`REJECTED` is repeatable and writes nothing.** Because the latch is set only at the setter
  boundary, a prewrite rejection leaves `m_b2Latch == false`; the owner may fix the condition and
  invoke again. **No `REJECTED→IDLE` "reset" arrow is implied** — the operation simply never left the
  pre-latch phase.
- **One shot once latched.** After the latch is set, the fixture performs **at most one** B2
  operation; `COMMITTED` and `QUARANTINED` are terminal. No second call, no re-issue, no retry.
- **No second call between the two writes.** The two setters execute in one synchronous
  `PerformAction` body with no `CallLater`/await between them (**INFERENCE**: single-threaded script
  within the frame; to be confirmed by construction during implementation).
- **Any failure at/after the first setter → `INDETERMINATE` → `QUARANTINED`.** Never relabelled
  `REJECTED`; never auto-retried; never speculatively rolled back; no "success" claim.
- **Quarantine reset (clarified):** only a **newly spawned instance** of the B2 lab weapon
  (fresh component state) clears the latch/quarantine, and the owner does this by re-spawning the
  fixture. **Re-equipping the same instance is UNRESOLVED** (the same action component/latch may be
  retained) and must **not** be relied on. There is no automatic/quarantine-clearing path in code.
- **Future per-insertion token.** The eventual repeated shell-reload needs a per-insertion-cycle
  token advanced only on a validated cycle. **Documented here, not implemented**; repeated
  animation/input callbacks are prevented by not implementing the callback path at all.

**Result states:** `REJECTED` (no write, repeatable), `COMMITTED` (both writes validated, §4),
`INDETERMINATE`→`QUARANTINED` (partial/uncertain → STOP/log, no repeat).

---

## 3. Order and risk (explicit)

**Proposed order for the first controlled experiment: donor-first.**

1. `d → d-1` on the donor.
2. **Immediate** readback of the **same** donor component/entity/location.
3. Re-check the **same** still-installed target, its pre-count, and the chamber/barrel snapshot.
4. `t → t+1` on the target.
5. **Immediate** target readback.

**Tradeoff (accepted, not hidden):**

- **donor-first:** if the second write fails → one real round **lost** (sums `d+t-1`). Chosen because a
  lost-but-accounted round is preferable to a duplicated round, and the loss is fully observable.
- **target-first:** if the donor write fails → one round **duplicated** (sums `d+t+1`).

**Neither order is safe under arbitrary failures** — there is **no proven atomic one-round transfer
API on the installed SDK for this weapon-attached magazine target** (absence observed in the inspected
`ArmaReforgerScriptAPIPublic` surface; not a claim that none exists anywhere in the engine). A
post-first-write uncertainty must **STOP and quarantine**, never be relabelled `REJECTED` or
auto-compensated. **Rollback is explicitly not guaranteed** and must not be claimed.

---

## 4. Commit criteria

`COMMITTED` requires **all** of the following, using values captured before each write:

| Criterion | Assertion |
|---|---|
| Donor count | `donorAfter == donorBefore - 1` |
| Target count | `targetAfter == targetBefore + 1` |
| Donor identity | same `BaseMagazineComponent` reference and same owning entity, `donorMag.GetOwner()==donorItem` |
| Target identity | same `BaseMagazineComponent` reference **and** same owning entity; `wpn.GetCurrentMagazine()==targetMag` |
| Donor storage | donor still `inv.Contains(donorItem)`; same `InventoryItemComponent.GetParentSlot()`/storage recorded |
| Ammo type | donor and target `GetAmmoType(0)` unchanged |
| **Chamber/barrel** | `muzzle.IsCurrentBarrelChambered()` and `muzzle.GetCurrentBarrelIndex()` **unchanged** (barrels count stable). **`muzzle.GetAmmoCount()` is NOT asserted equal** |
| Conservation | `donorBefore + targetBefore == donorAfter + targetAfter` |
| **Supply telemetry (not a predicate)** | `muzzle.GetAmmoCount()`/`GetMaxAmmoCount()` captured and logged; **may change** when the installed target increases (T4b: 6→7) |

- `COMMITTED` is declared **only** with all immediate checks passing.
- At **+250 ms** and **+1 s** the operation re-reads both magazines **without re-issuing setters**;
  any mismatch → `LATE_INDETERMINATE` → `QUARANTINE`, never a retroactive full proof.
- The **donor is never deleted** at 0; no loose-shell spawn, no UI mutation, no eject.

---

## 5. Telemetry (log only)

Single correlated `opId`; `key=value` lines; bounded. Each record carries:

- `opId`; stage `validate` / `pre` / `donor-post` / `target-post` / `commit` /
  `delayed+250ms` / `delayed+1000ms` / `reject` / `indeterminate` / `quarantine`.
- **Donor actual entity and component identity** (lab tag `I<n>`/`M<n>` for correlation only, plus
  prefab GUID/path), source storage slot + **storage-owner prefab path**, membership.
- **Target actual entity and component identity**; installed target and equipped B2 weapon entity;
  action-owner.
- **Chamber/barrel** (`IsCurrentBarrelChambered`, `GetCurrentBarrelIndex`, `GetBarrelsCount`) and
  **supply** (`muzzle.GetAmmoCount`/`GetMaxAmmoCount`) as **separate fields**.
- Actor; `srv`; baseline donor/target; total before/after; `state` and `reason` (`no-donor`,
  `no-permitted-storage`, `donor-installed-in-weapon`, `zero-ammo`, `incompatible-ammo`,
  `ambiguous-donor`, `target-full`, `wrong-weapon-context`, `not-owned`, `no-slot`, `donor-changed`,
  `target-changed`, `chamber-changed`, `donor-readback-mismatch`, `target-readback-mismatch`,
  `late-persistence-mismatch`, `quarantined`, …).
- Logging only: no donor presentation change, no exhausted-magazine deletion, no fake loose shells,
  no auto-eject, no input injection.

---

## 6. Acceptance / negative matrix

**Positive (one owner offline run):** one unique carried 12ga donor in a **permitted** carry container
(count ∈ [1,max]), target installed and not full, compatible type, chamber snapshot; one invocation →
donor `d→d-1`, target `t→t+1`, identities/storage/chamber unchanged, `d+t` conserved, persistence at
+250 ms/+1 s.

| Case | Trigger class | Expected | How tested |
|---|---|---|---|
| Zero-count donor | negative | `REJECTED zero-ammo` (no write) | owner offline |
| Target full (`== max`) | negative | `REJECTED target-full` | owner offline |
| Incompatible ammo type | negative | `REJECTED incompatible-ammo` | owner offline |
| Two compatible donors | negative | `REJECTED ambiguous-donor` | owner offline |
| **Donor is the installed target** | negative | During enumeration the target is excluded → if it is the only compatible mag the real outcome is **`REJECTED no-donor`** (as B1 does), **not** `donor-is-target`. `donor-is-target` is a defensive **second-stage** reason reachable only via a synthetic/mock identity test | owner offline + mock |
| Donor installed in another weapon | negative | `REJECTED donor-installed-in-weapon` | owner offline (equipped M16 in the actor inventory, as B1 logged) |
| Donor in a non-permitted storage | negative | `REJECTED no-permitted-storage` (whitelist) | owner offline |
| Missing / moved donor / slot | negative | `REJECTED donor-changed`/`not-owned` | owner offline |
| Changed equipped weapon / installed target | negative | `REJECTED wrong-weapon-context`/`target-changed` | owner offline |
| Client-authority call | negative | `REJECTED not-server` | static/log (offline `srv` != MP proof) |
| Duplicate action / callback | negative | `quarantined` (no second write) | owner offline (second invocation) |
| Chamber/barrel changed pre→post | commit | `INDETERMINATE`/`QUARANTINE` | **mock (pure transition logic, no setter)** |
| Donor readback mismatch after first setter | commit | `INDETERMINATE`/`QUARANTINE`, no retry | **mock (pure state-machine test, no setter)** |
| Target readback / identity failure after donor write | commit | `INDETERMINATE`/`QUARANTINE`, no rollback claim | **mock (no setter)** |
| Transient entity loss between setters | commit | `INDETERMINATE`/`QUARANTINE` | **mock (no setter)** |
| Delayed persistence mismatch (+250 ms/+1 s) | commit | `LATE_INDETERMINATE`/`QUARANTINE` | owner offline observation; not forced |
| Interruption / magazine swap mid-window | commit | `REJECTED` (pre) or `INDETERMINATE` (post-first-write) | design; not forced |

Rules:

- **No destructive forced failure in the owner Workbench.** Non-triggerable cases use **mock /
  pure-transition-logic** tests that **must not call any setter** (`SetAmmoCount`, `ClearChamber`,
  etc.); they exercise the state machine with synthetic captured values only.
- **STOP criteria:** any `INDETERMINATE`/`QUARANTINE`, chamber change, identity change, or
  non-conservation → report and quarantine; no retry.
- **Validation classes:** (a) *SDK static tests* — API/AST/compile + mock state-machine; (b) *single
  owner offline test* — positive run + safely triggerable negatives; (c) *future dedicated-server
  test* — MP authority/replication (out of scope here).

---

## 7. Packaging and owner procedure (after **separate** approval)

### 7.1 Fixture (corrected — avoids the mutating actions by construction)

Because inherited-action suppression is **not proven** (§1.4), the B2 fixture is **not** a child of
the G3B1 child. It is a **fresh thin child of the production MP-133** — the same proven pattern T4b
itself uses — carrying the T4b probe (baseline/diagnostics) plus **only** the B2 action:

- `Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et` (+`.meta`) inheriting
  `{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et` (exact parent path as
  referenced by the T4b prefab), containing:
  - `ARMST_T4B_WeaponProbe "<new lab GUID>" { m_iT4BStartAmmo <initial> }` (required T4b probe; class
    from the unchanged T4b script),
  - `ActionsManagerComponent "{A29AE67FF4D82B0F}" { additionalActions +{ ARMST_T4B_G3B2_TransferAction
    "<new lab GUID>" { ParentContextList { "default" } UIInfo UIInfo "<new lab GUID>" { … }
    m_bG3B2WriteEnabled 0 } } }`.
  - optional (not required for B2): the inherited `WeaponAnimationComponent {60B4EA76EB15F6E0}`
    override used by T4b, if the owner wants identical animation diagnostics.
- New lab GUIDs are assigned at implementation time and recorded in the manifest; they must be unique
  and lab-scoped.
- **The T4b `+1` action and the G3B1 action do not exist in this fixture** (production parent has
  neither), so they cannot write during a B2 run. The T4b probe's init baseline
  `SetAmmoCount(m_iT4BStartAmmo)` is the **existing verified pre-experiment setup write**, not a B2
  transaction write; document it explicitly. (If a zero-init-write setup is preferred, the probe can
  be omitted and the installed count set by the owner via gameplay — review decision.)
- **Alternative retained for completeness:** a child of the G3B1 child with proven child-local
  suppression would also satisfy the goal, but suppression is a **pre-implementation gate** (§1.4).

### 7.2 New source (additive)

- `Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c` — a new `ScriptedUserAction` implementing the
  state machine and a B2 state host component. It must **not** modify the G3B1 script or the T4b
  probe/action; the write gate attribute (e.g. `m_bG3B2WriteEnabled`) default **false**.

### 7.3 Owner procedure (later, after approval)

- **Write disabled by default.** First owner run is a **read-only dry-run**: resolve donor/target and
  the chamber/supply snapshot, run preflight, log the verdict, **no setters**. Confirm a Workbench
  preflight shows **B2 transfer uniquely invocable** and no mutating `+1`/G3B1 action present.
- **Independent source review** before any write-enabled run.
- **Owner alone** then compiles and runs: expendable target e.g. `2/10`, donor `10/10` in a
  **whitelisted** carry container, chamber snapshot; then the single isolated offline transfer only if
  explicitly authorized.
- **No** R / `ShellReloadSTM` / TXA/ANM / Core hooks / production change; no Astra.

---

## 8. Source / uncertainty matrix

| Item | Label | Note |
|---|---|---|
| `BaseMagazineComponent` ammo getters + `SetAmmoCount` | **SOURCE** | only ammo writer; no atomic transfer |
| `BaseWeaponComponent` current mag/muzzle/chambering getters | **SOURCE** | installed target + context |
| `BaseMuzzleComponent.GetAmmoCount/GetMaxAmmoCount` | **SOURCE** | **supply telemetry**, may change; not a chamber predicate |
| `BaseMuzzleComponent.IsCurrentBarrelChambered/GetCurrentBarrelIndex/GetBarrelsCount` | **SOURCE** | chamber/barrel invariant |
| `BaseWeaponManagerComponent.GetWeapons/GetWeaponsList/GetCurrentWeapon` | **SOURCE** | build `installedSet` to exclude weapon-installed donors |
| Inventory / storage / slot APIs (`Contains`, `GetStorages`, `GetAllItems`, `GetAllRootItems`, `GetParentSlot`, `GetStorage`, `GetOwner`) | **SOURCE** | nested discovery + provenance |
| `BaseActionsManagerComponent` per-action disable/remove | **SOURCE (absence observed)** | only `FindAction/GetActionsList/IsEnabled/…`; no disable/remove setter |
| `.et` array element removal operator | **SOURCE (absence observed)** | only `{ }` / `+{ }` found; no removal operator in inspected corpus/SDK |
| Child-local suppression / class replacement / context reparent of inherited actions | **UNRESOLVED** | **pre-implementation gate**; avoided via alternative path §7 |
| Donor storage-owner *type* classification ("carry container" vs weapon) via a generic SDK type | **UNRESOLVED** | use explicit fail-closed whitelist (§1.3-13c) |
| `slot.GetStorage().GetOwner()` carries `BaseWeaponComponent` ⇒ donor inside a weapon | **SOURCE** getters, **INFERENCE** meaning | used as the weapon-installed exclusion |
| Donor presentation/authorization/replication after setter | **INFERENCE** (owner PASS for decrement) | authorization/serialization **UNRESOLVED** |
| `SetAmmoCount` MP authority; offline `srv` | **UNRESOLVED** | offline is not MP proof |
| Cross-prefab 12ga `GetAmmoType(0)` equality | **UNRESOLVED** | strict non-empty equality required |
| `ResupplyMagazines*` semantics | **UNRESOLVED** | not used |
| Rollback / compensation guarantee | **UNRESOLVED** | must not be claimed |
| Exact raw G3-B1 classification log in-repo | **UNRESOLVED** | cited from owner-reported evidence only |

---

## 9. Proposed implementation allowlist (future, NOT done now)

**Will be added (new files only):**

- `labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c` (new).
- `labs/ARMSTMP133T4B_InstalledMagProbe/Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et` (+`.meta`, new;
  **child of the production MP-133**, carrying the T4b probe + B2 action).
- `labs/ARMSTMP133T4B_InstalledMagProbe/MANIFEST.sha256` (append new files; existing hashes kept).

**Will be edited (docs only):**

- `reports/MP133_V3_G3B2_TRANSACTION_DESIGN.md` (this document).
- `reports/MP133_V3_T4B_INSTALLED_MAG_PROBE.md` (evidence, when runs exist).
- `reports/MP133_INDEX.md`, `docs/sync/CURRENT_AI_SYNC.md`.

**Explicitly preserved / untouched:** T4b script `D581B9C9…`, T4b prefab `29C70A78…`, G3-B1 script
`A7CE4FE3…`, G3-B1 child `0C03C366…`, donor mag `437D75E3…`, historical `G3B1_DonorDevice`,
`addon.gproj` `200E3156…`; production Weapons/Core, frozen V2/P2, T2a/T4a, Astra/worlds/layers,
`.meta`/GUID identity; untracked owner file `reports/CORE_ARMST_READONLY_AUDIT.md`.

`GAMEPLAY_FILES_CHANGED_BY_DESIGN = 0` (this task writes documentation only).

---

## 10. Gate output

```
G3B2_DESIGN_RESULT:
BRANCH: t4b/installed-mag-probe
BASELINE: 0a4cc959c350b4b2a2f70ec5416a9d010cbf285d (reviewed) ; task HEAD d31df071d97ce5336f6794b6402e69e23a51e83c
SDK: Arma Reforger Tools buildid 24870687; ArmaReforgerScriptAPIPublic html
BLOCKER_1_MUZZLE: RESOLVED - chamber invariant uses IsCurrentBarrelChambered + GetCurrentBarrelIndex (+ GetBarrelsCount); GetAmmoCount = supply telemetry only (T4b evidence muzzleSupply 6->7, chamberUnchanged=1)
BLOCKER_2_INHERITED_ACTIONS: RESOLVED BY ALTERNATIVE PATH - no child-local suppression proven (no per-action disable in BaseActionsManagerComponent; no array-removal operator found); B2 fixture = fresh thin child of production MP-133 with T4b probe + B2 action only; B1/T4b actions absent by construction; suppression remains UNRESOLVED pre-implementation gate
BLOCKER_3_DONOR_SCOPE: RESOLVED - exclude any donor in the actor weapons' installedSet (GetWeapons->GetCurrentMagazine/GetOwner) and any donor whose storage owner has a BaseWeaponComponent; fail-closed donor-storage whitelist (default empty) for first B2 run
STATE_MACHINE: IDLE -> PREFLIGHT -> (REJECTED repeatable no-write | DONOR_WRITTEN -> TARGET_WRITTEN -> COMMITTED) ; at/after first setter uncertainty -> INDETERMINATE -> QUARANTINED ; quarantine cleared only by a newly spawned instance (re-equip UNRESOLVED)
ORDER: donor-first (d->d-1 then t->t+1); tradeoff = possible lost round vs duplication
COMMIT: donor==d-1, target==t+1, same entity+component identities, donor storage/membership/slot retained, target still installed, ammo type unchanged, chamber/barrel unchanged, d+t conserved; +250ms/+1s persistence; mismatch -> LATE_INDETERMINATE/QUARANTINE
IMPLEMENTATION_ALLOWLIST: new labs/.../ARMST_T4B_G3B2_Transfer.c ; new labs/.../Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et(+.meta) inheriting production MP-133 ; labs/.../MANIFEST.sha256 ; docs
GAMEPLAY_FILES_CHANGED_BY_DESIGN: 0
ASTRA: INDEPENDENT (not touched)
STATUS: G3B1_PASS / G3B2_DESIGN_CORRECTIONS_REQUIRED / IMPLEMENTATION_NOT_AUTHORIZED
NEXT_GATE: STOP_FOR_INDEPENDENT_DESIGN_REVIEW (rev 2)
```

---

## 11. Implementation (bounded source preparation; write gate OFF) — 2026-10-04

Authorized by Issue #34 comment `5973770796` after rev-2 design approval (comment `5973766922`).
Additive lab-only source + production-child prefab published; **write OFF by default**; **no**
Workbench/game run performed by the agent.

**New files** (local lab + published copy, local==published):

- `Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c` — new `ScriptedUserAction`
  `ARMST_T4B_G3B2_TransferAction`; SHA256 `4ED71240775F9FEE4DDAB93C876E65FE49209082294BEF216FA6C2867A1F5C17`.
- `Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et` — SHA256 `68F67CAB0C17201882FCB9D587E3F3F196231B46E4FCB3951DD8BDC185873E04`.
- `Prefabs/Test/ARMST_T4B_G3B2_TestWeapon.et.meta` — SHA256 `315C7AB6983B68C63C0AEC1D30625C5CA4B7477D72C1C75DF5291AC7438F9287`.

**Prefab:** thin child of the actual production parent
`{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et`, containing the T4b
probe `ARMST_T4B_WeaponProbe "0A1B2C3D4E5F6071" { m_iT4BStartAmmo 2 }` and exactly **one** new action
`ARMST_T4B_G3B2_TransferAction "1B2C3D4E5F607182"` (UIInfo `2C3D4E5F60718293`) with
`m_bG3B2WriteEnabled 0`.

**Action-inheritance proof (static):** the child references the production MP-133 parent and declares
only the B2 action — `ARMST_T4B_AddRoundWeaponAction = 0`, `ARMST_T4B_G3B1_ConsumeAction = 0`,
`ARMST_T4B_G3B2_TransferAction = 1` in the child. The T4b `+1` and G3B1 actions exist only in the
T4b/G3B1 child prefabs (not in the production parent chain), so they cannot be present or invoked in
the B2 fixture. A Workbench preflight by the owner should still confirm the visible action list.

**Write gate:** `[Attribute("false", UIWidgets.CheckBox, …)] bool m_bG3b2WriteEnabled = false;` in
source **and** `m_bG3B2WriteEnabled 0` in the published child prefab.

**Donor whitelist (fail-closed):** `m_sG3b2AllowedStorageOwner` default `""` and
`m_iG3b2AllowedStorageSlot` default `-1`; an empty owner rejects **every** donor.

**Setup mutation, separate from B2:** the unchanged T4b probe runs one
`SetAmmoCount(m_iT4BStartAmmo)` at init; the child sets `m_iT4BStartAmmo 2` (documented expendable
target count). This is setup, **not** the B2 action, and the fixture is **not** globally zero-write.
`B2_SETTER_CALLS_IN_DRY_RUN = 0`: both B2 `SetAmmoCount` calls sit **after** the dry-run guard
`if (!m_bG3b2WriteEnabled) { … return; }` (guard line 649; setters lines 716 and 758).

**New unique GUIDs** (0 occurrences across the addons tree): meta `{E7F809A1B2C3D4E5}`, instance
`F809A1B2C3D4E5F6`, probe `0A1B2C3D4E5F6071`, action `1B2C3D4E5F607182`, UIInfo `2C3D4E5F60718293`.

**Static checks:** braces 78/78, parens 530/530, ASCII, 885 lines; no
`modded`/`OnAnimationEvent`/`OnCharacterCommand`/`CMD_Weapon_Reload`/`SpawnMagazine`/`AttachMagazine`/
`DetachMagazine`/`ClearChamber`/`TryDeleteItem`/`GetLocalControlledEntity`/`SyncWithCharacter` in code
(only comment mentions). No Python interpreter in PATH (WindowsApps stub) →
`check_repository_integrity.py` **not run / not claimed**.

**Preserved:** T4b script `D581B9C9…`, T4b prefab `29C70A78…`, G3B1 script `A7CE4FE3…`, G3B1 child
`0C03C366…`, donor mag `437D75E3…`, `addon.gproj 200E3156…`, all `.meta`/GUID.
`GAMEPLAY_FILES_CHANGED_BY_DESIGN = 0` outside the two new lab files.

**Suggested first owner read-only preflight** (later, after independent source review — not
authorized yet): spawn/equip `ARMST_T4B_G3B2_TestWeapon.et`; confirm the action name; invoke once with
the write gate OFF; expect `[ARMST_T4B-G3B2]` `phase=classify-start` → `phase=classify-done` →
`phase=readonly` and **no `SetAmmoCount` from the B2 action**.

**STATUS:** `G3B2_DESIGN_APPROVED / G3B2_BOUNDED_SOURCE_PREPARATION_AUTHORIZED / B2_WRITE_ENABLED_RUN_NOT_AUTHORIZED / STOP_FOR_SOURCE_REVIEW`.
