# RUNTIME REGRESSION CHECKLIST (V2)

Source: `agent\compliance_audit_v2\runtime_regression_matrix.json` (authoritative audit V2 - 8 matrix cases).
Mode: PLAN / READ ONLY. **LIVE_FILES_CHANGED = NONE**

## Preflight result
- All 9 matrix target files exist on the current live addon.
- GUIDs verified: AKDovetail `D71FD2BD68AC4B31`; PSO `C850A33226B8F9C1`; 1P29 `952D9BD7B6F8F591`; SR-2 base `31FB2EC4F4AFFC05`; SR-2 mag `2610CA8D8632DEF4`; HKG36 base `A802C718201D72DF`; Groza base `903C7920F00AB654`; SOC94 base `E394112ABBC198D8`.
- Parents resolve (local or vanilla). AKDovetail model `Assets/addons/Dovetail/AKDovetailMount.xob` exists; slot `BB6000C24BAA468F`, pivots `snap_ris`/`snap_weapon` present.
- PSO default refs confirmed on `armst_Rifle_AKM_full` and `armst_AK74M_full`.
- Note: `armst_HKG36_CarryHandle_Optic.et` has **no .meta** (known REVIEW state from audit V2). It still loads for testing.
- **STALE_TEST_PATHS:** none - every audit path matches its current live path. Only SOC94 parent *path string* is malformed (`Rifles/AKM/armst_Rifle_AKM_base.et`) but GUID-resolves to the current AKM base; the SOC94 prefab path itself is current.

## Execution order (optimized for manual efficiency)

| # | TEST_ID | Focus |
|---|---------|-------|
| 1 | RT-01A | AKDovetail - prefab visibility (standalone) |
| 2 | RT-01B | AKDovetail - weapon -> adapter (AKM) |
| 3 | RT-01C | AKDovetail - adapter -> RIS optic |
| 4 | RT-01D | AKDovetail - full chain simultaneous |
| 5 | RT-01E | AKDovetail - remove / re-add cycle |
| 6 | RT-02 | PSO canonical on AKM_full / AK74M_full (+ manual dovetail attach) |
| 7 | RT-03 | 1P29 co-verify (already user-verified; regression NOT warranted) |
| 8 | RT-05 | SOC94 spawn / inherited structure |
| 9 | RT-04 | Groza 9x39 firing + casing/muzzle particles |
| 10 | RT-07 | G36 carry handle / picatinny chain / factory handling |
| 11 | RT-06 | SR-2 + 30rnd magazine |
| 12 | RT-08 | Broad arsenal sweep (28 bases + 20 variants) |

Rationale: AK-family optics are run consecutively on the same host frames (RT-01..RT-03), then the AKM-derived SOC94 (RT-05), then standalone subsystems (Groza, G36, SR-2), finishing with the full sweep. Visual checks precede gameplay; the nested adapter chain is proven via RT-01A..E before other optic attach tests.

## 1P29 regression decision
`armst_Optic_1P29.et` (GUID `952D9BD7B6F8F591`) is **RUNTIME_VERIFIED** by the user (WORKING: 4x PIP, ranges 100-500). The authoritative matrix marks RUNTIME_ALREADY_VERIFIED=true, RUNTIME_TEST_NEEDED=NO. The audit is read-only and no dependent file changed after that verification, so **no regression is warranted**; RT-03 is a reference card with an optional co-verify only.

## AKDovetailMount (RT-01) - explicit sub-test separation
The historical invisibility root cause (duplicate effective MeshObject) requires separate PASS accounting: A = standalone visibility; B = weapon->adapter outer contract; C = adapter->RIS child contract; D = full chain simultaneous; E = remove/re-add. Do not combine into one ambiguous PASS.

## PSO / 1P29 unified slot expectation
`AttachmentOpticsDovetailAK` is the single gameplay compatibility type for Russian side optics. Where the slot is tested (RT-02/RT-03), both PSO and 1P29 must attach to the same slot type. No separate physical-mount expectation - do not create one.

## RT-01A - armst_Optic_AKDovetailMount.et (adapter standalone)

