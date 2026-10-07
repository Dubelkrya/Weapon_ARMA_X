# MP-133 Task #1 — PACT attachment access probe: review evidence (Phase 1E / R1 correction)

Status: **PACT_PROBE_STAGE_READY_OWNER_REVIEW_R1**
Date: 2026-10-07
Task: Issue #34 comment `6042807676` (Phase 1E R1 safety correction).
Repo / branch / HEAD (before this commit): `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `d40f679f76c5ed0502c2d0f1fbe6b522f8b2d153`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; nothing installed; no Workbench/runtime; no force-add.

---

## 0. R1 correction applied (three points)

| # | Requirement | Status |
|---|---|---|
| R1 | request readback verifies the whole gate `req==true, elig==true, rep==false, stop==false`; on mismatch fail closed + safe reset all four + log `phase=reject reason=request-state-mismatch` | **DONE** |
| R2 | reset/manual-abort must not force inactive when reset failed; `m_bPactActive = (rbReq || rbElig)`; log `resetClean=`; clear Repeat/Stop too | **DONE** |
| R3 | reset on `ASTRA_Shell_ReturnReady_P`; `W ReturnReady` only if no P family observed; if P started but no P ReturnReady → leave active (second-R abort) | **DONE** |

Reset sources are logged distinctly: `source=p-return-ready`, `source=w-return-ready-no-p`, `source=manual-abort`.

---

## 1. Source baseline (owner's local lab) — verified

| Local lab file | SHA-256 | required | match |
|---|---|---|---|
| `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `ECD8DF6F8A96292E4646EBD9F2DF17C1E4153E19361C6D1B08131E8F3E2FC95A` | `ECD8DF6F…` | YES |
| `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `8176B363B876AD105110303C49321266B133C892CF985DFAB9453DABF90B215D` | `8176B363…` | YES |

No source drift.

## 2. Staged output (R1)

Root: `artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/` (git-ignored; not committed).

| Staged file | SOURCE_SHA256 | STAGED_SHA256 (R1) | source blob | staged blob |
|---|---|---|---|---|
| `ARMST_T4B_CustomRInputProbe.c` | `ECD8DF6F…C95A` | `2568DA60441BE34D6E0E96613393B4099A07B70875EC5AAB2CE10E8C8289D3E6` | `22a3db0` | `f661cd9` |
| `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `8176B363…15D` | `411D5E127C5E97D6A3BAAA91D7B79C0CE662F06600D03EC31080A2C878C72640` | `fa49109` | `8afef00` |

(Prior, superseded O1E staging: CustomR `68AE302E…`, AstraV2 `8F84BFE4…`.) Brace/paren: CustomR `{ }` 53/53, `( )` 303/303; AstraV2 `{ }` 36/36, `( )` 216/216.

## 3. Exact compile-visible accessor (unchanged, source evidence)

```text
CONTROLLED_RUNTIME_TYPE = IEntity (SCR_PlayerController.GetControlledEntity()); SCR_CharacterControllerComponent via controlled.FindComponent(SCR_CharacterControllerComponent)
CAST_OR_ACCESSOR       = CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent))
                         fallback: CharacterEntity.Cast(controlled).GetAnimGraphComponent()
RETURN_TYPE            = CharacterAnimGraphComponent   (engine; : BaseAnimationControllerComponent : GenericComponent)
SOURCE_EVIDENCE        = EnfusionScriptAPI/html/interfaceCharacterEntity.html (CharacterEntity.GetAnimGraphComponent -> CharacterAnimGraphComponent)
                         EnfusionScriptAPI/html/interfaceCharacterAnimGraphComponent.html (inherits BaseAnimationControllerComponent)
                         EnfusionScriptAPI/html/interfaceBaseAnimationControllerComponent.html (BindAttachment/BindAttBoolVariable/SetAttBoolVariable/GetAttBoolVariable)
                         EnfusionScriptAPI/html/interfaceIEntity.html (proto external Managed FindComponent(TypeName))
                         Core precedent: ARMST-PLATFORM---Core/Scripts/Game/MUTANTS/ARMST_MUTANTS_ANIM_COMPONENT.c:31 and .../ARMST_MUTANT_MOVEMENT_COMPONENT.c:143
                           -> AnimationControllerComponent.Cast(owner.FindComponent(AnimationControllerComponent))
WHY_COMPILE_VISIBLE_FROM_GAME_SCRIPT = engine animation-controller classes are part of the script API; the identical
                         `EngineAnimControllerClass.Cast(entity.FindComponent(EngineAnimControllerClass))` pattern is already
                         compiled and used in this project (Core) for a sibling of the same engine base.
```

