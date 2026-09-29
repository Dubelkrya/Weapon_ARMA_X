# FINAL REPORT — FULL OPTICS / SIGHTS / RAILS SYSTEM AUDIT (READ ONLY)

Date: 2026-09-21
Scope: ARMST-PLATFORM---Weapons optics/sights/rails/adapters/attachment-contracts architecture.
Mode: PLAN / READ ONLY. No gameplay resource modified.

## 0. Method

- Every prefab under Prefabs/ was parsed (142 prefabs) and its full parent chain resolved.
- Effective component maps were merged by instance identity, distinguishing LOCAL_ADDITION / LOCAL_OVERRIDE / INHERITED (vanilla knowledge base injected for the proven part/collimator/sight/attachment bases read from pristine vanilla sources; external-vanilla content is noted as EXTERNAL/UNKNOWN).
- Inherited+override of the SAME GID counted as ONE effective object.
- Static results are never claimed as runtime results.

## 1. Inventory (computed from effective maps)

- Prefabs scanned: 142
- Host slots (effective AttachmentSlotComponent across weapons + hosts): 56
- Attach modules (effective WeaponAttachmentAttributes carrying a type): 5 in the optics/rail scope:
  - AKDovetailMount -> AttachmentOpticsDovetailAK
  - armst_Optic_Collimator -> AttachmentOpticsRIS1913
  - armst_Optic_PSO1 -> AttachmentOpticsDovetailAK
  - HKG36 CarryHandle_Optic -> AttachmentOpticsG36
  - HKG36 CarryHandle_Picatinny -> AttachmentOpticsG36
