# G36 Handle Structural Search (READ ONLY)

## AttachmentType users
- AttachmentOpticsG36: only the G36 weapon slot + Scripts/Gamecode/Attachment_optic.c class def
- AttachmentOpticsCarryHandle: Optic_4x20_base.et, Collim_AP2k_base.et, Rifle_M16A2_base.et slot

## Compatible prefabs
- `Prefabs/Weapons/Attachments/Optics/Optic_4x20/Optic_4x20_base.et` (guid 9D450824D9661395)
  - parent: `{966B4E5523D2F166}Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et`
  - model: `{FB0E7050A887C7F5}Assets/Weapons/Attachments/Optics/4x20/Optic_4x20.xob`
  - type: `AttachmentOpticsCarryHandle {58E2B316401F7A2D}`
  - sights: SCR_2DPIPSightsComponent {5D0CC83435B55855} (SightsPosition {5D0CC83435B55853}; zoom 4x)
- `Prefabs/Weapons/Attachments/Optics/Optic_AP2k/Collim_AP2k_base.et` (guid 41F0FA8ED5CEC018)
  - parent: `{78689FF321194268}Prefabs/Weapons/Attachments/Optics/WeaponCollimator_Base.et`
  - model: `{0C16AEED5C13BF74}Assets/Weapons/Attachments/Optics/AP2k/Optic_AP2k.xob`
  - type: `AttachmentOpticsCarryHandle {604ACAC56AE9B0AA}`
  - sights: SCR_...SightsComponent (owns active sights)

## FOUND
- FOUND_PREFAB: `Prefabs/Weapons/Attachments/Optics/Optic_4x20/Optic_4x20_base.et`
- FOUND_GUID: 9D450824D9661395
- MODEL: `{FB0E7050A887C7F5}Assets/Weapons/Attachments/Optics/4x20/Optic_4x20.xob`
- SIGHTS: `SCR_2DPIPSightsComponent {5D0CC83435B55855} + SightsPosition {5D0CC83435B55853}`
- TARGET_SLOT: `AttachmentSlotComponent {6A0470709BAE058E} > AttachmentSlot InventoryStorageSlot optics`
- PROPOSED_DEFAULT_PREFAB_REF: `Prefab "{9D450824D9661395}Prefabs/Weapons/Attachments/Optics/Optic_4x20/Optic_4x20_base.et"` (NOT applied)

## Class compatibility caveat
- slot_class: AttachmentOpticsG36 (ARMST-defined in Scripts/Gamecode/Attachment_optic.c; parent AttachmentOptics)
- candidate_class: AttachmentOpticsCarryHandle (vanilla carry-handle mount; parent AttachmentOptics)
- issue: No prefab declares AttachmentOpticsG36; candidates declare AttachmentOpticsCarryHandle. Both derive from AttachmentOptics but are not proven to be interchangeable by the slot matcher. Exact mount is therefore not proven locally (may require slot class change or an ARMST AttachmentOpticsG36 prefab that is not present in the authoritative addon).
- No weapon/default slot references a prefab with AttachmentOpticsG36; no stale-path GUID reference to such a prefab found.

## CLASSIFICATION: FOUND_COMPATIBLE_CANDIDATES
LIVE_FILES_CHANGED: NONE
