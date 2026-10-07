# MP-133 Task #1 — WPROP probe review evidence (O1 / PHASE 1C + O1R / PHASE 1C-R)

Status: **T4B_WPROP_PROBE_REVIEW_READY_OWNER_GO**
Date: 2026-10-07
Task: Issue #34 comments `6039392248` (architecture authority) and `6041185715` (O1R authorization).
Repo / branch: `Dubelkrya/Weapon_ARMA_X` @ `t4b/installed-mag-probe`.
Starting HEAD for O1: `b7312401444501a67a4849d6dd54bbcbf3a02a19`. Current HEAD after the O1 plan commit: `524f43f4358e52114d9cf2fea8878ad047598ef2`.
Mode: **SOURCE / STATIC ONLY.** Staged scratch under git-ignored `artifacts/`; not installed; no `git add -f`; no runtime/Workbench.

This is the durable, independently reviewable record of the staged W-local request propagation probe (O1) plus the O1R safety correction. The staged scripts themselves live only under ignored `artifacts/`; the complete diffs below are the reviewable evidence.

---

## 1. Source identity

Tracked source at current HEAD `524f43f4358e52114d9cf2fea8878ad047598ef2`:

| Tracked file | blob | SHA-256 |
|---|---|---|
| `labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `02d1ada4a9f232a420eb7f37cacc41b25d58f551` | `F5D59DB9D00469E4664DE219CF29110A40D6DCE73DE23846ED60C44B6EFA68C1` |
| `labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `45e2a1455ef7891ed1ba26d2f2d3e8e6f5ae802d` | `7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A` |

Staged scratch (untracked, git-ignored, O1R `artifacts/astra-rebuild/stageT4BWPropagationProbe/Scripts/Game/ARMST_T4B/`):

