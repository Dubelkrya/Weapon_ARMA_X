# HKG36 Optic PIP / Reticle / FOV Provenance Audit (READ ONLY)

- MODEL: {9CF0737D5CB7F17D}Assets/Weapons_NATO/HKG36/HKG36_Plank.xob (MeshParam PIP; materials Glass_collim, Collimat, Dualoptics, Optic_pip)

## PIP resources
- `Assets/Weapons_NATO/HKG36/data/Optic_pip.emat` (guid 271341545D2AA982) - MatCommon AlbedoMap "$rendertarget" -> true PIP lens surface
- `Assets/Weapons_NATO/HKG36/data/Glass_collim.emat` (guid 8CD18F5545FEEE92) - glass lens (BCR/Opacity/NMO maps)
- `Assets/Weapons_NATO/HKG36/data/Dualoptics.emat` (guid B97EA982FE30C578) - 
- `Assets/Weapons_NATO/HKG36/data/Collimat.emat` (guid A0547437CBA21867) - 

- RETICLE_RESOURCES: NONE - no G36 reticle texture (no m_sReticleTexture/Glow or scope UI reticle tied to HKG36 found)
- MAGNIFICATION: NONE proven (no m_fMagnification/m_fBaseZoom/m_fZoomMax value tied to HKG36)
- FOV: NONE proven (no m_fObjectiveFov tied to HKG36)
- PIP_COMPONENT: Structure only: optics use `SCR_2DPIPSightsComponent` with m_sReticleTexture, m_sReticleGlowTexture, m_rScopeHDRMatrial, m_fBaseZoom/m_fMagnification/m_fObjectiveFov/m_fZoomMax, m_eZeroingType (e.g. Optic_4x20_base.et). Our new attachment currently uses a plain `SightsComponent` and lacks all PIP/reticle fields.
- SCOPE_MATERIALS: HKG36-specific Optic_pip (render target) + Glass_collim/Dualoptics/Collimat exist, but no prefab references Optic_pip GUID 271341545D2AA982 (only the .emat/.meta) -> no existing optic wires them.

## Current attachment
- prefab: Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Optic.et
- guid: EDBDAAE1FC7F4723
- has_AttachmentOpticsG36: True
- model_ok: True
- sights_component: plain SightsComponent (Enabled 1) with SightsRanges 200-800 / SightsPosition 0 0 0 / SightsPointFront offset / SightsPointRear pivot w_sight / m_iOpticDOFDistanceScale 30 (values from G36 weapon)
- missing_fields: ['m_sReticleTexture', 'm_sReticleGlowTexture', 'm_rScopeHDRMatrial (expect HKG36 Optic_pip)', 'm_fBaseZoom / m_fMagnification / m_fObjectiveFov / m_fZoomMax', 'm_vCameraAngles', 'm_fReticleAngularSize / m_fReticlePortion / m_fScopeRadius', 'm_eZeroingType', 'PIP-capable component class (SCR_2DPIPSightsComponent)']

## Classification: PARTIAL_G36_OPTIC_DATA_FOUND
- READY_TO_INSTALL_DEFAULT_PREFAB: NO
- No numerical FOV/zoom/reticle values were invented; installation withheld.

LIVE_FILES_CHANGED: NONE
