// Lab-only command-driven inner single-shell cycle. Runtime validation required.
// Only P commit writes via unchanged G3B2. W ReturnReady is lifecycle-only.
[BaseContainerProps()]
modded class ARMST_ShotgunReloadComponent
{
	ARMST_T4B_PCommitTransferAction m_T4BPTransferAction;
}

class ARMST_T4B_PCommitTransferAction : ARMST_T4B_G3B2_TransferAction
{
	protected IEntity m_PActor;
	protected SCR_PlayerController m_PRequester;
	protected BaseWeaponComponent m_PWeapon;
	protected BaseMagazineComponent m_PMagazine;
	protected BaseMuzzleComponent m_PMuzzle;
	protected int m_PAmmo;
	protected bool m_PChambered;
	protected bool m_PArmed;
	protected bool m_PStarted;
	protected bool m_PActive;
	protected bool m_PCommitted;
	protected bool m_PReady;
	protected bool m_WReady;
	protected bool m_PNextScheduled;
	protected int m_PGeneration;
	protected int m_PCycle;
	protected int m_PWatchTicks;
	protected bool m_PClosing;
	protected bool m_PFinished;
	protected bool m_WFinished;
	protected bool m_PCloseScheduled;
	protected int m_PEventStage;
	protected bool m_PStopAfterInsert;
	protected bool m_PDetached;
	protected int m_PDetachedIdleSamples;

	// Clip events carry no session ID. Do not re-arm while old graphs drain.
	bool IsPDraining() { return m_PClosing; }

	protected void ScheduleDrainP()
	{
		if (!m_PClosing || !m_PFinished || !m_WFinished || m_PCloseScheduled)
			return;
		m_PCloseScheduled = true;
		GetGame().GetCallqueue().CallLater(FinishDrainP, 200, false, m_PGeneration);
	}

	void FinishDrainP(int generation)
	{
		if (!m_PClosing || generation != m_PGeneration)
			return;
		// A different equipped weapon may already own the requester's new session.
		if (m_PRequester && m_PActor && T4B2CurrentWeapon(m_PActor) == m_PWeapon)
			m_PRequester.T4BPactResetFromEvent("session-drained");
		m_PClosing = false;
		TryMP153AutoRack();
		m_PRequester = null;
		m_PActor = null;
		m_PWeapon = null;
		m_PMagazine = null;
		m_PMuzzle = null;
		Print("[ARMST-T4B-PCOMMIT] phase=drained", LogLevel.NORMAL);
	}

	void WatchDetachedDrainP(int generation)
	{
		if (!Replication.IsServer() || !m_PClosing || generation != m_PGeneration)
			return;
		if (!m_PActor || !m_PWeapon || T4B2CurrentWeapon(m_PActor) != m_PWeapon)
			m_PDetached = true;
		SCR_CharacterControllerComponent controller;
		if (m_PActor)
			controller = SCR_CharacterControllerComponent.Cast(m_PActor.FindComponent(SCR_CharacterControllerComponent));
		// Do not replace missing animation acknowledgements with an unconditional timeout.
		// W must finish; the old character must leave reload before its bridge is detached.
		bool actorIdle = !m_PActor || (controller && !controller.IsReloading());
		if (m_PDetached && m_WFinished && actorIdle && !m_b2Latch)
			m_PDetachedIdleSamples++;
		else
			m_PDetachedIdleSamples = 0;
		if (m_PDetachedIdleSamples >= 2)
		{
			if (controller)
				controller.T4BReleasePTransfer(this);
			m_PFinished = true;
			Print("[ARMST-T4B-PCOMMIT] phase=detached-drain actorIdle=1 weaponFinished=1", LogLevel.NORMAL);
			ScheduleDrainP();
			return;
		}
		GetGame().GetCallqueue().CallLater(WatchDetachedDrainP, 100, false, generation);
	}

	bool IsPSessionActive() { return m_PActive; }

