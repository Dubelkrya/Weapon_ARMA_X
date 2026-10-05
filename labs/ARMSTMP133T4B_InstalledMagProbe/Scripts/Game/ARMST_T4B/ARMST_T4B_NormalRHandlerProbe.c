// ============================================================================
// ARMST MP-133 T4b - Task #1, V1 + INERT RELOAD-COMMAND BRIDGE (STAGED, source prep only).
//
// Base = current pickup-safe V1 handler-only (57c7124),
//        SHA-256 D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32.
//
// Adds ONLY: on a normal lab reload request, set the selected inert reload command
// (10) through the documented CharacterInputContext API, then consume the native
// request exactly as V1 already does. No ammo/magazine/chamber writer, no graph route.
//
// Command selection (Phase A, re-verified against the CURRENT lab graph
// Assets/MP133_AstraShellGraph_test/MP133_Astra2.agf): the active ASTRA2 graph
// references CMD_Weapon_Reload only for value 1 (rack bolt); the old whole-mag
// states (WeaponReloadSTM/MagReloadSTM/InsertMagAnim/RemoveMagAnim) were removed.
// cmd10 therefore has NO graph state, NO bolt/rack path, NO clip path and no
// production meaning in the lab graph. Native engine-level inertness is UNRESOLVED
// and is exactly what this probe measures (no side effects expected).
//
// HARD RULES: no global Update()/HandleWeapons(), no ReloadWeapon()/ReloadWeaponWith(),
// no SetAmmoCount(), no magazine spawn/attach/detach/despawn/release, no chamber writer,
// no CallCommand(), no ASTRA bool vars. Non-lab -> exact super, unchanged.
// ============================================================================
// Shared inert reload-command value (re-verified: no ASTRA2 graph state, no bolt/rack,
// no clip path). The weapon-local observer references this same global.
const int ARMST_T4B_INERT_RELOAD_CMD = 10;

// Reload command TYPE id. Evidence: T2c owner runtime observed commandID=0 for BOTH the
// native rack (intValue=1) and the stock remove+insert path (intValue=5). The SDK exposes
// no named CMD_Weapon_Reload constant (animation commands are string-bound via
// SCR_CharacterAnimationComponent.BindCommand), so the reload command type is pinned to the
// observed value. The observer proves the route ONLY when commandID == this AND
// intValue == ARMST_T4B_INERT_RELOAD_CMD; raw commandID/intValue are always logged so the
// owner can correct this constant from runtime evidence.
const int ARMST_T4B_RELOAD_COMMAND_ID = 0;

modded class SCR_CharacterCommandHandlerComponent
{
	// read-only instance-identity tracking for the magazine entity (reference-change tag)
	protected IEntity m_rprobeMagEnt;
	protected int m_rprobeMagTag;
	protected int m_rprobeMagNextTag;

	// one-shot latch for the inert-command bridge (one cold-start test only)
	protected bool m_bInertCmdSet;
	protected bool m_bInertCmdSkipLogged;

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

		// --- inert command bridge: ONE-SHOT per cold-start test (latch BEFORE the setter) ---
		if (startReloading && pInputCtx && !m_bInertCmdSet)
		{
			m_bInertCmdSet = true;
			pInputCtx.SetReloadWeapon(ARMST_T4B_INERT_RELOAD_CMD);
			Print("[ARMST-T4B-RPROBE] phase=inert-command-set inertCmd=" + ARMST_T4B_INERT_RELOAD_CMD.ToString()
				+ " once=1 cmd=" + pCurrentCommandID.ToString()
				+ " reloadType=" + reloadType.ToString(), LogLevel.NORMAL);
		}
		else if (startReloading && pInputCtx && !m_bInertCmdSkipLogged)
		{
			m_bInertCmdSkipLogged = true;
			Print("[ARMST-T4B-RPROBE] phase=inert-command-skip alreadySet=1 cmd=" + pCurrentCommandID.ToString()
				+ " reloadType=" + reloadType.ToString(), LogLevel.NORMAL);
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
