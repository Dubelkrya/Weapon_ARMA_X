// ============================================================================
// ARMST MP-133 T4b - +1 into the ALREADY INSTALLED lab magazine (DIAGNOSTIC ONLY)
// ----------------------------------------------------------------------------
// Isolated lab. A NEW lab weapon prefab (Prefabs/Test/ARMST_T4B_TestWeapon.et)
// inherits the production MP-133 and carries:
//   * ARMST_T4B_WeaponProbe         - sets a baseline ammo on ITS OWN installed
//                                     magazine on init and marks the lab weapon;
//   * the inherited ActionsManagerComponent "{A29AE67FF4D82B0F}" extended with one
//     weapon-local context action:
//   * ARMST_T4B_AddRoundWeaponAction - "T4b: +1 into installed mag"; performs ONE
//                                     guarded SetAmmoCount(old+1) on the magazine
//                                     that is currently installed in THIS weapon.
//
// No detach/replace/spawn, no donor, no inventory, no chamber/pump, no R/fire/Shift,
// no global modded hook, no per-item input listener, no native mag-animation events.
// Installed-SDK only: BaseWeaponComponent.GetCurrentMagazine/GetCurrentMuzzle,
// BaseMagazineComponent.Get/SetAmmoCount/GetMaxAmmoCount/GetOwner,
// BaseMuzzleComponent.GetAmmoCount/GetMaxAmmoCount/IsCurrentBarrelChambered.
//
// Synthetic +1 only: this CREATES a test cartridge on a disposable lab weapon. It is
// NOT a gameplay reload and does NOT prove multiplayer authority/replication.
// ============================================================================

class ARMST_T4B_WeaponProbeClass : ScriptComponentClass
{
}

[BaseContainerProps()]
class ARMST_T4B_WeaponProbe : ScriptComponent
{
	protected bool m_bInitDone = false;
	protected bool m_bBaselineDone = false;
	protected int m_iRetries = 0;
	protected int m_t4bTag = 1;

	// Baseline ammo for the ALREADY INSTALLED lab magazine (0..max). Default 0 so the
	// +1 test starts from 0/10; set to max to test the full-rejection case.
	[Attribute("0", UIWidgets.Slider, "T4b installed magazine baseline ammo", "0 15 1")]
	int m_iT4BStartAmmo;

	override void OnPostInit(IEntity owner)
	{
		super.OnPostInit(owner);
		if (m_bInitDone)
			return;
		m_bInitDone = true;
		if (m_t4bTag == 0)
			m_t4bTag = 1;

		BaseWeaponComponent wpn = T4BWeapon();
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-INSTALLED] #0 phase=init ev=component reason=attach"
			+ " " + T4BState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		if (wpn)
			ApplyBaseline();
		else
			GetGame().GetCallqueue().CallLater(T4BDeferredRetry, 250, false);
	}

	void T4BDeferredRetry()
	{
		if (m_bBaselineDone)
			return;
		m_iRetries++;
		if (T4BWeapon())
		{
			ApplyBaseline();
			return;
		}
		if (m_iRetries < 4)
			GetGame().GetCallqueue().CallLater(T4BDeferredRetry, 250, false);
		else
			Print("[ARMST_T4B-INSTALLED] #0 phase=reject ev=component reason=no-weapon-at-init", LogLevel.WARNING);
	}

	void ApplyBaseline()
	{
		BaseWeaponComponent wpn = T4BWeapon();
		if (!wpn)
			return;
		BaseMagazineComponent mag = wpn.GetCurrentMagazine();
		if (!mag)
		{
			Print("[ARMST_T4B-INSTALLED] #0 phase=reject ev=component reason=no-installed-magazine-at-init", LogLevel.WARNING);
			return;
		}

		int start = m_iT4BStartAmmo;
		if (start < 0)
			start = 0;
		int mx = mag.GetMaxAmmoCount();
		if (start > mx)
			start = mx;
		mag.SetAmmoCount(start);
		m_bBaselineDone = true;

		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-INSTALLED] #0 phase=baseline ev=component reason=init start=" + start.ToString()
			+ " " + T4BState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	BaseWeaponComponent T4BWeapon()
	{
		IEntity o = GetOwner();
		if (!o)
			return null;
		return BaseWeaponComponent.Cast(o.FindComponent(WeaponComponent));
	}

	string T4BState()
	{
		BaseWeaponComponent wpn = T4BWeapon();
		string wep = "-";
		int wpnTag = -1;
		int ammo = -1;
		int mx = -1;
		string magRes = "-";
		int mzAmmo = -1;
		int mzMax = -1;
		int chambered = -1;
		int barrel = -1;
		if (wpn)
		{
			IEntity we = wpn.GetOwner();
			if (we)
			{
				wpnTag = m_t4bTag;
				if (we.GetPrefabData())
					wep = we.GetPrefabData().GetPrefabName();
			}
			BaseMagazineComponent mag = wpn.GetCurrentMagazine();
			if (mag)
			{
				ammo = mag.GetAmmoCount();
				mx = mag.GetMaxAmmoCount();
				IEntity me = mag.GetOwner();
				if (me && me.GetPrefabData())
					magRes = me.GetPrefabData().GetPrefabName();
			}
			BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
			if (muzzle)
			{
				mzAmmo = muzzle.GetAmmoCount();
				mzMax = muzzle.GetMaxAmmoCount();
				barrel = muzzle.GetCurrentBarrelIndex();
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
				else
					chambered = 0;
			}
		}

		string s = "wpnTag=W" + wpnTag.ToString();
		s = s + " wep=" + wep;
		s = s + " mag=" + magRes;
		s = s + " ammo=" + ammo.ToString() + "/" + mx.ToString();
		s = s + " muzzle=" + mzAmmo.ToString() + "/" + mzMax.ToString();
		s = s + " chambered=" + chambered.ToString() + " barrel=" + barrel.ToString();
		return s;
	}
}

