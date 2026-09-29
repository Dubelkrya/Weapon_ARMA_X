# HK G36 Carry Handle + Optic Attachment (created, not installed)

- MODEL: `{9CF0737D5CB7F17D}Assets/Weapons_NATO/HKG36/HKG36_Plank.xob`
- NEW_PREFAB: `Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Optic.et`
- NEW_GUID: EDBDAAE1FC7F4723
- PARENT: `{966B4E5523D2F166}Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et`
- ATTACHMENT_TYPE: AttachmentOpticsG36 (matches G36 slot class)
- SIGHT PROVENANCE: SightsRanges/SightsPosition/SightsPointFront/SightsPointRear/m_iOpticDOFDistanceScale copied from G36 weapon local SightsComponent {BB23A637957CFFF8} (Enabled 0)
- MAGNIFICATION: NONE proven for G36 dual-optic (no FOV/zoom evidence); HKG36_Plank meta exposes MeshParam PIP + materials Optic_pip/Glass_collim/Collimat/Dualoptics but no reticle/magnification values
- RETICLE: NONE proven (no G36 reticle texture reference found)
- SIGHTS_POSITION: {G_SIGHTS} SightsPosition offset 0 0 0; SightsPointRear PivotID "w_sight" (proven from weapon)
- DEFAULT_PREFAB_INSTALLED: NO
- CLASS_MATCH: YES
- SAFETY_GATE: Sight completeness not provable (no PIP/reticle/FOV) -> prefab created but NOT installed on G36 per section 6.

LIVE_FILES_CHANGED: 1 new attachment prefab (+meta); G36 unchanged
