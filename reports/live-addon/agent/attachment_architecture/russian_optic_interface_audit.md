# Russian Optic Interface Target Architecture (derived, READ ONLY)

Patterns: A=NO_OPTIC_ATTACHMENT_INTERFACE, B=DIRECT_NATIVE_OPTIC_INTERFACE, C=DIRECT_STOCK_PICATINNY, D=NATIVE->OPTIONAL_RIS_ADAPTER, E=KEEP_OVERRIDE, F=REVIEW_REQUIRED

| weapon | current | type | origin | matching optics | pattern | notes |
|---|---|---|---|---|---|---|
| Prefabs/Weapons/Russian/Rifle/AK74/armst_AK74_base.et | none | None | - | none | A | no local optic slot; only disabled muzzle placeholder |
| Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_base.et | Stock | AttachmentOpticsDovetailAK | LOCAL_ADDITION | Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | B | native AK side dovetail; used by AKM/AKMS/VPO136 + SOC94 override; RIS optics would need adapter (pattern D later) |
| Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et | sights | AttachmentOpticsARMST_DovetailRU | LOCAL_OVERRIDE | armst_Optic_PSO1_DovetailRU.et | E | override of vanilla AK74N sights slot (vanilla type AttachmentOpticsDovetailAK); frozen; AEK971_OPTIC_INTERFACE=KEEP_CURRENT |
| Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et | none | None | - | none | A | no optic slot; project decided no generic mount; GROZA_OPTIC_INTERFACE=NONE |
| Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et | none/Stock | AttachmentOpticsDovetailSVD | LOCAL_OVERRIDE | none | E | overrides frozen; 65AE4CB5E23C0F63 repurposes AKM stock instance as SVD dovetail (conceptual oddity, INFO only) |
| Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et | Dovetail | AttachmentOpticsDovetailSVD | LOCAL_OVERRIDE | none | E | override of vanilla SVD dovetail; distinct native mount, no unification; no matching optic prefab yet (NO_ATTACHMENT_EXISTS_YET) |
| Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et | BayonetSlot | AttachmentOpticsDovetailAK | LOCAL_OVERRIDE | Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | E | override of vanilla AK74 BayonetSlot (vanilla type AttachmentBayonet6Kh4) repurposed to dovetail optic; SlotName misleading; frozen |
| Prefabs/Weapons/Russian/Rifle/VAL/armst_Rifle_val_base.et | BayonetSlot | AttachmentOpticsDovetailAK | LOCAL_OVERRIDE | Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | E | same as 9A91; live context Optic(slot_optics) |
| Prefabs/Weapons/Russian/Rifle/VSS/armst_Rifle_vss_base.et | BayonetSlot | AttachmentOpticsDovetailAK | LOCAL_OVERRIDE | Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | E | same as 9A91 |
| Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et | BayonetSlot | AttachmentOpticsDovetailAK | LOCAL_OVERRIDE | Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | E | same as 9A91; live context optic(slot_optics) |
| Prefabs/Weapons/Russian/MachineGuns/armst_PKM_base.et | none | None | - | none | A | 0 local slots; no local optic interface |
| Prefabs/Weapons/Russian/MachineGuns/armst_RPK74_base.et | none | None | - | none | A | 0 local slots; no local optic interface |

## Optic type matrix
| type | weapons | optic prefabs | defaults |
|---|---|---|---|
| AttachmentOpticsDovetailAK | Prefabs/Weapons/Russian/Rifle/9a91/armst_Rifle_9a91_base.et, Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_base.et, Prefabs/Weapons/Russian/Rifle/SVD/armst_Rifle_SVD_base.et, Prefabs/Weapons/Russian/Rifle/VAL/armst_Rifle_val_base.et, Prefabs/Weapons/Russian/Rifle/VSK94/armst_Rifle_VSK94_base.et, Prefabs/Weapons/Russian/Rifle/VSS/armst_Rifle_vss_base.et | Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | none |
| AttachmentOpticsARMST_DovetailRU | Prefabs/Weapons/Russian/Rifle/Aek971/armst_Rifle_AEK971_base.et | armst_Optic_PSO1_DovetailRU.et | none |
| AttachmentOpticsDovetailSVD | Prefabs/Weapons/Russian/Rifle/SOC94/armst_Rifle_SOC94_base.et | none | none |

## Optic prefabs
| path | outer type | child slots |
|---|---|---|
| Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | AttachmentOpticsDovetailAK | 0 |
| Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1_ak.et | AttachmentOpticsDovetailAKSVD | 0 |
| Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Optic.et | AttachmentOpticsG36 | 0 |
| Prefabs/Weapons/Attachments/Optics/HKG36/armst_HKG36_CarryHandle_Picatinny.et | AttachmentOpticsG36 | 1 |
| armst_Optic_PSO1_DovetailRU.et | AttachmentOpticsARMST_DovetailRU | 0 |

## Adapters / unused types
- Adapter prefabs found: 0.
- `AttachmentOpticsRIS1913`: no Russian usage (Groza RIS removed); no adapter prefab.
- `AttachmentOpticsDovetailAKSVD`: orphan type (only `armst_Optic_PSO1_ak.et` exposes it; no slot uses it).

LIVE_FILES_CHANGED: NONE
