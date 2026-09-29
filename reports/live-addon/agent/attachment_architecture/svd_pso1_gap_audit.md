# SVD PSO-1 Gap & Orphan AKSVD Type Audit (READ ONLY)

## PSO1_AK
- PATH: `Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1_ak.et`
- GUID: `F325FE2E3DDCDDAD`
- OUTER_TYPE: `AttachmentOpticsDovetailAKSVD`
- PARENT: `{C850A33226B8F9C1}.../armst_Optic_PSO1.et`
- MODEL/SIGHTS: inherited vanilla PSO-1 (`Optic_PSO1.xob`, `SCR_2DPIPSightsComponent`)
- LIVE_REFERENCES: none (0 live weapon/default references)

## DIFF_VS_PSO1
- Only difference: `armst_Optic_PSO1.et` declares `AttachmentType AttachmentOpticsDovetailAK`; `armst_Optic_PSO1_ak.et` overrides it to `AttachmentOpticsDovetailAKSVD`. Everything else (InventoryItemComponent, WeaponAttachmentAttributes instance `5284D858FFF9BE66`, model, sights) identical.

## AKSVD_TYPE_PROVENANCE
- `AttachmentOpticsDovetailAKSVD` occurs ONLY in `armst_Optic_PSO1_ak.et` (single occurrence across ARMST + Weapon_ARMA_X + VanillaSources). No weapon slot, no script/config ref, no vanilla definition. => non-vanilla, unused/experimental type (orphan).

## SVD_TYPE_PROVENANCE
- `AttachmentOpticsDovetailSVD` occurs in: ARMST `armst_Rifle_SOC94_base.et`; vanilla SVD `Rifle_SVD_base.et` (both Weapon_ARMA_X and VanillaSources); vanilla `Optic_PSO1_base.et` (outer type of the PSO-1 optic). => real vanilla SVD dovetail type with a real intended optic (vanilla PSO-1).

## SVD_SLOT
- instance `5472D211BFD78F81`, LOCAL_OVERRIDE of vanilla Rifle_SVD_base `Dovetail` slot; AttachmentType currently `AttachmentOpticsDovetailAK` (ARMST changed it from vanilla `AttachmentOpticsDovetailSVD`); no default prefab.

## SOC94_SLOT
- instance `65AE4CB5E23C0F63`, LOCAL_OVERRIDE (of AKM stock instance); AttachmentType `AttachmentOpticsDovetailSVD`; no default prefab; frozen.

## SVD_SOC94_SHARED_OPTIC_INTERFACE = NO
- SVD local type = `AttachmentOpticsDovetailAK`; SOC94 type = `AttachmentOpticsDovetailSVD`. They are currently different interfaces.

## CLASSIFICATION: A. PSO1_AK_IS_SVD_OPTIC_CANDIDATE
- `armst_Optic_PSO1_ak.et` is the only orphan PSO-1 optic (0 refs) and `AttachmentOpticsDovetailSVD` is a real vanilla SVD type currently used by SOC94. Repurposing this orphan optic (same PSO-1 model/sights) to expose `AttachmentOpticsDovetailSVD` would provide SOC94 (and the native SVD mount) with a matching optic without touching any weapon override.

## PROPOSED_FUTURE_DIFF (not applied)
- File: `armst_Optic_PSO1_ak.et`
- Change ONLY: `AttachmentType AttachmentOpticsDovetailAKSVD` -> `AttachmentType AttachmentOpticsDovetailSVD`
- Preserve: GUID `F325FE2E3DDCDDAD`, parent `armst_Optic_PSO1.et`, WeaponAttachmentAttributes instance `5284D858FFF9BE66`, model, sights, inventory grid.
- Optional: rename resource `armst_Optic_PSO1_ak.et` -> `armst_Optic_PSO1_svd.et` (GUID preserved) for semantic clarity.
- Do NOT touch SVD/SOC94 weapon overrides.
- Expected impact: 0 on current live weapons (0 references); provides a matching optic for `AttachmentOpticsDovetailSVD`.

## NOTE
- SVD base currently overrides its native mount to `AttachmentOpticsDovetailAK` (so it accepts `armst_Optic_PSO1.et`). It would only use the repurposed SVD optic if the project later changes that override (out of scope).

LIVE_FILES_CHANGED: NONE
