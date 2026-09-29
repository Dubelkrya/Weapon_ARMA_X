# FULL ARMST MOD COMPLIANCE AUDIT V2

**Mode:** PLAN / READ-ONLY — no live files modified
**Date:** 2026-09-20
**LIVE_FILES_CHANGED:** NONE

---

## 1. Executive summary

| Metric | Value |
|---|---|
| Resources audited | 1,197 live resource files (2,024 files total incl. 827 `.meta`) |
| Prefabs audited | 141 (all parsed, 0 parse errors; 1 stray non-Prefabs `.et`) |
| GUID collisions | 0 |
| Broken parent chains | 0 |
| Dangling GUID refs | 0 |
| Duplicate effective render components | 0 |
| CRITICAL / HIGH findings | 0 / 0 |
| Overall status | **PASS_WITH_KNOWN_DEBT** |

The addon is structurally sound under the current rules. All inheritance chains resolve
(local via current-or-registered path, external via vanilla); all GUID references resolve;
no duplicate effective render role exists anywhere (the historical AKDovetailMount
double-MeshObject failure is fixed in the current live state — one mesh is explicitly
disabled). The outstanding items are identity-hygiene debt from earlier folder
re-organizations (stale `.meta` Name paths and stale ref paths, both GUID-resolvable),
one malformed-but-resolvable parent path (SOC94), one missing `.meta` (G36 factory
carry handle), plus the documented intentional exceptions/frozen states.

---

## 2. Authoritative resource inventory