- Adapters (host slot + own WAA): AKDovetailMount, HKG36 CarryHandle_Picatinny (+ G36 Handle-Optic is module-only)
- Collimators: armst_Optic_Collimator (thin child of WeaponCollimator_Base)
- Magnified/PIP: none authored in live addon (PSO inherits vanilla PIP chain — intentional, out of this subsystem's remediation)
- Iron-sight systems: effective SightsComponent on weapon bases (21 weapon-related prefabs carry an iron/sight stack)

## 2. Inherited identity edges (engine scan, corrected interpretation)

- GUID_EXACT: 29 (local parents by exact identity)
- GUID_EXACT_EXTERNAL: 11 (vanilla resources resolved by GUID)
- VANILLA_KB: 4 (known bases injected)
- PATH_FALLBACK_ONLY / GUID_RESOLVES_STALE_PATH: 14 total
- "DANGLING" (82 in raw engine output) = NOT registered in ARMST metas; the overwhelming majority are vanilla-external parents (expected). The genuine in-addon identity anomalies are limited to the documented set below.

## 3. Effective component / cardinality audit

- All optics/rail/adapter modules show exactly ONE effective instance per role: InventoryItemComponent, MeshObject, RigidBody, ActionsManagerComponent, and exactly one AttachmentSlotComponent per host slot role. No TRUE singleton duplicates found.
- Override-layer-only cases (inherited GID + local override of the same GID) correctly treated as one effective object.

## 4. Compatibility (two-sided, by class)

- Criterion: module WAA AttachmentType == host slot AttachmentType (EXACT_MATCH); inheritance PROVEN not available offline (type classes in paks) -> UNRESOLVED, none claimed.
- Proven edges: DovetailAK (modules AKDovetail, PSO) <-> AK-family dovetail slots; RIS1913 (collimator module) <-> adapter child slot; G36 (carry-handle modules) <-> G36 host slot.
- No PROVEN incompatible pair among the optics/rail family when using class identity.

## 5. Multi-hop chains

1. AK DovetailAK slot -> AKDovetail outer (AttachmentOpticsDovetailAK) -> AKDovetail child RIS slot (AttachmentOpticsRIS1913, snap_ris / snap_weapon) -> armst_Optic_Collimator (AttachmentOpticsRIS1913). Each edge class-matches; runtime mount reported FAILING (see 9).
2. G36 slot -> CarryHandle_Picatinny (G36) -> child RIS slot (RIS1913) -> RIS optics.

## 6. Pivot contracts

- Slot pivot strings are serialized; model-side verification limited (read-only): AKDovetailMount model exposes snap_ris/snap_weapon (EXACT tokens); coll.xob currently exposes only `snap_weapon.001` (Blender suffix) - geometry contract flagged UNVERIFIED (model frozen).
- General host/child pivot names (snap_ris, snap_weapon, slot_optics, snap_muzzle...) are used consistently across the family.

## 7. Sight stack consistency

- COLLIMATOR chain (WeaponCollimator_Base -> armst_Optic_Collimator): SCR_CollimatorSightsComponent + SCR_CollimatorControllerComponent inherited (1+1), no PIP. CLEAN.
- No PIP/collimator conflicts; no duplicate stacks. CLEAN across the audited set.

## 8. Inventory / physical / interaction profiles (evidence)

- Modules carrying an explicit physical profile: PSO (inherited 0.58), Collimator (inherited 0.6 via WeaponCollimator_Base), AKDovetail (local 0.5).
- Modules with NO effective ItemPhysicalAttributes in the part family: HKG36 CarryHandle (handle + picatinny). Correlation: "Heavy" observed on part-family items lacking a physical profile (HKG36 handle; AKDovetail pre-fix). HEAVY_PREDICATE = UNRESOLVED (vanilla script in paks). Not upgraded to proof.
- Interaction profiles: AKDovetail local AM enabled (pickup/attach/attach-detach set per live serialization); collimator inherits the collimator AM (attach/detach); part-family handles inherit the DISABLED part-base AM (Equip only) even though world "Heavy"/interaction appears via the generic inventory pickup path. No duplicate managers.

## 9. AKDovetail + collimator forensics

- Static chain is class-consistent (DovetailAK -> RIS1913 -> RIS1913).
- Runtime: collimator does NOT mount on the AKDovetail RIS slot. Prefab-side differences found:
  - child mount geometry: collimator model lacks an exact `snap_weapon` pivot (only `snap_weapon.001`) - STRONG_CORRELATION (model frozen, not editable here).
  - slot PivotID/ChildPivotID (snap_ris / snap_weapon) vs model token - UNVERIFIED.
  - no other prefab-side incompatibility found (class/PIP/inventory all consistent).
- Ranked causes: (1) STRONG_CORRELATION - mount pivot exactness/geometry on the child model; (2) WEAK_CORRELATION - action/context availability on the adapter after multiple reworks.

## 10. HKG36 carry-handle sub-audit

- Parent GUID `C3DAB8D1B6068170` = DANGLING identity (not registered); path-fallback to the real WeaponPart_Base (0A9CD090EE3440E7). IDENTITY_DEBT / STRUCTURAL_BUG (non-blocking).
- Host slot (RIS1913) correct; outer G36 correct.
- Inventory profile: no ItemPhysicalAttributes -> "Heavy" correlation (same class as AKDovetail pre-fix).
- Interaction: inherited disabled AM.

## 11. Resource identity

- Systemic stale `.meta` registered-path debt (Assets/NATO vs Assets/Weapons_NATO etc.) - STALE_PATH_DEBT, GUID-resolves.
- Known identity anomaly: CarryHandle_Picatinny parent GUID dangling (fix direction: 0A9CD090EE3440E7).

## 12. Known intentional exceptions (not reopened)

G36 AK74 IK workaround; SIG550/VZ58 animation; Groza AK74 muzzle + casing debt; SR2 MagazineWellPP91; L1A1/SLR AK74 IK; deleted 7.62x39 tracer magazine; PSO DovetailAK convergence; single PSO; AKDovetail/Collimator as frozen current state.

## 13. Top fix candidates (descriptive only, NOT executed; ordered by dependency)

1. (HKG36 handle, part family) add effective ItemPhysicalAttributes (inherited-instance override, normal weight) - depends on: nothing; removes the "Heavy" profile gap.
2. (Identity) correct CarryHandle_Picatinny parent GUID to 0A9CD090EE3440E7.
3. (Collimator mount) confirm/normalize the child model mount pivot to exactly `snap_weapon` (model-side; user-frozen - requires approval).
4. (Retest) run the P0 chain once 1-3 are in place.

LIVE_GAMEPLAY_FILES_CHANGED: NONE
AUDIT_STATUS: COMPLETE