| Staged file | blob | SHA-256 |
|---|---|---|
| `ARMST_T4B_CustomRInputProbe.c` | `22a3db040bca3b83c052e4b85b1e7bfaa4957a50` | `ECD8DF6F8A96292E4646EBD9F2DF17C1E4153E19361C6D1B08131E8F3E2FC95A` |
| `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `fa49109f19c12aef805dfc993324c7948744691c` | `8176B363B876AD105110303C49321266B133C892CF985DFAB9453DABF90B215D` |

Both staged files originate from the CURRENT HEAD blobs above; only the O1/O1R delta was applied.

---

## 2. Exact fail-closed gate (R1)

Inside the complementary NON-RACK helper `T4BRTryShellProp`, before any WPROP request and in this order:

```
not T4B                      -> return (no log)
no controller                -> return (no log)
ctrl.IsReloading()           -> reject reason=busy-reloading
!magPresent                  -> reject reason=no-magazine
maxAmmo <= 0 || ammo < 0     -> reject reason=unresolved-ammo
ammo >= maxAmmo              -> reject reason=tube-full
chambered < 0 || chambered>1 -> reject reason=unresolved-chamber
no weapon manager/weapon/entity/W-anim-component -> reject (specific reason)
otherwise                    -> [ARMST-T4B-WPROP] phase=branch choice=shell ; W request
```

Equivalent required precondition: `magPresent == true && maxAmmo > 0 && ammo >= 0 && ammo < maxAmmo && (chambered == 0 || chambered == 1)`.

The frozen rack predicate/call (`T4BRTryRack(ctrl, labWeapon, magPresent, ammo, chambered, side)`, body and `ARMST_T4B_RACK_RELOAD_TYPE`) is **byte-identical**; the shell helper runs only when `!(magPresent && ammo > 0 && chambered == 0)`.

---

## 3. Exact manual-abort / reset path (R2)

Inside the W component `ARMST_T4B_AstraV2_WeaponAnimationComponent`:

- New explicit state `bool m_bWPropActive`.
- `T4BWPropRequest()`:
  - `T4BWPropBind()` (lazy one-time `BindBoolVariable` of `ASTRA_ShellRequest/Eligible/Repeat/Stop`).
  - if any bind id `< 0` (bounded inferred sentinel; see §6) → `m_bWPropActive = false`; `phase=reject reason=bind-invalid`; return false.
  - if `m_bWPropActive` → **deterministic manual abort (no timer)**: `SetBoolVariable(Request,false)`, `SetBoolVariable(Eligible,false)`, readback, log `phase=manual-abort`, `m_bWPropActive=false`, return false (no second session).
  - otherwise start one session: `session++`, clear `m_bWPropSawP/sawW`, write `Eligible=1, Repeat=0, Stop=0, Request=1`, readback all four; `m_bWPropActive = reqRb`.
  - if the request write did not read back true → safe reset (`Request=0, Eligible=0`), log `phase=reject reason=request-not-observable (safe reset applied)`, `m_bWPropActive` stays false.
  - else log `phase=request`.
- `T4BWPropReset()` (normal path): `Request=0`, `Eligible=0`, readback, `m_bWPropActive=false`, log `phase=reset`.
- `OnAnimationEvent`: on `ASTRA_Shell_ReturnReady_W` (existing W end/return-ready marker) while a session is active → log `phase=return-ready` (with `sawP/sawW`) and call `T4BWPropReset()`.
- P/W family observation flags are cleared at the start of each session.

Deterministic cleanup summary: PASS path resets on `ReturnReady_W`; FAIL/no-event path resets on the next qualified R via `manual-abort`; bind/write/readback failure never leaves the session active. **No timers.**

---

## 4. Static writer / call-site scan (staged)

| Pattern | CustomRInputProbe | AstraV2 component |
|---|---|---|
| `SetAmmoCount` | 0 | 0 |
| `ClearChamber` | 0 | 0 |
| `DetachCurrentMagazine` | 0 | 0 |
| `ReloadWeaponWith` | 0 | 0 |
| `SpawnMagazine` / `AttachMagazine` / `DetachMagazine` | 0 | 0 |
| `HandleWeaponReloading` | 0 | 0 |
| `CallLater` | 0 | 0 |
| bare `ReloadWeapon(` | 0 | 0 |
| `SetReloadWeapon` | 3 (all in the frozen rack helper/comment: 1 call) | 0 |
| `BindBoolVariable` / `SetBoolVariable` / `GetBoolVariable` | 0 | 5 / 11 / 9 (incl. signature comment) |
| `G3B2` | 1 (header-comment word only) | 0 |

Brace/paren balance: CustomRInputProbe `{ }` 41/41, `( )` 181/181; AstraV2 `{ }` 34/34, `( )` 203/203. No `git add -f`; the staged files are not committed.

---

## 5. P/W marker source classification (static, CURRENT labs `.txa`)

`P_Astra_*.txa` contain only `*_P` markers; `W_Astra_*.txa` contain only `*_W` markers:

| Source clip family | markers |
|---|---|
| `P_Astra_StartReload/GrabShell/InsertShell/CheckContinue/EndReload` | `ASTRA_Shell_StartReload_P`, `_GrabShell_P`, `_InsertShell_P`, `ASTRA_ShellInsertCommit_P`, `_CheckContinue_P`, `_EndReload_P`, `_ReturnReady_P`, `_Stop_P` |
| `W_Astra_StartReload/GrabShell/InsertShell/CheckContinue/EndReload` | matching `..._W`, incl. `ASTRA_ShellInsertCommit_W` in `W_Astra_InsertShell` only |

⇒ `*_P` originate only from P sources and `*_W` only from W sources, so an owner log containing both families proves both source sides executed even when callbacks are delivered to the same weapon receiver. **Gameplay authority remains W-only (`ASTRA_ShellInsertCommit_W`). P markers are visual/diagnostic only.**

---

## 6. Residual (bounded) assumptions

- The `< 0` bind-id invalid sentinel is an inferred assumption; the engine bind documentation does not publish a sentinel. The readback (`GetBoolVariable`) is the authoritative signal, and a non-observable write performs a safe reset (§3).
- W variable bind lifetime across weapon re-attach is not reset here; the probe is bounded to one fixture and one session per qualified R.

Neither affects the "no gameplay mutation / no native reload / no cmd1..6" invariants.

---

## 7. Owner runtime protocol (NOT authorized; description only)

State: canonical T4B MP-133, non-rack **shell-eligible** (e.g. tube `N < max`, chamber state resolves to 0 or 1), one physical R.

Expected on the first R:
```
RINPUT = YES
[ARMST-T4B-WPROP] phase=bind ...
[ARMST-T4B-WPROP] phase=branch choice=shell ...
[ARMST-T4B-WPROP] phase=request session=1 ...
P family executes   (phase=family-P ... first=<*_P name>)
W family executes   (phase=family-W ... first=<*_W name>)
[ARMST-T4B-WPROP] phase=return-ready ... sawP=1 sawW=1
[ARMST-T4B-WPROP] phase=reset ... readbackReq=0 readbackElig=0
cmd2..6 = 0 ; shell-probe cmd1 = 0 ; G3B2 = 0
ammo before == after ; donor before == after ; chamber before == after ; same Tube3 identity
controls remain functional
```
If W-local propagation does **not** run the graph, `ReturnReady_W` never arrives; a second R logs `phase=manual-abort` and clears `Request/Eligible`. That negative result is a valid probe outcome (W-only or no-graph).

W-only is NOT PASS. P-only is NOT PASS. Any gameplay-state mutation is FAIL. Install/compile/runtime require a separate owner GO.

---

## 8. Unchanged / boundaries

```
CURRENT_LABS_CHANGED = NO
LIVE_CHANGED = NO
GRAPH_CHANGED = NO
PREFAB_CHANGED = NO
INPUT_CONFIG_CHANGED = NO
META_CHANGED = NO
GUID_CHANGED = NO
G3B2_CHANGED = NO
G3B2_CALLED = NO
AMMO_WRITES_ADDED = NO
CHAMBER_WRITES_ADDED = NO
MAG_WRITES_ADDED = NO
SHELL_SETRELOADWEAPON_ADDED = NO
CMD2_6_ROUTE_ADDED = NO
PROVEN_RACK_BRANCH_CHANGED = NO
WORKBENCH_LAUNCHED = NO
REFORGER_LAUNCHED = NO
GAME_MODE_LAUNCHED = NO
RUNTIME_TEST = NO
COMPILE_TEST = NOT_RUN_BY_AGENT
```

Current labs/live/graph/prefab/config/meta/GUID are byte-unchanged by O1/O1R. Only tracked changes are the plan update and this report.

---

## 9. COMPLETE unified diff — `ARMST_T4B_CustomRInputProbe.c` (source → staged)

```diff
diff --git "a/labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c" "b/artifacts/astra-rebuild/stageT4BWPropagationProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c"
index 02d1ada..22a3db0 100644
@@ -38,6 +38,12 @@
 // callback a fail-closed T4B rack request is added (SetReloadWeapon(type=1)).
 // No ammo/mag/chamber writes; no input-config/ASTRA/G3B2 change; held off by
 // IsReloading(). Diagnostics print [ARMST-T4B-RACK]. Everything else identical.
+//
+// O1 PHASE 1C ADDITION (stageT4BWPropagationProbe): in the complementary NON-RACK
+// branch only, an animation-only weapon-local shell request is dispatched to the
+// AstraV2 weapon animation component (bind/set ASTRA_Shell* on the W instance).
+// Frozen rack branch above is unchanged; no ammo/mag/chamber writes; no native
+// reload; no cmd1..6; no P-side setter. Diagnostics print [ARMST-T4B-WPROP].
 // ============================================================================
 modded class SCR_PlayerController
 {
@@ -213,6 +219,75 @@ modded class SCR_PlayerController
 			+ " side=" + side, LogLevel.NORMAL);
 	}
 
