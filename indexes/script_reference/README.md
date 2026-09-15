# Script / module reference

This directory is the authoring entrypoint for ARMST weapon compatibility scripts, attachment modules, RIS/optic/muzzle interfaces, weapon attachment slots, sight mechanics, and compatibility validation.

## Files

- `manifest.json` — local ARMST marker/interface classes, confirmed Bohemia base types, module inventory, warnings, and the resolved TT ammo update.
- `slot_and_sight_summary.json` — weapon-side `AttachmentSlotComponent` compatibility usage plus the `SightsComponent` summary.
- `optic_compatibility_policy_v1.json` — strict optic mount-family policy, current PSO/slot findings, banned broad types, proposed ARMST leaf hierarchy, and migration order.

## Resolution model

1. Weapon-side `AttachmentSlotComponent` declares what interface a slot accepts.
2. Module-side `WeaponAttachmentAttributes -> AttachmentType` declares the module interface.
3. Engine compatibility is directional: `moduleType.IsInherited(slotType)`.
4. Proprietary/dovetail weapon slots should use leaf mount-family types, not broad parent types.
5. If one optical body supports multiple mounts, use thin child wrapper prefabs per mount family rather than one broad universal prefab.
6. Reuse Bohemia's RIS1913 length hierarchy for standardized rails.
7. `SightsComponent`, ADS, zeroing, sight pivots and sight ranges are prefab data, not compatibility marker-script behavior.
8. Resolve child-local serialization before parent values; never invent a missing type when a parent can be resolved.

## Known ARMST optic findings

- `Optic_PSO1.et` is AK-typed but currently fits AKM, VSS, VAL, 9A91, VSK94 and SVD because those weapon slots share `AttachmentOpticsDovetailAK`.
- `Optic_PSO1_ak.et` uses the broader parent `AttachmentOpticsDovetailAKSVD`; under the engine inheritance direction it has no compatible local narrower AK/SVD slot in the supplied snapshot.
- `armst_SVD` currently requests the AK dovetail type and should be migrated to an SVD-family leaf.
- G36 already uses a strict custom `AttachmentOpticsG36` pattern.
- Groza is standardized RIS1913; its rail-length class should be selected deliberately rather than replaced by a weapon-specific script type.

## Other known ARMST anomalies

- `MagazineWell763x25` uses registry name `MagazineWell763x25_Class`; preserve it until Workbench-safe migration is explicitly validated.
- `MagazineWellSR2` is declared but unused in the supplied prefabs; SR-2 currently serializes `MagazineWellPP91`.
- The supplied `Scripts.zip` contains no per-weapon behavioral script implementation; weapon behavior is predominantly prefab/component/config driven.

See `../../reports/SCRIPT_MODULE_AUTHORING_GUIDE.md` for the general module guide and `../../reports/OPTICS_COMPATIBILITY_SYSTEM.md` for the strict optics design and migration plan.
