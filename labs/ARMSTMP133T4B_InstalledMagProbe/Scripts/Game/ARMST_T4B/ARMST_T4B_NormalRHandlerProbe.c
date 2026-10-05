// ============================================================================
// ARMST MP-133 T4b - Task #1, NORMAL-R PRE-HANDLER AMMO MUTATION PROBE V2 (STAGED).
//
// Question: WHO/WHEN changes the fixed Tube3 from 2/3 to 1/3 relative to the
// first R press? V1 saw 2/3 baseline but already 1/3 at the first
// HandleWeaponReloading() entry -> mutation happens BEFORE the handler.
//
// V2 = observe-only + the existing lab-only suppress in HandleWeaponReloading.
// It adds STAGE logging (baseline / idle-control / pre-handler / handler-enter /
// handler-consume / post-handler-next-frame) with a monotonic seq= and the full
// snapshot incl. muzzleSupply, so the 2/3->1/3 transition can be localized.
//
// Pre-handler script hooks (SDK 1.8.0.13, all script/overridable):
//   void Update(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)   // per-tick
//   bool HandleWeapons(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)  // umbrella
//   bool HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)
//
// HARD RULES: no SetReloadWeapon/ReloadWeapon/ReloadWeaponWith/SetAmmoCount/
// CallCommand/SetVariableBool/Spawn|Attach|Detach|Despawn|MagRelease.
// Non-lab -> delegate unchanged to super in EVERY override.
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
	protected bool m_rprobePreLogged;
	protected bool m_rprobeHandlerLogged;
	protected bool m_rprobePostPending;

	// ---------------- helpers ----------------
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

	// ---------------- per-tick: baseline + idle-control + post-handler ----------------
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

	// ---------------- umbrella: first observation of an active reload request ----------------
	override bool HandleWeapons(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)
	{
		BaseWeaponComponent weapon = null;
		IEntity weaponEntity = null;
		ARMST_T4B_WeaponProbe probe = RProbeResolve(weapon, weaponEntity);
		if (probe && !m_rprobePreLogged && pInputCtx && pInputCtx.WeaponIsStartReloading())
		{
			RProbeLog("pre-handler", pCurrentCommandID, pInputCtx.GetWeaponReloadType(), pInputCtx.WeaponIsStartReloading(), weapon, weaponEntity);
			m_rprobePreLogged = true;
		}
		return super.HandleWeapons(pInputCtx, pDt, pCurrentCommandID);
	}

	// ---------------- the reload handler: observe once + consume (lab only) ----------------
	override bool HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)
	{
		BaseWeaponComponent weapon = null;
		IEntity weaponEntity = null;
		ARMST_T4B_WeaponProbe probe = RProbeResolve(weapon, weaponEntity);

		// non-lab: original behaviour, untouched
		if (!probe)
			return super.HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID);

		int rt = -1;
		bool sr = false;
		if (pInputCtx)
		{
			rt = pInputCtx.GetWeaponReloadType();
			sr = pInputCtx.WeaponIsStartReloading();
		}

		if (!m_rprobeHandlerLogged)
		{
			RProbeLog("handler-enter", pCurrentCommandID, rt, sr, weapon, weaponEntity);
			m_rprobeHandlerLogged = true;
		}
		RProbeLog("handler-consume", pCurrentCommandID, rt, sr, weapon, weaponEntity);
		m_rprobePostPending = true;

		return true; // consume lab reload request; native whole-mag reload must not proceed
	}
}
