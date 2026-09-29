# 1P29 Optic Resource Intake Audit (READ ONLY)

## Resource folder (ARMST)
`Prefabs/Weapons/Attachments/Optics/Optic_1P29/`
- `Optic_1P29_base.et` — GUID `952D9BD7B6F8F591` — EMPTY STUB (inherits WeaponOptic_Base, no components, ID 4BA426CBAED42A14)
- `.meta` — resource identity

## Model
- `{B7A579385AFC8581}Assets/Weapons/Attachments/Optics/1P29/Optic_1P29.xob` (game-provided; not exported into ARMST)
- HDR `{3BD4127D635A335E}.../1P29/Data/Optic_1P29_HDR.emat`; reticle `{4E6095CD6A337D2A}UI/Textures/Sights/1P29/1P29_black_solid_UI.edds`

## Existing 1P29 prefabs
- ARMST base `952D9BD7B6F8F591`: empty stub.
- ARMA_X playable `83FED4852D52BDDD` (`Optic_1P29.et`): empty stub inheriting ARMST 952D.
- PROVEN FULL base `0745A57C37C15101` (`Optic_1P29_base.et`): complete optic (InventoryItemComponent + WeaponAttachmentAttributes{AttachmentOpticsDovetailAK} + MeshObject + SCR_2DPIPSightsComponent + ActionsManagerComponent).

## Reference optic structure (relevant components only)
- Parent: `WeaponOptic_Base.et`
- `InventoryItemComponent` → `SCR_ItemAttributeCollection` → `WeaponAttachmentAttributes{AttachmentType AttachmentOpticsDovetailAK}` (+ name/desc/phys)
- `MeshObject` → 1P29 model
- `SCR_2DPIPSightsComponent` → SightsPosition, SightsRanges (100–500), SCR_SightsZoomFOVInfo (4x), front/rear pivots, reticle textures, HDR emat, FOV 8
- `ActionsManagerComponent` → attach action context "optic"

## Plan
- Target type: `AttachmentOpticsDovetailAK` (already present; no new type).
- Proposed path: `Prefabs/Weapons/Attachments/Optics/Optic_1P29/armst_Optic_1P29.et` (preferred) OR populate existing ARMST base stub `952D...`.
- Proposed parent: proven full 1P29 base `{0745A57C37C15101}` (correct 1P29 sight values), else `WeaponOptic_Base`.
- Compatibility: weapon dovetail → PSO-1 or 1P29; no weapon prefab changes required.

## Open issue
- Base-GUID discrepancy: ARMST `952D...` is empty while full content is under `0745...`; playable `83FED...` inherits the empty stub. A path/GUID decision is needed. No GUID invented.

READY_FOR_BUILD: YES (structural) — pending target-path decision
LIVE_FILES_CHANGED: NONE
