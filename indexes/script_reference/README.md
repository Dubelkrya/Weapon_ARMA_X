# Script / module reference

This directory is the authoring entrypoint for ARMST weapon compatibility scripts, attachment modules, RIS/optic/muzzle interfaces, weapon attachment slots, and sight-mechanics boundaries.

## Files

- `manifest.json` — local ARMST marker/interface classes, confirmed Bohemia base types, module inventory, warnings, and the resolved TT ammo update.
- `slot_and_sight_summary.json` — weapon-side `AttachmentSlotComponent` compatibility usage plus the `SightsComponent` summary.

## Resolution model

1. Reuse an existing engine compatibility type when it already represents the interface.
2. Create a local empty marker type only when a genuinely separate compatibility domain is required.
3. Weapon-side `AttachmentSlotComponent` declares what interface a slot accepts.
4. Module-side `AttachmentType` declares what interface the module belongs to.
5. `SightsComponent`, ADS, zeroing, sight pivots and sight ranges are prefab data, not compatibility marker-script behavior.
6. Resolve child-local serialization before parent values; never invent a missing type when a parent can be resolved.

## Known ARMST anomalies

- `MagazineWell763x25` uses registry name `MagazineWell763x25_Class`; preserve it until Workbench-safe migration is explicitly validated.
- `MagazineWellSR2` is declared but unused in the supplied prefabs; SR-2 currently serializes `MagazineWellPP91`.
- The supplied `Scripts.zip` contains no per-weapon behavioral script implementation; weapon behavior is predominantly prefab/component/config driven.

See `../../reports/SCRIPT_MODULE_AUTHORING_GUIDE.md` for the authoring guide and Bohemia public reference links.
