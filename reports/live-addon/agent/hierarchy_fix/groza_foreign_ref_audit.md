# Groza Foreign Ref Provenance Audit (READ ONLY)

## Groza state
- path: `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
- GUID: 903C7920F00AB654
- model: {277CC12370C4BCF0}Assets/Weapons_RUS/Groza/GROZA.xob
- parent: `{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et`
- MagazineWell: `MagazineWellVZ58_762 {5464E0EAAF7815B4}` in MuzzleComponent {CA6BE4D6B867541F}
- magazine template: `armst_Magazine_762x39_AKM_30rnd_Ball.et`
- muzzle effect: `Muzzle_AK74.ptc`; casing: `Casing_762x51.ptc`

## Magazine well provenance
- Prefabs/Weapons/Rifles/VZ58/Rifle_VZ58_base.et (VANILLA)
- Prefabs/Weapons/Magazines/Vz58/Magazine_762x39_Vz58_30rnd_Base.et (VANILLA)
- Prefabs/Weapons/Russian/Rifle/AKM/armst_Rifle_AKM_base.et (ARMST AKM)
- Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et (Groza)
- compatibility: Groza magazine template armst_Magazine_762x39_AKM_30rnd_Ball.et parents to Prefabs/Weapons/Magazines/Vz58/Magazine_762x39_Vz58_30rnd_Base.et which declares the same MagazineWellVZ58_762 well -> functional match.
- classification: **INTENTIONAL_SHARED_RESOURCE**

## Muzzle particle provenance
- Groza is the ONLY live user of Particles/Weapon/Muzzle_AK74.ptc.
- ARMST AKM base and vanilla VZ58 base use Muzzle_VZ58.ptc + Smoke_VZ58.ptc + Casing_762x39_PS.ptc with the same MagazineWellVZ58_762 well Groza uses.
- classification: **FOREIGN_LEGACY_ERROR**

## Users
- `Particles/Weapon/Muzzle_AK74.ptc`: armst_Groza_base.et
- `Particles/Weapon/Muzzle_VZ58.ptc`: armst_Rifle_AKM_base.et, Rifle_VZ58_base.et (VANILLA)
- `Particles/Weapon/Smoke_VZ58.ptc`: armst_Rifle_AKM_base.et, Rifle_VZ58_base.et (VANILLA)
- `Particles/Weapon/Casing_762x39_PS.ptc`: armst_Rifle_AKM_base.et, Rifle_VZ58_base.et (VANILLA)

## Replacement candidates
| current | candidate | confidence | evidence |
|---|---|---|---|
| `{6FC79968CA7F6FD2}Particles/Weapon/Muzzle_AK74.ptc` | `{0E66192FC96CDFB7}Particles/Weapon/Muzzle_VZ58.ptc` | HIGH | Groza shares VZ58_762 well and VZ58-derived AKM magazine; entire 7.62x39 family uses Muzzle_VZ58. No Groza-specific muzzle particle exists. |
| `{6A0F068A792EA37C}Particles/Weapon/Casing_762x51.ptc (supplementary)` | `{A89D3276591C9F57}Particles/Weapon/Casing_762x39_PS.ptc` | HIGH | Groza is 7.62x39, not 7.62x51. |

## Decision
- MagazineWellVZ58_762: INTENTIONAL_SHARED_RESOURCE (no replacement).
- Muzzle_AK74.ptc: FOREIGN_LEGACY_ERROR (family replacement `Muzzle_VZ58.ptc`, not applied).
- No changes applied (read-only).

LIVE_FILES_CHANGED: NONE
