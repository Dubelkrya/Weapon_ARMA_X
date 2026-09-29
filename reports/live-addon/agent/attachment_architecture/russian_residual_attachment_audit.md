# Russian Residual Attachment / Action Context Audit (READ ONLY)

## Prefabs/Weapons/Russian/Handguns/PP_19/armst_PP91_base.et
TOTAL_LOCAL_SLOTS: 0
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Handguns/Pm/armst_PM_base.et
TOTAL_LOCAL_SLOTS: 0
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Handguns/Sr_2/armst_SR_2_base.et
TOTAL_LOCAL_SLOTS: 0
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Handguns/TT/armst_TT_base.et
TOTAL_LOCAL_SLOTS: 0
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Handguns/armst_APB/armst_APB_base.et
TOTAL_LOCAL_SLOTS: 0
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et
TOTAL_LOCAL_SLOTS: 2
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 5F189C826D592450 | BayonetSlot | AttachmentOpticsDovetailAK | 1 | slot_optics | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
| 4E2B66CBA589F625 | Muzzle | AttachmentMuzzle9_39_armst | 1 | barrel_muzzle | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et
TOTAL_LOCAL_SLOTS: 1
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 4E2B66CBA589F625 | None | None | 0 | None | None | LOCAL_ADDITION | ['Prefabs/Weapons/Russian/Rifle/AK74/armst_AK105.et'] | KEEP_VARIANT_HOOK |
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_base.et
TOTAL_LOCAL_SLOTS: 4
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 65AE4CB5E23C0F63 | None | AttachmentStockVz58 | 1 | slot_barrel_muzzle | None | LOCAL_ADDITION | ['Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et', 'Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKMS.et', 'Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_VPO136.et', 'Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et'] | KEEP_VARIANT_HOOK |
| 65AE4CB5E23C0F65 | Stock | AttachmentOpticsDovetailAK | 1 | slot_optics | None | LOCAL_ADDITION | ['Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et', 'Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_full.et', 'Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et'] | KEEP_NATIVE_INTERFACE |
| 673A7B215304A28B | GP | AttachmentUnderBarrelGP25 | 1 | barrel_chamber | None | LOCAL_ADDITION | ['Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et', 'Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_full.et', 'Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et'] | KEEP_NATIVE_INTERFACE |
| 65AE4CB5E23C0F2C | Muzzle | AttachmentMuzzle762_39 | 1 | barrel_muzzle | None | LOCAL_ADDITION | ['Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM.et', 'Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et'] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 5
| instance | name | pivot | origin | owner | class |
|---|---|---|---|---|---|
| 5086F9ADF588DCA4 | None | None | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 5956E32BAAADE657 | None | None | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 5A1E58F7B04F9BE5 | None | slot_magazine | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 5A1E58F7AED270D4 | None | w_fire_mode | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 65AE4CB5E23C0CE9 | bayonet | slot_barrel_muzzle | LOCAL_ADDITION | slot | KEEP_REQUIRED |

## Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et
TOTAL_LOCAL_SLOTS: 3
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 55349E9229B55E29 | sights | AttachmentOpticsARMST_DovetailRU | 1 | None | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
| 5F189C826D592450 | BayonetSlot | None | 1 | None | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
| 4E2B66CBA589F625 | None | None | 0 | None | None | LOCAL_ADDITION | [] | REVIEW_REQUIRED |
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et
TOTAL_LOCAL_SLOTS: 1
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 4E2B66CBA589F625 | suppressor | None | 1 | slot_barrel_muzzle | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 4
| instance | name | pivot | origin | owner | class |
|---|---|---|---|---|---|
| 5086F9ADF588DCA4 | None | None | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 5956E32BAAADE657 | None | None | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 5A1E58F7B04F9BE5 | None | slot_magazine | LOCAL_ADDITION | core | KEEP_REQUIRED |
| 5A1E58F7AED270D4 | None | None | LOCAL_ADDITION | core | KEEP_REQUIRED |

## Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et
TOTAL_LOCAL_SLOTS: 4
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 65AE4CB5E23C0F63 | None | AttachmentOpticsDovetailSVD | 1 | None | None | LOCAL_OVERRIDE | [] | KEEP_OVERRIDE |
| 65AE4CB5E23C0F65 | Stock | None | 1 | slot_optic | None | LOCAL_OVERRIDE | [] | KEEP_OVERRIDE |
| 673A7B215304A28B | None | None | 0 | None | None | LOCAL_OVERRIDE | [] | KEEP_OVERRIDE |
| 65AE4CB5E23C0F2C | None | None | 0 | None | None | LOCAL_OVERRIDE | [] | KEEP_OVERRIDE |
ACTION CONTEXTS: 1
| instance | name | pivot | origin | owner | class |
|---|---|---|---|---|---|
| 69F2A461E52826BA | None | slot_optics | LOCAL_ADDITION | core | KEEP_REQUIRED |

## Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et
TOTAL_LOCAL_SLOTS: 1
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 5472D211BFD78F81 | None | AttachmentOpticsDovetailAK | 1 | None | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 0

## Prefabs/Weapons/Russian/Rifle/VAL/armst_Rifle_val_base.et
TOTAL_LOCAL_SLOTS: 2
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 5F189C826D592450 | BayonetSlot | AttachmentOpticsDovetailAK | 1 | slot_optics | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
| 4E2B66CBA589F625 | Muzzle | None | 0 | None | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 1
| instance | name | pivot | origin | owner | class |
|---|---|---|---|---|---|
| 69EE615D4B97703C | Optic | slot_optics | LOCAL_ADDITION | slot | KEEP_REQUIRED |

## Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et
TOTAL_LOCAL_SLOTS: 2
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 5F189C826D592450 | BayonetSlot | AttachmentOpticsDovetailAK | 1 | slot_optics | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
| 4E2B66CBA589F625 | Muzzle | AttachmentMuzzle9_39_armst | 1 | barrel_muzzle | {E10F09941AF1E123}Prefabs/Weapons/Attachments/Muzzle/armst_Suppressor_9a91.et | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 1
| instance | name | pivot | origin | owner | class |
|---|---|---|---|---|---|
| 69EE615C65C7D397 | optic | slot_optics | LOCAL_ADDITION | slot | KEEP_REQUIRED |

## Prefabs/Weapons/Russian/Rifle/VSS/armst_Rifle_vss_base.et
TOTAL_LOCAL_SLOTS: 2
| instance | slot | type | en | pivot | default | origin | descendants | class |
|---|---|---|---|---|---|---|---|---|
| 5F189C826D592450 | BayonetSlot | AttachmentOpticsDovetailAK | 1 | slot_optics | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
| 4E2B66CBA589F625 | Muzzle | None | 0 | None | None | LOCAL_ADDITION | [] | KEEP_NATIVE_INTERFACE |
ACTION CONTEXTS: 0

SAFE_CLEANUP_QUEUE: 0

LIVE_FILES_CHANGED: NONE

## Notes
- PKM / RPK74: 0 local AttachmentSlotComponent and 0 contexts => NO_LOCAL_ATTACHMENT_CLEANUP.
- Review item: AEK971 instance 4E2B66CBA589F625 (unnamed, type None, Enabled 0, no pivot, no descendants) => REVIEW_REQUIRED (same instance is the disabled Muzzle-family placeholder; AK74_base keeps it as KEEP_VARIANT_HOOK via AK105).
- Mislabeled native interfaces: 9A91/VAL/VSK94/VSS slot named BayonetSlot actually carries AttachmentOpticsDovetailAK with pivot slot_optics => dovetail optic mount (VALID_NATIVE_DOVETAIL, name misleading).
- AKM slot 65AE4CB5E23C0F65 named Stock carries AttachmentOpticsDovetailAK => dovetail optic interface (native).
- VAL/VSS muzzle slot 4E2B66CBA589F625 is disabled/untyped (MuzzleComponent architecture, out of scope) => KEEP.
- Groza: 1 slot (muzzle) + 4 contexts (magazine + 3 unnamed); no RIS, no iron-sight slots, no stale named contexts.
- SOC94 contexts: 1 local context tied to slot_optics => KEEP_REQUIRED (overrides frozen).
