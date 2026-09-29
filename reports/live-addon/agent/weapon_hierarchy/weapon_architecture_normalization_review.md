# Weapon Architecture Normalization Review

Analysis only. Current structure is exclusive; future review category is separate.

## Exclusive Current Structure

| # | Family root | Primary class | Structural attributes | Future review | Factual reason |
|---:|---|---|---|---|---|
| 1 | `Prefabs/Weapons/Core/Grenade_Base.et` | `OTHER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | No other exclusive class applies. |
| 2 | `Prefabs/Weapons/Core/Weapon_Base.et` | `CORE_HIERARCHY` | CORE_CONNECTED, MULTI_LEVEL_LOCAL_CHAIN, SHARED_INTERMEDIATE_BASE | `REVIEWABLE` | Local Weapon_Base/Rifle_Base inheritance is already the project core. |
| 3 | `Prefabs/Weapons/Handguns/armst_Handgun_Knife_base.et` | `OTHER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | No other exclusive class applies. |
| 4 | `Prefabs/Weapons/Handguns/armst_M9.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 5 | `Prefabs/Weapons/Handguns/armst_PM.et` | `LOCAL_FAMILY_OVER_EXTERNAL` | EXTERNAL_BOUNDARY_FAMILY, MULTI_LEVEL_LOCAL_CHAIN, SHARED_INTERMEDIATE_BASE | `REVIEWABLE` | A local reusable base feeds multiple descendants while the family boundary is external. |
| 6 | `Prefabs/Weapons/MachineGuns/armst_PKM.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 7 | `Prefabs/Weapons/MachineGuns/armst_RPK74.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 8 | `Prefabs/Weapons/Rifles/9a91/armst_Rifle_9a91_base.et` | `OTHER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | No other exclusive class applies. |
| 9 | `Prefabs/Weapons/Rifles/AK74/armst_AK74.et` | `LOCAL_VARIANT_CHAIN` | EXTERNAL_BOUNDARY_FAMILY | `ALREADY_STRUCTURED` | Multiple local inheritance levels exist without a broad reusable shared base. |
| 10 | `Prefabs/Weapons/Rifles/AK74/armst_AK74N.et` | `LOCAL_FAMILY_OVER_EXTERNAL` | EXTERNAL_BOUNDARY_FAMILY, MULTI_LEVEL_LOCAL_CHAIN, SHARED_INTERMEDIATE_BASE | `REVIEWABLE` | A local reusable base feeds multiple descendants while the family boundary is external. |
| 11 | `Prefabs/Weapons/Rifles/AK74/armst_AKS74U.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 12 | `Prefabs/Weapons/Rifles/AK74/armst_AKS74UN.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 13 | `Prefabs/Weapons/Rifles/Shotgun/armst_shotgun_base.et` | `LOCAL_FAMILY_OVER_EXTERNAL` | EXTERNAL_BOUNDARY_FAMILY, MULTI_LEVEL_LOCAL_CHAIN, SHARED_INTERMEDIATE_BASE | `REVIEWABLE` | A local reusable base feeds multiple descendants while the family boundary is external. |
| 14 | `Prefabs/Weapons/Rifles/VAL/armst_Rifle_val_base.et` | `OTHER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | No other exclusive class applies. |
| 15 | `Prefabs/Weapons/Rifles/VSK94/armst_Rifle_VSK94_base.et` | `OTHER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | No other exclusive class applies. |
| 16 | `Prefabs/Weapons/Rifles/VSS/armst_Rifle_vss_base.et` | `OTHER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | No other exclusive class applies. |
| 17 | `Prefabs/Weapons/Rifles/armst_AEK971_test_v11.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 18 | `Prefabs/Weapons/Rifles/armst_Rifle_M16A2.et` | `LOCAL_FAMILY_OVER_EXTERNAL` | EXTERNAL_BOUNDARY_FAMILY, SHARED_INTERMEDIATE_BASE | `REVIEWABLE` | A local reusable base feeds multiple descendants while the family boundary is external. |
| 19 | `Prefabs/Weapons/Rifles/armst_Rifle_M16A2_carbine.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 20 | `Prefabs/Weapons/Rifles/armst_SVD.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 21 | `Prefabs/Weapons/Rifles/armst_VZ58P.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |
| 22 | `Prefabs/Weapons/Rifles/armst_VZ58V.et` | `SINGLE_WEAPON_EXTERNAL_WRAPPER` | EXTERNAL_BOUNDARY_FAMILY, SINGLE_LOCAL_NODE | `LEAVE_UNTIL_FUNCTIONAL_REASON` | Exactly one concrete local weapon sits at an external boundary. |

## Counts

- CORE_HIERARCHY: 1
- LOCAL_FAMILY_OVER_EXTERNAL: 4
- SINGLE_WEAPON_EXTERNAL_WRAPPER: 10
- LOCAL_VARIANT_CHAIN: 1
- OTHER: 6
- PRIMARY_CLASS_TOTAL: 22

## Future Review Sets

- ALREADY_STRUCTURED: 1
- REVIEWABLE: 5
- LEAVE_UNTIL_FUNCTIONAL_REASON: 16
- FUTURE_REVIEW_ASSIGNMENTS: 22

## Scope

- Graph facts unchanged: 51 nodes, 32 leaves, 11 local bases, 29 local edges, 7 shared bases.
- `Magazine_Base.et` remains absent.
- No resource edits or migration actions are authorized.