+	// O1 PHASE 1C — complementary NON-RACK shell branch (animation-only W-local
+	// request propagation probe). No ammo/mag/chamber writes, no native reload,
+	// no cmd1..6. The frozen rack branch above is untouched and still runs first.
+	protected void T4BRTryShellProp(SCR_CharacterControllerComponent ctrl, bool labWeapon, bool magPresent, int ammo, int maxAmmo, int chambered, string side)
+	{
+		if (!labWeapon)
+			return;
+		if (!ctrl)
+			return;
+		if (ctrl.IsReloading())
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=busy-reloading side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		if (!magPresent)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=no-magazine side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		// R1 fail-closed gate: never start animation from unresolved/invalid telemetry.
+		// Required: magPresent==true, maxAmmo>0, ammo>=0, ammo<maxAmmo, chambered in {0,1}.
+		if (maxAmmo <= 0 || ammo < 0)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=unresolved-ammo ammo=" + ammo.ToString()
+				+ " maxAmmo=" + maxAmmo.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		if (ammo >= maxAmmo)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=tube-full ammo=" + ammo.ToString()
+				+ "/" + maxAmmo.ToString() + " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		if (chambered < 0 || chambered > 1)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=unresolved-chamber chambered=" + chambered.ToString()
+				+ " side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
+		if (!wm)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=no-weapon-manager side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
+		if (!wpn)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=no-current-weapon side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		IEntity we = wpn.GetOwner();
+		if (!we)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=no-weapon-entity side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		ARMST_T4B_AstraV2_WeaponAnimationComponent wcomp = ARMST_T4B_AstraV2_WeaponAnimationComponent.Cast(we.FindComponent(ARMST_T4B_AstraV2_WeaponAnimationComponent));
+		if (!wcomp)
+		{
+			Print("[ARMST-T4B-WPROP] phase=reject reason=no-w-anim-component side=" + side, LogLevel.NORMAL);
+			return;
+		}
+		Print("[ARMST-T4B-WPROP] phase=branch choice=shell ammo=" + ammo.ToString()
+			+ "/" + maxAmmo.ToString() + " chambered=" + chambered.ToString()
+			+ " side=" + side, LogLevel.NORMAL);
+		wcomp.T4BWPropRequest();
+	}
+
 	// Custom action callback: logs physical R and dispatches the T4B rack request.
 	protected void T4BRInputDown(float value = 0.0, EActionTrigger reason = 0)
 	{
@@ -273,5 +348,9 @@ modded class SCR_PlayerController
 			+ " chambered=" + chambered.ToString(), LogLevel.NORMAL);
 
 		T4BRTryRack(ctrl, labWeapon, magPresent, ammo, chambered, side);
