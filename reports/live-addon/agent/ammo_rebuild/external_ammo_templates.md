# External Ammo Template Extraction (Read-Only)

Source of external evidence: `Weapon_ARMA_X/Imported/VanillaSources`.
No local resource was created, moved, or edited.

## 5.56x45 (Western)

- Magazines: `Magazine_556x45_STANAG_30rnd_Base/M193_Ball/M855_Ball`, `Magazine_556x45_HKG36`, `Magazine_556x45_SIG_550`
- Ammo config (external): `Configs/Weapons/Ammo/Ammo_556x45.conf` GUID `2689915ED0E00994`
- AmmoResourceArray: M855 `AC26AB660097633D`, tracer M856 `A0CEFA7FA41091F7`, M193 `9CE4CC890A2A574F`, tracer M196 `9F01DD8C46AD2618`
- Base projectile parent: `Prefabs/Weapons/Core/Ammo_Bullet_Base.et` GUID `67FED88E5085F63F`
- Variant fields:
  - M855: InitSpeed 930, Mass 0.00402, AirDrag 0.000005, Diameter 5.7, PenetrationDepth 4, PenetrationSpeed 675
  - M995 AP: parent M855; InitSpeed 1030, Mass 0.0034, AirDrag 0.0000035, PenetrationDepth 12, PenetrationSpeed 926, MushroomingDamageMultiplier 0
- PP/BP: two distinct templates exist externally (M855-class vs M995 AP), but M995 is not in the magazine AmmoResourceArray.
- Confidence: PARTIAL. Status: REVIEW_REQUIRED.

## 7.62x51 (Western)

- Magazines: `armst_Magazine_762x51_HK3_20_M80_Ball`, `L1A1_20_M61_AP`, `L1A1_20_M80_Ball`, `L1A1_30_M61_AP`, `L1A1_30_M80_Ball`
- Dependency: magazine -> external `Magazine_762x51_M14_20rnd_Base.et` -> config `Configs/Weapons/Ammo/Ammo_762x51.conf` GUID `533A763E304771D9`
- AmmoResourceArray: M80 `C14C5DE6F97F06F0`, tracer M62 `9CCBDD2ACB73FFA9`, AP M61 `9F39DD07E2860466`, M118 `B7DC0C3C3D1784C2`
- Variant fields:
  - M80: InitSpeed 856, Mass 0.00953, DamageValue 142, AirDrag 0.0000083, PenetrationDepth 4, PenetrationSpeed 654
  - M61 AP: parent M80; Mass 0.00975, AirDrag 0.0000082, Length 34.9, PenetrationDepth 10, PenetrationSpeed 780, Mushrooming/Tumbling 0
- PP/BP: two templates exist and are both present in the external config.
- Confidence: PROVEN for templates. Status: REVIEW_REQUIRED (PP/BP labeling and local config still undecided).

## 9x19 (Western)

- Magazine: `Magazine_9x19_M9_15rnd_Ball.et`
- Dependency: magazine -> external `Magazine_9x19_M9_15rnd_Base.et` -> config `Configs/Weapons/Ammo/Ammo_9x19.conf` GUID `BC69F995CEEF2196`
- AmmoResourceArray: M882 `9D290AA75ADA4618`, JHP `9DA944F4D6A611BA`
- Variants: M882 (base), AP 7N21 (external, not in config), AP 7N31, HP M1153
- PP/BP: AP exists externally but is not part of this magazine config.
- Confidence: PARTIAL. Status: REVIEW_REQUIRED.

## 7.62x39 (Eastern)

- Magazines: `Magazine_762x39_AKM_10rnd_Ball.et`, `Magazine_762x39_AKM_30rnd_Ball.et`
- Dependency: AKM/Vz58 magazine base (external) -> config `Configs/Weapons/Ammo/Ammo_762x39.conf` GUID `6810AE1CC6F1621D`
- AmmoResourceArray: 57N231 `2FBCA0A7CEDDE7B0`, tracer 57T231P `B9AB11A51D795EC5`
- Variants: 57N231 (base), AP 7N23 (external, not in config), API 57BZ231
- PP/BP: AP exists externally but is not part of this magazine config.
- Confidence: PARTIAL. Status: REVIEW_REQUIRED.

## Same-caliber variants discovered (external)

- 5.56x45: M193, M855, M855A1, M995 AP, Mk262 OTM, Mk318 OTM, M196/M856 tracers.
- 7.62x51: M80, M80A1, M118, M118LR, M61 AP, M993 AP, M62 tracer, M852, Mk316.
- 9x19: M882, M1152, JHP, M1153 HP, 7N21 AP, 7N31 AP.
- 7.62x39: 57N231, 57N231U, 57N231_89, 57T231P tracer, 7N23 AP, 57BZ231 API.

## Magazine rebind observation

Magazines reference an `AmmoConfig` whose `AmmoResourceArray` defines the selectable ammo resources. One magazine prefab references one config; no PP/BP switching mechanism is present in current local evidence. Separate magazine prefabs or a config change would be required later. Not modified here.
