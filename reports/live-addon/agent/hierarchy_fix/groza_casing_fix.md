# Groza Casing Particle Fix

- resource: `Prefabs/Weapons/Russian/Rifle/Groza/armst_Groza_base.et`
- GUID: 903C7920F00AB654
- field: `MuzzleComponent {CA6BE4D6B867541F} > CaseEjectingEffectComponent {5122AAD190FCA21D} > ParticleEffect`
- casing before: `{6A0F068A792EA37C}Particles/Weapon/Casing_762x51.ptc`
- casing after: `{A89D3276591C9F57}Particles/Weapon/Casing_762x39_PS.ptc`

## Validation
```
{
 "template_unchanged": true,
 "GUID_CHANGES": 0,
 "PATH_CHANGES": 0,
 "META_UNCHANGED": true,
 "braces_balanced": true,
 "OTHER_GAMEPLAY_CHANGES": 0,
 "OTHER_WEAPONS_CHANGED": 0,
 "checks": {
  "casing_762x51_remaining": false,
  "muzzle_ak74_present": true,
  "well_present": true
 }
}
```
