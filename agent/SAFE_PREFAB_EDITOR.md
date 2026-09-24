# ARMST Safe Prefab Editor — local agent contract

Primary working root:

`C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

This is the authoritative weapon addon and the default target for local-agent prefab/config/script work. `Armst_Work` is not authoritative and must only be used when the user explicitly assigns a one-off sandbox/test task there.

The local agent is allowed to search prefab/config/script files, inspect inheritance and exact instance IDs, and make targeted edits. It must not invent gameplay values, instance IDs, resource GUIDs or structure.

Core procedure:

`SEARCH STRUCTURE -> IDENTIFY EXACT TARGET -> BACKUP -> ONE MINIMAL EDIT -> STATIC CHECK -> REPORT -> STOP`

## Search scope

Search is allowed to locate:

- exact prefab/config/script file;
- parent prefab;
- inherited object by exact instance ID;
- `AttachmentSlotComponent`;
- `WeaponAttachmentAttributes`;
- `FireModes`;
- `UIInfo` / `ItemDisplayName`;
- recoil sub-blocks;
- magazine well;
- referenced resource paths;
- adjacent/parent prefabs only to confirm hierarchy and inherited IDs.

Do not use search to invent or choose new balance/gameplay values.

## Never invent

Never synthesize:

- instance IDs;
- GUIDs;
- parent resources;
- `AttachmentType`;
- `MagazineWell`;
- RPM;
- burst size;
- recoil values;
- weight;
- dispersion;
- ammo;
- pivot names;
- offsets/angles;
- UI resource references.

If a required value is neither supplied by the task nor proven by an existing prefab/parent, stop without writing and report what is missing.

## Inheritance rules

1. Child prefab contains only real differences from parent.
2. Existing inherited object is overridden with its exact inherited instance ID.
3. Do not create a second object for the same inherited role.
4. Do not duplicate inherited values that are already correct.
5. Do not copy a large parent block to change one field.
6. Exact object nesting is mandatory.
7. If the target is not at the expected nesting level, resolve the real parent hierarchy first; never insert a block approximately.

## Fire modes

For an inherited fire mode, override by inherited instance ID only. Do not reconnect its `.conf`.

Correct existing Auto example:

```text
FireModes {
 BaseFireMode "{B80A64F4A8EF8333}" {
  RoundsPerMinute 900
 }
}
```

Wrong for inherited Auto:

```text
BaseFireMode "{B80A64F4A8EF8333}" : "{...}FireMode_Auto.conf" {
 ...
}
```

A genuinely new mode requires a new unique instance ID plus the appropriate config resource.

Validated AEK Burst pattern:

```text
BaseFireMode "{619AB45BF76565F3}" : "{B5D823125A678D73}Prefabs/Weapons/Core/Configs/FireModes/FireMode_Burst.conf" {
 BurstType Interruptable
 RoundsPerMinute 900
}
```

`Safe` is a safety state, not a firing mode for design counting.

## Recoil

Treat these independently:

- `LinearData`
- `AngularData`
- `TurnOffsetData`

Do not change `TurnOffsetData` merely because recoil should be lower.

Validated AEK inherited IDs:

- Recoil modifier: `{55349E9229B55D9A}`
- LinearData: `{58789524E765774D}`
- AngularData: `{58789524E7CAB55F}`
- TurnOffsetData: `{58789524E0951484}`

Current AEK recoil calibration is provisional and must not be changed without a specific task.

## AEK-971 current control point

Parent:

`{EAE9A298979C4721}Prefabs/Weapons/Rifles/AK74/Rifle_AK74N_base.et`

Key IDs / values:

- WeaponComponent `{CFBAA4B706BA66E8}`
- Auto `{B80A64F4A8EF8333}` → 900 RPM
- Single `{619AB45C30091E43}` → inherited
- Burst `{619AB45BF76565F3}` → `FireMode_Burst.conf`, `Interruptable`, 900 RPM, default MaxBurst 3
- Weight `3.5`
- muzzle attachment slot `{4E2B66CBA589F625}` — do not confuse with optic slot
- optic slot `{55349E9229B55E29}`
- optic AttachmentType object `{5A16F04B258689D6}`
- gameplay compatibility type `AttachmentOpticsARMST_DovetailRU`

For the optic slot do not locally rewrite pivot, child pivot, offsets or angles unless geometry itself is the task. Current physical contract is `slot_optics` / `snap_weapon`, inherited.

Current name: `AEK-971`

Current description:

`AEK-971 — автомат под патрон 5,45×39 мм со сбалансированной автоматикой. Поддерживает одиночный, автоматический огонь и очередь по 3 выстрела; оснащён боковым креплением для оптики.`

UI IDs:

- inventory `ItemDisplayName WeaponUIInfo`: `{5222CB07CFF6712A}`
- weapon `UIInfo WeaponUIInfo`: `{CC3BA6A2C42F09F4}`

Canonical sample: `reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et`.

## DovetailRU marker

The script type should already exist once:

```c
class AttachmentOpticsARMST_DovetailRUClass
{
};