// ----------------------------------------------------------------------------
// Weapon-local context interaction: "T4b: +1 into installed mag".
// ----------------------------------------------------------------------------
class ARMST_T4B_AddRoundWeaponAction : ScriptedUserAction
{
	protected bool m_bUsed = false;
	protected int m_iSeq = 0;
	protected IEntity m_t4bWeaponEntity;

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		m_t4bWeaponEntity = pOwnerEntity;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-INSTALLED] #0 phase=action-init ev=useraction reason=register"
			+ " " + T4BActionState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		outName = "T4b: +1 into installed mag";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Lab API test: SetAmmoCount(old+1) on the installed magazine; rejects when full or already used.";
		return true;
	}

	override bool CanBeShownScript(IEntity user)
	{
		return true;
	}

	override bool CanBePerformedScript(IEntity user)
	{
		return true;
	}

	override event bool HasLocalEffectOnlyScript()
	{
		return false;
	}

	override event bool CanBroadcastScript()
	{
		return true;
	}

	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
	{
		m_iSeq++;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;

		// Guard: exact lab weapon only (the action's owner must be the probe-carrying weapon).
		BaseWeaponComponent wpn = T4BActionWeapon();
		if (!wpn)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=no-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (!wpn.FindComponent(ARMST_T4B_WeaponProbe))
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=not-lab-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		BaseMagazineComponent magPre = wpn.GetCurrentMagazine();
		if (!magPre)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=no-installed-magazine srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		IEntity magEntPre = magPre.GetOwner();
		int a = magPre.GetAmmoCount();
		int mx = magPre.GetMaxAmmoCount();
		BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
		int mzPre = -1;
		int barrelPre = -1;
		bool chPre = false;
		if (muzzle)
		{
			mzPre = muzzle.GetAmmoCount();
			barrelPre = muzzle.GetCurrentBarrelIndex();
			chPre = muzzle.IsCurrentBarrelChambered();
		}

		Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
			+ " phase=pre ev=useraction reason=invoked"
			+ " " + T4BActionState()
			+ " used=" + T4BB(m_bUsed)
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		if (m_bUsed)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=already-used " + T4BActionState(), LogLevel.NORMAL);
			return;
		}
		if (a >= mx)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=full " + T4BActionState(), LogLevel.NORMAL);
			return;
		}
		if (a < 0)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=bad-ammo " + T4BActionState(), LogLevel.NORMAL);
			return;
		}

		int want = a + 1;
		magPre.SetAmmoCount(want);

		// Immediate read-back / identity checks.
		BaseMagazineComponent magPost = wpn.GetCurrentMagazine();
		IEntity magEntPost = null;
		int a2 = -1;
		if (magPost)
		{
			magEntPost = magPost.GetOwner();
			a2 = magPost.GetAmmoCount();
		}
		int mzPost = -1;
		int barrelPost = -1;
		bool chPost = false;
		BaseMuzzleComponent muzzle2 = wpn.GetCurrentMuzzle();
		if (muzzle2)
		{
			mzPost = muzzle2.GetAmmoCount();
			barrelPost = muzzle2.GetCurrentBarrelIndex();
			chPost = muzzle2.IsCurrentBarrelChambered();
		}

		bool sameMagazine = (magPost == magPre);
		bool sameOwner = (magEntPost == magEntPre);
		bool chamberUnchanged = (mzPre == mzPost) && (barrelPre == barrelPost) && (chPre == chPost);
		m_bUsed = true;

		Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
			+ " phase=post ev=useraction reason=write want=" + want.ToString()
			+ " got=" + a2.ToString()
			+ " sameMagazine=" + T4BB(sameMagazine)
			+ " sameOwner=" + T4BB(sameOwner)
			+ " chamberUnchanged=" + T4BB(chamberUnchanged)
			+ " " + T4BActionState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	string T4BB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	BaseWeaponComponent T4BActionWeapon()
	{
		IEntity o = GetOwner();
		if (!o)
			return null;
		return BaseWeaponComponent.Cast(o.FindComponent(WeaponComponent));
	}

	string T4BActionState()
	{
		BaseWeaponComponent wpn = T4BActionWeapon();
		string wep = "-";
		int ammo = -1;
		int mx = -1;
		string magRes = "-";
		int mz = -1;
		int chambered = -1;
		if (wpn)
		{
			IEntity we = wpn.GetOwner();
			if (we && we.GetPrefabData())
				wep = we.GetPrefabData().GetPrefabName();
			BaseMagazineComponent mag = wpn.GetCurrentMagazine();
			if (mag)
			{
				ammo = mag.GetAmmoCount();
				mx = mag.GetMaxAmmoCount();
				IEntity me = mag.GetOwner();
				if (me && me.GetPrefabData())
					magRes = me.GetPrefabData().GetPrefabName();
			}
			BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
			if (muzzle)
			{
				mz = muzzle.GetAmmoCount();
				chambered = 0;
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
			}
		}
		string s = "wep=" + wep;
		s = s + " mag=" + magRes;
		s = s + " ammo=" + ammo.ToString() + "/" + mx.ToString();
		s = s + " muzzle=" + mz.ToString();
		s = s + " chambered=" + chambered.ToString();
		return s;
	}
}
