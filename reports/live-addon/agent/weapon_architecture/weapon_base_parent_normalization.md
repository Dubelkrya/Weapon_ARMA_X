# ARMST Weapon Base Parent Normalization

## Stale renamed-parent path cleanup
- STALE_PARENT_PATHS_FOUND: 20
- STALE_PARENT_PATHS_FIXED: 20
- OLD_RENAMED_PARENT_PATH_REFS remaining: 0

Fixed files:
- `Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91_base.et.meta`
- `Prefabs/Weapons/Russian/Handguns/Pm/armst_PM_base.et.meta`
- `Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2_base.et.meta`
- `Prefabs/Weapons/Russian/Handguns/TT/armst_TT_base.et.meta`
- `Prefabs/Weapons/Russian/MachineGuns/armst_PKM_base.et.meta`
- `Prefabs/Weapons/Russian/MachineGuns/armst_RPK74_base.et.meta`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK105.et`
- `Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et.meta`
- `Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et.meta`
- `Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et.meta`
- `Prefabs/Weapons/Western/Handguns/armst_M9_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_HKG36_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/SLR/armst_SLR_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550_base.et`
- `Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/armst_Rifle_M16A2_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/armst_VZ58P_base.et.meta`
- `Prefabs/Weapons/Western/Rifle/armst_VZ58V_base.et.meta`

## AK74 reparent decisions (NOT applied)
```
{
 "armst_AK74N.et": "REVIEW_REQUIRED",
 "armst_AK74M.et": "REVIEW_REQUIRED",
 "armst_AKS.et": "REVIEW_REQUIRED",
 "armst_AK74M_full.et": "REVIEW_REQUIRED",
 "armst_AK105.et": "PATH_ONLY (already parented to base by GUID)"
}
```
- Reason: direct reparent to `armst_AK74_base.et` changes effective state (parents currently chain through concrete AK74N / distinct vanilla bases); materializing would be extensive and not provably zero-diff.

## AKM_full
- candidate reparent to `armst_Rifle_AKM_base.et`
```
{
 "changed_component_count": 3
}
```
- NOT applied: effective diff nonzero -> REVIEW_REQUIRED.

## M16A2 carbine
- parent: `{9207B5D36C3C8C94}Prefabs/Weapons/Rifles/M16/Rifle_M16A2_carbine_base.et` (vanilla carbine base) — unchanged; resolves independently of M16A2_base.

## VZ58
- `armst_VZ58P_base.et` and `armst_VZ58V_base.et` remain independent main weapons.

## Validation
- GUID_CHANGES: 0
- DANGLING_PARENT_REFS: 0
- UNRELATED_GAMEPLAY_CHANGES: 0
- only path text updated in .et/.meta; no component/gameplay edits

LIVE_FILES_CHANGED: path-text cleanup in 20 files