AttachmentOpticsARMST_DovetailRUClass AttachmentOpticsARMST_DovetailRUSource;

class AttachmentOpticsARMST_DovetailRU : AttachmentOptics
{
};
```

Do not duplicate, rename or change its inheritance without a separate task.

## Optic child pattern

Do not edit an original Bohemia optic merely to change ARMST gameplay compatibility. Prefer a thin child.

Validated PSO-1 child parent:

`{C850A33226B8F9C1}Prefabs/Weapons/Attachments/Optics/Optic_PSO1.et`

Inherited IDs:

- InventoryItemComponent `{52627A1F45CD4EB6}`
- SCR_ItemAttributeCollection `{52627A1EBB0698FD}`
- WeaponAttachmentAttributes `{5284D858FFF9BE66}`
- AttachmentType `{5D0CCDD0615C597D}`

Override only:

```text
WeaponAttachmentAttributes "{5284D858FFF9BE66}" {
 AttachmentType AttachmentOpticsARMST_DovetailRU "{5D0CCDD0615C597D}" {
 }
}
```

Canonical sample: `reports/samples/armst_Optic_PSO1_DovetailRU.et`.

## Safe edit procedure

Before every edit of an existing file:

1. Find the exact target file under the authoritative primary root unless the task explicitly names another root.
2. Record full path, size, SHA256, parent resource, target instance ID and a small before-snippet.
3. Create a side-by-side backup named `<filename>.before_agent_edit.bak`; if it already exists, create a timestamped backup instead of overwriting it.
4. Make exactly one logical change.
5. Verify balanced structure/braces, non-empty file, changed resource paths, expected target ID placement and minimal diff.
6. If the diff contains unrelated changes, roll back from backup and stop.

Examples of one logical change: name+description, Auto RPM, add Burst, change one slot AttachmentType, change weight, create one thin child optic.

## Existing-file overwrite rule

Overwrite an existing prefab only when the task explicitly says to modify that file. Backup is mandatory. Do not rename it, change its parent or reserialize unrelated blocks unless explicitly instructed. Prefer a text-level minimal patch.

If the task says to create a new sample, leave existing prefabs untouched and create a new child/copy as instructed.

## Stop conditions

Stop without writing when:

- target prefab exists in multiple locations and the active one is ambiguous;
- expected instance ID does not match;
- expected parent differs;
- target object is absent;
- structure conflicts with the task;
- a new GUID/ID is required but not supplied and cannot be obtained safely by the intended tool;
- the requested pass would alter multiple independent systems;
- a changed resource path does not exist;
- post-edit diff touches unrelated blocks;
- structural validation fails.

## Workbench boundary

Static validation does not equal Workbench/runtime validation. Never claim that a prefab works in Workbench unless it was actually opened/tested there.

Final status after each edit pass must be either:

`STATIC CHECK PASSED — WORKBENCH VALIDATION REQUIRED`

or:

`STOPPED — NO FILE MODIFIED`

## Report format

Report:

- TARGET
- BACKUP
- PARENT
- TARGET OBJECT
- CHANGE
- BEFORE
- AFTER
- DIFF
- STATIC CHECK
- UNRELATED FILES MODIFIED
- WORKBENCH

The local agent may search and edit safely, but architecture/gameplay values come from the task and canonical project knowledge. If structure is proven, make the minimal patch. If not, stop.
