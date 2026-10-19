# MP-133 autonomous continuation

Authority: direct owner task 2026-10-08, FULL AUTONOMY FOR GPT-6.1 SOL.
Supersedes per-step GO requirements. Workbench launch/control is OWNER ONLY,
including already-open windows, CLI launch and indirect automation.

## Continuation

LAST_COMPLETED_PHASE = installed bind-only candidate compiled; owner bind pair observed
CURRENT_PHASE = identify P entry predicate and pose contribution during shell request
LAST_SAFE_COMMIT = 8d3e896b96d3b14a269d678e76d946eb5d40c708 (repository checkpoint, NOT complete installed baseline)
CURRENT_BLOCKER = no captured P-instance gate values or active shell node at W request
NEXT_EXACT_ACTION = owner captures P variables and IdleReloadSTM active node during one shell request
DO_NOT_REOPEN = same bind-name comparison, CMD_Weapon_Reload_Test, speculative character-root rewrite

## Verified baseline and distinctions

- Repository branch t4b/installed-mag-probe, HEAD as above. Four existing untracked
  reports preserved. Do not git add -A or commit those reports incidentally.
- Installed CustomR SHA256:
  B13029AF6A739529802A31204E372D4EE95A8692D7D4856197D50644FC489F4C.
- Actual owner log logs_2026-10-08_21-46-33/script.log:122 records episode=1,
  weaponId=-575451861, missingId=-1603648848 and real component/weapon/actor
  references. Different names are distinguished; attachment resolution is NOT proven.
- Same owner log at 21:52:07.862 records W request readback=true, eligible=true,
  repeat=false, stop=false. W StartReload follows at 21:52:07.890.
- The owner log contains rack and firing separately. This is owner runtime
  evidence, not an agent-run compile-only experiment; do not describe the whole
  session as ammo-neutral or as a test without R.
- Installed P ASI has all five shell bindings. Shared AGF enters Astra only when:
  ASTRA_ShellRequest && ASTRA_ShellEligible && !ASTRA_ShellStop &&
  !ASTRA_FireStop && !Firing && WeaponInspectionState == 0 && Stance == 0 &&
  !IsCommand(CMD_Weapon_Reload).
- MasterControl evaluates IdleReloadSTM plus SightPose with Always eval both.
  This alone proves neither effective pose weight nor visible P shell output.
- Preserve native rack and working W. No G3B2 integration until animation cycle
  ownership and exactly-once insert commit are established.

## Technical sequence

1. Identify the failure boundary on the current P instance, without code edits.
   Read current AGR/AGF/ASI, current weapon prefab, WPROP code and owner log.
   Owner procedure below; no resource saving. Rollback: none, observation only.
2. Implement ONE correction selected by evidence: missing P input -> proven
   transport candidate; false gate -> narrow P-specific predicate/state repair;
   active source but no visible hands -> injection pose/IK/blend contribution.
   Before any resource edit, preserve current bytes and GUIDs, record PRE hashes,
   and checkpoint only explicitly selected baseline files in Git. Original
   resource restoration is not a substitute for a forward fix.
3. Owner compiles and performs one animation cycle. Static checks cannot pass
   this stage. Observe hands and weapon separately; record timing, cancellation,
   magazine identity/ammo/chamber before/after. Existing baseline initialization
   must be separated from animation effects.
4. Join proven animation cycle to G3B2 with a unique transaction/cycle token,
   server authority, fail-closed donor selection, no duplicate event commits,
   donor+target conservation, same Tube3 and unchanged chamber. Check interrupt,
   full tube, no donor, switch/unequip, fire and delayed transaction verification.
5. Owner validates repeat/end/interrupt and multiplayer behavior. Report offline
   proof separately from multiplayer suitability; never claim replication tested
   from offline success.

## Exact owner Workbench observation needed now

Use the existing T4B fixture, not a newly created character root or laboratory.
Do not edit graph values, save resources or invoke commands from editor tools.

1. Before the shell request, use Animation Editor Live Debug's existing Attach
   workflow (there is no Fetch in the owner's version). Select character and
   identify Weapon injection by MP133_Astra2_player.asi and MasterControl.
2. Stand upright, do not ADS, inspect or fire. Choose a shell-eligible state that
   will NOT enter rack (chambered=1 OR installed Tube3 empty). Record ammo and
   chamber baseline; do not press R to establish that baseline in this test.
3. Capture the P instance before and during ONE ordinary R request. Use recording
   if the existing UI supports it; no assumption that two instances can be
   recorded simultaneously. Required evidence is THIS P instance, not an unknown
   W instance or the shared AGR shown offline.
4. Capture ASTRA_ShellRequest, ASTRA_ShellEligible, ASTRA_ShellStop,
   ASTRA_FireStop, Firing, WeaponInspectionState, Stance; whether reload command
   is present if exposed; and active IdleReloadSTM state. Show instance identity
   and changing frame/time in screenshots or video.
5. If AstraShell becomes active, also capture ShellReloadSTM active phase and
   MasterControl/SightPose pose contribution if exposed. Film the hands.
6. Send screenshots/video and script.log. If the UI cannot expose a requested
   field, state exactly which field is unavailable; do not fabricate a negative.

Interpretation: request false during confirmed W pulse identifies an input
boundary, not a clip failure. Request true plus any false gate identifies the
specific predicate to address. Active shell sources with no visible hands moves
the investigation to output contribution. Missing frame coverage is inconclusive.

## Current changes

This continuation document only. No gameplay edit, Workbench automation,
runtime emission, baseline ammo write or G3B2 call performed in this phase.