+
+		bool rackPredicate = (magPresent && ammo > 0 && chambered == 0);
+		if (!rackPredicate)
+			T4BRTryShellProp(ctrl, labWeapon, magPresent, ammo, maxAmmo, chambered, side);
 	}
 }
```

---

## 10. COMPLETE unified diff — `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` (source → staged)

```diff
diff --git "a/labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c" "b/artifacts/astra-rebuild/stageT4BWPropagationProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c"
index 45e2a14..fa49109 100644
@@ -37,6 +37,17 @@ class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComp
 	// passive native mag-event correlation counter
 	protected int m_iMagEvtSeq;
 
+	// O1 PHASE 1C W-local request propagation probe (weapon-local setters only).
+	protected bool m_bWPropBound;
+	protected int m_iWPropReq = -1;
+	protected int m_iWPropElig = -1;
+	protected int m_iWPropRep = -1;
+	protected int m_iWPropStop = -1;
+	protected int m_iWPropSession;
+	protected bool m_bWPropActive;
+	protected bool m_bWPropSawP;
+	protected bool m_bWPropSawW;
+
 	protected void AstraEnsureInstanceInit()
 	{
 		if (m_bInstanceInitLogged)
@@ -47,6 +58,104 @@ class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComp
 		Print("[ARMST-T4B-ASTRA] component_init instance=" + m_iInstance.ToString() + " init=lazy_first_event", LogLevel.NORMAL);
 	}
 
