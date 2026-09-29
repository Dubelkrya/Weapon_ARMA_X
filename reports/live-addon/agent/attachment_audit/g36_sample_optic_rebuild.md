# HK G36 Sample-Based Handle Rebuild

- HANDLE_PARENT: {966B4E5523D2F166}Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et
- HANDLE_MODEL: {9CF0737D5CB7F17D}Assets/Weapons_NATO/HKG36/HKG36_Plank.xob
- ATTACHMENT_TYPE: AttachmentOpticsG36
- DUPLICATE_COMPONENTS_REMOVED: local duplicate SCR_2DPIPSightsComponent {0ABB174A9D3F1ECF} + duplicate local component set replaced by overrides of inherited IDs
- EFFECTIVE_PIP_COMPONENT_COUNT: 1
- InventoryItemComponent=1 MeshObject=1 secondary SightsComponent=1 (Enabled 0=True)
- PIP_PIVOTS: SightsPosition {584E83B41FD2B6D5} / PointFront {584E83BC7A32CEE7} / PointRear {584E83BC7F8BAFF3}; SightsFOVInfo {584E83B41719648C}
- PIVOT_ALIGNMENT: RUNTIME_REQUIRED (HKG36_Plank named pivots not statically exposed)
- MAGNIFICATION: 3 ; FOV: 4 ; BaseZoom 3 ; ZoomMax 3 ; InterpSpeed 6
- RETICLE: TEMPORARY SampleOptic_Reticle ; HDR: TEMPORARY SampleOptic HDR
- UPPER_REFLEX: DEFERRED (secondary SightsComponent left present but Enabled 0)
- G36_DEFAULT_PREFAB: `{EDBDAAE1FC7F4723}.../armst_HKG36_CarryHandle_Optic.et` (True)
- G36_LOCAL_SIGHTS: DISABLED (True)
- OTHER_G36_CHANGES: 0 ; GUID_COLLISIONS: 0
- At task start the backup already contained the default optics Prefab and slot Offset -0.0004 0 0.0106; the install step was therefore an idempotent no-op. G36 net change = 0.
- SAMPLE ASSET RISK: SampleOptic_Reticle.edds / Optic_SampleOptic_HDR.emat GUIDs were not found in local files or resourceDatabase; refs may be unresolved at runtime.
- RUNTIME_STATUS: NOT_TESTED

## Runtime smoke checklist (required)
1. spawn G36
2. HKG36_Plank handle appears automatically
3. handle position/orientation correct
4. attachment removable
5. ADS enters handle PIP optic
6. PIP image renders
7. sample reticle visible
8. ~3x magnification
9. sight aligned with barrel
10. removing handle removes optic
11. no duplicate sight switching
12. no invisible SampleOptic mesh