**CURRENT_PATH:** Prefabs/Weapons/Attachments/Optics/AKDovetailMount/armst_Optic_AKDovetailMount.et
**GUID:** D71FD2BD68AC4B31
**PRECONDITION:** Workbench open in prefab preview; current addon resource database loaded
**STEPS:**
1. Open prefab preview for adapter
2. Confirm the Dovetail AK model renders (one visible mesh)
3. Zoom/rotate - no empty or invisible state
**PASS_CRITERIA:**
  - Adapter renders visible Dovetail model
  - No mesh/entity errors in console
**FAIL_SYMPTOMS:**
  - Adapter invisible (historical duplicate-mesh symptom)
  - Double geometry / z-fighting
**RESULT:** NOT_TESTED
**NOTES:** PREFAB_VISIBILITY (A) - one visible MeshObject; other MeshObject is Enabled 0 (inert).
**FAILURE_TRIAGE:** RENDERING

## RT-01B - armst_Optic_AKDovetailMount.et (weapon -> adapter)

**CURRENT_PATH:** armst_Rifle_AKM.et + armst_Rifle_AKM_base.et (dovetail slot)
**GUID:** D71FD2BD68AC4B31
**PRECONDITION:** RT-01A passed
**STEPS:**
1. Spawn armst_Rifle_AKM
2. Open inventory, place adapter into dovetail slot
3. Confirm adapter model attaches at dovetail, snap_weapon pivot aligns
**PASS_CRITERIA:**
  - Adapter attaches to AKM dovetail slot; renders in correct position/orientation
**FAIL_SYMPTOMS:**
  - Adapter rejected by slot
  - Adapter floating/misaligned
  - Invisible after attach
**RESULT:** NOT_TESTED
**NOTES:** ATTACHMENT_OUTER_CONTRACT (B) - outer type AttachmentOpticsDovetailAK.
**FAILURE_TRIAGE:** ATTACHMENT_OUTER_CONTRACT

## RT-01C - armst_Optic_AKDovetailMount.et (adapter -> RIS optic)

**CURRENT_PATH:** armst_Rifle_AKM.et + armst_Rifle_AKM_base.et (dovetail slot)
**GUID:** D71FD2BD68AC4B31
**PRECONDITION:** RT-01B passed
**STEPS:**
1. With adapter attached, open child RIS1913 slot
2. Place a RIS/Picatinny optic
3. Confirm optic mounts on snap_ris pivot
**PASS_CRITERIA:**
  - RIS optic attaches via BB6000C24BAA468F (AttachmentOpticsRIS1913); renders on snap_ris
**FAIL_SYMPTOMS:**
  - RIS optic rejected
  - Optic misaligned on adapter
**RESULT:** NOT_TESTED
**NOTES:** ATTACHMENT_CHILD_CONTRACT (C) - PivotID snap_ris / ChildPivotID snap_weapon.
**FAILURE_TRIAGE:** ATTACHMENT_CHILD_CONTRACT

## RT-01D - armst_Optic_AKDovetailMount.et (chain simultaneous)

**CURRENT_PATH:** armst_Rifle_AKM.et + armst_Rifle_AKM_base.et (dovetail slot)
**GUID:** D71FD2BD68AC4B31
**PRECONDITION:** RT-01B and RT-01C passed
**STEPS:**
1. AKM + adapter + RIS optic equipped together
2. ADS through optic, fire
**PASS_CRITERIA:**
  - WEAPON->ADAPTER->OPTIC chain correct visually and mechanically while firing
**FAIL_SYMPTOMS:**
  - Elements spontaneously detach
  - Sight axis wrong during fire
**RESULT:** NOT_TESTED
**NOTES:** Combined chain state (D).
**FAILURE_TRIAGE:** ATTACHMENT_OUTER_CONTRACT

## RT-01E - armst_Optic_AKDovetailMount.et (remove / re-add)

**CURRENT_PATH:** armst_Rifle_AKM.et + armst_Rifle_AKM_base.et (dovetail slot)
**GUID:** D71FD2BD68AC4B31
**PRECONDITION:** RT-01D passed
**STEPS:**
1. Remove adapter, re-add
2. Remove RIS optic, re-add
3. Confirm final chain state identical
**PASS_CRITERIA:**
  - Remove/re-add completes without corruption; no orphan or duplicate attachments
