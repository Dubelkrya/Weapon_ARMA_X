# ARMST ammunition AP/BP gameplay policy

> [!IMPORTANT]
> **Status: CURRENT GAMEPLAY DESIGN.** This defines the intended role model; individual caliber families remain unimplemented until authored and Workbench-tested.

Status: active gameplay design v1. This document defines the intended two-role ammunition split; it is not proof that every local prefab has already been converted.

## Naming

Project UI labels:

- `АП` — anti-personnel / soft-target role: higher direct damage, lower armor penetration.
- `БП` — armor-piercing / penetrator role: lower direct damage, higher armor penetration.

Machine-readable role names:

- `anti_personnel`
- `armor_piercing`

Important: `АП` here is a project gameplay label for anti-personnel ammunition. It is not the English abbreviation `AP = armor piercing` and must not be used as a claim about the real-world designation of a cartridge.

## Core balance rule

Each kinetic caliber family gets a shared caliber baseline. The AP/BP variants are derived from that baseline rather than being balanced independently.

Initial v1 multipliers:

| Role | Direct Damage | PenetrationDepth | Intent |
|---|---:|---:|---|
| АП / anti_personnel | ×1.25 | ×0.70 | Best against unarmored/soft targets |
| БП / armor_piercing | ×0.80 | ×1.50 | Best against armor/cover, lower flesh damage |

For v1, do **not** change `InitSpeed`, `Mass`, `AirDrag`, ballistic table, dispersion, recoil or weapon-side velocity coefficients only to create the AP/BP split. `PenetrationSpeed`, `PenetrationDensity`, mushrooming and tumbling values also remain source/default unless a later test proves they are needed for the gameplay separation.

This keeps the first implementation auditable: the role difference comes from only two gameplay variables — direct kinetic damage and penetration depth.

## Secondary tags are orthogonal

Tracer, incendiary, subsonic and precision are secondary properties, not replacements for AP/BP. Examples:

- `armor_piercing + tracer`
- `anti_personnel + precision`
- `anti_personnel + subsonic`

`AmmoMapping` still defines what is actually loaded in a magazine; filenames do not.

## Current caliber inventory and proposed role mapping

The table combines the current local ammunition/magazine snapshot with the supplied Configs snapshots. `existing` means a plausible source resource already exists. `custom` means ARMST needs a dedicated gameplay child/projectile or equivalent local resource.

| Caliber | АП / high-damage candidate | БП / high-penetration candidate | Status / note |
|---|---|---|---|
| 12 ga | Buckshot / soft-target shell | custom hard/penetrator slug | special shotgun implementation; pellet and slug architecture must be handled separately |
| 5.45×39 | `Ammo_545x39_Ball_7N6.et` | custom BP projectile | 7T3 tracer and 7U1 subsonic are secondary/special roles, not the BP base |
| 5.56×45 | `Ammo_556x45_Ball_M193.et` | `Ammo_556x45_Ball_M855.et` | natural existing gameplay pair |
| 7.62×39 | `Ammo_762x39_Ball_57N231.et` | custom BP projectile | tracer remains a secondary tag |
| 7.62×51 | `Ammo_762x51_Ball_M80.et` | `Ammo_762x51_AP_M61.et` | existing pair; M118 remains precision-oriented |
| 7.62×54R | `Ammo_762x54r_Ball_57N323S.et` or 7N1 precision child | `Ammo_762x54r_API_7BZ3.et` | existing penetrator candidate; 7N1 can carry AP+precision role |
| 7.63×25 | custom AP child from current Ball | current `Ammo_763x25_Ball.et` can serve as the higher-penetration baseline candidate | current ARMST projectile already has explicit penetration data; final role assignment needs Workbench test |
| 9×18 | `Ammo_9x18_Ball_57N181.et` | custom BP projectile | only one current allowed projectile in supplied config snapshot |
| 9×19 | `Ammo_9x19_HP_JHP.et` | `Ammo_9x19_Ball_M882.et` as gameplay BP candidate | M882 is not being claimed as a real armor-piercing cartridge; this is a gameplay role split |
| 9×39 | `Ammo_9x39_SP5_Ball.et` | `Ammo_9x39_SP6_Ball.et` | natural existing pair, but current source values do not yet enforce the desired damage-vs-penetration tradeoff |
| 12.7×99 | `Ammo_127x99_Ball_M33.et` | `Ammo_127x99_AP_M2.et` | M20 remains BP+tracer/incendiary secondary variant |
| 12.7×108 | custom AP/soft-target resource or separately approved existing round | existing API/APIT resources | current supplied config is penetrator-heavy; do not invent a soft-target mapping without a project resource |
| 14.5×114 | custom AP/soft-target resource or separately approved existing round | existing API/APIT resources | current supplied config is penetrator-heavy |
| 25×137 | `Ammo_25x137_HEIT_M792.et` | `Ammo_25x137_APDST_M791.et` | same gameplay axis, but HEI damage is explosive; keep explosive damage separate from kinetic damage |

`Ammo_Grenade_HE_VOG25` is excluded from this binary kinetic policy. Explosive grenades are balanced through their own damage/blast model.

## Existing source facts that must not be lost

- 9×19 config already allows both M882 Ball and JHP.
- 5.56×45 config already includes M193 and M855 families.
- 7.62×51 config already includes M80 and M61 AP.
- 7.62×54R config already includes Ball/7N1/API families.
- 9×39 has distinct SP5 and SP6 local projectiles.
- 7.63×25 is supplied by the later TT config snapshot and currently resolves to `Ammo_763x25_Ball.et`.

These source names are provenance. The AP/BP classification is an ARMST gameplay layer and must be stored separately from claims about real ammunition behavior.

## Authoring pattern

For calibers with a suitable existing projectile pair, prefer thin child/projectile overrides or explicit approved local resources rather than rewriting unrelated parent data.

For calibers that need a new role:

1. keep the existing projectile as the source/parent when its ballistics are appropriate;
2. create a dedicated local AP or BP child;
3. change only the gameplay fields required by this policy;
4. add the new resource to the caliber `AmmoResourceArray`;
5. create/adjust magazine variants through `AmmoMapping` rather than filename assumptions;
6. test one caliber family at a time in Workbench.

Do not globally rewrite every projectile in one pass.

## Validation order

First validation family should be 9×39 because SP5/SP6 already provide a clean two-resource test case. The second should be 5.56×45 because M193/M855 already exist in the same config. Only after those two prove the damage/penetration model should custom BP children be created for 5.45×39, 7.62×39, 9×18 and the remaining families.

The numeric multipliers above are starting gameplay targets, not final balance. Final values require armor/soft-target Workbench tests.