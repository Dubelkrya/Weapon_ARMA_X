# ARMST prefab authoring reference

> [!IMPORTANT]
> **Status: CURRENT AUTHORING GUIDE / WORKBENCH-BACKED.** Live addon and newer Workbench evidence still outrank this document when they conflict.

Generated from `Weapons.zip` on 2026-09-15. The local addon is the source of truth.

## What is indexed

- 702 `.et/.conf` source files parsed.
- 162 weapon-like prefab/config entries indexed for authoring in the Excel `Prefab индекс` sheet.
- Provenance is kept per resolved value (`defined_in` / inherited source).

## Mandatory authoring rules

1. Follow the inheritance chain before adding anything. A child prefab should contain **only differences** from its parent.
2. Override an inherited object with the **same instance ID**. Do not create a second `ItemPhysicalAttributes`, recoil modifier, sights object, fire mode, etc.
3. Do not repeat values already correct in the parent. Example: all handguns inherit `Single 500 RPM` from `Handgun_Base.et`; TT does not need its own fire-mode block unless the rate actually changes.
4. Separate weapon handling from projectile lethality. Weight, dispersion, sights, fire modes and weapon recoil belong to the weapon prefab; damage/penetration/ballistics belong to ammo/projectile resources.
5. If the archive does not prove a value, keep it unknown. Filename numbers are not evidence.
6. Preserve inherited instance IDs and object nesting. A syntactically valid block inserted at the wrong hierarchy level can still produce wrong Workbench data or crash the editor.
7. Structural validation and Workbench/runtime validation are separate stages. Balanced braces and valid text are necessary but do not prove that Enfusion resolves the prefab correctly.

## Safe workflow for creating a new weapon prefab

Use this workflow whenever a weapon is built from an existing working family/base.

1. **Start from a known-good prefab.** Make the first test child as close to a literal clone as possible. Change only identity/name if needed.
2. Open that minimal clone in Workbench before adding gameplay changes. If it does not open, stop: the problem is structural/resource-related, not weapon balance.
3. Add **one functional change at a time** and reopen the prefab after each step. Recommended order:
   - identity/name;
   - fire rate on an existing fire mode;
   - additional fire mode, if required;
   - recoil/handling;
   - dispersion / weapon-side velocity coefficient;
   - magazine/attachment compatibility;
   - sights/optics geometry;
   - visual/animation-specific differences.
4. If Workbench starts crashing or data appears in the wrong UI field, return to the last known-good revision and inspect only the last added block.
5. Do not combine several unverified overrides in the first version. A large one-shot prefab makes it difficult to identify which component/path is invalid.
6. After every successful step, treat that prefab as the new control point for the next change.

The purpose of this staged process is not merely debugging convenience. It protects inherited object identity and reveals when a correct-looking text block was serialized at the wrong level.

## Fire modes: inherited override vs new mode

This distinction is mandatory.

### Overriding an existing inherited fire mode

If `Auto`, `Single`, `Safe`, or another mode already exists in the parent, override the inherited `BaseFireMode` **by the existing instance ID only**.

Correct pattern:

```text
FireModes {
 BaseFireMode "{INHERITED_AUTO_INSTANCE_ID}" {
  RoundsPerMinute 900
 }
}
```

Do **not** reconnect the original `.conf` resource to an already inherited object:

```text
// WRONG for an inherited mode
BaseFireMode "{INHERITED_AUTO_INSTANCE_ID}" : "{GUID}.../FireMode_Auto.conf" {
 RoundsPerMinute 900
}
```

Re-attaching a config to an inherited fire-mode object can cause Workbench to serialize/display it as a separate or malformed element instead of a clean override.

### Adding a genuinely new fire mode

A new mode that does not exist in the parent is different. It needs:

- a new unique instance ID;
- the appropriate fire-mode config resource;
- only the local differences from that config.

Example shape:

```text
FireModes {
 BaseFireMode "{NEW_INSTANCE_ID}" : "{GUID}Prefabs/Weapons/Core/Configs/FireModes/FireMode_Burst.conf" {
  BurstType Interruptable
  RoundsPerMinute 900
 }
}
```

For a burst mode, prefer the engine/config default for `MaxBurst` when it already represents the desired burst length. Override `MaxBurst` only when the weapon actually differs from the referenced config.

### Safe is not a firing mode for design counting

Workbench may show `Safe`, `Single`, `Auto`, `Burst`, etc. in the same `FireModes` collection. For gameplay/design documentation, distinguish the safety state from modes that actually fire rounds.

### Cyclic RPM and single fire

A real-world cyclic rate primarily describes the weapon's automatic operating cycle. Do not automatically force the same `RoundsPerMinute` override onto `Single` just because `Auto` changes. If the inherited single-shot mode already behaves correctly, leave it inherited unless there is a demonstrated reason to change it.