	// Only after BOTH graphs returned ready. Reuse native rack, never write ammo.
	protected void TryMP153AutoRack()
	{
		if (!Replication.IsServer() || m_b2Quarantined || m_b2Latch)
			return;
		if (!m_PRequester || !m_PActor || m_PRequester.GetControlledEntity() != m_PActor)
			return;
		if (!m_PWeapon || T4B2CurrentWeapon(m_PActor) != m_PWeapon)
			return;
		IEntity owner = m_PWeapon.GetOwner();
		if (!owner || !owner.GetPrefabData())
			return;
		ResourceName prefab = owner.GetPrefabData().GetPrefabName();
		if (prefab != "{92DB80A098AABF1C}Prefabs/Weapons/Shootgun/Russian/armst_Shotgun_mp_153.et")
			return;
		if (!m_PMagazine || !m_PMuzzle || m_PWeapon.GetCurrentMagazine() != m_PMagazine || m_PWeapon.GetCurrentMuzzle() != m_PMuzzle)
			return;
		if (m_PMagazine.GetAmmoCount() <= 0 || m_PMuzzle.IsCurrentBarrelChambered())
			return;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(m_PActor.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl || ctrl.IsReloading())
		{
			Print("[ARMST-MP153-AUTORACK] phase=skip reason=controller-busy-or-missing", LogLevel.NORMAL);
			return;
		}
		CharacterInputContext input = ctrl.GetInputContext();
		if (!input)
			return;
		// Native reload type 1 is the same rack request used by the R handler.
		input.SetReloadWeapon(1);
		Print("[ARMST-MP153-AUTORACK] phase=request after=both-return-ready", LogLevel.NORMAL);
	}

