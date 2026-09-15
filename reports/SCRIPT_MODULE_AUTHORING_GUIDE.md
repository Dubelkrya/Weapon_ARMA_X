# ARMST SCRIPT / MODULE AUTHORING GUIDE

## What the supplied scripts actually do

`Scripts.zip` contains compatibility/type declarations, not full weapon-behavior implementations.

The recurring Enfusion pattern is:

```c
class MyTypeClass {}
MyTypeClass MyTypeSource;

class MyType : ExistingBaseType
{
};
```

Bohemia's official `SampleMod_NewWeapon` uses the same pattern for a custom magazine well, muzzle attachment interface and RIS/optic attachment interfaces. Therefore this is treated as the canonical pattern for new compatibility types.

## Decision tree for a new weapon/module

1. Reuse an existing attachment or magazine-well type if it already represents the interface.
   - RIS1913 optics: use an existing `AttachmentOpticsRIS1913*` class.
   - AK/SVD dovetail: use the matching `AttachmentOpticsDovetail*` class.
   - Standard muzzle calibers: use the matching `AttachmentMuzzle*`.
   - Standard magazine families: use the matching `MagazineWell*`.

2. Create a new empty marker type only when compatibility must be distinct.
   Existing ARMST examples:
   - `AttachmentMuzzle9_39_armst : AttachmentMuzzle`
   - `AttachmentOpticsG36 : AttachmentOptics`
   - `MagazineWell763x25 : BaseMagazineWell`
   - `MagazineWell9x39 : BaseMagazineWell`

3. Wire the type in prefab serialization.

Weapon-side slot:
```text
AttachmentSlotComponent "{...}" {
  AttachmentSlot InventoryStorageSlot optics {
    AttachmentType AttachmentOpticsRIS1913 "{...}" {
    }
  }
}
```

Module-side compatibility:
```text
WeaponAttachmentAttributes "{...}" {
  AttachmentType AttachmentOpticsDovetailAK "{...}" {
  }
}
```

Magazine compatibility:
```text
MagazineWell MagazineWell763x25 "{...}" {
}
```

4. Sight mechanics are separate from attachment compatibility. `SightsComponent`, `SightsPosition`, `SightsRanges`, front/rear pivots and DOF values live in the `.et` prefab. The supplied ARMST scripts do not implement those mechanics.

## RIS1913 hierarchy

Bohemia's current hierarchy is:
- `AttachmentOpticsRIS1913 : AttachmentOptics`
- `AttachmentOpticsRIS1913Medium : AttachmentOpticsRIS1913`
- `AttachmentOpticsRIS1913Short : AttachmentOpticsRIS1913Medium`
- `AttachmentOpticsRIS1913VeryShort : AttachmentOpticsRIS1913Short`

The source comments associate the hierarchy with rail length / supported optic size. Use the narrowest existing type that correctly represents the rail; do not create a duplicate ARMST RIS class without a compatibility reason.

## ARMST findings

- `AttachmentMuzzle9_39_armst` is used by the 9A91 suppressor and 9A91/VSK94 muzzle slots.
- `AttachmentOpticsG36` is used by the G36 optic slot.
- `MagazineWell12g`, `MagazineWell763x25`, `MagazineWell9x39`, `MagazineWell9x39_9a91`, `MagazineWellAPB`, and `MagazineWellPP91` are active compatibility classes.
- `MagazineWellSR2` exists in script but has no usage in the supplied prefabs; SR-2 currently serializes `MagazineWellPP91`.
- `MagazineWell763x25_Class` uses an underscore in its registry-class name. Bohemia's sample convention is `<Type>Class`; preserve the existing source until a Workbench-safe rename is explicitly tested.
- PSO-1 uses existing dovetail classes. Groza uses existing RIS1913 classes. These do not need duplicate ARMST scripts.
- No per-weapon behavioral `.c` class exists in the supplied `Scripts.zip`; the supplied weapon mechanics are predominantly prefab/component/config driven.

## TT ammo now resolved

`Configs(1).zip` supplies `Ammo_763x25.conf` and maps it only to `Ammo_763x25_Ball.et`.

`Ammo_763x25_Ball.et` source values:
- InitSpeed: 430
- InitSpeedVariation: 15
- Mass: 0.00804
- AirDrag: 0.0000125
- Diameter: 9.1
- Length: 15.5
- PenetrationDepth: 20
- PenetrationDensity: 0.65
- PenetrationSpeed: 355
- primary kinetic DamageValue: inherited 50 from `Ammo_Bullet_Base`
- BallisticTableConfig: `AIBT_9x19_Ball_M882.conf`

These are source values from the supplied project snapshot, even where they look physically unusual. Do not silently replace them with real-world Tokarev values.

## Public references

- Bohemia optic/RIS types: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Weapon/Attachments/Attachments_optics.c
- Bohemia muzzle types: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Weapon/Attachments/Attachments_muzzle.c
- Bohemia magazine wells: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Weapon/MagazineWell.c
- Official SampleMod_NewWeapon scripts: https://github.com/BohemiaInteractive/Arma-Reforger-Samples/tree/main/SampleMod_NewWeapon/Scripts/Game/Weapon
