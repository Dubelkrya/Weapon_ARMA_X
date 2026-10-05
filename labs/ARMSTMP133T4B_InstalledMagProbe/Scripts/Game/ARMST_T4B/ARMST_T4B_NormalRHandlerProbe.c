// ============================================================================
// ARMST MP-133 T4b - Task #1, Layer-C NORMAL-R handler PROBE (phase 1).
//
// Purpose (lab diagnostic ONLY): prove at runtime that
//   1) a normal R is delivered to SCR_CharacterCommandHandlerComponent.HandleWeaponReloading;
//   2) the request can be CONSUMED for the T4b lab weapon before native whole-mag
//      reload starts;
//   3) nothing about the fixed tube / ammo / chamber changes.
//
// Gate: for EVERY non-lab weapon/character this override delegates UNCHANGED to
//       super (original engine behaviour). Lab identity uses the proven T4b
//       component gate ARMST_T4B_WeaponProbe on the current weapon entity.
//
// Phase 1 is OBSERVE + SUPPRESS only. FORBIDDEN here (do not add):
//   SetReloadWeapon / ReloadWeapon / ReloadWeaponWith / SetAmmoCount /
//   spawn|attach|detach|despawn magazines / custom animation variables.
//
// This is a temporary diagnostic probe, NOT final reload architecture.
// ============================================================================
modded class SCR_CharacterCommandHandlerComponent
{
	// read-only instance-identity tracking for the magazine entity (reference-change tag)
	protected IEntity m_rprobeMagEnt;
	protected int m_rprobeMagTag;
	protected int m_rprobeMagNextTag;

	override bool HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)
	{
		// --- resolve current weapon via the character controller ---
		BaseWeaponComponent weapon = null;
		CharacterControllerComponent ctrl = GetControllerComponent();
		if (ctrl)
		{
			BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
			if (wm)
				weapon = wm.GetCurrentWeapon();
		}

		IEntity weaponEntity = null;
		if (weapon)
			weaponEntity = weapon.GetOwner();

		// --- lab identity gate: proven ARMST_T4B_WeaponProbe component ---
		ARMST_T4B_WeaponProbe probe = null;
		if (weaponEntity)
			probe = ARMST_T4B_WeaponProbe.Cast(weaponEntity.FindComponent(ARMST_T4B_WeaponProbe));

		// --- non-lab: original behaviour, untouched ---
		if (!probe)
			return super.HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID);

		// ================= lab-only diagnostic branch (READ-ONLY) ============
		int reloadType = -1;
		bool startReloading = false;
		if (pInputCtx)
		{
			reloadType = pInputCtx.GetWeaponReloadType();
			startReloading = pInputCtx.WeaponIsStartReloading();
		}

		string wep = "-";
		if (weaponEntity && weaponEntity.GetPrefabData())
			wep = weaponEntity.GetPrefabData().GetPrefabName();

		BaseMagazineComponent mag = null;
		IEntity magEnt = null;
		int magAmmo = -1;
		int magMax = -1;
		if (weapon)
		{
			mag = weapon.GetCurrentMagazine();
			if (mag)
			{
				magEnt = mag.GetOwner();
				magAmmo = mag.GetAmmoCount();
				magMax = mag.GetMaxAmmoCount();
			}
		}

		string magName = "-";
		if (magEnt && magEnt.GetPrefabData())
			magName = magEnt.GetPrefabData().GetPrefabName();

		// read-only instance identity: reference-change tag (SDK 1.8.0.13 exposes no raw
		// entity-ID for IEntity; the proven lab pattern is reference comparison + tag).
		// A different tag => the engine despawned/replaced the magazine entity instance,
		// even if the prefab name is identical.
		string magEntity = "-";
		if (magEnt)
		{
			if (magEnt != m_rprobeMagEnt)
			{
				m_rprobeMagEnt = magEnt;
				m_rprobeMagNextTag++;
				m_rprobeMagTag = m_rprobeMagNextTag;
			}
			magEntity = "M" + m_rprobeMagTag.ToString();
		}

		int barrel = -1;
		int chambered = -1;
		if (weapon)
		{
			BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
			if (muzzle)
			{
				barrel = muzzle.GetCurrentBarrelIndex();
				chambered = 0;
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
			}
		}

		Print("[ARMST-T4B-RPROBE] phase=handler-enter cmd=" + pCurrentCommandID.ToString()
			+ " reloadType=" + reloadType.ToString()
			+ " startReloading=" + startReloading.ToString()
			+ " wep=" + wep
			+ " mag=" + magName
			+ " magEntity=" + magEntity
			+ " magAmmo=" + magAmmo.ToString() + "/" + magMax.ToString()
			+ " barrel=" + barrel.ToString()
			+ " chambered=" + chambered.ToString()
			+ " consumed=1", LogLevel.NORMAL);

		// consume the lab reload request; native whole-mag reload must not proceed
		return true;
	}
}