**FAIL_SYMPTOMS:**
  - Adapter invisible after re-add
  - Attachment duplication
  - Inventory desync
**RESULT:** NOT_TESTED
**NOTES:** Cleanup cycle (E).
**FAILURE_TRIAGE:** ATTACHMENT_OUTER_CONTRACT

## RT-02 - armst_Optic_PSO1.et (canonical)

**CURRENT_PATH:** Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et
**GUID:** C850A33226B8F9C1
**PRECONDITION:** PSO default refs present on armst_Rifle_AKM_full and armst_AK74M_full
**STEPS:**
1. Spawn armst_Rifle_AKM_full (default PSO installed)
2. Confirm PSO renders on dovetail, ADS shows 4x PIP reticle
3. Spawn armst_AK74M_full and repeat
4. Manually attach armst_Optic_PSO1 to a stock AK dovetail slot
**PASS_CRITERIA:**
  - PSO renders with PIP sight on both full variants
  - PSO performs 4x view with correct range behavior
**FAIL_SYMPTOMS:**
  - PSO invisible
  - PIP black/blank
  - PSO rejects dovetail slot
**RESULT:** NOT_TESTED
**NOTES:** Single PSO architecture (AttachmentOpticsDovetailAK unified type).
**FAILURE_TRIAGE:** SIGHTS/PIP

## RT-03 - armst_Optic_1P29.et

**CURRENT_PATH:** Prefabs/Weapons/Attachments/Optics/Optic_1P29/armst_Optic_1P29.et
**GUID:** 952D9BD7B6F8F591
**PRECONDITION:** Already user runtime verified WORKING. No regression warranted: no dependent file changed since verification (audit read-only)
**STEPS:**
1. Optional co-verify only: attach armst_Optic_1P29 to the same AK dovetail slot used in RT-02
**PASS_CRITERIA:**
  - [Reference] If co-verified: 1P29 renders 4x PIP and functions (as previously confirmed)
**FAIL_SYMPTOMS:**
  - [Reference] 1P29 invisible / PIP broken / slot rejected
**RESULT:** VERIFIED_RUNTIME (PASS)
**NOTES:** User-confirmed WORKING (4x PIP, ranges 100-500). Regression NOT warranted (no change since verification).
**FAILURE_TRIAGE:** SIGHTS/PIP

## RT-04 - armst_Groza_base.et

**CURRENT_PATH:** Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et
**GUID:** 903C7920F00AB654
**PRECONDITION:** Preflight: parent Rifle_Base.et; MagazineWell9x39; default magazine SP5 (77215B3A185D1EFD)
**STEPS:**
1. Spawn Groza (SP5 20rnd default loaded)
2. Check magazine well accepts Groza 9x39 SP5/SP6 magazines
3. Fire - confirm ejection cycle and casing particle (Casing_762x39_PS.ptc known debt)
**PASS_CRITERIA:**
  - SP5 loads by default; SP6 also loads; weapon fires and ejects; muzzle (Muzzle_AK74.ptc) and casing particle play
**FAIL_SYMPTOMS:**
  - Magazine rejected (wrong well)
  - Firing fails
  - No ejection/casing particle (caliber mismatch of casing is accepted known debt)
**RESULT:** NOT_TESTED
**NOTES:** Known debt remains visible as-is; not to be fixed by this test.
**FAILURE_TRIAGE:** AMMO/MAGAZINE

## RT-05 - armst_Rifle_SOC94_base.et

**CURRENT_PATH:** Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et
**GUID:** E394112ABBC198D8
**PRECONDITION:** Parent resolves by GUID 140E94F473B60FE3 (armst_Rifle_AKM_base); parent path string malformed but GUID-matched
**STEPS:**
1. Spawn SOC94
2. Confirm full AKM-derived structure (attachments, stock interface)
3. Fire a few rounds
**PASS_CRITERIA:**
  - SOC94 inherits correctly; no load failure despite malformed parent path (GUID resolution works); fires normally
**FAIL_SYMPTOMS:**
  - SOC94 fails to spawn / empty entity / missing inherited components
