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
// No ammo/mag/chamber writes; no input-config/ARMST/G3B2 change; held off by
// IsReloading(). Diagnostics print [ARMST-T4B-RACK]. Everything else identical.
//
// O1 PHASE 1C ADDITION (stageT4BWPropagationProbe): in the complementary NON-RACK
// branch only, an animation-only weapon-local shell request is dispatched to the
// ArmstV2 weapon animation component (bind/set ARMST_Shell* on the W instance).
// Frozen rack branch above is unchanged; no ammo/mag/chamber writes; no native
// reload; no cmd1..6; no P-side setter. Diagnostics print [ARMST-T4B-WPROP].
//
// LAB ROOT REPAIR: the non-rack shell branch writes four shared character-root
// variables through the real CharacterAnimationComponent. Requires the isolated
// root declaration gate. Delivery to injected P remains an owner runtime gate.
// No attachment writers, native reload, ammo changes or command emission.
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

	// Bind-only candidate: one attempt per player-controller lifetime; never rearmed.
	protected bool m_bAttachmentIdProbeAttempted;
	protected int m_iAttachmentIdProbeEpisode;

	// O1 PHASE 1E PACT attachment-aware P-side probe state.
	protected IEntity m_T4BRootActor;
	protected IEntity m_T4BRootWeapon;
	protected CharacterAnimationComponent m_T4BRootAnim;
	protected int m_iPactReq = -1;
	protected int m_iPactElig = -1;
	protected int m_iPactRep = -1;
	protected int m_iPactStop = -1;
	protected int m_iPactSession;
	protected bool m_bPactActive;

	// O1 PHASE 1J CMDBIND probe one-shot gate.
	protected bool m_bCmdBindLogged;

	override void OnUpdate(float timeSlice)
	{
		super.OnUpdate(timeSlice);
		T4BEnsureLocalReloadInput();
	}

	// Both the existing controller update and the held double-barrel frame hook
	// use one idempotent listener registration; never register on remote controllers.
	void T4BEnsureLocalReloadInput()
	{
		if (GetGame().GetPlayerController() != this)
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
		T4BRootMaintainIdentity();
	}

	// PROVEN lifecycle hook for loss of local ownership -> remove the listener.
	override void OnOwnershipChanged(bool changing, bool becameOwner)
	{
		if (!becameOwner)
			T4BPactResetFromEvent("ownership-lost");
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

	// Two raw attachment-name binds only. No ID dereference, validity inference,
	// setters, commands, shell request or gameplay writes. No retry after a skip.
	protected void T4BAttachmentIdBindOnlyProbe(SCR_CharacterControllerComponent ctrl, IEntity weaponEntity)
	{
		if (m_bAttachmentIdProbeAttempted)
			return;
		m_bAttachmentIdProbeAttempted = true;
		m_iAttachmentIdProbeEpisode++;

		if (!m_bIsLocalPlayerController || !ctrl || !weaponEntity)
		{
			Print("[ARMST-T4B-ATTID] phase=skip reason=missing-context", LogLevel.NORMAL);
			return;
		}
		IEntity actor = GetControlledEntity();
		if (!actor || ctrl.GetOwner() != actor)
		{
			Print("[ARMST-T4B-ATTID] phase=skip reason=actor-identity", LogLevel.NORMAL);
			return;
		}
		BaseWeaponManagerComponent manager = ctrl.GetWeaponManagerComponent();
		if (!manager)
		{
			Print("[ARMST-T4B-ATTID] phase=skip reason=no-weapon-manager", LogLevel.NORMAL);
			return;
		}
		BaseWeaponComponent currentWeapon = manager.GetCurrentWeapon();
		if (!currentWeapon || currentWeapon.GetOwner() != weaponEntity)
		{
			Print("[ARMST-T4B-ATTID] phase=skip reason=current-weapon-identity", LogLevel.NORMAL);
			return;
		}
		ARMST_T4B_ArmstV2_WeaponAnimationComponent animComp = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(weaponEntity.FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
		if (!animComp || animComp.GetOwner() != weaponEntity)
		{
			Print("[ARMST-T4B-ATTID] phase=skip reason=animation-component-identity", LogLevel.NORMAL);
			return;
		}

		int weaponId = animComp.BindAttachment("Weapon");
		int missingId = animComp.BindAttachment("ARMST_NonexistentAttachment_Probe");
		// Bind-only: attachment IDs are passed through without interpreting their sign.
		// No GetAtt/SetAtt operations or commands; a returned variable ID is NOT P proof.
		int attachmentRequestId = animComp.BindAttBoolVariable(weaponId, "ARMST_ShellRequest");
		PrintFormat("[ARMST-T4B-ATTID] phase=variable-bind episode=%1 attachmentId=%2 variableId=%3 component=%4 weapon=%5", m_iAttachmentIdProbeEpisode, weaponId, attachmentRequestId, animComp, weaponEntity);
		// Object references are session-local evidence, not persistent/network IDs.
		PrintFormat("[ARMST-T4B-ATTID] phase=pair episode=%1 componentType=ARMST_T4B_ArmstV2_WeaponAnimationComponent component=%2 weapon=%3 actor=%4 weaponId=%5 missingId=%6", m_iAttachmentIdProbeEpisode, animComp, weaponEntity, actor, weaponId, missingId);
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

		ARMST_ShotgunReloadComponent reload = ARMST_ShotgunReloadComponent.Cast(we.FindComponent(ARMST_ShotgunReloadComponent));
		if (!reload) { T4BRResetDiag(); return; }
		if (reload.m_bNativeDoubleBarrelReload)
		{
			InputManager nativeInput = GetGame().GetInputManager();
			if (nativeInput)
				nativeInput.ActivateContext("ARMST_MP133_ReloadContext");
			return;
		}

		// DIAG 2: full local->weapon->probe path reached (one-shot per T4B entry).
		if (!m_bT4BRWeaponGateLogged)
		{
			m_bT4BRWeaponGateLogged = true;
			Print("[ARMST-T4B-RCTX] phase=weapon_gate_pass", LogLevel.NORMAL);
			T4BAttachmentIdBindOnlyProbe(ctrl, we);
		}

		T4BCmdBindProbe(ctrl, we);

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

	// O1 PHASE 1C — complementary NON-RACK shell branch (animation-only W-local
	// request propagation probe). No ammo/mag/chamber writes, no native reload,
	// no cmd1..6. The frozen rack branch above is untouched and still runs first.
	protected void T4BRTryShellProp(SCR_CharacterControllerComponent ctrl, bool labWeapon, bool magPresent, int ammo, int maxAmmo, int chambered, string side)
	{
		if (!labWeapon)
			return;
		if (!ctrl)
			return;
		if (ctrl.IsReloading())
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=busy-reloading side=" + side, LogLevel.NORMAL);
			return;
		}
		if (!magPresent)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=no-magazine side=" + side, LogLevel.NORMAL);
			return;
		}
		// R1 fail-closed gate: never start animation from unresolved/invalid telemetry.
		// Required: magPresent==true, maxAmmo>0, ammo>=0, ammo<maxAmmo, chambered in {0,1}.
		if (maxAmmo <= 0 || ammo < 0)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=unresolved-ammo ammo=" + ammo.ToString()
				+ " maxAmmo=" + maxAmmo.ToString() + " side=" + side, LogLevel.NORMAL);
			return;
		}
		if (ammo >= maxAmmo)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=tube-full ammo=" + ammo.ToString()
				+ "/" + maxAmmo.ToString() + " side=" + side, LogLevel.NORMAL);
			return;
		}
		if (chambered < 0 || chambered > 1)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=unresolved-chamber chambered=" + chambered.ToString()
				+ " side=" + side, LogLevel.NORMAL);
			return;
		}
		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
		if (!wm)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=no-weapon-manager side=" + side, LogLevel.NORMAL);
			return;
		}
		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=no-current-weapon side=" + side, LogLevel.NORMAL);
			return;
		}
		IEntity we = wpn.GetOwner();
		if (!we)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=no-weapon-entity side=" + side, LogLevel.NORMAL);
			return;
		}
		ARMST_T4B_ArmstV2_WeaponAnimationComponent wcomp = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(we.FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
		if (!wcomp)
		{
			Print("[ARMST-T4B-WPROP] phase=reject reason=no-w-anim-component side=" + side, LogLevel.NORMAL);
			return;
		}
		Print("[ARMST-T4B-WPROP] phase=branch choice=shell ammo=" + ammo.ToString()
			+ "/" + maxAmmo.ToString() + " chambered=" + chambered.ToString()
			+ " side=" + side, LogLevel.NORMAL);
		ARMST_ShotgunReloadComponent donorGate = ARMST_ShotgunReloadComponent.Cast(we.FindComponent(ARMST_ShotgunReloadComponent));
		if (!donorGate || !donorGate.m_T4BPTransferAction)
			return;
		if (!donorGate.m_T4BPTransferAction.ReadyP(ctrl.GetOwner(), wpn))
			return;
		if (!wcomp.T4BWPropRequest())
		{
			T4BPactResetFromEvent("w-request-not-active");
			return;
		}
		T4BRTryPact(ctrl, side);
	}

	// Initial dispatch; the armed action owns subsequent full-cycle dispatches.
	protected int m_iT4BPCommandEpisode;

	protected void T4BRTryPact(SCR_CharacterControllerComponent ctrl, string side)
	{
		if (!Replication.IsServer() || !ctrl)
			return;
		IEntity actor = ctrl.GetOwner();
		if (!actor || actor != GetControlledEntity())
			return;
		BaseWeaponManagerComponent manager = ctrl.GetWeaponManagerComponent();
		if (!manager)
			return;
		BaseWeaponComponent current = manager.GetCurrentWeapon();
		if (!current)
			return;
		IEntity weapon = current.GetOwner();
		if (!weapon || !weapon.FindComponent(ARMST_ShotgunReloadComponent))
			return;
		CharacterAnimationComponent anim = CharacterAnimationComponent.Cast(actor.FindComponent(CharacterAnimationComponent));
		if (!anim)
			return;
		TAnimGraphCommand command = anim.BindCommand("CMD_ARMST_TransportProbe");
		if (command == -1)
		{
			Print("[ARMST-T4B-PCMD] phase=reject reason=root-command-unavailable", LogLevel.NORMAL);
			return;
		}
		if (!ctrl.T4BArmPTransfer(current, this))
		{
			Print("[ARMST-T4B-PCOMMIT] phase=reject reason=transfer-arm-unavailable", LogLevel.NORMAL);
			return;
		}
		// ArmP is the session latch; subsequent R cancels an active session.
		m_iT4BPCommandEpisode++;
		PrintFormat("[ARMST-T4B-PCMD] phase=dispatch episode=%1 actor=%2 weapon=%3 command=%4 side=%5 pReceipt=UNPROVEN", m_iT4BPCommandEpisode, actor, weapon, command, side);
		anim.CallCommand(command, 1, 0.0);
	}

	// Preserve the existing W-event reset entry point. Clear on the original owner,
	// not whichever character happens to be controlled when the callback arrives.
	void T4BPactResetFromEvent(string source)
	{
		if (!m_bPactActive)
			return;
		if (m_T4BRootActor && m_T4BRootAnim && CharacterAnimationComponent.Cast(m_T4BRootActor.FindComponent(CharacterAnimationComponent)) == m_T4BRootAnim)
		{
			m_T4BRootAnim.SetSharedVariableBool(m_iPactReq, false, true);
			m_T4BRootAnim.SetSharedVariableBool(m_iPactElig, false, true);
			m_T4BRootAnim.SetSharedVariableBool(m_iPactRep, false, true);
			m_T4BRootAnim.SetSharedVariableBool(m_iPactStop, false, true);
			PrintFormat("[ARMST-T4B-ROOTARMST] phase=reset session=%1 source=%2 pReceipt=UNPROVEN", m_iPactSession, source);
		}
		else
		{
			Print("[ARMST-T4B-ROOTARMST] phase=reset-unavailable reason=original-owner-gone", LogLevel.NORMAL);
		}
		m_bPactActive = false;
		m_T4BRootActor = null;
		m_T4BRootWeapon = null;
		m_T4BRootAnim = null;
	}

	// Identity/lifetime cleanup only; no per-frame request emission or timers.
	protected void T4BRootMaintainIdentity()
	{
		if (!m_bPactActive)
			return;
		IEntity actor = GetControlledEntity();
		if (!actor || actor != m_T4BRootActor)
		{
			T4BPactResetFromEvent("controlled-actor-changed");
			return;
		}
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(actor.FindComponent(SCR_CharacterControllerComponent));
		BaseWeaponManagerComponent manager = null;
		if (ctrl)
			manager = ctrl.GetWeaponManagerComponent();
		BaseWeaponComponent current = null;
		if (manager)
			current = manager.GetCurrentWeapon();
		if (!current || current.GetOwner() != m_T4BRootWeapon)
			T4BPactResetFromEvent("equipped-weapon-changed");
	}

	// O1 PHASE 1G — READ-ONLY P-owner diagnostic. Enumerates candidate animation
	// controller owners on the controlled character and, if found, performs a
	// BindAttachment("Weapon") lookup only. No attachment-variable writes and no
	// attachment/custom commands are issued; no graph mutation; no gameplay writes.
	// Diagnostics print [ARMST-T4B-POWNER].
	protected void T4BRTryPOwner(SCR_CharacterControllerComponent ctrl, string side)
	{
		IEntity controlled = null;
		if (ctrl)
			controlled = ctrl.GetOwner();
		if (!controlled)
		{
			Print("[ARMST-T4B-POWNER] phase=owner ok=false reason=no-controlled side=" + side, LogLevel.NORMAL);
			return;
		}
		Print("[ARMST-T4B-POWNER] phase=owner ok=true side=" + side, LogLevel.NORMAL);

		AnimationControllerComponent acc = AnimationControllerComponent.Cast(controlled.FindComponent(AnimationControllerComponent));
		CharacterAnimGraphComponent cagc = CharacterAnimGraphComponent.Cast(controlled.FindComponent(CharacterAnimGraphComponent));
		CharacterAnimationComponent cac = CharacterAnimationComponent.Cast(controlled.FindComponent(CharacterAnimationComponent));

		Print("[ARMST-T4B-POWNER] phase=find animController=" + (acc != null).ToString()
			+ " charAnimGraph=" + (cagc != null).ToString()
			+ " charAnim=" + (cac != null).ToString(), LogLevel.NORMAL);

		int att = -1;
		if (acc)
			att = acc.BindAttachment("Weapon");
		Print("[ARMST-T4B-POWNER] phase=bindAtt owner=animationController binding=Weapon id=" + att.ToString()
			+ " valid=" + (att >= 0).ToString(), LogLevel.NORMAL);

		if (cagc)
		{
			int att2 = cagc.BindAttachment("Weapon");
			Print("[ARMST-T4B-POWNER] phase=bindAtt owner=characterAnimGraph binding=Weapon id=" + att2.ToString()
				+ " valid=" + (att2 >= 0).ToString(), LogLevel.NORMAL);
		}
	}

	// O1 PHASE 1J - injected-only custom-command bind probe. REGISTRATION/ADDRESSABILITY
	// ONLY: binds one inert command name on the character animation component and on the
	// equipped ArmstV2 weapon animation component, plus one known positive control
	// (CMD_Weapon_Reload) and one deliberately absent negative control. No command calls,
	// no setters, no WPROP request, no gameplay writes. Diagnostics print [ARMST-T4B-CMDBIND].
	protected void T4BCmdBindProbe(SCR_CharacterControllerComponent ctrl, IEntity weaponEntity)
	{
		if (m_bCmdBindLogged)
			return;
		m_bCmdBindLogged = true;

		CharacterAnimationComponent charAnim = null;
		if (ctrl)
			charAnim = ctrl.GetAnimationComponent();

		ARMST_T4B_ArmstV2_WeaponAnimationComponent wcomp = null;
		if (weaponEntity)
			wcomp = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(weaponEntity.FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));

		int customW = -99;
		if (wcomp)
			customW = wcomp.BindCommand("CMD_ARMST_TransportProbe");

		if (!charAnim)
		{
			Print("[ARMST-T4B-CMDBIND] phase=post actorPresent=" + (ctrl != null).ToString()
				+ " weaponPresent=" + (wcomp != null).ToString()
				+ " customW=" + customW.ToString()
				+ " customCharValid=NA rootCtlValid=NA absentValid=NA", LogLevel.NORMAL);
			return;
		}

		// Character side: BaseAnimPhysComponent.BindCommand -> TAnimGraphCommand.
		TAnimGraphCommand customChar = charAnim.BindCommand("CMD_ARMST_TransportProbe");
		TAnimGraphCommand rootCtl = charAnim.BindCommand("CMD_Weapon_Reload");
		TAnimGraphCommand absent = charAnim.BindCommand("CMD_ARMST_AbsentProbe_ZZZ");

		Print("[ARMST-T4B-CMDBIND] phase=post actorPresent=" + (ctrl != null).ToString()
			+ " weaponPresent=" + (wcomp != null).ToString()
			+ " customW=" + customW.ToString()
			+ " customCharValid=" + (customChar >= 0).ToString()
			+ " rootCtlValid=" + (rootCtl >= 0).ToString()
			+ " absentValid=" + (absent >= 0).ToString(), LogLevel.NORMAL);
	}

	// Custom action callback: logs physical R and dispatches the T4B rack request.
	protected void T4BRInputDown(float value = 0.0, EActionTrigger reason = 0)
	{
		if (GetGame().GetPlayerController() != this)
			return;
		Print("[ARMST-DB-INPUT] custom-r-down", LogLevel.NORMAL);

		// Intent only. Resolve actor, current weapon and ammo on this controller's server.
		if (Replication.IsServer())
			RpcAsk_T4BReloadIntent();
		else
			Rpc(RpcAsk_T4BReloadIntent);
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Server)]
	protected void RpcAsk_T4BReloadIntent()
	{
		if (!Replication.IsServer())
			return;
		if (m_bT4BIntentThrottled)
			return;
		m_bT4BIntentThrottled = true;
		GetGame().GetCallqueue().CallLater(T4BClearIntentThrottle, 150, false);
		Print("[ARMST-T4B-NET] phase=server-intent", LogLevel.NORMAL);

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
				{
					ARMST_ShotgunReloadComponent nativeReload = ARMST_ShotgunReloadComponent.Cast(we.FindComponent(ARMST_ShotgunReloadComponent));
					if (nativeReload && nativeReload.m_bNativeDoubleBarrelReload)
					{
						nativeReload.DBRequestNative(ctrl);
						return;
					}
				}
				if (we)
					labWeapon = (we.FindComponent(ARMST_ShotgunReloadComponent) != null);
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

		// A second R cancels automatic follow-up cycles; it must not rack mid-insertion.
		if (ctrl)
		{
			BaseWeaponManagerComponent sessionManager = ctrl.GetWeaponManagerComponent();
			if (sessionManager && sessionManager.GetCurrentWeapon())
			{
				IEntity sessionWeapon = sessionManager.GetCurrentWeapon().GetOwner();
				ARMST_ShotgunReloadComponent sessionProbe = ARMST_ShotgunReloadComponent.Cast(sessionWeapon.FindComponent(ARMST_ShotgunReloadComponent));
				if (sessionProbe && sessionProbe.m_T4BPTransferAction && sessionProbe.m_T4BPTransferAction.IsPDraining())
				{
					Print("[ARMST-T4B-NET] phase=reject reason=session-draining", LogLevel.NORMAL);
					return;
				}
				if (sessionProbe && sessionProbe.m_T4BPTransferAction && sessionProbe.m_T4BPTransferAction.IsPSessionActive())
				{
					sessionProbe.m_T4BPTransferAction.CancelP("second-r");
					return;
				}
			}
		}
		T4BRTryRack(ctrl, labWeapon, magPresent, ammo, chambered, side);

		bool rackPredicate = (magPresent && ammo > 0 && chambered == 0);
		if (!rackPredicate)
			T4BRTryShellProp(ctrl, labWeapon, magPresent, ammo, maxAmmo, chambered, side);
	}

	protected bool m_bT4BIntentThrottled;
	void T4BClearIntentThrottle() { m_bT4BIntentThrottled = false; }
}
