# Single PSO Minimal Migration Plan (READ ONLY)

- CANONICAL_PSO: `Prefabs/Weapons/Attachments/Optics/armst_Optic_PSO1.et` GUID `C850A33226B8F9C1`
- RECOMMENDED_CANONICAL_TYPE: `AttachmentOpticsDovetailAK` (already canonical type + live defaults; fewest changes)
- NUMBER_OF_SLOT_FIELDS_REQUIRING_CHANGE: 2

## Exact override exception set (AttachmentType only)
| weapon | instance | current type | target type |
|---|---|---|---|
| AEK971 | 55349E9229B55E29 | AttachmentOpticsARMST_DovetailRU | AttachmentOpticsDovetailAK |
| SOC94 | 65AE4CB5E23C0F63 | AttachmentOpticsDovetailSVD | AttachmentOpticsDovetailAK |

All other fields (PivotID, ChildPivotID, Enabled, Default Prefab, instance ID, component identity, parent, GUID) remain unchanged. No other slot needs a change (AKM/9x39/SVD already AK).

## Defaults
- `C850A33226B8F9C1` defaults on `armst_Rifle_AKM_full.et` and `armst_AK74M_full.et` remain valid.
- DEFAULTS_BROKEN_BY_MIGRATION: 0

## Retirement
- `armst_Optic_PSO1_ak.et` (F325FE2E3DDCDDAD): LIVE_REFERENCES_AFTER = 0 -> SAFE_TO_RETIRE_AFTER_MIGRATION
- `armst_Optic_PSO1_DovetailRU.et` (5B318FB72398CB0A): LIVE_REFERENCES_AFTER = 0 -> SAFE_TO_RETIRE_AFTER_MIGRATION

## Type status after
- `AttachmentOpticsDovetailSVD`: ORPHAN_AFTER_MIGRATION (still used by vanilla external)
- `AttachmentOpticsARMST_DovetailRU`: ORPHAN_AFTER_MIGRATION (keep definition)
- `AttachmentOpticsDovetailAKSVD`: ALREADY_ORPHAN

## Migration order
1. AEK971 slot type RU -> AK
2. SOC94 slot type SVD -> AK
3. verify 0 refs to duplicate optic GUIDs + defaults intact
4. retire duplicate optics (+ .meta) after backup
5. leave RU type definition as orphan

## Physical vs compatibility
Compatibility architecture only: one PSO gameplay prefab for all configured slots. Not a claim of one physical mount model; no model/pivot/geometry changes.

LIVE_FILES_CHANGED: NONE