## Recoil authoring: treat sub-blocks separately

Do not treat recoil as one scalar. The Workbench recoil modifier exposes multiple `RecoilData` sub-blocks, including at least:

- `LinearData`
- `AngularData`
- `TurnOffsetData`

Each block has its own curves, magnitudes, min/max ranges and scales.

### General rule

Change only the part of recoil that corresponds to the intended gameplay effect, and validate it in Workbench immediately.

For example, if the design goal is lower shot impulse / muzzle rise while preserving the parent weapon's return behaviour, first test overrides to `LinearData` and/or `AngularData` while leaving `TurnOffsetData` inherited.

Project Workbench testing showed that changing `TurnOffsetData` can noticeably change the weapon's return/settling behaviour. Therefore:

- do not reduce `TurnOffsetData` merely because the weapon should have less recoil;
- do not assume that scaling all `Curve Magnitudes` produces only a smaller kick;
- keep return behaviour separate from initial kick/rotation unless the design explicitly requires a different return characteristic.

### Minimal recoil override pattern

```text
WeaponAimModifiers {
 RecoilWeaponAimModifier "{INHERITED_RECOIL_MODIFIER_ID}" {
  LinearData RecoilData "{INHERITED_LINEAR_DATA_ID}" {
   "Curve Magnitudes" ...
  }
  AngularData RecoilData "{INHERITED_ANGULAR_DATA_ID}" {
   "Curve Magnitudes" ...
  }
 }
}
```

If `TurnOffsetData` does not need to change, omit it completely from the child prefab.

The exact values above are weapon/balance data, not a universal template. The universal rule is the override shape and preservation of inherited IDs.

## Attachment compatibility: migrate both sides

Workbench testing confirmed that attachment compatibility is a two-sided contract. Changing only the weapon slot type is not sufficient.

The weapon side requests a compatibility type through `AttachmentSlotComponent -> AttachmentType`. The module/optic side declares its compatibility through `WeaponAttachmentAttributes -> AttachmentType`. The module type must equal or inherit the type required by the weapon slot.

Therefore, when introducing a new project compatibility family:

1. Add the marker class in script first and allow Workbench to recompile scripts.
2. On the weapon, override only the inherited optic/attachment slot and replace only its `AttachmentType`. Preserve the inherited `AttachmentSlotComponent` ID and inherited `AttachmentType` object ID.
3. Do not rewrite physical placement data merely to change compatibility. Keep inherited pivots, `Pivot ID`, `Child Pivot ID`, offsets, angles, helper prefabs and snap geometry unless there is a separate geometry reason to change them.
4. On the optic/module, use the same compatibility family in `WeaponAttachmentAttributes -> AttachmentType`.
5. Prefer a thin child prefab for the compatible optic/module instead of modifying the original source prefab. The child should inherit the model, optics, zeroing, animations and geometry and override only the compatibility type when that is the only difference.
6. Test the pair in Workbench by actually mounting the child module on the weapon. A visible slot alone does not prove compatibility.

Weapon-side shape:

```text
AttachmentSlotComponent "{INHERITED_SLOT_ID}" {
 AttachmentType AttachmentOpticsARMST_DovetailRU "{INHERITED_ATTACHMENT_TYPE_ID}" {
 }
}
```

Module-side thin-child shape:

```text
GameEntity : "{PARENT_GUID}path/to/original_optic.et" {
 components {
  InventoryItemComponent "{INHERITED_INVENTORY_ITEM_ID}" {
   Attributes SCR_ItemAttributeCollection "{INHERITED_ATTRIBUTE_COLLECTION_ID}" {
    CustomAttributes {
     WeaponAttachmentAttributes "{INHERITED_WEAPON_ATTACHMENT_ATTRIBUTES_ID}" {
      AttachmentType AttachmentOpticsARMST_DovetailRU "{INHERITED_ATTACHMENT_TYPE_ID}" {
      }
     }
    }
   }
  }
 }
}
```

This pattern was validated in Workbench: a weapon slot using `AttachmentOpticsARMST_DovetailRU` accepted a thin child optic using the same compatibility family while all placement geometry remained inherited.

Compatibility and geometry are separate systems. A correct `AttachmentType` does not fix a wrong pivot, and changing pivots is not required when the existing physical mount geometry is already correct.

## Workbench validation checklist

After every authoring step:

1. Open the prefab directly in Workbench.
2. Confirm the expected component count/collection count.
3. Expand the edited component and verify that the changed value appears in the intended inherited object, not in a duplicated element.
4. For fire modes, verify the visible order/types (`Safe`, `Single`, `Auto`, `Burst`, etc.) and inspect RPM / burst fields individually.
5. For recoil, inspect `LinearData`, `AngularData`, and `TurnOffsetData` separately; do not judge only by one visible magnitude row.
6. For attachments, verify both sides: the weapon slot requests the intended type and the module's `WeaponAttachmentAttributes` declares the same/inheriting type; then perform an actual mount test.
7. Confirm that untouched inherited values still display their parent values.
8. Only after the prefab opens and the UI hierarchy looks correct should runtime shooting tests begin.

