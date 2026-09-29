# reports/live-addon — imported from the live addon's `agent/` directory

**Provenance.** Every file here was moved verbatim out of the live addon on
2026-09-29, out of `ARMST-PLATFORM---Weapons/agent/<subdirectory>/`. Each file
is byte-identical to what was in the addon: it was copied, re-hashed, and the
hash compared against the pre-move hash before the source was deleted.
312 files moved, 312 hashes verified, 0 mismatches.

These are historical audit outputs, reports and dumps from previous sessions.
They are kept for provenance and for the reasoning behind past decisions. They
are **not** regenerated, and they are **not** kept up to date.

## Why they moved

The live addon is a mod project. It should contain only what the game,
Workbench, or the modder's runtime needs — `.et`, `.conf`, `.meta`, `.c`,
`.layer`, assets, and Workbench's own generated files. Audit markdown, scanner
JSON/CSV dumps, Python tooling and authoring guides are development material
and belong in the tools repository. See
[`../../AGENTS.md`](../../AGENTS.md).

## Important caveats

- **Stale by construction.** These describe the addon as it was when they were
  written. Verify anything you rely on against the live addon.
- **Superseded in places.** Newer work is recorded in
  [`../KNOWLEDGE_STATUS.md`](../KNOWLEDGE_STATUS.md) and
  [`../../docs/sync/CURRENT_AI_SYNC.md`](../../docs/sync/CURRENT_AI_SYNC.md).
- **Do not treat these as authoring rules.** For current policy use `reports/`
  and `agent/`.

## The one exception

`weapon_relocation/reference_fix_backup/` contains a **backup copy of an
authored world layer**. It is a `.layer` file, and it is retained here purely as
provenance. It is not a replacement for the live
`worlds/Weapon_test/weapon_test_Layers/default.layer`, which remains the real
resource and must not be edited from this copy.

## Subdirectories

| Directory | Contents |
|---|---|
| `ammo_audit/` | 9x18 / 9x39 calibre metadata audits and application records |
| `ammo_rebuild/` | Ammunition prefab reconstruction builds and plans |
| `attachment_architecture/` | Attachment hierarchy and slot architecture reports |
| `attachment_audit/` | Attachment audit output |
| `compliance_audit_v2/` | Prefab compliance audit |
| `description_audit/` | Display name/description audits |
| `hierarchy_fix/` | Inheritance-hierarchy fix reports |
| `identity_audit/` | Resource identity audits |
| `inheritance_audit/` | Inheritance chain audits |
| `magazine_audit/` | Magazine audits |
| `magazine_split/` | Magazine split records |
| `naming_audit/` | Naming convention audits |
| `optic_rail_audit_v1/` | Optic rail / dovetail audits |
| `prefab_audit/` | Prefab audit report output (tooling is in `tools/`) |
| `weapon_architecture/` | Weapon architecture reports |
| `weapon_audit/` | Weapon audit output |
| `weapon_cleanup/` | Weapon cleanup records |
| `weapon_hierarchy/` | Weapon hierarchy reports |
| `weapon_relocation/` | Weapon relocation records and the layer backup above |

Python tooling was split out to [`../../tools/live-addon/`](../../tools/live-addon/).