+	// O1 PHASE 1C — bind the CURRENT graph's shell request variables on THIS weapon
+	// instance. Source-proven engine API on the AnimationControllerComponent family
+	// (EnfusionScriptAPI interfaceBaseAnimationControllerComponent.html):
+	//   proto external int  BindBoolVariable(string varName)
+	//   proto external void SetBoolVariable(int varId, bool value)
+	//   proto external bool GetBoolVariable(int varId)
+	protected void T4BWPropBind()
+	{
+		if (m_bWPropBound)
+			return;
+		m_bWPropBound = true;
+		m_iWPropReq = BindBoolVariable("ASTRA_ShellRequest");
+		m_iWPropElig = BindBoolVariable("ASTRA_ShellEligible");
+		m_iWPropRep = BindBoolVariable("ASTRA_ShellRepeat");
+		m_iWPropStop = BindBoolVariable("ASTRA_ShellStop");
+		Print("[ARMST-T4B-WPROP] phase=bind req=" + m_iWPropReq.ToString()
+			+ " elig=" + m_iWPropElig.ToString()
+			+ " rep=" + m_iWPropRep.ToString()
+			+ " stop=" + m_iWPropStop.ToString(), LogLevel.NORMAL);
+	}
+
+	// Animation-only, one-cycle shell request originated on the WEAPON side.
+	// No ammo/mag/chamber writes, no native reload command, no P-side setter.
+	// Repeat is forced false. Only current graph variables are bound.
+	bool T4BWPropRequest()
+	{
+		T4BWPropBind();
+		// NOTE: the < 0 invalid-sentinel is a bounded assumption (engine bind docs do
+		// not publish the sentinel); the readback below is the authoritative signal.
+		if (m_iWPropReq < 0 || m_iWPropElig < 0 || m_iWPropRep < 0 || m_iWPropStop < 0)
+		{
+			m_bWPropActive = false;
+			Print("[ARMST-T4B-WPROP] phase=reject reason=bind-invalid req=" + m_iWPropReq.ToString()
+				+ " elig=" + m_iWPropElig.ToString()
+				+ " rep=" + m_iWPropRep.ToString()
+				+ " stop=" + m_iWPropStop.ToString(), LogLevel.NORMAL);
+			return false;
+		}
+		// R2: deterministic manual abort (no timer). A second qualified R while the
+		// previous session never produced ReturnReady_W means W-local propagation did
+		// NOT run; reset to safe defaults instead of opening a second session.
+		if (m_bWPropActive)
+		{
+			SetBoolVariable(m_iWPropReq, false);
+			SetBoolVariable(m_iWPropElig, false);
+			bool abortReqRb = GetBoolVariable(m_iWPropReq);
+			bool abortEligRb = GetBoolVariable(m_iWPropElig);
+			Print("[ARMST-T4B-WPROP] phase=manual-abort session=" + m_iWPropSession.ToString()
+				+ " write req=0 elig=0 readbackReq=" + abortReqRb.ToString()
+				+ " readbackElig=" + abortEligRb.ToString(), LogLevel.NORMAL);
+			m_bWPropActive = false;
+			return false;
+		}
+		m_iWPropSession++;
+		m_bWPropSawP = false;
+		m_bWPropSawW = false;
+		SetBoolVariable(m_iWPropElig, true);
+		SetBoolVariable(m_iWPropRep, false);
+		SetBoolVariable(m_iWPropStop, false);
+		SetBoolVariable(m_iWPropReq, true);
+		bool reqRb = GetBoolVariable(m_iWPropReq);
+		bool eligRb = GetBoolVariable(m_iWPropElig);
+		bool repRb = GetBoolVariable(m_iWPropRep);
+		bool stopRb = GetBoolVariable(m_iWPropStop);
+		m_bWPropActive = reqRb;
+		if (!reqRb)
+		{
+			// A failed / non-observable write must not leave the session marked active.
+			SetBoolVariable(m_iWPropReq, false);
+			SetBoolVariable(m_iWPropElig, false);
+			Print("[ARMST-T4B-WPROP] phase=reject reason=request-not-observable session=" + m_iWPropSession.ToString()
+				+ " readbackReq=" + reqRb.ToString() + " (safe reset applied)", LogLevel.NORMAL);
+			return false;
+		}
+		Print("[ARMST-T4B-WPROP] phase=request session=" + m_iWPropSession.ToString()
+			+ " write req=1 elig=1 rep=0 stop=0"
+			+ " readbackReq=" + reqRb.ToString()
+			+ " readbackElig=" + eligRb.ToString()
+			+ " readbackRep=" + repRb.ToString()
+			+ " readbackStop=" + stopRb.ToString(), LogLevel.NORMAL);
+		return reqRb;
+	}
+
+	// Deterministic reset driven by the existing W ReturnReady marker (no timer).
+	protected void T4BWPropReset()
+	{
+		if (m_iWPropSession <= 0)
+			return;
+		SetBoolVariable(m_iWPropReq, false);
+		SetBoolVariable(m_iWPropElig, false);
+		bool reqRb = GetBoolVariable(m_iWPropReq);
+		bool eligRb = GetBoolVariable(m_iWPropElig);
+		m_bWPropActive = false;
+		Print("[ARMST-T4B-WPROP] phase=reset session=" + m_iWPropSession.ToString()
+			+ " write req=0 elig=0 readbackReq=" + reqRb.ToString()
+			+ " readbackElig=" + eligRb.ToString(), LogLevel.NORMAL);
+	}
+
 	// Weapon-local observer: does the handler-emitted inert reload command reach this
 	// equipped lab weapon receiver? Route is proven ONLY when BOTH the reload command
 	// type (commandID) AND intValue==ARMST_T4B_INERT_RELOAD_CMD match — never on intValue
