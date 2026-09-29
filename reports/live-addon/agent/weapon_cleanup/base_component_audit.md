# ARMST Base Component Cleanup Audit (READ ONLY)

BASE_WEAPONS_AUDITED: 23
LOCAL_COMPONENTS_TOTAL: 175
DISABLED_LOCAL_COMPONENTS: 26
KEEP_REQUIRED: 10
KEEP_OVERRIDE: 117
KEEP_VARIANT_HOOK: 33
KEEP_ATTACHMENT_INTERFACE: 15
REMOVE_DEAD_LOCAL: 0
REVIEW_REQUIRED: 0
DUPLICATE_COMPONENT_GROUPS: 37
OBSOLETE_ATTACHMENT_SLOTS: 0
SAFE_CLEANUP_QUEUE: 0

## Per-weapon
| weapon | local | disabled | overrides | variant hooks | attachments | cleanup |
|---|---|---|---|---|---|---|
| Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91_base.et | 10 | 1 | 8 | 2 | 0 | 0 |
| Prefabs/Weapons/Russian/Handguns/Pm/armst_PM_base.et | 6 | 1 | 4 | 2 | 0 | 0 |
| Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2_base.et | 10 | 1 | 8 | 2 | 0 | 0 |
| Prefabs/Weapons/Russian/Handguns/TT/armst_TT_base.et | 9 | 1 | 7 | 2 | 0 | 0 |
| Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB_base.et | 10 | 1 | 8 | 2 | 0 | 0 |
| Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et | 8 | 2 | 6 | 0 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et | 3 | 2 | 0 | 2 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_base.et | 12 | 0 | 3 | 5 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et | 8 | 3 | 5 | 2 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et | 9 | 1 | 3 | 3 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et | 9 | 3 | 6 | 2 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et | 7 | 1 | 4 | 2 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/VAL/armst_Rifle_val_base.et | 8 | 1 | 7 | 0 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et | 9 | 2 | 7 | 0 | 1 | 0 |
| Prefabs/Weapons/Russian/Rifle/VSS/armst_Rifle_vss_base.et | 7 | 1 | 6 | 0 | 1 | 0 |
| Prefabs/Weapons/Western/Rifle/HKG33/armst_Rifle_HKG33_base.et | 6 | 1 | 4 | 1 | 1 | 0 |
| Prefabs/Weapons/Western/Rifle/HKG36/armst_Rifle_HKG36_base.et | 10 | 1 | 3 | 3 | 1 | 0 |
| Prefabs/Weapons/Western/Rifle/L85/armst_Rifle_L85_base.et | 6 | 1 | 4 | 1 | 1 | 0 |
| Prefabs/Weapons/Western/Rifle/SLR/armst_SLR_base.et | 6 | 1 | 4 | 1 | 1 | 0 |
| Prefabs/Weapons/Western/Rifle/Sig550/armst_Rifle_Sig550_base.et | 6 | 1 | 4 | 1 | 1 | 0 |
| Prefabs/Weapons/Western/Rifle/armst_Rifle_M16A2_base.et | 2 | 0 | 2 | 0 | 0 | 0 |
| Prefabs/Weapons/Western/Rifle/armst_VZ58P_base.et | 7 | 0 | 7 | 0 | 0 | 0 |
| Prefabs/Weapons/Western/Rifle/armst_VZ58V_base.et | 7 | 0 | 7 | 0 | 0 | 0 |

## Conclusion
- No local component qualifies for REMOVE_DEAD_LOCAL: every local component is either an override of an inherited instance, a variant hook (referenced by a child), a required gameplay/structural component, or an attachment interface.
- Disabled components are retained (disabled != dead; overrides have priority).
- Duplicate same-class instances are intentional (e.g., multiple AttachmentSlotComponent) or overrides.

LIVE_FILES_CHANGED: NONE
