# AEK-971 — test checkpoint V8

Date: 2026-09-15
Status: Workbench-tested checkpoint; exact balance deferred.

## Scope

This checkpoint records the working AEK-971 prototype state so later iterations do not repeat already-solved prefab/override mistakes.

The prototype is intentionally based on the working AK-74 chain and is not yet a final production AEK-971 prefab.

## Working base

Parent:
`{923D948AB0D57A50}Prefabs/Weapons/Rifles/AK74/Rifle_AK74_long_base.et`

The AK-74 clone opened correctly in Workbench. This confirmed that the parent chain and base prefab structure are valid.

## Fire modes — confirmed working

Expected selector states:
- Safe — inherited
- Single — inherited from AK-74
- Auto — inherited object, RPM overridden to 900
- Burst — new 3-round burst mode

### Correct Auto override

Do NOT reconnect `FireMode_Auto.conf` on an inherited fire-mode object.
Override the inherited object only by its existing instance ID:

```text
BaseFireMode "{B80A64F4A8EF8333}" {
 RoundsPerMinute 900
}
```

Confirmed inherited Auto instance ID:
`{B80A64F4A8EF8333}`

Single is intentionally left untouched/inherited.

### Correct Burst addition

Burst is a genuinely new fire mode, so using the burst config as a parent is correct:

```text
BaseFireMode "{619AB45BF76565F3}" : "{B5D823125A678D73}Prefabs/Weapons/Core/Configs/FireModes/FireMode_Burst.conf" {
 BurstType Interruptable
 RoundsPerMinute 900
}
```

This was confirmed to work in Workbench.

## Recoil — accepted provisional V8

Exact balance is postponed. Current values are only a working gameplay baseline for the balanced-action concept.

Existing recoil modifier:
`RecoilWeaponAimModifier "{55349E9229B55D9A}"`

LinearData instance:
`{58789524E765774D}`

AngularData instance:
`{58789524E7CAB55F}`

Accepted provisional override:

```text
WeaponAimModifiers {
 RecoilWeaponAimModifier "{55349E9229B55D9A}" {
  LinearData RecoilData "{58789524E765774D}" {
   "Curve Magnitudes" 0.94 0.8 1
  }
  AngularData RecoilData "{58789524E7CAB55F}" {
   "Curve Magnitudes" 0.94 0.8 1
  }
 }
}
```

### Important: return behavior

`TurnOffsetData` is NOT overridden in V8.
It remains inherited from AK-74.

Reason: changing TurnOffset changed the return/settling behavior rather than only the primary recoil impulse. For now we preserve AK-74 return behavior and reduce only Linear + Angular recoil amplitude.

Do not reintroduce the V7 TurnOffset override unless deliberately testing return behavior.

## Known failed / superseded approaches

### V1
Too many changes were introduced at once. Workbench crashed when opening the prefab. Do not use V1 as a basis.

### V3 fire-mode mistake
Inherited `FireMode_Auto.conf` / `FireMode_Single.conf` were reattached as if they were new objects. Workbench showed malformed/duplicated fire-mode structure.

Rule learned:
- inherited object -> override by inherited instance ID only;
- genuinely new object -> may inherit from a `.conf` resource.

### V7 recoil mistake
Changed Angular + TurnOffset while leaving Linear at AK-74 behavior. This mainly affected return/offset behavior and did not produce the intended obvious reduction in primary recoil.

V7 is superseded by V8.

## Current working prefab

Local reference filename:
`armst_AEK971_test_v8_BALANCED_RECOIL_CORRECT.et`

## Deferred work

Do not tune these yet unless explicitly resuming balance work:
- final Linear recoil values;
- final Angular recoil values;
- TurnOffset / return behavior;
- camera recoil/shake;
- dispersion;
- muzzle velocity coefficient;
- optics/DovetailRU;
- final AEK mesh/animation differences;
- production naming/GUID/resource placement.

## Resume rule

When resuming AEK-971 work, start from V8, not from earlier versions.
First preserve the confirmed fire-mode structure. Change only one subsystem per test iteration.
