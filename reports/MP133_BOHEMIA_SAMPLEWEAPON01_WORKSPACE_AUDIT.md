# MP-133 Task #1 — Bohemia SampleWeapon_01 workspace audit

**Status:** `BOHEMIA_SAMPLEWEAPON01_WORKSPACE_AUDIT_COMPLETE`  
**Date:** 2026-10-06  
**Upstream:** `BohemiaInteractive/Arma-Reforger-Samples` @ `83f12390d3dd61ed834d379f621520ed9f1b891d`  
**Owner input:** complete 14-file `sampleweapon_01` animation workspace set.  
**Mode:** reference/read-only with respect to live ARMST addon. No ASTRA2/prefab/world/Core/production files changed.

## 1. Authenticity / completeness

The owner supplied:
- `sampleweapon_01.agf/.meta`
- `sampleweapon_01.agr/.meta`
- `sampleweapon_01.ast/.meta`
- `sampleweapon_01.aw/.meta`
- `sampleweapon_01_grip.asi/.meta`
- `sampleweapon_01_player.asi/.meta`
- `sampleweapon_01_weapon.asi/.meta`

All 14 owner-uploaded files have Git-blob SHA values equal to the official Bohemia files at upstream commit `83f12390d3dd61ed834d379f621520ed9f1b891d`. This is an exact official workspace snapshot.

## 2. Workspace structure

`sampleweapon_01.aw` binds:
- `sampleweapon_01.ast`
- `sampleweapon_01_weapon.asi`
- `sampleweapon_01_player.asi`
- `sampleweapon_01.agr`

The separate `sampleweapon_01_grip.asi` is not listed in this `.aw` and points to standard `ak74.ast`. It must not be treated as part of the main reload graph merely because it is stored beside it.

## 3. Commands declared by the official graph

`sampleweapon_01.agr` declares only:
- `CMD_Weapon_Reload`
- `CMD_Weapon_Action_Interrupt`
- `CMD_Weapon_Inspection`

No custom SampleWeapon reload command is demonstrated.

This confirms that commands are explicit graph declarations, but this sample does not demonstrate a custom gameplay command producer or a way to replace native R with a custom command.

## 4. Native reload dispatch

The normal reload entry condition is:

`IsCommand(CMD_Weapon_Reload) && !inRange(GetCommandI(CMD_Weapon_Reload), 7, 9) && GetCommandI(CMD_Weapon_Reload) != -2`

Therefore 7, 8 and 9 are explicitly excluded from this rifle's normal reload state machine. This supports the owner's correction: cmd7 must not be assumed to be a generic tubular-magazine shell-load path just because global documentation describes single-projectile semantics for UGL use.

Inside `WeaponReloadSTM`:

| intValue | Official state | Graph behavior |
|---:|---|---|
| 1 | `ReloadActionBolt` | rack bolt |
| 2 | `NoMagReload` | insert magazine |
| 3 | `NoMagNoBulletReload` | insert magazine, then transition to rack |
| 4 | `MagReload` | remove -> insert |
| 5 | `MagNoBulletReload` | remove -> insert, then transition to rack |
| 6 | `RemoveMag` | remove magazine |

The cmd3 and cmd5 paths transition internally to `ReloadActionBolt` based on remaining animation time; the graph does not need to emit a new cmd1 for that transition.

## 5. Consequence for our runtime cmd1 -> cmd5 -> cmd3 evidence

The clean no-handler owner log observed separate weapon-local `OnCharacterCommand` callbacks with int values 1, then 5, then 3.

The official AGF shows that cmd5 can transition to its rack animation internally without changing the command to cmd3. Therefore the later observed `OnCharacterCommand(..., 3, ...)` is not simply the AGF's internal `MagNoBulletReload -> ReloadActionBolt` transition.

It is evidence of a later command update/generated reload command above the graph layer. Exact cause (held R, engine follow-up, input-state re-evaluation, etc.) remains unresolved and must be measured.

## 6. Template and two-instance synchronization

`sampleweapon_01.ast` defines shared logical reload lines including:
- `Reload_InsertMag`
- `Reload_RemoveMag`
- `ReloadActionBolt`

Player and weapon ASIs bind those same logical lines to distinct animations:
- player: `p_rfl_sampleweapon...`
- weapon: `w_rfl_sampleweapon...`

This is the intended Bohemia pattern: one graph/state logic with synchronized player and weapon animation instances.

It validates the general ASTRA2 choice of paired player/weapon phase animations under one graph; it does not validate ARMST-specific shell-loading control flow.

## 7. What this example does NOT solve

This workspace does not demonstrate:
- cancelling/consuming native cmd5 from `OnCharacterCommand`;
- weapon-local replacement of native R;
- a custom command generated from normal reload input;
- cmd7 driving a tube magazine;
- per-shell donor transfer;
- a safe way to prevent native whole-mag mutation.

The global `HandleWeaponReloading` route remains rejected by our runtime evidence.

## 8. New high-value direction

The official sample cleanly separates:
1. command selection in the graph;
2. logical animation lines in AST;
3. player and weapon resources in ASIs;
4. physical weapon actions synchronized to the animation pipeline.

For Task #1, the next evidence target should be the native whole-mag mutation boundary, not more command guessing.

In a clean no-handler runtime, correlate cmd5/cmd3 with native player-side magazine events/actions and identify the first point where the installed tube identity changes/disappears. Only then test a weapon-local suppression/redirect candidate while preserving cmd1 rack.

## 9. Architectural constraint

Bohemia SampleWeapon and Chungus are references, not templates to copy. The final ARMST/MP-133 solution must be independently derived from our runtime, official SDK/API behavior, ASTRA2, and minimal intervention preserving native weapon behavior.

## 10. Imported reference

Pinned files are stored under:

`references/bohemia/Arma-Reforger-Samples/83f12390/`

They are reference-only and covered by the upstream APL.

**Final status:** `BOHEMIA_SAMPLEWEAPON01_WORKSPACE_AUDIT_COMPLETE`.
