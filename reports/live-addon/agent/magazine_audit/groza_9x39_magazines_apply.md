# Groza 9x39 Magazines (applied)

## SP5
- path: Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP5.et
- guid: 77215B3A185D1EFD
- capacity: 20
- model: Groza_mag.xob
- well: MagazineWell9x39
- mapping_len: 20
- mapping_val: ['0']
- name: Groza 20rnd SP5 Magazine
## SP6
- path: Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP6.et
- guid: 168348351F5C3F54
- capacity: 20
- model: Groza_mag.xob
- well: MagazineWell9x39
- mapping_len: 20
- mapping_val: ['1']
- name: Groza 20rnd SP6 Magazine

## Groza weapon
- well: MagazineWell9x39 {55349E9229B55D96}
- default magazine: Prefabs/Weapons/Magazines/Russian/9x39/Groza/armst_Magazine_9x39_Groza_20rnd_SP5.et
- OLD_762x39_MAG_REFS_REMAINING: 0
- MAGAZINEWELL_VZ58_REFS_REMAINING: 0
- casing unchanged: True ; muzzle unchanged: True

## Validation
`
{
 "NEW_GUID_OWNER_COUNTS": {
  "77215B3A185D1EFD": 1,
  "168348351F5C3F54": 1
 },
 "GUID_COLLISIONS": 0,
 "DANGLING_REFS": 0,
 "OTHER_WEAPONS_CHANGED": 0
}
`

- Muzzle: KEEP / INTENTIONAL_SHARED_EFFECT
- Casing: OPEN_TECHNICAL_DEBT / Casing_762x39_PS.ptc

LIVE_FILES_CHANGED: 2 new Groza magazines (+metas); Groza well + default template changed
