# HK G36 Carry Handle + Optic Attachment Audit (READ ONLY)

## Handle prefab
- HANDLE_PREFAB: NONE - no G36/HKG36 carry-handle or integrated-optic attachment prefab exists in live addon or exported resources
- HANDLE_MODEL: NONE dedicated; G36 assets are HKG36.xob (weapon), HKG36_mag.xob, HKG36_Plank.xob, Plank_Pika.xob; no carry-handle/optic mesh

## Current G36 attachment structure
- BayonetSlot `AttachmentSlotComponent {6A0470709BAE0574}` enabled=False type=`AttachmentBayonetM9 {6A0470709BAE0571}` default=`None`
- Handguard `AttachmentSlotComponent {6A0470709BAE0589}` enabled=True type=`AttachmentHandGuardM16 {6A0470709BAE0575}` default=`None`
- optics `AttachmentSlotComponent {6A0470709BAE058E}` enabled=True type=`AttachmentOpticsG36 {6A0470709BAE058B}` default=`None`
- sights: `SightsComponent {BB23A637957CFFF8}` enabled=0 (weapon-side sights disabled; sight functionality intended to come from an attachment)

## Proven default-attachment pattern
- Default-installed attachment = `Prefab "{GUID}path"` inside `AttachmentSlot InventoryStorageSlot <slot>` of an AttachmentSlotComponent
  - armst_AK74M.et optics/handguard default Prefab
  - armst_AK74M_full.et default Prefab PSO1/UGL/Suppressor
  - armst_Rifle_AKMS.et default Prefab stock
- attachment provides `InventoryItemComponent > WeaponAttachmentAttributes > AttachmentType <class>` matching the weapon slot class
- DEFAULT_ATTACHMENT_FIELD: `Prefab`
- TARGET_SLOT: `AttachmentSlotComponent {6A0470709BAE058E} > AttachmentSlot InventoryStorageSlot optics`
- TARGET_ATTACHMENT_TYPE: `AttachmentOpticsG36`

## Sight ownership
- OWNED_BY_ATTACHMENT (G36 local SightsComponent {BB23A637957CFFF8} is Enabled 0; the carry-handle/optic prefab must supply the active SightsComponent)
- None active: weapon SightsComponent is disabled, so adding an attachment SightsComponent will not create duplicate active sight systems. Weapon retains dormant SightsRanges data {BB23A637957CFFF8} (KEEP_ON_WEAPON / DISABLE_WHEN_ATTACHMENT_USED).

## Removability
- default_removable: SUPPORTED pattern (default attachments via `Prefab` are normal attachments and removable)
- default_locked: NO proven locking field found in local resources (only unrelated vehicle `Type Locked`)
- recommendation: DEFAULT_REMOVABLE

## Pre-existing M16-derived components
- AttachmentType AttachmentHandGuardM16 {6A0470709BAE0575}
- AttachmentSlotComponent Handguard {6A0470709BAE0589}
- AttachmentType AttachmentBayonetM9 {6A0470709BAE0571}
- uses M16 sound set / particles (pre-existing)

## Proposed minimal build (future, not implemented)
### G36 changes
- Set `Prefab "{<new handle GUID>}Prefabs/Weapons/Attachments/.../armst_G36_CarryHandle_Optic.et"` inside AttachmentSlotComponent {6A0470709BAE058E} > optics slot (default install). No other G36 change.
### Handle prefab changes
- Create a carry-handle+optic attachment prefab providing: MeshObject (handle/optic mesh), InventoryItemComponent>WeaponAttachmentAttributes>AttachmentType AttachmentOpticsG36, and an active SightsComponent with the G36 optic reticle/ranges.
### NEW_RESOURCES_REQUIRED: YES (attachment prefab; possibly a dedicated carry-handle/optic mesh asset)

LIVE_FILES_CHANGED: NONE
