# Russian Optic Orphan Attachment Type Audit (READ ONLY)

## AttachmentOpticsARMST_DovetailRU
- DEFINITION: `Scripts/Gamecode/Attachment_optic.c` (lines 11-19)
- BASE: `AttachmentOptics`
- ORIGIN: ADDON_DEFINED
- BODY: helper class + Source var + `class AttachmentOpticsARMST_DovetailRU : AttachmentOptics {}`
- LIVE_REFERENCES: definition file only (no slots, no prefabs, no children, no script logic)
- CLASSIFICATION: SAFE_REMOVE_ADDON_ORPHAN

## AttachmentOpticsDovetailAKSVD
- DEFINITION: NOT_FOUND (no class definition anywhere)
- LIVE_REFERENCES: none
- CLASSIFICATION: NOT_FOUND (no cleanup action; nothing to remove)

## AttachmentOpticsRIS1913
- STATUS: KEEP_FUTURE_INTERFACE
- CURRENT_LIVE_USAGE: `Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Picatinny.et` (RIS child slot)

## AttachmentOpticsDovetailSVD
- STATUS: KEEP_EXTERNAL_TYPE
- CURRENT_ARMST_USAGE: 0
- VANILLA_PROVENANCE: `Rifle_SVD_base.et`, `Optic_PSO1_base.et` (Weapon_ARMA_X + VanillaSources)

## Expected cleanup diff (NOT executed)
- `Scripts/Gamecode/Attachment_optic.c`: remove the 3 `AttachmentOpticsARMST_DovetailRU` lines only; keep the G36 class block.

LIVE_FILES_CHANGED: NONE