If a value does not appear where expected, treat that as an authoring-path/instance-ID problem before trying to compensate with different numbers.

## Common failure patterns learned from Workbench testing

### 1. Re-attaching `.conf` to inherited objects

Symptom: extra/malformed entries appear in a collection, fields show zeros/defaults, or the edited value lands on the wrong entry.

Fix: use the inherited instance ID only. Use `: "...conf"` only for a genuinely new object.

### 2. Editing several systems at once

Symptom: prefab crashes Workbench and the offending block is unclear.

Fix: revert to a known-good clone and add one system at a time.

### 3. Correct ID at the wrong nesting level

Symptom: file parses but Workbench ignores the value or shows it in an unexpected place.

Fix: reproduce the exact parent hierarchy down to the target object, then override only the target fields.

### 4. Treating recoil as a single number

Symptom: the weapon feels similar in kick but returns differently, or vice versa.

Fix: inspect and tune `LinearData`, `AngularData`, and `TurnOffsetData` independently.

### 5. Overriding inherited values unnecessarily

Symptom: child prefabs become large, hard to review, and fragile against parent changes.

Fix: remove every local field that is already correct in the parent.

### 6. Migrating only the weapon side of an attachment family

Symptom: the slot exists in Workbench, but no intended module can be attached.

Fix: migrate the module side too. Its `WeaponAttachmentAttributes -> AttachmentType` must equal or inherit the type requested by the weapon slot. Prefer a thin child module prefab instead of editing the original asset.

## Canonical handgun chain

`Handgun_Base.et -> Handgun_PM_base.et -> armst_PM.et -> armst_TT.et`

`Handgun_Base.et` defines the common single-shot mode (500 RPM), ADS time 0.2 s, and camera recoil object `58DEF2AB0413E346`.

`Handgun_PM_base.et` defines PM-specific weight 0.70 kg, 200 volume, dispersion 0.4 m at 100 m, magazine, and weapon recoil object `58FCF59C4FED2924` based on `Handgun_9_recoil.conf`.

`armst_PM.et` is mostly an ARMST wrapper.

`armst_TT.et` supplies the TT mesh, 7.62x25 magazine well/template, local sights geometry/effects and melee value. Without explicit overrides, weight/dispersion/recoil resolve from PM.

## Handgun recoil reference

Shared config: `Prefabs/Weapons/Core/Recoil/Handgun_9_recoil.conf` (`7EE41322045592D4`).

- Linear data ID: `58FCF59C4660D33B`
- Angular data ID: `58FCF59C4660D2CC` — PM baseline Y 4.25..4.5, side Z -6..6
- Turn offset data ID: `58FCF59C4660D2CF` — PM baseline Y 45..46.5, side X -3..3
- Camera recoil ID: `58DEF2AB0413E346` — handgun base rotation 0.005/0.005/3 to 0.012/0.012/4

## TT balanced override sample

This is an **authoring sample**, not a claim about the scanned source. It is deliberately expressed as minimal overrides:

```text
SCR_WeaponAttachmentsStorageComponent "{51F080D5CE45A1A2}" {
 Attributes SCR_ItemAttributeCollection "{51F080D5C64F12C5}" {
  ItemPhysAttributes ItemPhysicalAttributes PhysicalAttributes {
   Weight 0.85
  }
  CustomAttributes {
   SCR_RecoilCameraShakeParams "{58DEF2AB0413E346}" {
    m_vRotationImpulseMin 0.006 0.006 3.6
    m_vRotationImpulseMax 0.014 0.014 4.8
   }
  }
 }
}
WeaponComponent "{CFBAA4B706BA66E8}" {
 components {
  MuzzleComponent "{50F64C45E7271D47}" {
   BulletInitSpeedCoef 1
   DispersionDiameter 0.35
   DispersionRange 100
   WeaponAimModifiers {
    RecoilWeaponAimModifier "{58FCF59C4FED2924}" {
     AngularData RecoilData "{58FCF59C4660D2CC}" {
      "Curve Mins" 0.1 4.8 -6.5
      "Curve Maxs" 0.1 5.1 6.5
     }
     TurnOffsetData RecoilData "{58FCF59C4660D2CF}" {
      "Curve Mins" -3.2 48 0
      "Curve Maxs" 3.2 50 0
     }
    }
   }
  }
 }
}
```

The important part is not the exact tuning numbers; it is the override shape and inherited IDs. Future prefabs should obtain those IDs and baselines from `indexes/prefab_authoring_reference.json`, not from memory.
