# ASTRA_PARALLEL_W4_CONTINUATION_RESULT

2026-10-04. FINAL_STATUS=ASTRA_NODE_FOUNDATION_SOURCE_READY_OWNER_WORKBENCH

This is an animation-only source milestone, not a working ammunition-transfer implementation. Workbench, script/graph compilation, paired playback and runtime were not run. Existing ten local ANM binaries and modified importer metadata were preserved and excluded from publication.

## Implemented source behavior

In `labs/ARMST_MP133_AstraShellGraph/Assets/MP133_AstraShellGraph/MP133_Astra.agf`, MasterControl again owns native IdleReloadSTM. Only its Idle state can enter AstraShell. Explicit AstraShell/Erc GroupSelect selects paired ASI sources. ShellReloadSTM runs StartReload -> GrabShell -> InsertShell -> CheckContinue, repeats Grab/Insert when eligible, otherwise EndReload -> AstraWaitRelease. Request must be released to rearm.

Stop/FireStop/ineligibility at the Start or Grab boundary exits without starting Insert. Once Insert starts, it finishes before exit. Hold stop parameters until exit: no input latch is implemented. A request held during a native state can enter later when native Idle returns. WaitRelease does not route pump/inspection; release Request first.

Native command 1 routing is retained for the separate pump/chambering path. A guard prevents graph selection of native whole-magazine commands while Request is held, but cannot suppress engine-side command effects. Never use native R to trigger this diagnostic shell session. No open-action loading branch was added.

The diagnostic component accepts early End without a commit candidate, resets after ReturnReady, and records live magazine presence separately from cached magTag. It records current-barrel chamber state and index. Only the W-authored insertion marker is a local candidate, not an ammunition transaction. P/W suffixes identify authored tracks, not proof of receiver ownership. The cycle latch is not a network idempotency protocol.

## Reference decisions and ownership

[Chungus graph audit](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5967373293) and [event audit](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5967403894), plus the owner's screenshot, support separating state transitions, animation sources and script ammo actions. Adopt that separation and repeated insertion; defer distinct first-shell motion and the open-action branch. Reject dummy rounds and missing-magazine recovery. BlendOut/BlendOut2 are reference transition mechanisms, not transplanted ammo callbacks or frame numbers.

Owner-reported T4b evidence says command 1 chambers with the installed tube, whereas command 3 can lose the physical magazine even after event sanitization. This is not a runtime result for this graph. T4b source logging occurs after super.OnCharacterCommand; exact native detachment ownership remains unresolved. No T4b code was copied or changed.

Installed SDK BaseItemAnimationComponent exposes SyncWithCharacter and OnCharacterBoolVariable callbacks; these do not establish a supported setter bridge from weapon script to injected player graph. Initial control remains Animation Editor parameters. Real R/trigger dispatch, paired instance propagation and stop latching require a separate proven input adapter. Official wiki retrieval returned 403; no fresh wiki validation is claimed.

Future transfer contract: one authority validates weapon identity, same physical installed magazine, donor, capacity and chamber snapshot immediately before mutation. Use session/cycle identity for deduplication; P markers cannot constitute a second authority. Stop before commit rejects the operation; after a successful commit retain the round and stop the next cycle. Weapon loss/owner mismatch rejects or quarantines the operation. No transfer or fallback spawning is implemented here.

## Static evidence

- 91 offline unit tests pass, including nine tests reading the actual serialized graph's predicates and transitions. Coverage includes all boundary boolean combinations, early stop, completion of an active insertion, repeated cycles and release rearm. This does not execute Enfusion scheduling.
- Repository integrity passes. Generator output AGF matches the authored V2 AGF. Generator preserves existing metadata instead of replacing importer changes.
- Ten TXA sources remain unchanged. Their hashes, local ANM sizes/hashes and metadata are listed in [manifest](astra-shell-graph/foundation_v2.json). Local binary presence does not prove valid event tracks.
- Of 653 baseline files, only own AGF, diagnostic script and README changed. The other 650 scoped files, including owner ANM/meta/database and sampled protected addon sources, are unchanged. This is a scoped check, not an entire-installation audit.

## Owner test checklist

1. Open only Astra lab and compile scripts/graph. Verify prefab animator override and all five Erc rows in both ASIs. Preserve existing imported GUIDs; inspect ten ANMs and ASTRA event tracks before reimporting anything.
2. In paired preview: stance 0, inspection 0, Firing false, native Idle. Request=true, Repeat=false, Eligible=true: exactly one Insert then End and WaitRelease.
3. Hold Request: no new session. Release, then request with Repeat=true: observe three insertion cycles.
4. Hold Stop during Grab: no Insert candidate. Hold Stop during Insert: finish current Insert, then exit. Repeat with FireStop and Eligible=false. Eligible=false before entry prevents entry.
5. Release Request and clear diagnostic stops. Test native command 1 separately. Confirm both poses, installed magazine identity and chamber outcome; do not infer chambering from animation alone.
6. Return compile errors or video plus ordered diagnostic log. Check hand/shell visibility and seams: Start/Check/End are hold placeholders, no separate shell prop exists. In an equipped test, verify component construction and actual callback delivery before discussing gameplay integration.

No production resources, Core, T2A, T4b, dependency graph or worlds were edited. Disable this lab to roll back. The earlier V1 report is historical; this report supersedes its outer routing and stop semantics.
