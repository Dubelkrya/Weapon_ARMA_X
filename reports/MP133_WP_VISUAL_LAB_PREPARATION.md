# MP133_WP_VISUAL_LAB — isolated preparation

2026-10-08. Result: **LAB_BLOCKED**. Direct owner GO permits preparation only; installation, compile, runtime, commit/push remain prohibited. Rack FROZEN; G3B2 HOLD.

## Baseline and scope

Repository HEAD: `8d3e896b96d3b14a269d678e76d946eb5d40c708`, branch previously confirmed `t4b/installed-mag-probe`. Current HEAD/status checked. Preserved three existing untracked reports: CORE_ARMST_READONLY_AUDIT.md, MP133_MINIMAL_GRAPH_DIAGNOSTIC_DESIGN.md, MP133_TASK1_VANILLA_CHARACTER_FIRST_ROUTE.md. Latest direct owner instructions supersede old sync/plan proposals. Character-root architecture and CMD_Weapon_Reload_Test remain closed.

Current source is the installed ARMSTMP133T4B_InstalledMagProbe addon, consumed read-only. No old_pa or backup resources used. AGENTS/read-only boundaries, current continuation, prior observer and vanilla-route reports, inspection evidence and current prefab/graph/ASIs/scripts inspected.

## Concrete preparation findings

1. `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` derives from production MP-133, adds ARMST_T4B_WeaponProbe with `m_iT4BStartAmmo 2`, and assigns Tube3. `Scripts/Game/ARMST_T4B/ARMST_T4B_InstalledMagProbe.c:229` calls `mag.SetAmmoCount(start)` during baseline setup. An unchanged copy is therefore NOT ammo-neutral. Setting the initial count to zero would still be a writer, not a fix. This is a removable isolation requirement, not proof that every future laboratory is impossible.
2. The current arrangement is shared Astra AGR + separate weapon/player ASIs + AnimInjection BindingName Weapon + BindWithInjection 1. Preserve that arrangement in any future fixture; do not reinterpret component binding lists as a W-to-P bridge.
3. `MP133_Astra2.agf` has inspection states/consumers based on WeaponInspectionState. The player ASI contains Inspection bindings; the weapon ASI contains NO Inspection bindings. Existing inspection poses thus do not supply two independently attributable visible reactions as-is. Native inspection API changes inspection mode/state, not merely an arbitrary graph command: [CharacterControllerComponent](https://community.bistudio.com/wikidata/external-data/arma-reforger/ArmaReforgerScriptAPIPublic/interfaceCharacterControllerComponent.html). Prior owner evidence reports inspection regression; exact active input and safe return behavior are not established for this fixture. Do not invent a key or call SetInspect as a substitute.
4. Existing W/P Astra clips are not event-free diagnostic poses. W_Astra_StartReload.txa:255 includes ASTRA_Shell_StartReload_W; P_Astra_GrabShell.txa:7727 includes ASTRA_Shell_GrabShell_P. Source TXA evidence does not independently certify the compiled ANM event payload. AstraV2 OnAnimationEvent:208 calls lazy initialization and super before filtering; later markers update diagnostic state and ReturnReady invokes the current PACT reset. Reusing these clips with the existing component is not a proven inert visual test. No gameplay mutation from these two markers is asserted; zero-effect dispatch is simply not established.
5. Idle/equip/ADS presentation alone cannot prove a particular request reached W/P. A weapon moving with the character can be inherited/root motion rather than W graph motion. A successful native inspection reaction would prove only that inspection route, not arbitrary Astra-command transport.

## One considered visual experiment, not created

```text
existing character root (unchanged)
  native inspection input [current availability unresolved]
    +-> Weapon injection / P instance -> player inspection hand reaction
    +-> synced W instance -> distinct weapon-local reaction [not supplied by current ASI]
```

Required future isolation would exclude WeaponProbe, reload actions/transfer services and Astra diagnostic event handlers, while preserving the single inherited weapon animation component and original injection binding. A separate W reaction must have established bone ownership and event-free behavior. Neither an arbitrary pose offset nor a reload clip renamed "inspection" is accepted as verified evidence. No such fixture, GUID, graph, prefab, script, ASI, ANM or TXA was generated.

## Safety and remaining dependencies

- No safe current trigger + two independent visual consumers established. This is the deciding blocker, not the prior receipt/health event-capture requirement.
- Removing the known initialization writer is feasible in a new fixture, but a full inherited component/action chain and global T4B script matching must be checked before declaring it isolated. Merely changing a path/GUID does not prevent script selection.
- Inspection intentionally changes handling/pose; current graph includes TagWeaponCannotFire. ADS/fire/switch behavior cannot be promised unchanged while inspection is active. Successful exit and restored controls require later owner verification.
- No native reload/rack command, SetReloadWeapon, ammo/chamber writer or G3B2 transport may be introduced to supply the missing trigger.
- No zero-mutation runtime result is claimed. Existing resources were never executed.

## Owner procedure / disposition

**No runnable Workbench procedure is issued:** there is no prepared candidate to import or test. Do not install this report, launch a test against the original weapon, press R, invoke commands, or use preview Play as an unreviewed substitute. Future review must first identify the exact isolated fixture, safe input, W-local visible motion, P-local visible motion, clip event policy and cancellation behavior. After a separately approved candidate exists, owner captures before/after Tube3 identity/count, chamber and actor/equipped identity; visual W/P positives remain limited to the chosen route. Missing visibility is INCONCLUSIVE, not transport rejection.

Stop this preparation. Per owner direction, do not open another broad SOURCE-ONLY search. The next decision is an alternative synchronization approach or a specifically authorized change to the experiment's prerequisites, not installation of a fictitious lab.

## Files and guards

Created: this report only. Functional files created/changed: **0**. No installation, staging into active addons, Workbench, compile, runtime, command emission, commit or push.

Protected inventory: .et/.conf/.meta/.c/.layer/.agr/.agf/.asi/.ast/.gproj/.anm/.txa; sorted absolutePath|SHA256 rows, LF-joined UTF-8 aggregate (no trailing LF).

| Root | Files | PRE SHA-256 |
|---|---:|---|
| ARMSTMP133T4B_InstalledMagProbe | 105 | D540BE18C0EA0A4754F34D27C260F1BAF9971DC9C1B76674D095C26BC3B48B76 |
| ARMST-PLATFORM---Core | 5521 | 2EDF4D1DCA02F0C662AE1CA567D8B9655C374BC817883B7625A7AF02D8860B4B |
| ARMST-PLATFORM---Weapons | 1584 | A7C611FE0417F5A5E1DA6E4209F01E3CF846295E9ADA57999713FF1B4CC2AECF |
| Armst_Work | 163 | 62AD288141B18B222E058011B29672E23996D7B651C8C4C79E7535BD24123E29 |

POST: all four counts and aggregate SHA-256 values exactly equal PRE after report creation. GAMEPLAY_FILES_CHANGED_BY_CLEANUP=0. No unrelated tests or dependency repairs.