**RESULT:** NOT_TESTED
**NOTES:** Verifies malformed parent path does not break inherited structure.
**FAILURE_TRIAGE:** RESOURCE_LOADING

## RT-06 - armst_SR_2_base.et + armst_Magazine_9x18_SR2_30rnd_Ball.et

**CURRENT_PATH:** Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2_base.et + Prefabs/Weapons/Magazines/Russian/9x18/PM/9x18/armst_Magazine_9x18_SR2_30rnd_Ball.et
**GUID:** 31FB2EC4F4AFFC05 / 2610CA8D8632DEF4
**PRECONDITION:** Preflight: MagazineWellPP91 shared compat; own mag capacity 30
**STEPS:**
1. Spawn SR-2
2. Load armst_Magazine_9x18_SR2_30rnd_Ball (capacity 30)
3. Fire and reload
**PASS_CRITERIA:**
  - SR-2 accepts its 30rnd mag via PP91 well; loads, fires, feeds 30 rounds; reload works
**FAIL_SYMPTOMS:**
  - Magazine rejected
  - Capacity mismatch visible
  - Feeding failure
**RESULT:** NOT_TESTED
**NOTES:** Shared PP91 well is intentional.
**FAILURE_TRIAGE:** AMMO/MAGAZINE

## RT-07 - armst_Rifle_HKG36_base.et + armst_HKG36_CarryHandle_Optic.et

**CURRENT_PATH:** Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_HKG36_base.et + Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Optic.et
**GUID:** A802C718201D72DF / none (missing meta - known)
**PRECONDITION:** Preflight: weapon slot AttachmentOpticsG36; no direct RIS on weapon; carry-handle optic = factory variant
**STEPS:**
1. Spawn HKG36; verify no direct RIS slot on weapon
2. Attach Carry Handle Optic (AttachmentOpticsG36)
3. Attach Picatinny carry handle variant, then a RIS optic into it
4. Confirm factory handling (AnimationIKPose p_ak74_ik.anm workaround) works
**PASS_CRITERIA:**
  - Carry handle optic mounts on G36 slot; sight/PIP functions; picatinny chain works; no direct RIS on weapon
**FAIL_SYMPTOMS:**
  - Carry handle rejected
  - Factory sight inoperative
  - ADS animation glitch (workaround - report only, not to fix)
**RESULT:** NOT_TESTED
**NOTES:** Carry-handle .et has no .meta (known REVIEW state) - load path must still work for testing.
**FAILURE_TRIAGE:** SIGHTS/PIP

## RT-08 - All main weapons (28 bases + 20 non-base playable variants; 12ga excluded by scope)

**CURRENT_PATH:** Prefabs/Weapons/Russian/... + Prefabs/Weapons/Western/... (see NOTES)
**GUID:** multiple
**PRECONDITION:** RT-01..RT-07 subsystem smoke tests completed or referenced
**STEPS:**
1. For each weapon in the sweep list: spawn in game/editor
2. Confirm mesh visible (no invisible entity)
3. ADS + fire one mag
4. Reload (where applicable)
5. Attach its default optic/magazine where defined
**PASS_CRITERIA:**
  - Every listed weapon spawns visibly, fires, reloads; default submounts attach; no console load errors
**FAIL_SYMPTOMS:**
  - Invisible weapon
  - Spawn failure
  - Fire/reload failure
  - Missing default magazine/optic
  - Console resource load errors
**RESULT:** NOT_TESTED
**NOTES:** Sweep target set = 28 bases + 20 non-base variants from full_mod_inventory.json / weapon_compliance_audit.json of audit V2.
**FAILURE_TRIAGE:** RESOURCE_LOADING

## Failure triage categories
Classify any reported failure into exactly one of:
- RENDERING
- ATTACHMENT_OUTER_CONTRACT
- ATTACHMENT_CHILD_CONTRACT
- PIVOT_ALIGNMENT
- INVENTORY/ACTION
- SIGHTS/PIP
- ANIMATION/IK
- AMMO/MAGAZINE
- RESOURCE_LOADING
- OTHER
No fix proposals are part of this preparation task.
