# Script / module reference

This directory is the authoring entrypoint for ARMST weapon compatibility scripts, attachment modules, RIS/optic/muzzle interfaces, weapon attachment slots, sight mechanics, and compatibility validation.

## Files

- `manifest.json` — local ARMST marker/interface classes, confirmed Bohemia base types, module inventory, warnings, and the resolved TT ammo update.
- `slot_and_sight_summary.json` — weapon-side `AttachmentSlotComponent` compatibility usage plus the `SightsComponent` summary.
- `optic_compatibility_policy_v2.json` — **current gameplay policy**: researched real compatibility stays separate, while approved Russian/Soviet side-rail weapons and optics share the `DovetailRU` gameplay family implemented by `AttachmentOpticsARMST_DovetailRU`.
- `optic_compatibility_policy_v1.json` — archived strict mount-family design retained for analysis/history; it is no longer the active gameplay policy.

## Resolution model

1. Weapon-side `AttachmentSlotComponent` declares what interface a slot accepts.
2. Module-side `WeaponAttachmentAttributes -> AttachmentType` declares the module interface.
3. Engine compatibility is directional: `moduleType.IsInherited(slotType)`.
4. ARMST keeps **RealCompatibility** and **GameplayCompatibility** as separate data layers.
5. Approved Russian/Soviet side-rail weapons and optics use the gameplay family `DovetailRU` / `AttachmentOpticsARMST_DovetailRU`.
6. This DovetailRU rule is an explicit gameplay simplification, not a claim that every real side-rail/bracket is mechanically identical.
7. Reuse Bohemia's RIS1913 length hierarchy for standardized Picatinny/RIS rails; do not merge RIS1913 into DovetailRU.
8. Keep proprietary interfaces such as `AttachmentOpticsG36` separate.
9. `SightsComponent`, ADS, zeroing, sight pivots and sight ranges are prefab data, not compatibility marker-script behavior.
10. Pivot/snap placement is validated separately from AttachmentType compatibility.

## Current ARMST optic migration

Current supplied snapshot candidates for `DovetailRU` include AKM, VSS, VAL, 9A91, VSK94, SVD and SOC94. `Optic_PSO1.et` and `Optic_PSO1_ak.et` should converge to `AttachmentOpticsARMST_DovetailRU` for gameplay compatibility while keeping their researched real-world mount facts separately.

G36 remains a strict custom `AttachmentOpticsG36` interface. Groza remains in the Bohemia RIS1913 family.

## Other known ARMST anomalies

- `MagazineWell763x25` uses registry name `MagazineWell763x25_Class`; preserve it until Workbench-safe migration is explicitly validated.
- `MagazineWellSR2` is declared but unused in the supplied prefabs; SR-2 currently serializes `MagazineWellPP91`.
- The supplied `Scripts.zip` contains no per-weapon behavioral script implementation; weapon behavior is predominantly prefab/component/config driven.

See `../../reports/SCRIPT_MODULE_AUTHORING_GUIDE.md` for the general module guide, `../../reports/OPTICS_COMPATIBILITY_SYSTEM_V2.md` for the active gameplay optics design, and `../../reports/samples/AttachmentOpticsARMST.c` for the script template.