## 4. Static forbidden-operation scan (R1 staged)

| Pattern | CustomRInputProbe | AstraV2 component |
|---|---|---|
| `SetAmmoCount` / `ClearChamber` | 0 / 0 | 0 / 0 |
| bare `ReloadWeapon(` / `ReloadWeaponWith` | 0 / 0 | 0 / 0 |
| `HandleWeaponReloading` | 0 | 0 |
| `CallLater` (timers) | 0 | 0 |
| `SetReloadWeapon` | 3 (frozen rack helper only) | 0 |
| `GetAttBoolVariable` | 12 (all-4 readbacks + resets) | 0 |

## 5. Behavior and cleanup lifecycle (R1)

On the non-rack shell branch (after the unchanged `wcomp.T4BWPropRequest()`), `T4BRTryPact(ctrl, side)`:
`phase=owner` → `phase=attachment` (`BindAttachment("Weapon")`, fail-closed) → `phase=bind` (4 vars, fail-closed) → then:
- if `m_bPactActive` → **manual abort**: write `Request=0/Eligible=0/Repeat=0/Stop=0`, readback Req+Elig, `m_bPactActive=(rbReq||rbElig)`, log `phase=manual-abort source=manual-abort resetClean=…`;
- else write `Eligible=1/Repeat=0/Stop=0/Request=1`, **read back all four**, require `req&&elig&&!rep&&!stop`; on mismatch safe-reset all four, `m_bPactActive=(any true)`, log `phase=reject reason=request-state-mismatch`; on success `m_bPactActive=true`, log `phase=request … rbReq/rbElig/rbRep/rbStop`.

Deterministic cleanup (no timer), per R3:
- `ASTRA_Shell_ReturnReady_P` observed → `T4BPactResetFromEvent("p-return-ready")` (authoritative);
- `ASTRA_Shell_ReturnReady_W` observed **and no P family seen** (`!m_bWPropSawP`) → `T4BPactResetFromEvent("w-return-ready-no-p")`;
- P started but no P ReturnReady → PACT stays active → second qualified R `manual-abort`.

`T4BPactResetFromEvent(source)` writes all four to false, reads back Req+Elig, `m_bPactActive=(rbReq||rbElig)`, logs `phase=reset source=<source> resetClean=…`.

Second staged script justification: the P reset must be triggered by an animation event, which only the W animation component receives; the extension is minimal and does not change the W path semantics.

## 6. Expected compile outcomes

- `CharacterAnimGraphComponent`, `CharacterEntity`, `BindAttachment`, `BindAttBoolVariable`, `SetAttBoolVariable`, `GetAttBoolVariable` resolve from the game module (engine API + Core precedent).
- Both staged files compile together (same addon).
- If the compiler rejects the engine classes → `PACT_COMPILE_BLOCKED`; the `CharacterEntity` fallback branch can then be removed (FindComponent route alone).

## 7. Expected owner runtime logs (design only, not run here)

```
[ARMST-T4B-PACT] phase=owner ok=true via=findcomponent|charentity
[ARMST-T4B-PACT] phase=attachment ok=true id=<n> binding=Weapon
[ARMST-T4B-PACT] phase=bind ok=true req=.. elig=.. rep=.. stop=..
[ARMST-T4B-PACT] phase=request session=1 writeReq=1 writeElig=1 writeRep=0 writeStop=0 rbReq=true rbElig=true rbRep=false rbStop=false active=true side=..
... P and/or W marker families ...
[ARMST-T4B-PACT] phase=reset source=p-return-ready|w-return-ready-no-p resetClean=true rbReq=false rbElig=false active=false
   (or) [ARMST-T4B-PACT] phase=manual-abort source=manual-abort resetClean=true ... active=false
   (on failure) [ARMST-T4B-PACT] phase=reject reason=request-state-mismatch ... resetReq/.. active=..
```

## 8. PASS/FAIL classification table

