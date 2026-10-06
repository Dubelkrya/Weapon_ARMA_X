// ============================================================================
// ARMST MP-133 T4b - Phase B0 custom-R input probe (STAGED, lab-only, log-only).
//
// Corrected per owner review 6022566622:
//   - weapon-change callback signature now matches ScriptInvoker<BaseWeaponComponent>;
//   - invoker Insert/Remove balanced (same stored weapon manager);
//   - proven local-player gate (SCR_PlayerController.GetLocalControlledEntity)
//     around AddActionListener / ActivateContext / DeactivateContext / logging;
//   - explicit initial T4BRSyncContext() after local registration.
//
// Passive only: NO writers, NO Update, NO timers, NO HandleWeaponReloading, NO
// ReloadWeapon/ReloadWeaponWith/SetReloadWeapon/SetCurrentCommand/CallCommand,
// NO ammo/mag/chamber mutation.
//
// Local-player pattern source (PROVEN, installed ARMST): historical
// ARMST_MP133_AnimationLab/Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c:
//   override protected void OnControlledByPlayer(IEntity owner, bool controlled)
//   { bool local = (owner == SCR_PlayerController.GetLocalControlledEntity()); ... }
// ============================================================================
modded class SCR_CharacterControllerComponent
{
	protected int m_iT4BRInputSeq;
	protected bool m_bT4BRListenerActive;
	protected bool m_bT4BRContextActive;
	protected BaseWeaponManagerComponent m_pT4BRWeaponManager;

	override void OnInit(IEntity owner)
	{
		super.OnInit(owner);

		// Balanced subscription: store the manager so OnDelete can Remove the same invoker.
		m_pT4BRWeaponManager = GetWeaponManagerComponent();
		if (m_pT4BRWeaponManager && m_pT4BRWeaponManager.m_OnWeaponChangeCompleteInvoker)
			m_pT4BRWeaponManager.m_OnWeaponChangeCompleteInvoker.Insert(T4BRWeaponChanged);
	}

	// Local-player gate: only the locally controlled character registers the global
	// input listener / activates the global context.
	override protected void OnControlledByPlayer(IEntity owner, bool controlled)
	{
		super.OnControlledByPlayer(owner, controlled);

		bool local = (owner == SCR_PlayerController.GetLocalControlledEntity());
		InputManager im = GetGame().GetInputManager();
		if (!im)
			return;

		if (controlled && local)
		{
			if (!m_bT4BRListenerActive)
			{
				im.AddActionListener("ARMST_MP133_Reload", EActionTrigger.DOWN, T4BRInputDown);
				m_bT4BRListenerActive = true;
			}
			T4BRSyncContext(); // explicit initial sync (lab MP-133 may already be current)
		}
		else
		{
			T4BRTeardownLocal();
		}
	}

	protected void T4BRTeardownLocal()
	{
		InputManager im = GetGame().GetInputManager();
		if (im)
		{
			if (m_bT4BRListenerActive)
			{
				im.RemoveActionListener("ARMST_MP133_Reload", EActionTrigger.DOWN, T4BRInputDown);
				m_bT4BRListenerActive = false;
			}
			if (m_bT4BRContextActive)
			{
				im.DeactivateContext("ARMST_MP133_ReloadContext");
				m_bT4BRContextActive = false;
			}
		}
	}

	override void OnDelete(IEntity owner)
	{
		T4BRTeardownLocal();
		if (m_pT4BRWeaponManager && m_pT4BRWeaponManager.m_OnWeaponChangeCompleteInvoker)
			m_pT4BRWeaponManager.m_OnWeaponChangeCompleteInvoker.Remove(T4BRWeaponChanged);
		m_pT4BRWeaponManager = null;
		super.OnDelete(owner);
	}

	// Signature matches ScriptInvoker<BaseWeaponComponent>. Argument is NOT used for any
	// gameplay mutation; it only triggers a local-gated context re-sync.
	protected void T4BRWeaponChanged(BaseWeaponComponent newWeapon)
	{
		if (GetOwner() != SCR_PlayerController.GetLocalControlledEntity())
			return;
		T4BRSyncContext();
	}

	protected void T4BRSyncContext()
	{
		if (GetOwner() != SCR_PlayerController.GetLocalControlledEntity())
			return;

		InputManager im = GetGame().GetInputManager();
		if (!im)
			return;

		bool lab = false;
		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		if (wm)
		{
			BaseWeaponComponent wpn = wm.GetCurrentWeapon();
			if (wpn)
			{
				IEntity we = wpn.GetOwner();
				if (we && we.FindComponent(ARMST_T4B_WeaponProbe))
					lab = true;
			}
		}

		if (lab && !m_bT4BRContextActive)
		{
			im.ActivateContext("ARMST_MP133_ReloadContext");
			m_bT4BRContextActive = true;
		}
		else if (!lab && m_bT4BRContextActive)
		{
			im.DeactivateContext("ARMST_MP133_ReloadContext");
			m_bT4BRContextActive = false;
		}
	}

	// Log-only: the custom action received physical R. No reload call, no writes.
	protected void T4BRInputDown(float value = 0.0, EActionTrigger reason = 0)
	{
		if (GetOwner() != SCR_PlayerController.GetLocalControlledEntity())
			return;

		m_iT4BRInputSeq++;

		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		BaseWeaponComponent wpn = null;
		if (wm)
			wpn = wm.GetCurrentWeapon();

		bool labWeapon = false;
		bool magPresent = false;
		int ammo = -1;
		int maxAmmo = -1;
		int chambered = -1;
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
	}
}
