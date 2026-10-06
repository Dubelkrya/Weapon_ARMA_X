// ============================================================================
// ARMST MP-133 T4b - Phase B0 custom-R input probe (STAGED, lab-only, log-only).
//
// Purpose: prove routing of ONE physical R for the lab MP-133:
//   physical R -> ARMST_MP133_Reload action -> [ARMST-T4B-RINPUT] log,
//   while the vanilla reload must NOT receive the same R (observed via the existing
//   ARMST_T4B_AstraV2_WeaponAnimationComponent.OnCharacterCommand [ARMST-T4B-CMDROUTE]).
//
// Passive only: NO writers, NO Update, NO timers, NO HandleWeaponReloading, NO
// ReloadWeapon/ReloadWeaponWith/SetReloadWeapon, NO ammo/mag/chamber mutation.
//
// Context lifecycle (event-driven, no polling): the ARMST_MP133_ReloadContext is
// activated only while the current weapon carries ARMST_T4B_WeaponProbe, on weapon
// change complete; deactivated on leaving the lab weapon and on delete.
// ============================================================================
modded class SCR_CharacterControllerComponent
{
	protected int m_iT4BRInputSeq;
	protected bool m_bT4BRContextActive;

	override void OnInit(IEntity owner)
	{
		super.OnInit(owner);

		InputManager im = GetGame().GetInputManager();
		if (im)
			im.AddActionListener("ARMST_MP133_Reload", EActionTrigger.DOWN, T4BRInputDown);

		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		if (wm && wm.m_OnWeaponChangeCompleteInvoker)
			wm.m_OnWeaponChangeCompleteInvoker.Insert(T4BRWeaponChanged);
	}

	override void OnDelete(IEntity owner)
	{
		InputManager im = GetGame().GetInputManager();
		if (im)
		{
			im.RemoveActionListener("ARMST_MP133_Reload", EActionTrigger.DOWN, T4BRInputDown);
			if (m_bT4BRContextActive)
			{
				im.DeactivateContext("ARMST_MP133_ReloadContext");
				m_bT4BRContextActive = false;
			}
		}
		super.OnDelete(owner);
	}

	// Weapon change complete -> re-evaluate the lab gate (event-driven, no polling).
	protected void T4BRWeaponChanged()
	{
		T4BRSyncContext();
	}

	protected void T4BRSyncContext()
	{
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
