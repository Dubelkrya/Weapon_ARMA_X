# PP / BP Creation Plan

STRICT READ-ONLY. No resources, GUIDs, parents, projectiles, configs or values were created.

## PP/BP convention discovery

- Literal PP/BP ammo variants were NOT found.
- `PP` search hits were weapon names (`PP91`), not an ammunition armour convention.
- No literal `BP` ammunition variants were found.
- No project-local two-variant PP/BP naming or config convention exists in the current addon.
- Closest existing two-variant local pattern (NOT declared equivalent):
  - `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP5_Ball.et`
  - `Prefabs/Weapons/Ammo/Russian/9x39/Ammo_9x39_SP6_Ball.et`
  - and 12ga shell variants.

## Unique calibers found

| Caliber | Region usage | Magazines | Current ammo source | Local replacement feasible now |
|---|---|---|---|---|
| 5x56 | Western | STANAG, HKG36, SIG550 families | external config `Configs/Weapons/Ammo/Ammo_556x45.conf` | REVIEW_REQUIRED |
| 762x51 | Western | HK3/L1A1 family | external parent `Magazine_762x51_M14_20rnd_Base.et`, no local AmmoConfig | REVIEW_REQUIRED |
| 9x19 | Western | M9 | external parent `Magazine_9x19_M9_15rnd_Base.et`, no local AmmoConfig | REVIEW_REQUIRED |
| 762x39 | Eastern (SOC94) | `Magazine_762x39_AKM_10rnd_Ball.et` (region Russian) | external Vz58 magazine base / external ammo config | REVIEW_REQUIRED |

## Creation template status

For every Western/Eastern caliber, the local evidence is insufficient to derive a safe PP/BP clone template:
- base ammo prefab bodies are not present locally;
- parent ammo resources are external/vanilla;
- local `Configs/Weapons/Ammo/` contains only `12g`, `763x25`, `9x39`;
- projectile/damage/penetration values for Western calibers are not locally serialized.

Therefore:
- BASE_RESOURCE_TO_CLONE_OR_INHERIT: NOT_LOCALLY_PROVABLE
- BASE_GUID / BASE_PATH: NOT_LOCALLY_PROVABLE
- PARENT_RESOURCE / PROJECTILE_RESOURCE / CONFIG_RESOURCE: EXTERNAL/VANILLA or NOT_PROVABLE
- FIELDS_THAT_DIFFER_BETWEEN_VARIANTS: NOT_PROVABLE from current local evidence

## Proposed target structure (not created)

- `Prefabs/Weapons/Ammo/Western/5x56/Ammo_5x56_PP.et` / `Ammo_5x56_BP.et`
- `Prefabs/Weapons/Ammo/Western/762x51/Ammo_762x51_PP.et` / `Ammo_762x51_BP.et`
- `Prefabs/Weapons/Ammo/Western/9x19/Ammo_9x19_PP.et` / `Ammo_9x19_BP.et`
- `Prefabs/Weapons/Ammo/Eastern/762x39/Ammo_762x39_PP.et` / `Ammo_762x39_BP.et`

No GUID, parent, projectile or config was invented.

## Magazine rebind plan (not executed)

Current representation:
- magazines use `MagazineComponent` with `AmmoConfig` and/or `AmmoMapping`;
- `AmmoMapping` contains numeric entries per magazine slot;
- the local magazines do not currently declare a PP/BP variant switch.

Consequences:
- one magazine currently references one ammo configuration/behaviour;
- two PP/BP variants cannot be bound simultaneously without an explicit switching mechanism;
- no such switching mechanism is present in the current local evidence.
- MAGAZINE_REBIND: REVIEW_REQUIRED

## Blocking issues found during inventory

- missing local magazine files: `Magazine_556x45_STANAG_30rnd_M196_Tracer.et`, `Magazine_556x45_STANAG_30rnd_M856_Tracer.et`;
- missing local magazine file: `Magazine_762x39_AKM_30rnd_Tracer.et`;
- misplacement: `Magazine_9x39_30rnd_val_SP5/SP6` are physically in `Russian/9x39/VSS/` while their recorded target is `Russian/9x39/VAL/`;
- parent identity mismatch observed in `Magazine_556x45_STANAG_30rnd_M193_Ball.et` parent GUID `FB5EB0F6D447E858` vs current local M193 GUID `FB5EB0F6D447E859`;
- these are read-only findings and were not repaired.