	// Read-only gate BEFORE either W request or P command. The commit still repeats
	// the entire G3B2 preflight at insertion time; this is not a donor reservation.
	bool ReadyP(IEntity actor, BaseWeaponComponent weapon)
	{
		IEntity modeOwner = GetOwner();
		if (!modeOwner)
			return false;
		ARMST_ShotgunReloadComponent mode = ARMST_ShotgunReloadComponent.Cast(modeOwner.FindComponent(ARMST_ShotgunReloadComponent));
		if (mode && mode.m_bNativeDoubleBarrelReload)
			return false;
		if (!Replication.IsServer() || m_PActive || m_PClosing || m_b2Latch || m_b2Quarantined || !actor || !weapon)
			return false;
		IEntity actionOwner = GetOwner();
		if (!actionOwner || weapon.GetOwner() != actionOwner || T4B2CurrentWeapon(actor) != weapon)
			return false;
		SCR_InventoryStorageManagerComponent inventory = T4B2Inv(actor);
		BaseMagazineComponent magazine = weapon.GetCurrentMagazine();
		BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
		if (!inventory || !magazine || !magazine.GetOwner() || !muzzle)
			return false;
		m_opUser = actor;
		m_opActionOwner = actionOwner;
		m_opWeapon = weapon;
		m_opInv = inventory;
		m_opTargetMag = magazine;
		m_opTargetEnt = magazine.GetOwner();
		m_opRefType = magazine.GetAmmoType(0);
		m_opTAmmo = magazine.GetAmmoCount();
		m_opTMax = magazine.GetMaxAmmoCount();
		m_opMuzzle = muzzle;
		m_opCh = muzzle.IsCurrentBarrelChambered();
		m_opBarrel = muzzle.GetCurrentBarrelIndex();
		m_opBarrels = muzzle.GetBarrelsCount();
		m_opSupply = muzzle.GetAmmoCount();
		m_opSupplyMax = muzzle.GetMaxAmmoCount();
		T4B2Scan();
		bool ready = T4B2Preflight();
		Print("[ARMST-T4B-PCOMMIT] phase=pre-start eligible=" + ready.ToString() + " reason=" + m_opRejectReason, LogLevel.NORMAL);
		return ready;
	}

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		super.Init(pOwnerEntity, pManagerComponent);
		ARMST_ShotgunReloadComponent probe = ARMST_ShotgunReloadComponent.Cast(pOwnerEntity.FindComponent(ARMST_ShotgunReloadComponent));
		if (probe && !probe.m_T4BPTransferAction)
			probe.m_T4BPTransferAction = this;
	}

	override bool CanBeShownScript(IEntity user) { return false; }
	override bool CanBePerformedScript(IEntity user) { return false; }
	// Block every manual/broadcast entry; only the armed P event calls the base transaction.
	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity) {}
	override event bool CanBroadcastScript() { return false; }

	bool ArmP(IEntity actor, BaseWeaponComponent weapon, SCR_PlayerController requester)
	{
		IEntity modeOwner = GetOwner();
		if (!modeOwner)
			return false;
		ARMST_ShotgunReloadComponent mode = ARMST_ShotgunReloadComponent.Cast(modeOwner.FindComponent(ARMST_ShotgunReloadComponent));
		if (mode && mode.m_bNativeDoubleBarrelReload)
			return false;
		if (!requester || requester.GetControlledEntity() != actor)
			return false;
		if (!Replication.IsServer() || m_PActive || m_PClosing || m_b2Latch || m_b2Quarantined || !actor || !weapon)
			return false;
		if (weapon.GetOwner() != GetOwner() || T4B2CurrentWeapon(actor) != weapon)
			return false;
		BaseMagazineComponent mag = weapon.GetCurrentMagazine();
		BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
		if (!mag || !muzzle || mag.GetMaxAmmoCount() <= 0 || mag.GetAmmoCount() >= mag.GetMaxAmmoCount())
			return false;
		if (!mode || !mode.ShotgunCanInsert(mag, muzzle))
			return false;
		m_PActor = actor;
		m_PRequester = requester;
		m_PWeapon = weapon;
		m_PMagazine = mag;
		m_PMuzzle = muzzle;
		m_PAmmo = mag.GetAmmoCount();
		m_PChambered = muzzle.IsCurrentBarrelChambered();
		m_PStarted = false;
		m_PFinished = false;
		m_WFinished = false;
		m_PCloseScheduled = false;
		m_PEventStage = 0;
		m_PStopAfterInsert = false;
		m_PDetached = false;
		m_PDetachedIdleSamples = 0;
		m_PArmed = true;
		m_PActive = true;
		m_PCommitted = false;
		m_PReady = false;
		m_WReady = false;
		m_PNextScheduled = false;
		m_PGeneration++;
		m_PCycle = 1;
		m_PWatchTicks = 0;
		GetGame().GetCallqueue().CallLater(WatchP, 100, false, m_PGeneration);
		Print("[ARMST-T4B-PCOMMIT] phase=armed authority=P cycle=1 repeatFullCycles=1", LogLevel.NORMAL);
		return true;
	}

	void ReceiveP(IEntity actor, string name)
	{
		if (!Replication.IsServer() || actor != m_PActor)
			return;
		if (name == "ARMST_Shell_ReturnReady_P")
		{
			m_PFinished = true;
			if (m_PActive)
				CancelP("p-return-ready");
			ScheduleDrainP();
			return;
		}
		if (!m_PActive || !Replication.IsServer())
			return;
		if (actor != m_PActor || !m_PWeapon || T4B2CurrentWeapon(actor) != m_PWeapon)
		{
			CancelP("actor-or-weapon-changed");
			return;
		}
		if (name == "ARMST_Shell_StartReload_P")
		{
			if (m_PCycle != 1 || m_PEventStage != 0)
				return;
			m_PStarted = true;
			m_PEventStage = 1;
			// Once on the first cycle; restore before any continuation transition.
			if (m_PCycle == 1)
			{
				ARMST_T4B_ArmstV2_WeaponAnimationComponent pulseAnim = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(GetOwner().FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
				if (pulseAnim && !pulseAnim.T4BPRepeatPulse())
				{
					CancelP("repeat-pulse-restore-failed");
					return;
				}
			}
		}
		if (name == "Weapon_Action_Interrupt" || name == "Weapon_TriggerPulled")
		{
			CancelP("interrupt-or-trigger");
			return;
		}
		if (name == "ARMST_Shell_GrabShell_P" && m_PStarted && m_PEventStage == 1)
			m_PEventStage = 2;
		if (name == "ARMST_Shell_InsertShell_P" && m_PEventStage == 2)
			m_PEventStage = 3;
		if (name == "ARMST_Shell_CheckContinue_P" && m_PCommitted)
		{
			m_PReady = true;
			ScheduleNextP();
			return;
		}
		if (name == "ARMST_Shell_EndReload_P" || name == "ARMST_Shell_Stop_P" || name == "ARMST_Shell_ReturnReady_P")
		{
			CancelP("cycle-ended-before-commit");
			return;
		}
		if (name != "ARMST_ShellInsertCommit_P" || !m_PArmed)
			return;
		// Consume before all checks: duplicates and rejects never retry this arm.
		m_PArmed = false;
		if (!m_PStarted || m_PEventStage != 3 || !m_PMagazine || !m_PMuzzle)
		{
			Print("[ARMST-T4B-PCOMMIT] phase=reject reason=missing-start-or-components", LogLevel.NORMAL);
			CancelP("commit-precondition");
			return;
		}
		if (m_PWeapon.GetCurrentMagazine() != m_PMagazine || m_PWeapon.GetCurrentMuzzle() != m_PMuzzle)
		{
			Print("[ARMST-T4B-PCOMMIT] phase=reject reason=magazine-or-muzzle-changed", LogLevel.NORMAL);
			CancelP("commit-identity");
			return;
		}
		if (m_PMagazine.GetAmmoCount() != m_PAmmo || m_PMuzzle.IsCurrentBarrelChambered() != m_PChambered)
		{
			Print("[ARMST-T4B-PCOMMIT] phase=reject reason=ammo-or-chamber-changed", LogLevel.NORMAL);
			CancelP("commit-state");
			return;
		}
		Print("[ARMST-T4B-PCOMMIT] phase=invoke event=ARMST_ShellInsertCommit_P authority=P", LogLevel.NORMAL);
		super.PerformAction(GetOwner(), actor);
		// A scheduled G3B2 validation exists only after a successful synchronous commit.
		if (m_b2Quarantined || !m_b2Latch || m_dScheduledOp != m_i2OpId || m_PMagazine.GetAmmoCount() != m_PAmmo + 1)
		{
			CancelP("transaction-not-committed");
			return;
		}
		m_PCommitted = true;
	}

	void ReceiveW(string name)
	{
		if (!Replication.IsServer())
			return;
		if (name == "ARMST_Shell_ReturnReady_W")
		{
			m_WFinished = true;
			ScheduleDrainP();
			return;
		}
		if (!m_PActive || name != "ARMST_Shell_CheckContinue_W")
			return;
		m_WReady = true;
		ScheduleNextP();
	}

	protected bool IdentityP()
	{
		if (!Replication.IsServer() || !m_PActor || !m_PWeapon || !m_PMagazine || !m_PMuzzle)
			return false;
		// Session actor was resolved by the requesting server-side player controller.
		// Never compare a remote actor with the process-global local player.
		if (!m_PRequester || m_PRequester.GetControlledEntity() != m_PActor)
			return false;
		if (T4B2CurrentWeapon(m_PActor) != m_PWeapon || m_PWeapon.GetOwner() != GetOwner())
			return false;
		if (m_PWeapon.GetCurrentMagazine() != m_PMagazine || m_PWeapon.GetCurrentMuzzle() != m_PMuzzle)
			return false;
		if (m_PMuzzle.IsCurrentBarrelChambered() != m_PChambered)
			return false;
		int expected = m_PAmmo;
		if (m_PCommitted)
			expected++;
		return m_PMagazine.GetAmmoCount() == expected;
	}

	void WatchP(int generation)
	{
		if (!m_PActive || generation != m_PGeneration)
			return;
		m_PWatchTicks++;
		if (!IdentityP() || m_b2Quarantined || m_PWatchTicks >= 300)
		{
			CancelP("identity-quarantine-or-timeout");
			return;
		}
		GetGame().GetCallqueue().CallLater(WatchP, 100, false, generation);
	}

	void ScheduleNextP()
	{
		if (!m_PActive || !m_PCommitted || !m_PReady || !m_WReady || m_PNextScheduled)
			return;
		m_PNextScheduled = true;
		// Let both event handlers finish their reset. Runtime must verify graph re-entry.
		GetGame().GetCallqueue().CallLater(NextP, 1, false, m_PGeneration);
	}

	void NextP(int generation)
	{
		if (!m_PActive || generation != m_PGeneration)
			return;
		if (!m_PCommitted || !m_PReady || !m_WReady)
			return;
		if (!IdentityP() || m_b2Quarantined)
		{
			CancelP("repeat-identity-or-quarantine");
			return;
		}
		T4B2VerifyAnimationBoundary();
		if (m_b2Quarantined)
		{
			CancelP("repeat-boundary-quarantine");
			return;
		}
		if (m_b2Latch)
		{
			GetGame().GetCallqueue().CallLater(NextP, 25, false, generation);
			return;
		}
		if (m_dScheduledOp != 0 || !m_dSample250Ok || m_dSamples != 2)
		{
			CancelP("repeat-not-verified");
			return;
		}
		// Both graphs reached CheckContinue and the current transfer is verified.
		// Stop here instead of cancelling one graph halfway through insertion.
		if (m_PStopAfterInsert)
		{
			CancelP("requested-stop-at-boundary");
			return;
		}
		ARMST_ShotgunReloadComponent capacity = ARMST_ShotgunReloadComponent.Cast(GetOwner().FindComponent(ARMST_ShotgunReloadComponent));
		if (!capacity || !capacity.ShotgunCanInsert(m_PMagazine, m_PMuzzle))
		{
			CancelP("component-loaded-limit");
			return;
		}
		if (m_PCycle >= capacity.ShotgunTubeLimit(m_PMagazine))
		{
			CancelP("tube-full-or-cycle-limit");
			return;
		}
		// Read-only donor classification again; empty or ambiguous means STOP, no retry.
		T4B2Scan();
		if (!T4B2HasSelectedDonor())
		{
			CancelP("repeat-no-single-donor");
			return;
		}
		CharacterAnimationComponent anim = CharacterAnimationComponent.Cast(m_PActor.FindComponent(CharacterAnimationComponent));
		ARMST_T4B_ArmstV2_WeaponAnimationComponent wanim = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(GetOwner().FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
		if (!anim || !wanim)
		{
			CancelP("repeat-no-animation-component");
			return;
		}
		TAnimGraphCommand command = anim.BindCommand("CMD_ARMST_TransportProbe");
		int weaponCommand = wanim.BindCommand("CMD_ARMST_TransportProbe");
		if (command == -1 || weaponCommand == -1)
		{
			CancelP("repeat-dispatch-unavailable");
			return;
		}
		m_PAmmo = m_PMagazine.GetAmmoCount();
		m_PCycle++;
		m_PStarted = true; // Inner loop does not replay StartReload.
		m_PEventStage = 1;
		m_PCommitted = false;
		m_PReady = false;
		m_WReady = false;
		m_PNextScheduled = false;
		m_PArmed = true;
		m_PWatchTicks = 0;
		Print("[ARMST-T4B-PCOMMIT] phase=inner-dispatch cycle=" + m_PCycle.ToString() + " decision=continue", LogLevel.NORMAL);
		wanim.CallCommand(weaponCommand, 2, 0.0);
		anim.CallCommand(command, 2, 0.0);
	}

	void CancelP(string reason)
	{
		if (!m_PActive)
			return;
		if (reason == "second-r")
		{
			m_PStopAfterInsert = true;
			Print("[ARMST-T4B-PCOMMIT] phase=stop-requested boundary=check-continue", LogLevel.NORMAL);
			ScheduleNextP();
			return;
		}
		m_PArmed = false;
		m_PActive = false;
		m_PClosing = true;
		m_PGeneration++; // Invalidate all outstanding watch/continuation callbacks.
		m_PNextScheduled = false;
		// Release a graph waiting at CheckContinue. Each graph also has a 10s exit.
		CharacterAnimationComponent stopAnim;
		if (m_PActor)
			stopAnim = CharacterAnimationComponent.Cast(m_PActor.FindComponent(CharacterAnimationComponent));
		ARMST_T4B_ArmstV2_WeaponAnimationComponent stopWeapon = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(GetOwner().FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
		if (stopAnim)
		{
			TAnimGraphCommand stopCommand = stopAnim.BindCommand("CMD_ARMST_TransportProbe");
			if (stopCommand != -1)
				stopAnim.CallCommand(stopCommand, 3, 0.0);
		}
		if (stopWeapon)
		{
			stopWeapon.T4BWPropRequestStop();
			int stopWeaponCommand = stopWeapon.BindCommand("CMD_ARMST_TransportProbe");
			if (stopWeaponCommand != -1)
				stopWeapon.CallCommand(stopWeaponCommand, 3, 0.0);
		}
		Print("[ARMST-T4B-PCOMMIT] phase=cancel reason=" + reason, LogLevel.NORMAL);
		ScheduleDrainP();
		GetGame().GetCallqueue().CallLater(WatchDetachedDrainP, 100, false, m_PGeneration);
	}
}
