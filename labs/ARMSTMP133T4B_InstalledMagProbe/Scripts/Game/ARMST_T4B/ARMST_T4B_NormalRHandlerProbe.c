// ============================================================================
// ARMST MP-133 T4b - Task #1, PICKUP BISECT CONTROL: V1 + Update() only.
//
// Proven:
//   V1 (57c7124)  = HandleWeaponReloading() only  -> pickup WORKS.
//   V2 (C9D49A1B) = V1 + Update() + HandleWeapons() -> pickup BROKEN.
//
// This control = V1 + ONLY the V2 Update() override (NO HandleWeapons()).
//   pickup works  -> regression is in HandleWeapons()
//   pickup broken -> regression is in Update()
//
// The reload handler below is the exact V1 (57c7124) handler, unchanged.
// Diagnostic/read-only. Non-lab delegates unchanged to super in every override.
// HARD RULES: no SetReloadWeapon/ReloadWeapon/ReloadWeaponWith/SetAmmoCount/
// CallCommand/SetVariableBool/Spawn|Attach|Detach|Despawn|MagRelease.
// ============================================================================
modded class SCR_CharacterCommandHandlerComponent
{
	// --- magazine instance identity (reference-change tag) ---
	protected IEntity m_rprobeMagEnt;
	protected int m_rprobeMagTag;
	protected int m_rprobeMagNextTag;

	// --- stage sequencing / change detection (read-only, does not alter game state) ---
	protected int m_rprobeSeq;
	protected bool m_rprobeBaselineLogged;
	protected int m_rprobeLastAmmo = -2;
	protected int m_rprobeLastSupply = -2;
	protected int m_rprobeLastChambered = -2;
	protected bool m_rprobePostPending;

	// ---------------- helpers (from V2; used by Update) ----------------
	protected ARMST_T4B_WeaponProbe RProbeResolve(out BaseWeaponComponent weapon, out IEntity weaponEntity)
	{
		weapon = null;
		weaponEntity = null;
		CharacterControllerComponent ctrl = GetControllerComponent();
		if (ctrl)
		{
			BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
			if (wm)
				weapon = wm.GetCurrentWeapon();
		}
		if (weapon)
			weaponEntity = weapon.GetOwner();
		if (!weaponEntity)
			return null;
		return ARMST_T4B_WeaponProbe.Cast(weaponEntity.FindComponent(ARMST_T4B_WeaponProbe));
	}

	protected string RProbeTag(IEntity magEnt)
	{
		if (!magEnt)
			return "-";
		if (magEnt != m_rprobeMagEnt)
		{
			m_rprobeMagEnt = magEnt;
			m_rprobeMagNextTag++;
			m_rprobeMagTag = m_rprobeMagNextTag;
		}
		return "M" + m_rprobeMagTag.ToString();
	}

	// logs one stage snapshot; also refreshes the last-state cache
	protected void RProbeLog(string phase, int cmd, int reloadType, bool startReloading, BaseWeaponComponent weapon, IEntity weaponEntity)
	{
		m_rprobeSeq++;

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
		string magEntity = RProbeTag(magEnt);

		int supply = -1;
		int supplyMax = -1;
		int barrel = -1;
		int chambered = -1;
		if (weapon)
		{
			BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
			if (muzzle)
			{
				supply = muzzle.GetAmmoCount();
				supplyMax = muzzle.GetMaxAmmoCount();
				barrel = muzzle.GetCurrentBarrelIndex();
				chambered = 0;
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
			}
		}

		Print("[ARMST-T4B-RPROBE] seq=" + m_rprobeSeq.ToString()
			+ " phase=" + phase
			+ " cmd=" + cmd.ToString()
			+ " reloadType=" + reloadType.ToString()
			+ " startReloading=" + startReloading.ToString()
			+ " wep=" + wep
			+ " mag=" + magName
			+ " magEntity=" + magEntity
			+ " magAmmo=" + magAmmo.ToString() + "/" + magMax.ToString()
			+ " muzzleSupply=" + supply.ToString() + "/" + supplyMax.ToString()
			+ " barrel=" + barrel.ToString()
			+ " chambered=" + chambered.ToString(), LogLevel.NORMAL);

		m_rprobeLastAmmo = magAmmo;
		m_rprobeLastSupply = supply;
		m_rprobeLastChambered = chambered;
	}

	// ---------------- per-tick: baseline + idle-control + post-handler (V2 Update) ----------------
	override void Update(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)
	{
		BaseWeaponComponent weapon = null;
		IEntity weaponEntity = null;
		ARMST_T4B_WeaponProbe probe = RProbeResolve(weapon, weaponEntity);
		if (!probe)
		{
			super.Update(pDt, pCurrentCommandID, pCurrentCommandFinished);
			return;
		}

		// current raw state for change detection
		IEntity me = null;
		int a = -1;
		if (weapon)
		{
			BaseMagazineComponent mag = weapon.GetCurrentMagazine();
			if (mag)
			{
				me = mag.GetOwner();
				a = mag.GetAmmoCount();
			}
		}
		int s = -1;
		int c = -1;
		if (weapon)
		{
			BaseMuzzleComponent mz = weapon.GetCurrentMuzzle();
			if (mz)
			{
				s = mz.GetAmmoCount();
				c = 0;
				if (mz.IsCurrentBarrelChambered())
					c = 1;
			}
		}

		bool changed = (me != m_rprobeMagEnt) || (a != m_rprobeLastAmmo) || (s != m_rprobeLastSupply) || (c != m_rprobeLastChambered);

		if (!m_rprobeBaselineLogged)
		{
			RProbeLog("baseline", pCurrentCommandID, -1, false, weapon, weaponEntity);
			m_rprobeBaselineLogged = true;
		}
		else if (m_rprobePostPending)
		{
			RProbeLog("post-handler-next-frame", pCurrentCommandID, -1, false, weapon, weaponEntity);
			m_rprobePostPending = false;
		}
		else if (changed)
		{
			RProbeLog("idle-control", pCurrentCommandID, -1, false, weapon, weaponEntity);
		}

		super.Update(pDt, pCurrentCommandID, pCurrentCommandFinished);
	}

	// ---------------- reload handler: exact V1 (57c7124), unchanged ----------------
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

		// read-only instance identity: reference-change tag
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
