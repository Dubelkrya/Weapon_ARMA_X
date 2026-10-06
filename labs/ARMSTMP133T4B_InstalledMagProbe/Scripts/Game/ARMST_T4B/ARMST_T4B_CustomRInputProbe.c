// ============================================================================
// ARMST MP-133 T4b - Phase B custom-R input probe (STAGED, lab-only, log-only).
//
// CONTEXT LIFECYCLE V2 (owner review 6023891764):
//   - unsupported `override void OnDelete(IEntity owner)` on SCR_PlayerController
//     REMOVED (PlayerController/SCR_PlayerController expose no OnDelete).
//   - listener teardown now uses the PROVEN lifecycle hook
//     `override void OnOwnershipChanged(bool changing, bool becameOwner)`
//     (SDK 1.8.0.13: SCR_PlayerController.OnOwnershipChanged overrides
//     PlayerController.OnOwnershipChanged(bool changing, bool becameOwner)); super kept.
//   - periodic context activation unchanged: SCR_PlayerController.OnUpdate ->
//     local gate -> controlled entity -> character controller -> weapon manager ->
//     current weapon -> ARMST_T4B_WeaponProbe -> ActivateContext(...).
//     `DeactivateContext` does NOT exist in 1.8.0.13 -> never called.
//
// Passive/log-only: NO HandleWeaponReloading, NO ReloadWeapon/ReloadWeaponWith/
// SetReloadWeapon/SetCurrentCommand/CallCommand, NO SetAmmoCount/ClearChamber,
// NO mag/chamber mutation, NO ASTRA, NO G3B2. Per-frame body = local gate +
// weapon probe + ActivateContext ONLY.
// ============================================================================
modded class SCR_PlayerController
{
	protected int m_iT4BRInputSeq;
	protected bool m_bT4BRListenerActive;

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

	// The ONLY per-frame gameplay-adjacent action: keep the lab context active while
	// the local controlled entity has the canonical T4B MP-133 current. No deactivate.
	protected void T4BRMaintainContext()
	{
		IEntity controlled = GetControlledEntity();
		if (!controlled)
			return;

		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(controlled.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl)
			return;

		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
		if (!wm)
			return;

		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn)
			return;

		IEntity we = wpn.GetOwner();
		if (!we)
			return;

		if (!we.FindComponent(ARMST_T4B_WeaponProbe))
			return;

		InputManager im = GetGame().GetInputManager();
		if (im)
			im.ActivateContext("ARMST_MP133_ReloadContext");
	}

	// Log-only: the custom action received physical R. No reload call, no writes.
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
	}
}
