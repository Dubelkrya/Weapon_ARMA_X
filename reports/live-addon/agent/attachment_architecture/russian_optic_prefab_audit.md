# Russian Optic Prefab & Type Plan (READ ONLY)

## Optics
| path | guid | outer type | role | compatibility | defaults | refs |
|---|---|---|---|---|---|---|
| Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et | C850A33226B8F9C1 | AttachmentOpticsDovetailAK | AK_NATIVE_OPTIC | AKM + 9A91/VAL/VSS/VSK94 (AttachmentOpticsDovetailAK) | armst_Rifle_AKM_full.et, armst_AK74M_full.et | armst_Rifle_AKM_full.et, armst_AK74M_full.et, armst_Optic_PSO1_ak.et (parent), armst_Optic_PSO1_DovetailRU.et (parent) |
| Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1_ak.et | F325FE2E3DDCDDAD | AttachmentOpticsDovetailAKSVD | DUPLICATE_CANDIDATE / LEGACY_ORPHAN (same model as PSO1, only outer type differs) | no weapon slot uses AttachmentOpticsDovetailAKSVD | none | none |
| armst_Optic_PSO1_DovetailRU.et | 5B318FB72398CB0A | AttachmentOpticsARMST_DovetailRU | GENERIC_RUSSIAN_DOVETAIL_OPTIC (project custom dovetail) | AEK971 (AttachmentOpticsARMST_DovetailRU) | none | none |
| Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et | 966B4E5523D2F166 | None | abstract base | - | none | HKG36 attachments |

## Types
| type | slots | optic prefabs | adapters | status |
|---|---|---|---|---|
| AttachmentOpticsDovetailAK | AKM 65AE4CB5E23C0F65, 9A91/VAL/VSS/VSK94 5F189C826D592450 | armst_Optic_PSO1.et | none | LIVE |
| AttachmentOpticsDovetailSVD | SVD 5472D211BFD78F81 (override), SOC94 65AE4CB5E23C0F63 (override) | none | none | TYPE_WITHOUT_OPTIC |
| AttachmentOpticsARMST_DovetailRU | AEK971 55349E9229B55E29 (override) | armst_Optic_PSO1_DovetailRU.et | none | LIVE |
| AttachmentOpticsDovetailAKSVD | none | armst_Optic_PSO1_ak.et | none | ORPHAN |
| AttachmentOpticsRIS1913 | none | none | none | UNUSED |

## Findings
- PSO1 (`armst_Optic_PSO1.et`, DovetailAK) = AK native optic; default on AKM_full and AK74M_full.
- PSO1_ak (`armst_Optic_PSO1_ak.et`, DovetailAKSVD) = same model, only outer type differs; no weapon slot -> ORPHAN/DUPLICATE candidate.
- PSO1_DovetailRU (`armst_Optic_PSO1_DovetailRU.et`, ARMST_DovetailRU) = AEK971 matching optic (exact type); not installed as default.
- SVD gap: no optic prefab with AttachmentOpticsDovetailSVD; SVD_NATIVE_OPTIC_EXISTS = UNRESOLVED.
- 9x39 share AttachmentOpticsDovetailAK with AKM -> INTENTIONAL_SHARED; frozen weapon overrides, do not unify further.
- Attachments all inherit PSO-1 model/sights from vanilla Optic_PSO1_base (SCR_2DPIPSightsComponent).
- No adapters exist; future native->adapter->AttachmentOpticsRIS1913 candidates listed.

LIVE_FILES_CHANGED: NONE
