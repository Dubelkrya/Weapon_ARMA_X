# MP-133 Task #1 — PACT attachment access probe: review evidence (Phase 1E, stage only)

Status: **PACT_PROBE_STAGE_READY_OWNER_REVIEW**
Date: 2026-10-07
Task: Issue #34 comment `6042531682` (Phase 1E — PACT ATTACHMENT ACCESS PROBE, STAGE ONLY).
Repo / branch / HEAD: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe` @ `a364a7c8fcb7cf0a3ee80f8d625a959a268ae2f2`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; nothing installed; no Workbench/runtime; no force-add.

---

## 1. Source baseline (owner's local lab) — verified

Functional source baseline = the owner's CURRENT local T4B lab (the reviewed WPROP install). Both match the required hashes:

| Local lab file | SHA-256 | required | match |
|---|---|---|---|
| `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `ECD8DF6F8A96292E4646EBD9F2DF17C1E4153E19361C6D1B08131E8F3E2FC95A` | `ECD8DF6F…` | YES |
| `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `8176B363B876AD105110303C49321266B133C892CF985DFAB9453DABF90B215D` | `8176B363…` | YES |

(Repo `labs/` intentionally differ: `F5D59DB9…` / `7BE1D375…`; not used as baseline.) No source drift ⇒ not `PACT_STAGE_BLOCKED_SOURCE_DRIFT`.

## 2. Staged output

Root: `artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/` (git-ignored; not committed, no `git add -f`).

| Staged file | SOURCE_SHA256 | STAGED_SHA256 | source blob | staged blob |
|---|---|---|---|---|
| `ARMST_T4B_CustomRInputProbe.c` | `ECD8DF6F…C95A` | `68AE302E2E0560CFFE87CAB867B6054AD273E1D97C0FFBE267356F335F036F3D` | `22a3db0` | `74d1209` |
| `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `8176B363…15D` | `8F84BFE4D5613F4AE41A750ADCC922E79CA00FF249988164F35395854FAF6E6F` | `fa49109` | `b5f1b54` |

Brace/paren balance: CustomR `{ }` 52/52, `( )` 262/262; AstraV2 `{ }` 34/34, `( )` 209/209.

## 3. Exact compile-visible accessor (source evidence)

```text
CONTROLLED_RUNTIME_TYPE = IEntity (SCR_PlayerController.GetControlledEntity()); SCR_CharacterControllerComponent via controlled.FindComponent(SCR_CharacterControllerComponent)
CAST_OR_ACCESSOR       = CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent))
                         fallback: CharacterEntity.Cast(controlled).GetAnimGraphComponent()
RETURN_TYPE            = CharacterAnimGraphComponent   (engine; : BaseAnimationControllerComponent : GenericComponent)
SOURCE_EVIDENCE        = EnfusionScriptAPI/html/interfaceCharacterEntity.html  (proto external CharacterAnimGraphComponent CharacterEntity.GetAnimGraphComponent())
                         EnfusionScriptAPI/html/interfaceCharacterAnimGraphComponent.html (inherits BaseAnimationControllerComponent)
                         EnfusionScriptAPI/html/interfaceBaseAnimationControllerComponent.html (BindAttachment/BindAttBoolVariable/SetAttBoolVariable/GetAttBoolVariable)
                         EnfusionScriptAPI/html/interfaceIEntity.html (proto external Managed FindComponent(TypeName))
                         Core precedent: ARMST-PLATFORM---Core/Scripts/Game/MUTANTS/ARMST_MUTANTS_ANIM_COMPONENT.c:31 and .../AGENT/Components/ARMST_MUTANT_MOVEMENT_COMPONENT.c:143
                           -> AnimationControllerComponent.Cast(owner.FindComponent(AnimationControllerComponent))
WHY_COMPILE_VISIBLE_FROM_GAME_SCRIPT = engine animation-controller classes are part of the script API; the identical
                         `EngineAnimControllerClass.Cast(entity.FindComponent(EngineAnimControllerClass))` pattern is already
                         compiled and used in this project (Core mutants) for a sibling of the same engine base.
```

The accessor is the only unknown the probe must falsify at runtime; both branches fail closed (log `phase=owner ok=false`) if the component/accessor is unavailable.

## 4. Static forbidden-operation scan (staged)

