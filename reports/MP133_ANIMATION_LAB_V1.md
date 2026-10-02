# MP-133 AnimationLab V1 - implementation report

Status: IMPLEMENTED (addon built) / COMPILATION + RUNTIME NOT VERIFIED (no Workbench run in this session).

Date: 2026-10-02. Issue: #25. Supersedes the read-only boundary of #24 for the
isolated experiment only.

> **V2 (2026-10-02, same session):** reload trigger moved from a custom input
> action (H, config-merged — did not fire) to the vanilla RELOAD key **R**,
> intercepted lab-only in `OnApplyControls` and driven with the same
> `inputCtx.SetReloadWeapon(7)` mechanism the Core proves for its rack action.
> The input config files were removed (no config merging involved at all).
> Description below reflects V2.

---

## 1. Scope and isolation

> **OWNER OVERRIDE (issue #25, 2026-10-02):** the deliverable is ONLY fully
> configured prefabs plus their isolated scripts/animation resources. No world,
> `.ent`, `.layer`, scenario, spawn point or placed entity may be created,
> modified, saved or removed. The owner places the prefab in their own world.
> A lab world/layer was created earlier in this session and has been **removed**
> to comply; it is not a deliverable.

Everything game-loadable lives in ONE new addon:

```
C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST_MP133_AnimationLab\
```

New `addon.gproj`:
- ID `ARMSTMP133AnimationLab`
- GUID `{1187677F04E33069}`
- Dependencies on the active Weapons addon (`6A70E400C54051DC`) and Core addon
  (`69E4C3542B6CDC19`) plus the vanilla project ref (`58D0FB3206B6F859`),
  matching the dependency IDs actually found in the live `addon.gproj` files.

No original file was modified. Proof artifacts:
- `Weapon_ARMA_X/artifacts/MP133_Lab/original_consumed_hashes.txt` - SHA-256 of
  the 16 consumed original files (MP-133 graphs/instances/prefabs/metas),
  recorded before any lab work and re-verified at the end (`GAMEPLAY_FILES_CHANGED=0`,
  verified again for `MP133.agf`, `MP133.agr`, `armst_Shotgun_mp_133.et`).
- The user's uncommitted `MP133.agf` (ARMST PROTOTYPE insert state) was copied,
  never edited in place. Its hash is in the manifest.

The two profile files I temporarily touched to explore launching the Workbench
(`.projectList_app1874910_user76561198132769588.conf`,
`wbSettingsDump.ini`) were restored byte-for-byte afterwards. The Workbench was
NOT left running and was not used for validation per owner instruction.

## 2. New resources and GUID map

| Resource | GUID | Role |
|---|---|---|
| `addon.gproj` | `{1187677F04E33069}` | project |
| `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.ast` | `{138604905EC95210}` | template (same rows as original) |
| `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr` | `{F23E6BC494967D16}` | graph root -> lab .agf/.ast |
| `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agf` | `{1EB8E2249801B1E3}` | graph file (original + lab insert-loop transition) |
| `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.aw` | `{EA8670F3600F156D}` | Animation workspace |
| `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi` | `{DE3BB4522642DDE0}` | weapon instance rows -> original clips |
| `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_player.asi` | `{B51A94B5A27E09B4}` | player instance rows -> original clips |
| `Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et` | `{FC1935AF936F63E5}` | lab MP-133 test prefab |
| `Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et` | `{4B288C21B7125D50}` | lab MP-133 RIS test prefab |
| `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Component.c` | - | weapon component |
| `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c` | - | character flow component |
| `Assets/Weapons_RUS/Mp_133/Workspace/LabClips/*_Lab_Inject.txa` | - | sanitized clip SOURCES (see section 7) |

No input/actions config is shipped (V2): the lab reload triggers on the vanilla
R reload request, converted lab-only in the character controller.

Component instance IDs inside the lab prefabs are new
(`{21B3393B3149815A}`), entity IDs `{77AB6DD3F7C4DF4D}` / `{4293C409C16270F8}`.
Inherited objects that are overridden keep their ORIGINAL instance IDs
(`WeaponAnimationComponent {60B4EA76EB15F6E0}`, `AnimInjection {532F3A9CB912F2BA}`, ...) per authoring policy.

## 3. What the lab graph adds (minimal change)

`MP133_Lab.agf` = byte-copy of the original `MP133.agf` + ONE transition added
inside `WeaponReloadSTM`:

```
InsertSingleProjectile -> InsertSingleProjectile
  Condition "IsEvent("BlendOut") && GetCommandI(CMD_Weapon_Reload) == 7"
  PostEval 1, BlendFn S
```

Semantics:
- While the gameplay keeps `CMD_Weapon_Reload == 7` alive, the existing MP-133
  insert clip loops, one shell-insert cycle per clip.
- When the gameplay clears the command (sends `-2`, the vanilla "reload
  finished" value), the current clip finishes, the loop stops, and the original
  parent `Reload -> Buffer4 -> Idle` exit path (already in the graph) finishes
  the reload. No other node/row/transition was changed; pump (`==1`),
  inspection, safety, fire, sight and modes rows are untouched.

## 4. Gameplay ownership and exactly-one commit

Single source of truth:

| State | Owner | Written by |
|---|---|---|
| Tube ammo count | `BaseMagazineComponent` (engine) | lab commit (`SetAmmoCount`, master/server only) and vanilla fire |
| Chamber | `BaseMuzzleComponent` (engine, read-only) | engine |
| Reserve shells | `ARMST_MP133_Lab_Component.m_iLabReserveShells` | lab commit (server only) |
| Insert/graph state | shared anim graph (CMD_Weapon_Reload) | lab client pulsing |

Flow:
1. Owner client, when the vanilla reload request appears for a lab weapon
   (`WeaponIsStartReloading()` / `GetWeaponReloadType() != 0` inside
   `OnApplyControls`, V2 — no config action involved), calls `LabBeginInsert()`.
   A local pre-check (`LabClientCanInsert`, tube present + not already full)
   prevents starting a pointless loop. `Rpc(RpcAsk_LabBeginInsert)` is sent and
   a 60 ms pulse keeps `inputCtx.SetReloadWeapon(7)` alive so the graph runs one
   insert clip per cycle (the same input-context mechanism the Core uses for its
   rack action; `CMD_Weapon_Reload == 7` matches the lab graph's
   `InsertSingleProjectile`).
2. Server (`RpcAsk_LabBeginInsert`) re-validates with `LabServerCanInsert`
   (tube present, under capacity, reserve > 0) BEFORE opening the insert window;
   a failing request is answered with `RpcDo_LabCeaseInsert` and no window opens.
3. Server, upon the commit animation event (`ARMST_Lab_Shell_Commit` OR
   `Weapon_AttachMagazine`), runs `LabServerCommitInsert` which commits exactly
   one shell only when:
   - the server insert window is active AND commit cooldown is clear AND
   - weapon/tube still valid AND effective capacity resolved AND
   - `currentAmmo < cap` AND `reserve > 0`.
   Then: `reserve--`, `tube.SetAmmoCount(current+1)`, cooldown 500 ms.
3. On rejection (full / empty reserve) the server sends
   `RpcDo_LabCeaseInsert` (RplRcver.Owner) and the client stops the loop.

Anti-duplication measures:
- Only the server writes ammo (all client paths only drive animation).
- Cooldown (500 ms) blocks replay of frame 43 after an interrupted clip restart
  (genuine cycles are ~3.3 s apart at 30 fps/107 frames).
- The lab never decrements on `Weapon_Rack_Bolt`; the existing Core ARMST rack
  handler (server-side, cooldown + pending dedupe) remains the sole rack ammo
  owner, so the pump cannot double-decrement.
- Fire is vanilla (magazine decrement via engine).

## 5. Interrupt behaviour

- `Weapon_Rack_Bolt` event -> server closes the insert window; the rack ammo
  effect is the Core handler's. A shell not yet committed at the event cannot
  be lost because commit events only fire inside a completed clip after frame 43;
  an interrupted clip cannot commit.
- H release / weapon lowered / weapon switch -> client stops pulsing (sends -2)
  and informs the server.
- Tube full / reserve empty -> server closes the window and asks the owner to stop.
- Re-equip: the client pulse self-terminates when `GetCurrentWeaponLab()` is null,
  and re-pressing H starts a fresh window. State is per-character, no global leak.

## 6. Networking

- Client->server: `RpcAsk_LabBeginInsert` / `RpcAsk_LabEndInsert`
  `[RplRpc(RplChannel.Reliable, RplRcver.Server)]`.
- Server->owner: `RpcDo_LabCeaseInsert` `[RplRpc(RplChannel.Reliable, RplRcver.Owner)]`
  (same RplRcver pattern already compiled in Core).
- `SetAmmoCount` is documented as master-only (API doc), the server is the
  master for the tube entity while the weapon is held under an authoritative
  character.
- Client prediction: the client merges replicate tube counts; the reserve
  counter is server-only and not yet replicated (see risks).

## 7. Original vs isolated animation events

Original reload inject clips (`W_/P_MP133_Reload_Inject`) carry
`Weapon_SpawnMagazine`(10), `Weapon_AttachMagazine`(43), `Weapon_MagRelease`(64),
`BlendOut`(100). These are magazine-swap events - in the lab's shell-insert loop
they are benign only because the command path is lab-controlled and the server
commit is gated; the production weapon already plays these clips during reload
in the live game.

To avoid the magazine-swap semantics entirely, the lab also ships sanitized
sources: `LabClips/W_MP133_Lab_Inject.txa` / `P_MP133_Lab_Inject.txa` with the
events renamed to `ARMST_Lab_Shell_Spawn` / `ARMST_Lab_Shell_Commit` /
`ARMST_Lab_Shell_Release` (motion/keyframes identical, only event names and
`#custProp sourceFile` kept). These `.txa` files are NOT compiled `.anm`; they
need one re-import in the Workbench Animation Editor (see RU checklist step 9),
after which the `_Lab_weapon/_player.asi` rows can be re-pointed at the
sanitized clips. The lab listens for both event names so it keeps working with
either clip source.

## 8. Verified-during-this-session vs NOT verified

Verification performed (static, no Workbench launch):
- All lab files: ASCII, balanced braces.
- All referenced GUIDs resolve to a lab resource, a vanilla/AK74 asset, or
  original MP-133 assets with the exact GUIDs read from the originals.
- Lab prefab parents reference the exact GUID paths used by
  the live Weapons test layer (proven to load in the live project).
- Every `.asi` row (Group.Column.Row) used by the lab resolves against the lab
  `.ast` template; the insert-loop graph transition is present.
- AUTOMATED: these checks are reproducible via
  `agent/scripts/validate_mp133_lab.py` and pinned as 7 unit tests in
  `agent/tests/test_mp133_lab_validation.py` (all PASS, run with Rizom/Blender
  embedded Python since no standalone Python is installed on this station).
- Enfusion API names/signatures used were confirmed against:
  - the local official API reference installed with Arma Reforger Tools
    (`Workbench\docs\ArmaReforgerScriptAPIPublic`): BaseWeaponComponent,
    BaseMagazineComponent (SetAmmoCount master-only), BaseMuzzleComponent,
    CharacterInputContext (SetReloadWeapon/GetWeaponReloadType/WeaponIsRaised),
    CharacterCommandHandlerComponent, SCR_CharacterControllerComponent
    (ReloadWeapon, GetOnAnimationEvent, GetInputContext, GetWeaponManagerComponent),
    CharacterAnimationComponent (BindCommand/CallCommand via BaseAnimPhysComponent),
    WeaponAnimationComponent / BaseItemAnimationComponent (IsAnimationEvent);
  - existing compilable Core/Weapons code (RPC patterns, RplRcver.Server/Owner,
    InputManager listeners, CallLater/Remove, ScriptInvoker.Insert/Remove,
    class component attributes, GameAnimationUtils.RegisterAnimationEvent).

NOT verified (engine/compile/runtime) - REQUIRES the owner to open the Workbench
once and run the in-game test:
- Script compilation of the two lab `.c` files.
- Resource import/scan of the new .agr/.agf/.ast/.asi/.aw/.et metas.
- Animation Editor graph load of `MP133_Lab.agr` (node/transition validity).
- Any runtime behavior claim (pump sync, loop cadence, event delivery to the
  server, tube/chamber interaction). These are reported as UNVERIFIED, not PASS.

### Compile feedback log (owner runs)

| Run | Result |
|---|---|
| 2026-10-02 (owner) | `ARMST_MP133_Lab_Component.c,42`: `Can't find variable 'Toggle'` -> fixed: `UIWidgets.Toggle` does not exist in this engine revision; project-wide precedent is `UIWidgets.CheckBox` for booleans. Also removed `static const` members from the ScriptComponent (no project precedent) and the defensive `OnDelete` override; command values now live as instance consts in the character file (`LAB_INSERT_CMD=7`, `LAB_RELOAD_DONE=-2`), matching the Core `protected const` pattern. Recompile expected to surface any remaining issues, if any.

## 9. Known assumptions and risks

1. R interception (V2): the lab converts the vanilla reload request inside
   `OnApplyControls` and re-drives `SetReloadWeapon(7)` continuously. If the
   native starts its own reload handling on the same frame as R, the native's
   magazine-swap ops could still briefly run. Expected outcome: the graph plays
   the insert clip (not the remove/insert swap) because the final command value
   for the frame is 7, and the tube-manager never performs a swap because the
   detach/attach anim (RemoveMag rows + `Weapon_DetachMagazine` events) is not
   played. This is the single most important runtime item to observe
   (checklist D4); if vanilla still swaps the tube, the follow-up is to disable
   the native reload action for lab weapons (needs the vanilla action name from
   the player-visible input config).
2. `CMD_Weapon_Reload == 7` entry semantics and the 60 ms pulse are assumed to
   work with Enfusion command semantics (the Core already relies on
   `SetReloadWeapon(1)` for its rack, so type-7 through the same API is the
   same class of risk). The graph entry condition and exit path are the
   original graph's own conditions, which lowers risk.
3. Animation events (`Weapon_AttachMagazine`, `ARMST_Lab_Shell_Commit`) must
   reach the SERVER character. The Core rack handler already relies on this for
   `Weapon_Rack_Bolt`, so the mechanism is presumed present for the same graph;
   this still needs a runtime check (single player counts as server+client).
4. Forced capacity is the existing ARMST rule: `ARMST_SHOTGUN_COMPONENTS
   .m_MaxMagazineAmmo` default 2 (no override on the MP-133 chain), despite the
   tube `MaxAmmo 10` + 10 AmmoMapping. The lab reads that rule via
   `GetEffectiveTubeCapacity()`; set `m_iTubeCapacityOverride > 0` on the lab
   prefab to test other capacities.
5. Reserve is a virtual counter (30 by default), not inventory loose shells
   (no inventory shell-item source exists yet in the addon). A future
   `m_aReserveShellPrefabs` inventory source can replace it without touching
   the commit path.
6. `Weapon_SpawnMagazine/_MagRelease` on the original inject clips still fire
   during lab insert loops. They are expected to be inert in this context (the
   weapon does not spawn/attach magazine entities on this command path), but
   that is exactly the runtime item to observe; the sanitized clips remove it.
7. `RpcDo_LabCeaseInsert` uses RplRcver.Owner; players = server+owner in the
   supplied solo test, so the replication identity must be confirmed in-game.
8. No git executable is installed on this machine, so no commits/pushes were
   made; the lab addon is delivered as files. Remote/branch state is unchanged.

## 10. Acceptance matrix (planned)

| Check | Where it is proven |
|---|---|
| Isolation (originals unchanged) | this report §1 + sha manifest |
| Dependencies resolve | live gproj IDs used; verify on project open |
| Resource wiring | static GUID/path checks above; verify on import |
| Compile (lab scripts) | NOT VERIFIED - compile on Workbench open, watch script.log |
| Graph load/preview | NOT VERIFIED - open MP133_Lab.aw in Animation Editor |
| One-shell commit | runtime test H-hold vs tube count (see RU checklist) |
| Negative/phantom-ammo | runtime tests (full tube, reserve 0, interrupted) |
| Pump exactly-once | runtime test (LSHIFT+R) |
| Dual-instance commit | single commit path only (server), test logs |
| Networking | runtime solo/MP test |
| Recovery | runtime interrupt/re-equip tests |
| Production untouched | sha manifest + no writes outside lab addon |

## 11. Critique of the current production ammo hack and the target model

The current production shotgun ammo logic (Core `ARMST_WEAPONS_HANDLER.c`,
reviewed 2026-10-02) works but is a band-aid:

- **Several writers on the same counter.** Tube ammo is written by: engine fire,
  the Core rack handler (`TAO_DecrementAmmoOnRack`, event-driven), the vanilla
  mag-swap, and `WeaponHandler` (called on EVERY ammo-count change), which trims
  the tube to `ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo` (2) and SPAWNS a new
  magazine entity with the excess into the world/inventory. Five different
  moments/owners -> races, duplicates and inventory pollution.
- **Capacity enforced by splitting, not by logic.** The tube is declared
  `MaxAmmo 10` but the design wants 2; the "fix" is to physically cut the
  magazine and drop the rest, instead of limiting insertion.
- **No per-shell reload.** Reload is a wholesale tube-magazine swap; the
  `== 7` insert state exists only as a prototype in `MP133.agf` and was never
  driven by gameplay.
- **Rack needs a client "pending" flag**; if the rack event fires without a
  pending request (auto-rack paths) the decrement is skipped -> drift.

Target model (implemented in the lab; see section 4):

| State | Single owner | Written by |
|---|---|---|
| Tube | `BaseMagazineComponent` (engine) | lab insert commit + engine fire (master only) |
| Reserve | `ARMST_MP133_Lab_Component` (lab, server-only field) | lab commit |
| Chamber | `BaseMuzzleComponent` (engine) | engine |
| Rack transfer | existing Core handler (kept for production semantics) | 1 tube->chamber per rack event |

The key production takeaway: capacity must be enforced where insertion happens
(one place, with validation + debounce), not by trimming/spawning magazines
after the fact. That is exactly the isolated experiment Issue #25 asked to
prove; a production PR would move this component (plus an inventory shell
source for reserve) into the Weapons/Core addons - out of scope for this lab.