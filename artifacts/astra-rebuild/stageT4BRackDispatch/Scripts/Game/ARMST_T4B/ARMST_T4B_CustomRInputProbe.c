// ============================================================================
// ARMST MP-133 T4b - Phase B custom-R input probe + ROUTING DIAGNOSTICS (STAGED).
//
// Owner runtime (Issue #34 comment 6024714308):
//   PHASE_B_COMPILE_PASS, but [ARMST-T4B-RINPUT] did NOT appear while vanilla
//   cmd1/cmd5/cmd3 still fired -> CUSTOM_R_ROUTING_FAIL.
// Bounded diagnostic boundaries to locate WHERE custom R is lost. NO behavior
// change; the [ARMST-T4B-RINPUT] callback is unchanged.
//
// DIAG 1: [ARMST-T4B-RCTX] phase=listener_registered action=ARMST_MP133_Reload
//         right after AddActionListener; registration stays max-once via m_bT4BRListenerActive.
// DIAG 2: [ARMST-T4B-RCTX] phase=weapon_gate_pass
//         once when the full local->weapon->probe path is first reached; the diagnostic
//         bool resets when the current weapon is no longer the T4B probe (re-entry logs again).
// DIAG 3: [ARMST-T4B-RCTX] phase=context_state active=true|false
//         queried from the single IsContextActive() read; logged on first observation and
//         on a state change, hard-capped at 2 lines per T4B entry -> no frame spam.
// DIAG 4: one-shot activation-result line per T4B entry, carrying result=<bool>,
//         active=<bool> and actionPresent=<bool>; actionPresent is computed by an
//         action-count / action-name enumeration scan of the runtime registry.
//
// Context-state API VERIFIED in the installed SDK (Doxygen 1.8.0.13),
// docs/EnfusionScriptAPI/html/interfaceInputManager.html (and interfaceActionManager.html):
//   proto external bool ActivateContext ( string contextName, int duration=0)
//   proto external bool IsContextActive ( string contextName)
//   (action registry enumeration: action count + action name by index)
//   -> CONTEXT_ACTIVE_QUERY = VERIFIED_IS_CONTEXT_ACTIVE.
// Exactly one ActivateContext call site and one IsContextActive call site; no
// context deactivation or context reset call is present (and none is needed).
//
// Context lifecycle unchanged: periodic ActivateContext in SCR_PlayerController.OnUpdate,
// local-only, T4B-probe gated.
//
// Passive/log-only: NO reload APIs, NO ammo/mag/chamber writers, NO animation-graph execution, NO timers.
// ============================================================================
//
// STAGED RACK DISPATCH (stageT4BRackDispatch): behind the existing custom-R
// callback a fail-closed T4B rack request is added (SetReloadWeapon(type=1)).
// No ammo/mag/chamber writes; no input-config/ASTRA/G3B2 change; held off by
// IsReloading(). Diagnostics print [ARMST-T4B-RACK]. Everything else identical.
// ============================================================================
modded class SCR_PlayerController
{
	protected int m_iT4BRInputSeq;
	protected bool m_bT4BRListenerActive;

	// one-shot diagnostic gates (Print spam suppression only; no gameplay effect)
	protected bool m_bT4BRWeaponGateLogged;
	protected bool m_bT4BRContextStateKnown;
	protected bool m_bT4BRContextActiveLast;
	protected bool m_bT4BRContextChangeLogged;
	protected bool m_bT4BRContextResultLogged;
	protected const int ARMST_T4B_RACK_RELOAD_TYPE = 1;

	override void OnUpdate(float timeSlice)
	{
		super.OnUpdate(timeSlice);

		if (!m_bIsLocalPlayerController)
			return;

		// registration-once; duplicate listeners prevented by m_bT4BRListenerActive
		InputManager im = GetGame().GetInputManager();
		if (im && !m_bT4BRListenerActive)
		{
			im.AddActionListener("ARMST_MP133_Reload", EActionTrigger.DOWN, T4BRInputDown);
			m_bT4BRListenerActive = true;
			// DIAG 1: listener registration (tied to the max-once registration).
			Print("[ARMST-T4B-RCTX] phase=listener_registered action=ARMST_MP133_Reload", LogLevel.NORMAL);
		}

		T4BRMaintainContext();
	}

	// PROVEN lifecycle hook for loss of local ownership -> remove the listener.
	override void OnOwnershipChanged(bool changing, bool becameOwner)
	{
		super.OnOwnershipChanged(changing, becameOwner);

		if (!becameOwner && m_bT4BRListenerActive)
		{
			InputManager im = GetGame().GetInputManager();
			if (im)
				im.RemoveActionListener("ARMST_MP133_Reload", EActionTrigger.DOWN, T4BRInputDown);
			m_bT4BRListenerActive = false;
		}
	}

	// Reset one-shot diagnostics when the T4B condition is not met, so re-entry logs again.
	protected void T4BRResetDiag()
	{
		m_bT4BRWeaponGateLogged = false;
		m_bT4BRContextStateKnown = false;
		m_bT4BRContextChangeLogged = false;
		m_bT4BRContextResultLogged = false;
	}

	// The ONLY per-frame gameplay-adjacent action: keep the lab context active while
	// the local controlled entity has the canonical T4B MP-133 current. No deactivate.
	protected void T4BRMaintainContext()
	{
		IEntity controlled = GetControlledEntity();
		if (!controlled) { T4BRResetDiag(); return; }

		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(controlled.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl) { T4BRResetDiag(); return; }

		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
		if (!wm) { T4BRResetDiag(); return; }

		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn) { T4BRResetDiag(); return; }

		IEntity we = wpn.GetOwner();
		if (!we) { T4BRResetDiag(); return; }

		if (!we.FindComponent(ARMST_T4B_WeaponProbe)) { T4BRResetDiag(); return; }

		// DIAG 2: full local->weapon->probe path reached (one-shot per T4B entry).
		if (!m_bT4BRWeaponGateLogged)
		{
			m_bT4BRWeaponGateLogged = true;
			Print("[ARMST-T4B-RCTX] phase=weapon_gate_pass", LogLevel.NORMAL);
		}

		InputManager im = GetGame().GetInputManager();
		if (!im)
			return;

		// exactly one activation call per eligible frame; capture its bool return.
		bool activated = im.ActivateContext("ARMST_MP133_ReloadContext");
		bool activeNow = im.IsContextActive("ARMST_MP133_ReloadContext");

		// DIAG 4: one-shot activation result + action-registry presence.
		if (!m_bT4BRContextResultLogged)
		{
			m_bT4BRContextResultLogged = true;

			bool actionPresent = false;
			int actionCount = im.GetActionCount();
			for (int i = 0; i < actionCount; i++)
			{
				if (im.GetActionName(i) == "ARMST_MP133_Reload")
				{
					actionPresent = true;
					break;
				}
			}

			Print("[ARMST-T4B-RCTX] phase=context_activate_result result=" + activated.ToString()
				+ " active=" + activeNow.ToString()
				+ " actionPresent=" + actionPresent.ToString(), LogLevel.NORMAL);
		}

		// DIAG 3: context state after activation (first observation + at most one change).
		if (!m_bT4BRContextStateKnown)
		{
			m_bT4BRContextStateKnown = true;
			m_bT4BRContextActiveLast = activeNow;
			if (activeNow)
				Print("[ARMST-T4B-RCTX] phase=context_state active=true", LogLevel.NORMAL);
			else
				Print("[ARMST-T4B-RCTX] phase=context_state active=false", LogLevel.NORMAL);
		}
		else if (!m_bT4BRContextChangeLogged && activeNow != m_bT4BRContextActiveLast)
		{
			m_bT4BRContextChangeLogged = true;
			m_bT4BRContextActiveLast = activeNow;
			if (activeNow)
				Print("[ARMST-T4B-RCTX] phase=context_state active=true", LogLevel.NORMAL);
			else
				Print("[ARMST-T4B-RCTX] phase=context_state active=false", LogLevel.NORMAL);
		}
	}

	// Fail-closed T4B native-equivalent rack request. Source-proven reads only:
	// T4B identity (probe), installed-mag presence/ammo (magazine component),
	// chamber flag (muzzle), controller reload state (IsReloading). No
	// ammo/mag/chamber writes; reload type pinned to 1 (rack). One request per
	// physical DOWN; held off while a native reload is in flight.
	protected void T4BRTryRack(SCR_CharacterControllerComponent ctrl, bool labWeapon, bool magPresent, int ammo, int chambered, string side)
	{
		if (!labWeapon)
		{
			Print("[ARMST-T4B-RACK] phase=reject reason=not-t4b", LogLevel.NORMAL);
			return;
		}
		if (!ctrl)
		{
			Print("[ARMST-T4B-RACK] phase=reject reason=no-controller", LogLevel.NORMAL);
			return;
		}
		if (!magPresent || ammo <= 0 || chambered != 0)
		{
			Print("[ARMST-T4B-RACK] phase=reject reason=state magPresent=" + magPresent.ToString()
				+ " ammo=" + ammo.ToString() + " chambered=" + chambered.ToString(), LogLevel.NORMAL);
			return;
		}
		if (ctrl.IsReloading())
		{
			Print("[ARMST-T4B-RACK] phase=reject reason=busy-reloading", LogLevel.NORMAL);
			return;
		}
		CharacterInputContext ic = ctrl.GetInputContext();
		if (!ic)
		{
			Print("[ARMST-T4B-RACK] phase=reject reason=no-input-context", LogLevel.NORMAL);
			return;
		}
		ic.SetReloadWeapon(ARMST_T4B_RACK_RELOAD_TYPE);
		Print("[ARMST-T4B-RACK] phase=request method=SetReloadWeapon type=" + ARMST_T4B_RACK_RELOAD_TYPE.ToString()
			+ " ammo=" + ammo.ToString() + " chambered=" + chambered.ToString()
			+ " side=" + side, LogLevel.NORMAL);
	}

	// Custom action callback: logs physical R and dispatches the T4B rack request.
	protected void T4BRInputDown(float value = 0.0, EActionTrigger reason = 0)
	{
		if (!m_bIsLocalPlayerController)
			return;

		m_iT4BRInputSeq++;

		IEntity controlled = GetControlledEntity();
		SCR_CharacterControllerComponent ctrl = null;
		if (controlled)
			ctrl = SCR_CharacterControllerComponent.Cast(controlled.FindComponent(SCR_CharacterControllerComponent));

		bool labWeapon = false;
		bool magPresent = false;
		int ammo = -1;
		int maxAmmo = -1;
		int chambered = -1;
		if (ctrl)
		{
			BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
			BaseWeaponComponent wpn = null;
			if (wm)
				wpn = wm.GetCurrentWeapon();
			if (wpn)
			{
				IEntity we = wpn.GetOwner();
				if (we)
					labWeapon = (we.FindComponent(ARMST_T4B_WeaponProbe) != null);
				BaseMagazineComponent mag = wpn.GetCurrentMagazine();
				if (mag)
				{
					magPresent = true;
					ammo = mag.GetAmmoCount();
					maxAmmo = mag.GetMaxAmmoCount();
				}
				BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
				if (muzzle)
				{
					chambered = 0;
					if (muzzle.IsCurrentBarrelChambered())
						chambered = 1;
				}
			}
		}

		string side = "CL";
		if (Replication.IsServer())
			side = "SV";

		Print("[ARMST-T4B-RINPUT] seq=" + m_iT4BRInputSeq.ToString()
			+ " action=ARMST_MP133_Reload"
			+ " phase=down"
			+ " side=" + side
			+ " labWeapon=" + labWeapon.ToString()
			+ " currentMagPresent=" + magPresent.ToString()
			+ " ammo=" + ammo.ToString() + "/" + maxAmmo.ToString()
			+ " chambered=" + chambered.ToString(), LogLevel.NORMAL);

		T4BRTryRack(ctrl, labWeapon, magPresent, ammo, chambered, side);
	}
}