| Pattern | CustomRInputProbe | AstraV2 component |
|---|---|---|
| `SetAmmoCount` | 0 | 0 |
| `ClearChamber` | 0 | 0 |
| `DetachCurrentMagazine` | 0 | 0 |
| `ReloadWeaponWith` | 0 | 0 |
| bare `ReloadWeapon(` | 0 | 0 |
| `HandleWeaponReloading` | 0 | 0 |
| `CallLater` (timers) | 0 | 0 |
| `SetReloadWeapon` | 3 (all in the frozen rack helper: 1 call) | 0 |
| `G3B2` | 1 (header-comment word) | 0 |
| PACT calls present | `BindAttachment` 1, `BindAttBoolVariable` 4, `SetAttBoolVariable` write 6, `GetAttBoolVariable` read 3, `CharacterAnimGraphComponent` cast 2 | 0 (only delegates reset) |

The frozen rack predicate and `SetReloadWeapon(1)` path are **byte-identical** (only a call was appended in the non-rack helper).

## 5. Behavior and cleanup lifecycle

On the existing non-rack shell branch (after the unchanged `wcomp.T4BWPropRequest()`), `T4BRTryPact(ctrl, side)`:
1. obtains the character anim-graph owner (`phase=owner`);
2. `BindAttachment("Weapon")` (`phase=attachment`), fail-closed if `< 0`;
3. `BindAttBoolVariable` for `ASTRA_ShellRequest/Eligible/Repeat/Stop` (`phase=bind`), fail-closed if any `< 0`;
4. second-R safety: if `m_bPactActive` → write `Request=0/Eligible=0`, readback, log `phase=manual-abort`;
5. else write `Eligible=1, Repeat=0, Stop=0, Request=1`, readback Request, log `phase=request`, set `m_bPactActive`.

Cleanup (deterministic, no timer):
- **Preferred (implemented):** the W animation component, on the existing `ASTRA_Shell_ReturnReady_W` event, calls `SCR_PlayerController.Cast(GetGame().GetPlayerController()).T4BPactResetFromEvent()`, which writes attachment `Request=0/Eligible=0`, confirms readback, and logs `phase=reset source=return-ready`.
- **Fallback (implemented):** a second qualified R while still active performs `phase=manual-abort` (write 0 + readback).
- A failed bind/write never leaves `m_bPactActive` permanently asserted incorrectly: it is set from the Request readback only.

Second staged script justification: the preferred animation-event-based P reset cannot be implemented in the controller alone (the controller receives no animation events); it is delivered by the existing W animation component which already observes `ASTRA_Shell_ReturnReady_W`. The addition is 4 lines and does not change the W path semantics.

## 6. Expected compile outcomes

- `CharacterAnimGraphComponent`, `CharacterEntity`, `BindAttachment`, `BindAttBoolVariable`, `SetAttBoolVariable`, `GetAttBoolVariable` resolve from the game module (engine API + Core precedent).
- Both staged files compile together (same addon); `SCR_PlayerController.T4BPactResetFromEvent()` is a public method defined in the same addon.
- If the compiler rejects `CharacterEntity`/`CharacterAnimGraphComponent`, that is `PACT_COMPILE_BLOCKED` and the fallback `CharacterEntity` branch can be removed (FindComponent route alone).

## 7. Expected owner runtime logs (design only, not run here)

```
[ARMST-T4B-RINPUT] ... (non-rack shell-eligible state)
[ARMST-T4B-WPROP] phase=branch choice=shell ...
[ARMST-T4B-WPROP] phase=request session=1 ...
[ARMST-T4B-PACT] phase=owner ok=true via=findcomponent|charentity
[ARMST-T4B-PACT] phase=attachment ok=true id=<n> binding=Weapon
[ARMST-T4B-PACT] phase=bind ok=true req=.. elig=.. rep=.. stop=..
[ARMST-T4B-PACT] phase=request session=1 writeReq=1 writeElig=1 writeRep=0 writeStop=0 readbackReq=true active=true
... P and/or W marker families ...
[ARMST-T4B-PACT] phase=reset source=return-ready readbackReq=false readbackElig=false
[ARMST-T4B-WPROP] phase=return-ready ... ; phase=reset ...
```

## 8. PASS/FAIL classification table

| Outcome | Condition |
|---|---|
| `PACT_PW_PASS` | P family AND W family observed; P+W reset readback false; same Tube3; ammo/chamber unchanged; no gameplay mutation |
| `PACT_P_ONLY_FAIL` | P family yes / W no |
| `PACT_W_ONLY_FAIL` | attachment request succeeds (readback true) but P family still absent |
| `PACT_BIND_FAIL` | `phase=owner/attachment/bind ok=false` — accessor/attachment/variable not resolvable |
| `PACT_COMPILE_BLOCKED` | staged accessor/API not compile-visible |
| `PACT_GAMEPLAY_MUTATION_FAIL` | any forbidden gameplay mutation |

