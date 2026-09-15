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

## Source inventory vs active gameplay policy

The supplied prefab/script snapshots may still serialize built-in classes such as `AttachmentOpticsDovetailAK`, `AttachmentOpticsDovetailAKSVD` and `AttachmentOpticsDovetailSVD`. Those entries remain useful as **source inventory / migration input**.

They are not the active ARMST gameplay policy for approved Russian/Soviet side-rail optics.

Active policy is defined by:

- `indexes/script_reference/optic_compatibility_policy_v2.json`
- `reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md`

Approved Russian/Soviet side-rail weapons and optics use the gameplay family:

`DovetailRU` → `AttachmentOpticsARMST_DovetailRU`

Real-world compatibility remains separate research data and may be narrower than gameplay compatibility.

## Decision tree for a new weapon/module

1. Reuse an existing type when it already represents the intended **active gameplay interface**.
   - RIS1913/Picatinny: use the appropriate `AttachmentOpticsRIS1913*` engine class.
   - Approved ARMST Russian/Soviet side rail: use `AttachmentOpticsARMST_DovetailRU`.
   - G36 proprietary interface: keep `AttachmentOpticsG36`.
   - Standard muzzle calibers: use the matching `AttachmentMuzzle*` type.
   - Standard magazine families: use the matching `MagazineWell*` type.

2. Create a new empty marker type only when compatibility must be distinct.
   Existing ARMST examples include:
   - `AttachmentMuzzle9_39_armst : AttachmentMuzzle`
   - `AttachmentOpticsG36 : AttachmentOptics`
   - `AttachmentOpticsARMST_DovetailRU : AttachmentOptics`
   - `MagazineWell763x25 : BaseMagazineWell`
   - `MagazineWell9x39 : BaseMagazineWell`

3. Wire the type in prefab serialization using exact inherited instance IDs.

Weapon-side slot example:
```text
AttachmentSlotComponent "{INHERITED_SLOT_ID}" {
 AttachmentType AttachmentOpticsARMST_DovetailRU "{INHERITED_ATTACHMENT_TYPE_ID}" {
 }
}
```

Module-side compatibility example:
```text
WeaponAttachmentAttributes "{INHERITED_ATTRIBUTES_ID}" {
 AttachmentType AttachmentOpticsARMST_DovetailRU "{INHERITED_ATTACHMENT_TYPE_ID}" {
 }
}
```

Magazine compatibility example:
```text
MagazineWell MagazineWell763x25 "{...}" {
}
```

4. Sight mechanics are separate from attachment compatibility. `SightsComponent`, `SightsPosition`, `SightsRanges`, front/rear pivots and DOF values live in the `.et` prefab. Compatibility marker scripts do not implement those mechanics.

## Two-sided attachment compatibility

Workbench validation confirmed that changing only the weapon slot is insufficient.

The engine compatibility contract is:

- weapon side requests a type via `AttachmentSlotComponent -> AttachmentType`;
- module side declares a type via `WeaponAttachmentAttributes -> AttachmentType`;
- module type must equal or inherit the slot-required type.

For a project compatibility migration, update both sides. A visible slot is not proof that the module can attach.

Prefer a thin child optic/module prefab when the only intended difference from a source asset is compatibility. Do not rewrite model, reticle, zeroing, animation or snap geometry without a separate reason.

## DovetailRU marker type

Canonical script:

```c
class AttachmentOpticsARMST_DovetailRUClass
{
};

AttachmentOpticsARMST_DovetailRUClass AttachmentOpticsARMST_DovetailRUSource;

class AttachmentOpticsARMST_DovetailRU : AttachmentOptics
{
};
```

This class defines compatibility only. It does not implement magnification, ADS, zeroing or pivot behavior.

## DovetailRU geometry rule

Compatibility and physical positioning are separate systems.

When migrating an inherited Russian side-rail slot to `AttachmentOpticsARMST_DovetailRU`:

- preserve the inherited `AttachmentSlotComponent` instance ID;
- preserve the inherited `AttachmentType` object instance ID;
- do not rewrite `PivotID`, `ChildPivotID`, offsets, angles, helper prefabs or snap geometry unless geometry itself needs correction.

The AEK-971 / PSO-1 validation proved this pattern: weapon and thin child optic shared `AttachmentOpticsARMST_DovetailRU` while physical slot/snap geometry remained inherited, and the optic mounted successfully in Workbench.

## RIS1913 hierarchy

Bohemia's current hierarchy is:
- `AttachmentOpticsRIS1913 : AttachmentOptics`
- `AttachmentOpticsRIS1913Medium : AttachmentOpticsRIS1913`
- `AttachmentOpticsRIS1913Short : AttachmentOpticsRIS1913Medium`
- `AttachmentOpticsRIS1913VeryShort : AttachmentOpticsRIS1913Short`

The source comments associate the hierarchy with rail length / supported optic size. Use the narrowest existing type that correctly represents the rail; do not create a duplicate ARMST RIS class without a compatibility reason.

## ARMST findings

- `AttachmentMuzzle9_39_armst` is used by the 9A91 suppressor and 9A91/VSK94 muzzle slots in the supplied snapshot.
- `AttachmentOpticsG36` is used by the G36 optic slot and remains separate from DovetailRU.
- `MagazineWell12g`, `MagazineWell763x25`, `MagazineWell9x39`, `MagazineWell9x39_9a91`, `MagazineWellAPB`, and `MagazineWellPP91` are active compatibility classes in the supplied snapshot.
- `MagazineWellSR2` exists in script but has no usage in the supplied prefabs; SR-2 currently serializes `MagazineWellPP91`.
- `MagazineWell763x25_Class` uses an underscore in its registry-class name. Bohemia's sample convention is `<Type>Class`; preserve the existing source until a Workbench-safe rename is explicitly tested.
- PSO source prefabs in the supplied snapshot use built-in dovetail classes. Under active gameplay policy, do not edit the original source merely to migrate gameplay compatibility; prefer a thin ARMST child using `AttachmentOpticsARMST_DovetailRU`.
- Groza uses existing RIS1913 classes and must not be auto-converted to DovetailRU.
- No per-weapon behavioral `.c` class exists in the supplied `Scripts.zip`; supplied weapon mechanics are predominantly prefab/component/config driven.

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
