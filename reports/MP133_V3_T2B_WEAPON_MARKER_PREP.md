# MP-133 V3 — T2b weapon-only marker (prepared lab `.txa`)

**Status:** `T2B_TXA_REBUILT_NO_BOM; AWAITING_OWNER_REIMPORT`.
Lab-only; production Weapons/Core/frozen V2 untouched; Workbench/game NOT RUN by the
agent. Source: Issue #27 comment 5969580576. Bridge implementation is **PAUSED**;
`reports/MP133_V3_EVENT_BRIDGE_DESIGN.md` is retained only as a fallback.

> Incident (fixed): the first lab `.txa` was written with `Set-Content -Encoding UTF8`,
> which prepended a **UTF-8 BOM** (`EF BB BF`) that the valid clips do not have (they start
> with the literal `$anim`). The first import therefore produced an **empty 44-byte
> `W_MP133_T2B_Bolt.anm`** (vs 6467 B player, 1848 B production weapon) and the animation
> set showed `ReloadActionBolt` with a warning/stop icon. The `.txa` was rebuilt at the byte
> level from the production file (Latin1, no BOM, original CRLF) and is now **byte-identical
> to the production clip except the inserted marker line**; the empty `.anm` was removed and
> the `.anm.meta` was kept (GUID `{0C775A2108B6D5AD}` preserved). Owner re-import required.

## Goal

Add a **weapon-only** marker `ARMST_T2B_WM_6E28B9A4` to a lab copy of the weapon
`ReloadActionBolt` clip, keep the **player-only** marker `ARMST_T2A_PM_C41F7A29`, and
compare order / count / time of both during one rack motion — without a bridge and
without touching ammo/R/pump.

## Prepared in the existing `ARMSTMP133T2A_Diag` lab

- New clip source (lab-local): `Assets/Weapons_RUS/Mp_133/T2A/T2AClips/W_MP133_T2B_Bolt.txa`
  — a copy of the production `W_MP133_Reload_Bolt.txa`, **native events preserved**
  (`BlendIn[5]`, `Weapon_EnableFire[10]`, `Weapon_Rack_Bolt[14]`) plus the new
  **`ARMST_T2B_WM_6E28B9A4` at frame 12**.
- Timing: the player bolt clip and this weapon bolt clip are both **20 frames @ 30 fps**;
  the player marker is at frame 12, so the weapon marker is placed at the **equivalent
  phase** (frame 12), not blindly at a different clip's frame.
- The player marker, imported player ANM `{3581B839F53FC345}`, both player ASI
  `ReloadActionBolt` mappings, the test prefab `{5FB844730BED8BD1}`, graph and component
  setup are **unchanged**. Production player/weapon clips untouched.
- Logging (`Scripts/Game/ARMST_MP133_T2A/ARMST_MP133_T2A_Log.c`): the weapon
  `ARMST_T2A_WeaponAnimationComponent.OnAnimationEvent` and the character invoker now
  register and log **both** markers explicitly (uncapped):
  `[ARMST_T2A-WPN] MARKER-PLAYER|MARKER-WEAPON …` and
  `[ARMST_T2A-CHR] MARKER-PLAYER|MARKER-WEAPON …`; the generic weapon-event trace stays
  capped. Subscription guard / init counter / 1 Hz prefab+component confirmation retained.

## Static preflight (agent) — PASS

- Player marker present only in the player `.txa` (1); weapon marker only in the new weapon
  `.txa` (1); **no cross-contamination** (0/0).
- `modded WeaponAnimationComponent` absent; `ARMST_T2A_WeaponAnimationComponent` + its
  `_Class` present; character `modded SCR_CharacterControllerComponent` passive.
- No `HandleWeaponReloading`/`HandleWeaponFire`/`AddActionListener`/`SetReloadWeapon`/ammo
  or magazine mutation; braces/ASCII clean; stale `resourceDatabase.rdb` removed.

## Owner steps (import + repoint)

1. Loadout unchanged: `ARMST-PLATFORM---Weapons` + `ARMSTMP133T2A_Diag`; Core and V2/P2 OFF.
2. **Owner imported once, but the ANM came out empty (44 B)** due to the `.txa` BOM above;
   the returned ANM ResourceName/GUID is
   `{0C775A2108B6D5AD}Assets/Weapons_RUS/Mp_133/T2A/T2AClips/W_MP133_T2B_Bolt.anm`
   (`.meta` Name matches, `.meta` kept unchanged).
3. **Agent (done):** rebuilt `W_MP133_T2B_Bolt.txa` byte-identically to production (no BOM)
   with only the marker line added; removed the empty `.anm`; kept `.anm.meta`; repointed
   **only** `Reload.Erc.ReloadActionBolt` / `Reload.Pne.ReloadActionBolt` in the cloned
   `MP133_T2A_weapon.asi` to the imported ANM. Validated: new ANM 2× in the ASI, production
   bolt resource 0×, other reload rows unchanged (`Reload_Inject` `{45B1772B8AFEAE47}`,
   `Reload_Rem` `{FBC8FA7934FA4394}`), `.meta` GUID consistent; stale `resourceDatabase.rdb`
   removed. The `.anm` is binary/compressed, so native-event preservation is asserted from
   the `.txa` source and confirmed by the runtime log.
4. **TODO (owner re-import):** in the Animation Editor re-import/export
   `W_MP133_T2B_Bolt.txa` → `W_MP133_T2B_Bolt.anm`; confirm the new `.anm` is non-trivial
   (production weapon bolt ≈ 1848 B) and `ReloadActionBolt` turns **green** in both columns.
   If Workbench assigns a different GUID, send the new `.anm.meta` and the agent repoints.
5. **TODO (owner run):** equip `MP-133 [T2A-DIAG]`, several deliberate **short-R** racks;
   capture `console.log`/`script.log`.

## Result assessment (after the owner run)

- (a) does the weapon-only marker reach the **weapon** callback?
- (b) does the player marker still reach the **character** callback?
- (c) ordering / time offset / count across deliberate cycles (per receiver).
- (d) does either marker ever occur without the corresponding animation?
- (e) source proof vs owner runtime.
No exactly-once or precise-synchronization claim from a single solo run; no MP-authority
claim until a separately approved two-peer test.

## STOP conditions

- Any compiler/resource error in the lab; native short-R / hold-R regression; wrong
  clip/component; unexpected marker duplication; or the transitive Weapons UI dependency
  (`6922BE16974B3AED`) prevents the test → STOP and report.

## Dependency note

Weapons `addon.gproj` depends on `58D0FB3206B6F859` (common base) + `6922BE16974B3AED`
(not a local addon; per owner an ASTRA/UI-related project). The lab transitively pulls it.
No addon is added/enabled/modified by T2b.

## NOT RUN

Workbench import/compile and the runtime T2b result are **OWNER TEST REQUIRED**.