Key owner test fixture (deferred): Tube3 `< 3`, `chambered = 1`, not reloading, physical R once.

## 9. Unchanged / boundaries

No functional file changed. Local lab, repo `labs/`, AGR/AGF/AST/ASI/TXA/ANM, prefab, config/input/keyBindingMenu, `.meta`/GUID, G3B2, production Weapons/Core are byte-identical. Only this report and the plan are committed.

---

## 10. COMPLETE unified diff — `ARMST_T4B_CustomRInputProbe.c` (local lab → staged)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c" "b/artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c"
index 22a3db0..74d1209 100644
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
@@ -286,6 +301,126 @@ modded class SCR_PlayerController
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
+			bool abortReq = agc.GetAttBoolVariable(m_iPactAtt, m_iPactReq);
+			bool abortElig = agc.GetAttBoolVariable(m_iPactAtt, m_iPactElig);
+			m_bPactActive = false;
+			Print("[ARMST-T4B-PACT] phase=manual-abort writeReq=0 writeElig=0 readbackReq="
+				+ abortReq.ToString() + " readbackElig=" + abortElig.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+
+		m_iPactSession++;
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactElig, 1.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactRep, 0.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactStop, 0.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactReq, 1.0);
+		bool rb = agc.GetAttBoolVariable(m_iPactAtt, m_iPactReq);
+		m_bPactActive = rb;
+		Print("[ARMST-T4B-PACT] phase=request session=" + m_iPactSession.ToString()
+			+ " writeReq=1 writeElig=1 writeRep=0 writeStop=0 readbackReq=" + rb.ToString()
+			+ " active=" + m_bPactActive.ToString() + " side=" + side, LogLevel.NORMAL);
+	}
+
+	// O1 PHASE 1E PACT — deterministic reset from the existing W ReturnReady animation
+	// event lifecycle (invoked by the W animation component). Writes attachment
+	// Request=false + Eligible=false and confirms readback. No timer.
+	void T4BPactResetFromEvent()
+	{
+		if (!m_bPactActive)
+			return;
+		if (m_iPactAtt < 0 || m_iPactReq < 0 || m_iPactElig < 0)
+			return;
+		IEntity controlled = GetControlledEntity();
+		if (!controlled)
+			return;
+		CharacterAnimGraphComponent agc = CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent));
+		if (!agc)
+		{
+			CharacterEntity ce = CharacterEntity.Cast(controlled);
+			if (ce)
+				agc = ce.GetAnimGraphComponent();
+		}
+		if (!agc)
+			return;
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactReq, 0.0);
+		agc.SetAttBoolVariable(m_iPactAtt, m_iPactElig, 0.0);
+		bool rb = agc.GetAttBoolVariable(m_iPactAtt, m_iPactReq);
+		bool rbElig = agc.GetAttBoolVariable(m_iPactAtt, m_iPactElig);
+		m_bPactActive = false;
+		Print("[ARMST-T4B-PACT] phase=reset source=return-ready readbackReq=" + rb.ToString()
+			+ " readbackElig=" + rbElig.ToString(), LogLevel.NORMAL);
 	}
 
 	// Custom action callback: logs physical R and dispatches the T4B rack request.
```

## 11. COMPLETE unified diff — `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` (local lab → staged)

```diff
diff --git "a/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c" "b/artifacts/astra-rebuild/stageT4BPACTProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c"
index fa49109..b5f1b54 100644
@@ -211,6 +211,13 @@ class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComp
 		}
 		if (name == "ASTRA_Shell_ReturnReady_W")
 		{
+			// O1 PHASE 1E PACT: deterministic P-attachment reset from the existing W
+			// return-ready animation event lifecycle (delegates to the local player
+			// controller, which owns the PACT attachment handles). No timer.
+			SCR_PlayerController t4bPc = SCR_PlayerController.Cast(GetGame().GetPlayerController());
+			if (t4bPc)
+				t4bPc.T4BPactResetFromEvent();
+
 			if (m_iWPropSession > 0)
 			{
 				Print("[ARMST-T4B-WPROP] phase=return-ready session=" + m_iWPropSession.ToString()
```

Final status: **PACT_PROBE_STAGE_READY_OWNER_REVIEW**. STOP (no install, no compile, no runtime).
