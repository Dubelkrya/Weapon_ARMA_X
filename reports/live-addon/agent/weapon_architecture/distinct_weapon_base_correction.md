# Distinct Weapon Base Correction

- SOC94 OLD: `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_SOC94.et`
- SOC94 NEW: `Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_SOC94_base.et`
- GUID: E394112ABBC198D8 (preserved=True)
- content_identical: True
- parent before/after: `{140E94F473B60FE3}Rifles/AKM/armst_Rifle_AKM_base.et` / `{140E94F473B60FE3}Rifles/AKM/armst_Rifle_AKM_base.et`
- old path refs remaining: 0

## Classification
- SOC94: DISTINCT_MAIN_WEAPON (model SOK_94_weapon.xob, display SOK-94) -> renamed
- VPO136: AMBIGUOUS (display VPO-136 but no distinct local model; inherits AKM mesh) -> not renamed
- AKMS: AKM_VARIANT (real AKMS but AKM mesh inherited) -> not renamed
- AKM_full: LOADOUT_VARIANT -> not renamed
- AKS74U: AMBIGUOUS (distinct compact weapon inside AK74 folder; not normalized here)
- AKS74UN: LOADOUT_VARIANT (night variant of AKS74U)

OVERRIDES_CHANGED: 0
PARENTS_CHANGED: 0
GUID_CHANGES: 0
DANGLING_REFS: 0
STATUS: PASS