Live addon: `…\addons\ARMST-PLATFORM---Weapons`
(external backups under `agent\`, `.git`, and `Weapon_ARMA_X` excluded; `Weapon_ARMA_X` is not present on this machine).

| Category | Count |
|---|---|
| TOTAL_RESOURCES | 1,197 |
| PREFABS (.et) | 142 (141 under `Prefabs\`, 1 stray `Assets\Toz\1.et`) |
| SCRIPTS (.c) | 10 |
| MODELS (.xob) | 69 (+ 68 source `.fbx`, 69 `.txo`) |
| MATERIALS (.emat) | 98 |
| TEXTURES (.edds) | 157 (+ 185 `.txa`, `.dds` etc.) |
| ANIMATIONS (.anm) | 181 (+ 41 `.asi`, 20 each `.agf/.agr/.ast/.aw`) |
| PARTICLES (.ptc) | 3 |
| CONFIGS (.conf) | 22 |
| SOUNDS | 10 `.acp` + 20 `.wav` |

---

## 3. GUID / meta integrity

- **GUID_COLLISIONS:** 0 (827 metas, no duplicate resource GUID)
- **Path collisions (same path, different GUID):** 0
- **MISSING_META (exported resources):** 1 — `Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Optic.et`
  → **REVIEW_REQUIRED / INFO** (do not auto-create; this is the known G36 factory-handle
  discrepancy — still present in live state). 10 script `.c` files carry no `.meta` by
  design; `Assets\addons\stocks\Data\stock_BC.dds` is a raw source texture.
- **ORPHAN_META:** 1 — `Prefabs/Weapons/Rifles.meta` (folder meta for removed
  `Prefabs/Weapons/Rifles` folder; **0 live refs**)
- **STALE_PATH_REFS:** 183 (ref uses an old path but the GUID matches a registered local
  resource → resolves by GUID at runtime) — MEDIUM identity debt
- **STALE_META_NAME_PATHS:** 490 of 827 metas (~59%) — `.meta` `Name` lines still point at
  pre-reorganization paths (NATO/RUS asset folders, magazine folders, rifle folders).
  Internally coherent (children refs use the same registered paths); resolvable by GUID.
- **DANGLING_GUID_REFS:** 0 — 1,123 external refs all resolve to vanilla/game resources
  (a sample was verified against the game's `resourceDatabase.rdb`).
- Intentionally deleted resources confirmed absent: `Magazine_762x39_AKM_30rnd_Tracer.et`
  (never recreated, 0 refs), PSO duplicates `armst_Optic_PSO1_ak.et` /
  `armst_Optic_PSO1_DovetailRU.et` (0 files, 0 refs).

---

## 4. Inheritance graph

- **141/141 prefabs parsed** (0 parse errors, chains not flattened)
- **BROKEN_PARENT:** 0 — every parent either resolves locally (current or old-but-registered
  path with matching GUID) or is a vanilla external base
- **SELF_CYCLE / INHERITANCE_CYCLE:** 0
- **STALE_PARENT_PATH (malformed):** 1 —
  `armst_Rifle_SOC94_base.et` parent = `{140E94F473B60FE3}Rifles/AKM/armst_Rifle_AKM_base.et`
  (missing `Prefabs/Weapons/` prefix; GUID 140E94F473B60FE3 = local AKM_base → resolves by
  GUID). **MEDIUM / REVIEW_REQUIRED** (not auto-fixed).
- Local chains remain as-is per working-chain policy.

## 5. Effective component map (mandatory)

Full effective maps exist for all 141 prefabs (`effective_component_audit.json`) with per
component: CLASS, GID, ORIGIN (`INHERITED` / `LOCAL_OVERRIDE` / `LOCAL_ADDITION`), at-path.
Only locally-known ancestors are walkable (external vanilla chain ends at the local root);
no materialization was performed.

## 6. Duplicate effective role audit

Attention classes (MeshObject, InventoryItemComponent, WeaponAttachmentAttributes,
SCR_WeaponAttachmentsStorageComponent, ActionsManagerComponent, SightsComponent,
SCR_2DPIPSightsComponent, WeaponComponent, MuzzleComponent, MagazineWellComponent,
AttachmentSlotComponent, MagazineComponent, SlotManagerComponent, RigidBody):

- **Only real duplicate:** `armst_Optic_AKDovetailMount.et` → 2 effective MeshObject
  (see §7). One is `Enabled 0` and carries no `Object` → **inert**. No duplicate *render*
  role exists anywhere.
- 16 weapons have 2–4 effective `AttachmentSlotComponent` — **INTENTIONAL_MULTI_COMPONENT**
  (multiple physical slots).
- No other class appears >1× in any effective map (single WeaponComponent, single
  SightsComponent, single MagazineWell, single MuzzleComponent, etc.).
- No `VALID_OVERRIDE`, `SUSPICIOUS_DUPLICATE_ROLE`, or `PROVEN_INVALID_DUPLICATE_ROLE`
  found this pass.

## 7. MeshObject hard rule

`armst_Optic_AKDovetailMount.et` (GUID `D71FD2BD68AC4B31`):
- LOCAL_MESHOBJECT_COUNT = **2**
- EFFECTIVE_MESHOBJECT_COUNT = **2** (parent `WeaponPart_Base` is a vanilla part base; no
  additional local mesh source)
- ENABLED (render) count = **1**
- Model binding: `{18C9F66F09FF1531}Assets/addons/Dovetail/AKDovetailMount.xob`
- Second mesh `557E85EE39CED921`: `Enabled 0`, no Object → inert placeholder
- **Classification: CURRENTLY_VALID** (no competing render role; the historical
  double-mesh invisibility failure is not present in the current live state; one inert
  disabled entry remains as LOW debt, left untouched)

## 8. Minimal child / override policy

- `armst_Optic_1P29.et` is a **MINIMAL_CHILD**: ID-only descriptor over the vanilla
  `Optic_1P29_base` (0 local components, 0 materialization). Per instruction, no inherited
  components were materialized for audit consistency.
- All other local overrides remain **FROZEN**. No override-rule violations found.
- Authorized historical exception verified intact: Single PSO migration
  (AEK971 `55349E9229B55E29`, SOC94 `65AE4CB5E23C0F63` → `AttachmentOpticsDovetailAK`).

## 9. Weapon base architecture

- 28 main playable bases (25 named in rules + SOC94 + Handgun_Knife + Shotgun base), all
  named `armst_*_base`, **BASE_NAMING_OK**, no `technical_base → duplicate weapon` pattern.
- **VPO136** is an AKM variant (child of `armst_Rifle_AKM_base`, no own base) ✓
- **SOC94** has its own base ✓
- 20 non-base playable variants (AK74 family, AKM family, shotguns, M16A2 carbine).

## 10. Targeted rule verifications

| Rule | Result |
|---|---|
| 14 — Single PSO | PASS — count = 1, GUID `C850A33226B8F9C1`, type `AttachmentOpticsDovetailAK`, dup refs = 0 |
| 15 — 1P29 | PASS_RUNTIME_VERIFIED (user runtime WORKING); minimal-child structure kept |
| 16 — AKDovetail | CURRENTLY_VALID (see §7); RIS slot `BB6000C24BAA468F` = `AttachmentOpticsRIS1913`, PivotID `snap_ris`, ChildPivotID `snap_weapon`; outer type `AttachmentOpticsDovetailAK` |
| 19 — Groza freeze | PASS_WITH_KNOWN_DEBT — direct RIS = 0, external ironsight slots = 0, stale named contexts = 0 (4 contexts: 3 unnamed frozen + magazine `slot_magazine`), muzzle architecture kept, `Muzzle_AK74.ptc` intentional, `Casing_762x39_PS.ptc` = known debt |
| 20 — underbarrel placeholder `51F6738D2EC74BE1` | Absent in 9A91, AEK971, VAL, VSS, VSK94 ✓ |
| 21 — AEK971 placeholder `4E2B66CBA589F625` | Absent in AEK971 ✓ |
| 22 — AKM legacy dovetail `65AE4CB5E23C0F65` | KEEP_LEGACY_OVERRIDE_DEPENDENCY (present, untouched) |
| 23 — AKM stock `65AE4CB5E23C0F63` / `AttachmentStockVz58` | KEEP (present, working interface) |
| 24 — G36 | Weapon slot `AttachmentOpticsG36`; no direct RIS on weapon; Picatinny carry handle = outer G36 + child RIS1913; `p_ak74_ik.anm` workaround kept; carry-handle meta discrepancy = INFO/REVIEW |
| 25 — SIG550/VZ58 | INTENTIONAL workaround — KEEP |
| 26 — L1A1/SLR AK74 IK | UNRESOLVED / KEEP |
| 27 — SR2 | Own mag `armst_Magazine_9x18_SR2_30rnd_Ball.et` GUID `2610CA8D8632DEF4`, capacity 30, `MagazineWellPP91` shared-compat — KEEP |
| 28 — Groza 9x39 mags | SP5 `77215B3A185D1EFD`, SP6 `168348351F5C3F54`, both `MagazineWell9x39`, capacity 20, default SP5; 7.62x39 magazine refs = 0 (only the casing particle path contains "762x39") |
| 29 — Ammo family | PP/BP resolved in configs for 9x18, 5.56×45, 7.62×39, 7.62×51, 9×19; no structural/reference errors (no rebalancing performed) |

## 11. Severity ledger

- **CRITICAL:** none
- **HIGH:** none
- **MEDIUM:** SOC94 malformed parent path; systemic stale identity paths (490 meta + 183 refs — review/Workbench re-save scope)
- **LOW:** orphan `Rifles.meta`; G36 carry-handle `.meta` missing; AKDovetail inert disabled MeshObject entry; `BayonetSlot` instance `5F189C826D592450` carries `AttachmentOpticsDovetailAK` on 9A91/VAL/VSS/VSK94 (naming debt only — slot name vs type mismatch, functionally converged as intended)
- **INFO:** all intentional exceptions / frozen workarounds (list in `known_exceptions.json`)

## 12. Safe cleanup queue

`safe_cleanup_queue.json` — 1 item (LOW):
- `Prefabs/Weapons/Rifles.meta` (orphan folder meta, 0 live GUID refs, folder no longer
  exists). Deleting it changes nothing at runtime.
Everything else is either REVIEW-only (missing meta creation, stale-path normalization,
meta re-save, AKDovetail disabled mesh), frozen, or covered by exceptions.

## 13. Runtime regression matrix

`runtime_regression_matrix.json` — 8 entries. Statically-closable items are closed; the
following require runtime confirmation (1P29 is the only runtime-verified item):
- AKDovetailMount visibility + RIS attach
- Canonical PSO defaults on AKM_full / AK74M_full
- Groza 9×39 firing practice (casing particle debt visible)
- SOC94 spawn (GUID-resolved parent)
- SR-2 + 30rnd mag feed
- G36 factory carry handle
- Broad weapon coverage (20 variants + 27 bases): spawn/ADS/fire/reload

## 14. Resource-build readiness

- **RESOURCE_VALIDATION_READY = YES** (all refs resolve; no broken parents; no GUID
  collisions; the only validation-blocking-class issues are absent).
- **OPTIONAL_NEXT_STEP (read-only):** open the project in Bohemia Interactive Workbench
  (Arma Reforger Tools) and run the built-in resource-verification/reimport preview, which
  reports stale-path mismatches without requiring source edits. No destructive
  conversion/reimport command was executed (and none is recommendable without explicit
  approval, since a full resource re-save would rewrite every `.meta` Name line — a
  mutation).

---

## FINAL REPORT

- **MODEL_ACTUALLY_USED:** `deepseek-v4-flash` (opencode-go)
- **LIVE_ADDON:** `…\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`
- **RESOURCES_AUDITED:** 1,197
- **PREFABS_AUDITED:** 141
- **MAIN_WEAPONS_FOUND:** 28 bases + 20 non-base playable variants
- **GUID_COLLISIONS:** 0
- **MISSING_META:** 1 (G36 factory carry handle; scripts/raw texture by-design)
- **DANGLING_REFS:** 0
- **BROKEN_PARENT_CHAINS:** 0 (1 malformed-but-resolvable parent path on SOC94)
- **EFFECTIVE_COMPONENT_ISSUES:** 0 duplicate render roles
- **DUPLICATE_EFFECTIVE_MESHOBJECTS:** 1 declaration-dup, render = 1 (CURRENTLY_VALID)
- **REDUNDANT_MATERIALIZATION:** 0
- **STALE_ATTACHMENT_SLOTS:** 0 structural; 1 naming debt (BayonetSlot name)
- **STALE_ACTION_CONTEXTS:** 0
- **OVERRIDE_RULE_VIOLATIONS:** 0
- **KNOWN_DEBTS:** stale meta/ref paths (490 + 183); Groza casing; SOC94 parent path; G36 meta
- **INTENTIONAL_EXCEPTIONS:** 12ga OOS, tracer retired, Groza muzzle/casing, G36 IK,
  SIG550/VZ58, SR2 PP91 well, L1A1/SLR IK, frozen overrides + PSO migration
- **AKDOVETAILMOUNT_CURRENT_STATE:** CURRENTLY_VALID
- **PSO_CURRENT_STATE:** PASS (single, correct)
- **1P29_CURRENT_STATE:** PASS_RUNTIME_VERIFIED (minimal child)
- **GROZA_CURRENT_STATE:** PASS_WITH_KNOWN_DEBT
- **AKM_CURRENT_STATE:** PASS (legacy interface kept)
- **AEK971_CURRENT_STATE:** PASS (placeholders absent; slot authorized)
- **G36_CURRENT_STATE:** PASS (structure per spec; carry-handle meta = REVIEW/INFO)
- **AMMO_MAGAZINE_STATE:** PASS (PP/BP + Groza 9×39 + SR2 confirmed)
- **SAFE_CLEANUP_QUEUE_COUNT:** 1
- **RUNTIME_TEST_QUEUE_COUNT:** 8
- **CRITICAL:** 0 — **HIGH:** 0 — **MEDIUM:** 2 classes — **LOW:** 4 — **INFO:** per exceptions
- **OVERALL_STATUS:** **PASS_WITH_KNOWN_DEBT**
- **LIVE_FILES_CHANGED:** NONE