@@ -79,6 +188,37 @@ class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComp
 		if (!name.StartsWith("ASTRA_Shell"))
 			return;
 
+		// --- O1 PHASE 1C WPROP: P/W marker-family classification + W-authored reset ---
+		// P files (P_Astra_*.txa) contain only *_P markers; W files only *_W markers
+		// (statical classification). Observing both families here is the probe's
+		// "both sides executed" evidence; gameplay authority stays W-only.
+		if (m_iWPropSession > 0)
+		{
+			bool familyP = name.EndsWith("_P");
+			bool familyW = name.EndsWith("_W");
+			if (familyP && !m_bWPropSawP)
+			{
+				m_bWPropSawP = true;
+				Print("[ARMST-T4B-WPROP] phase=family-P session=" + m_iWPropSession.ToString()
+					+ " first=" + name, LogLevel.NORMAL);
+			}
+			if (familyW && !m_bWPropSawW)
+			{
+				m_bWPropSawW = true;
+				Print("[ARMST-T4B-WPROP] phase=family-W session=" + m_iWPropSession.ToString()
+					+ " first=" + name, LogLevel.NORMAL);
+			}
+		}
+		if (name == "ASTRA_Shell_ReturnReady_W")
+		{
+			if (m_iWPropSession > 0)
+			{
+				Print("[ARMST-T4B-WPROP] phase=return-ready session=" + m_iWPropSession.ToString()
+					+ " sawP=" + m_bWPropSawP.ToString() + " sawW=" + m_bWPropSawW.ToString(), LogLevel.NORMAL);
+				T4BWPropReset();
+			}
+		}
+
 		// Both suffixes are logged on THIS receiver. A _P name does not prove
 		// delivery to a character callback. Only _W may arm a candidate.
 		string result = "observed";
```

Note: the two `diff --git` / `index` lines are shown with repo-relative paths; the actual `git diff --no-index` invocation used absolute paths and reported identical `index 02d1ada..22a3db0` and `index 45e2a14..fa49109` blob ids.

---

Final status: **T4B_WPROP_PROBE_REVIEW_READY_OWNER_GO**. STOP (no install, no runtime).