| Outcome | Condition |
|---|---|
| `PACT_PW_PASS` | P family AND W family observed; reset `source=p-return-ready`, resetClean=true; same Tube3; ammo/chamber unchanged |
| `PACT_P_ONLY_FAIL` | P family yes / W no |
| `PACT_W_ONLY_FAIL` | request readback OK but P family absent (reset via `w-return-ready-no-p`) |
| `PACT_BIND_FAIL` | `phase=owner/attachment/bind ok=false` |
| `PACT_COMPILE_BLOCKED` | staged accessor/API not compile-visible |
| `PACT_GAMEPLAY_MUTATION_FAIL` | any forbidden gameplay mutation |

## 9. Unchanged / boundaries

No functional file changed. Local lab, repo `labs/`, AGR/AGF/AST/ASI/TXA/ANM, prefab, config/input/keyBindingMenu, `.meta`/GUID, G3B2, production Weapons/Core are byte-identical. Only this report and the plan are committed.

---

## 10. COMPLETE unified diff — `ARMST_T4B_CustomRInputProbe.c` (local lab → staged R1)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c" "b/artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c"
index 22a3db0..f661cd9 100644
@@ -44,6 +44,12 @@
 // AstraV2 weapon animation component (bind/set ASTRA_Shell* on the W instance).
 // Frozen rack branch above is unchanged; no ammo/mag/chamber writes; no native
 // reload; no cmd1..6; no P-side setter. Diagnostics print [ARMST-T4B-WPROP].
