# ARMST prefab authoring reference

Generated from `Weapons.zip` on 2026-09-15. The local addon is the source of truth.

## What is indexed

- 702 `.et/.conf` source files parsed.
- 162 weapon-like prefab/config entries indexed for authoring in the Excel `Prefab индекс` sheet.
- Provenance is kept per resolved value (`defined_in` / inherited source).

## Mandatory authoring rules

1. Follow the inheritance chain before adding anything. A child prefab should contain **only differences** from its parent.
2. Override an inherited object with the **same instance ID**. Do not create a second `ItemPhysicalAttributes`, recoil modifier, sights object, etc.
3. Do not repeat values already correct in the parent. Example: all handguns inherit `Single 500 RPM` from `Handgun_Base.et`; TT does not need its own fire-mode block unless the rate actually changes.
4. Separate weapon handling from projectile lethality. Weight, dispersion, sights, fire modes and weapon recoil belong to the weapon prefab; damage/penetration/ballistics belong to ammo/projectile resources.
5. If the archive does not prove a value, keep it unknown. Filename numbers are not evidence.

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
