# MP-133 AnimationLab V1 - implementation report

Status: IMPLEMENTED (addon built) / COMPILATION + RUNTIME NOT VERIFIED (no Workbench run in this session).

Date: 2026-10-02. Issue: #25. Supersedes the read-only boundary of #24 for the
isolated experiment only.

---

## 1. Scope and isolation

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
| `Worlds/MP133_Lab/MP133_Lab.ent` (+ Layer) | `{423396FF72C33C45}` | test world entry |
| `Configs/System/chimeraInputCommon.conf` | `{4839B8D36948C9E8}` | lab insert action (keyboard H) |
| `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Component.c` | - | weapon component |
| `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c` | - | character flow component |
| `Assets/Weapons_RUS/Mp_133/Workspace/LabClips/*_Lab_Inject.txa` | - | sanitized clip SOURCES (see section 7) |

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
1. Client (owner) presses H with a lab weapon equipped -> `m_bLabClientInsertActive`
   + `Rpc(RpcAsk_LabBeginInsert)`; a 60 ms callqueue job keeps
   `CallCommand(CMD_Weapon_Reload, 7, 0)` alive so the graph loops the insert clip.
2. Server (same character's `SCR_CharacterControllerComponent`), upon the
   commit animation event (`ARMST_Lab_Shell_Commit` OR `Weapon_AttachMagazine`),
   runs `LabServerCommitInsert` which commits exactly one shell only when:
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
- Lab prefab parents and the world/layer reference the exact GUID paths used by
  the live Weapons test layer (proven to load in the live project).
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

## 9. Known assumptions and risks

1. `CMD_Weapon_Reload == 7` entry + constant command pulsing is assumed to work
   with Enfusion command semantics (command int latched ; `IsCommand` on event
   frame). The graph entry condition and the -2 exit path are the original
   graph's own conditions, which lowers risk. If pulsing each 60 ms causes
   thrash, pulse-once-at-down is the documented fallback (single line change).
2. Animation events (`Weapon_AttachMagazine`, `ARMST_Lab_Shell_Commit`) must
   reach the SERVER character. The Core rack handler already relies on this for
   `Weapon_Rack_Bolt`, so the mechanism is presumed present for the same graph;
   this still needs a runtime check (single player counts as server+client).
3. Forced capacity is the existing ARMST rule: `ARMST_SHOTGUN_COMPONENTS
   .m_MaxMagazineAmmo` default 2 (no override on the MP-133 chain), despite the
   tube `MaxAmmo 10` + 10 AmmoMapping. The lab reads that rule via
   `GetEffectiveTubeCapacity()`; set `m_iTubeCapacityOverride > 0` on the lab
   prefab to test other capacities.
4. Reserve is a virtual counter (30 by default), not inventory loose shells
   (no inventory shell-item source exists yet in the addon). A future
   `m_aReserveShellPrefabs` inventory source can replace it without touching
   the commit path.
5. `Weapon_SpawnMagazine/_MagRelease` on the original inject clips still fire
   during lab insert loops. They are expected to be inert in this context (the
   weapon does not spawn/attach magazine entities on this command path), but
   that is exactly the runtime item to observe; the sanitized clips remove it.
6. `RpcDo_LabCeaseInsert` uses RplRcver.Owner; players = server+owner in the
   supplied solo test, so the replication identity must be confirmed in-game.
7. No git executable is installed on this machine, so no commits/pushes were
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