+//
+// O1 PHASE 1E ADDITION (stageT4BPACTProbe): in the same non-rack shell branch an
+// attachment-aware P-side request is dispatched (engine CharacterAnimGraphComponent
+// -> BindAttachment("Weapon") -> BindAttBoolVariable("ASTRA_Shell*") -> SetAttBoolVariable).
+// Animation-only; no ammo/mag/chamber writes; no native reload; no cmd1..6.
+// Diagnostics print [ARMST-T4B-PACT]; reset is event-based + second-R fallback.
 // ============================================================================
 modded class SCR_PlayerController
 {
@@ -58,6 +64,15 @@ modded class SCR_PlayerController
 	protected bool m_bT4BRContextResultLogged;
 	protected const int ARMST_T4B_RACK_RELOAD_TYPE = 1;
 
+	// O1 PHASE 1E PACT attachment-aware P-side probe state.
+	protected int m_iPactAtt = -1;
+	protected int m_iPactReq = -1;
+	protected int m_iPactElig = -1;
+	protected int m_iPactRep = -1;
+	protected int m_iPactStop = -1;
+	protected int m_iPactSession;
+	protected bool m_bPactActive;
+
 	override void OnUpdate(float timeSlice)
 	{
 		super.OnUpdate(timeSlice);
@@ -286,6 +301,158 @@ modded class SCR_PlayerController
 			+ "/" + maxAmmo.ToString() + " chambered=" + chambered.ToString()
 			+ " side=" + side, LogLevel.NORMAL);
 		wcomp.T4BWPropRequest();
+
+		T4BRTryPact(ctrl, side);
+	}
+
+	// O1 PHASE 1E PACT — attachment-aware P-side request probe. Animation-only.
+	// Addresses the character's injected attachment "Weapon" through the engine
+	// CharacterAnimGraphComponent (BaseAnimationControllerComponent family; same
+	// FindComponent pattern proven in Core) and binds/writes ASTRA_Shell* on THAT
+	// attachment instance. Fail-closed on any unresolved handle. No ammo/mag/chamber
+	// writes; no native reload; no cmd1..6.
+	protected void T4BRTryPact(SCR_CharacterControllerComponent ctrl, string side)
+	{
+		IEntity controlled = null;
+		if (ctrl)
+			controlled = ctrl.GetOwner();
+		if (!controlled)
+		{
+			Print("[ARMST-T4B-PACT] phase=owner ok=false reason=no-controlled side=" + side, LogLevel.NORMAL);
+			return;
+		}
+
+		CharacterAnimGraphComponent agc = CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent));
+		string via = "findcomponent";
+		if (!agc)
+		{
+			CharacterEntity ce = CharacterEntity.Cast(controlled);
+			if (ce)
+			{
+				agc = ce.GetAnimGraphComponent();
+				via = "charentity";
+			}
+		}
+		if (!agc)
+		{
+			Print("[ARMST-T4B-PACT] phase=owner ok=false reason=anim-graph-component-unavailable side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		Print("[ARMST-T4B-PACT] phase=owner ok=true via=" + via + " side=" + side, LogLevel.NORMAL);
+
+		if (m_iPactAtt < 0)
+			m_iPactAtt = agc.BindAttachment("Weapon");
+		if (m_iPactAtt < 0)
+		{
+			Print("[ARMST-T4B-PACT] phase=attachment ok=false id=" + m_iPactAtt.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		Print("[ARMST-T4B-PACT] phase=attachment ok=true id=" + m_iPactAtt.ToString() + " binding=Weapon", LogLevel.NORMAL);
+
+		if (m_iPactReq < 0)
+		{
+			m_iPactReq = agc.BindAttBoolVariable(m_iPactAtt, "ASTRA_ShellRequest");
+			m_iPactElig = agc.BindAttBoolVariable(m_iPactAtt, "ASTRA_ShellEligible");
+			m_iPactRep = agc.BindAttBoolVariable(m_iPactAtt, "ASTRA_ShellRepeat");
+			m_iPactStop = agc.BindAttBoolVariable(m_iPactAtt, "ASTRA_ShellStop");
+		}
+		if (m_iPactReq < 0 || m_iPactElig < 0 || m_iPactRep < 0 || m_iPactStop < 0)
+		{
+			Print("[ARMST-T4B-PACT] phase=bind ok=false req=" + m_iPactReq.ToString()
+				+ " elig=" + m_iPactElig.ToString() + " rep=" + m_iPactRep.ToString()
+				+ " stop=" + m_iPactStop.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		Print("[ARMST-T4B-PACT] phase=bind ok=true req=" + m_iPactReq.ToString()
+			+ " elig=" + m_iPactElig.ToString() + " rep=" + m_iPactRep.ToString()
+			+ " stop=" + m_iPactStop.ToString(), LogLevel.NORMAL);
+
+		if (m_bPactActive)
+		{
+			// Deterministic manual abort (fallback): a second qualified R while still
+			// active clears the P request instead of requesting again. No timer.
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactReq, 0.0);
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactElig, 0.0);
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactRep, 0.0);
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactStop, 0.0);
+			bool abortReq = agc.GetAttBoolVariable(m_iPactAtt, m_iPactReq);
+			bool abortElig = agc.GetAttBoolVariable(m_iPactAtt, m_iPactElig);
+			bool abortClean = (!abortReq && !abortElig);
+			m_bPactActive = (abortReq || abortElig);   // R2: stay active if reset not clean
+			Print("[ARMST-T4B-PACT] phase=manual-abort source=manual-abort resetClean=" + abortClean.ToString()
+				+ " rbReq=" + abortReq.ToString() + " rbElig=" + abortElig.ToString()
+				+ " active=" + m_bPactActive.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+
+		m_iPactSession++;
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactElig, 1.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactRep, 0.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactStop, 0.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactReq, 1.0);
+		bool rbReq = agc.GetAttBoolVariable(m_iPactAtt, m_iPactReq);
+		bool rbElig = agc.GetAttBoolVariable(m_iPactAtt, m_iPactElig);
+		bool rbRep = agc.GetAttBoolVariable(m_iPactAtt, m_iPactRep);
+		bool rbStop = agc.GetAttBoolVariable(m_iPactAtt, m_iPactStop);
+		if (!(rbReq && rbElig && !rbRep && !rbStop))
+		{
+			// R1: whole-gate readback failed -> fail closed and safe-reset all four.
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactReq, 0.0);
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactElig, 0.0);
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactRep, 0.0);
+			agc.SetAttBoolVariable(m_iPactAtt, m_iPactStop, 0.0);
+			bool srReq = agc.GetAttBoolVariable(m_iPactAtt, m_iPactReq);
+			bool srElig = agc.GetAttBoolVariable(m_iPactAtt, m_iPactElig);
+			bool srRep = agc.GetAttBoolVariable(m_iPactAtt, m_iPactRep);
+			bool srStop = agc.GetAttBoolVariable(m_iPactAtt, m_iPactStop);
+			m_bPactActive = (srReq || srElig || srRep || srStop);
+			Print("[ARMST-T4B-PACT] phase=reject reason=request-state-mismatch session=" + m_iPactSession.ToString()
+				+ " rbReq=" + rbReq.ToString() + " rbElig=" + rbElig.ToString() + " rbRep=" + rbRep.ToString() + " rbStop=" + rbStop.ToString()
+				+ " resetReq=" + srReq.ToString() + " resetElig=" + srElig.ToString() + " resetRep=" + srRep.ToString() + " resetStop=" + srStop.ToString()
+				+ " active=" + m_bPactActive.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		m_bPactActive = true;
+		Print("[ARMST-T4B-PACT] phase=request session=" + m_iPactSession.ToString()
+			+ " writeReq=1 writeElig=1 writeRep=0 writeStop=0"
+			+ " rbReq=" + rbReq.ToString() + " rbElig=" + rbElig.ToString() + " rbRep=" + rbRep.ToString() + " rbStop=" + rbStop.ToString()
+			+ " active=" + m_bPactActive.ToString() + " side=" + side, LogLevel.NORMAL);
 	}
 
 	// Custom action callback: logs physical R and dispatches the T4B rack request.
```

(Reset method `T4BPactResetFromEvent(string source)` added after `T4BRTryPact`, with R2 readback semantics and sources `p-return-ready` / `w-return-ready-no-p`.)

## 11. COMPLETE unified diff — `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` (local lab → staged R1)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c" "b/artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c"
index fa49109..8afef00 100644
@@ -209,8 +209,25 @@ class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComp
 					+ " first=" + name, LogLevel.NORMAL);
 			}
 		}
-		if (name == "ASTRA_Shell_ReturnReady_W")
+		// R3: PACT reset lifecycle. P ReturnReady is authoritative; W ReturnReady resets
+		// only when no P family was observed (W-only / no-P fallback). If P started but
+		// never reaches P ReturnReady, PACT stays active so the second-R manual abort
+		// remains available. No timer.
+		if (name == "ASTRA_Shell_ReturnReady_P")
 		{
+			SCR_PlayerController t4bPcP = SCR_PlayerController.Cast(GetGame().GetPlayerController());
+			if (t4bPcP)
+				t4bPcP.T4BPactResetFromEvent("p-return-ready");
+		}
+		else if (name == "ASTRA_Shell_ReturnReady_W")
+		{
+			if (!m_bWPropSawP)
+			{
+				SCR_PlayerController t4bPcW = SCR_PlayerController.Cast(GetGame().GetPlayerController());
+				if (t4bPcW)
+					t4bPcW.T4BPactResetFromEvent("w-return-ready-no-p");
+			}
+
 			if (m_iWPropSession > 0)
 			{
 				Print("[ARMST-T4B-WPROP] phase=return-ready session=" + m_iWPropSession.ToString()
```

---

## Required final fields

```
HEAD =
CUSTOM_R_SOURCE_SHA256 = ECD8DF6F8A96292E4646EBD9F2DF17C1E4153E19361C6D1B08131E8F3E2FC95A
CUSTOM_R_STAGED_SHA256 = 2568DA60441BE34D6E0E96613393B4099A07B70875EC5AAB2CE10E8C8289D3E6
ASTRA_SOURCE_SHA256 = 8176B363B876AD105110303C49321266B133C892CF985DFAB9453DABF90B215D
ASTRA_STAGED_SHA256 = 411D5E127C5E97D6A3BAAA91D7B79C0CE662F06600D03EC31080A2C878C72640
REQUEST_READBACK_ALL4 = YES
MISMATCH_SAFE_RESET = YES
RESET_ACTIVE_FROM_READBACK = YES
P_RETURN_READY_PRIMARY_RESET = YES
W_RETURN_READY_NO_P_FALLBACK = YES
SECOND_R_MANUAL_ABORT = YES
FUNCTIONAL_FILES_CHANGED = NO
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
G3B2_CHANGED = NO
LIVE_CHANGED = NO
WORKBENCH_LAUNCHED = NO
RUNTIME_TEST = NO
```

Final status: **PACT_PROBE_STAGE_READY_OWNER_REVIEW_R1**. STOP (no install, no compile, no runtime).
