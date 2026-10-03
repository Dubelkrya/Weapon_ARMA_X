// ============================================================================
// ARMST MP-133 T4b (UNIFIED) - installed-magazine +1 + T2a/T2c/T3-class diagnostics
// ----------------------------------------------------------------------------
// One working lab weapon (Prefabs/Test/ARMST_T4B_TestWeapon.et) that BOTH performs a
// guarded synthetic +1 on its ALREADY INSTALLED magazine AND passively observes weapon
// events / commands / magazine identity / ammo / muzzle / chamber.
//
// Ported capabilities (from T2a/T2c/T3), combined into the T4b probe as the snapshot hub:
//   * weapon-side OnAnimationEvent (selective, pre/post super)  -> [ARMST_T4B-EVT]
//   * OnCharacterCommand                                       -> [ARMST_T4B-CMD]
//   * T3-style snapshots: weapon/mag entity reference tags, ammo/max, muzzle supply,
//     barrel index, chamber-specific flag, chNeed/chPoss     -> [ARMST_T4B-INSTALLED]
// NOT ported on purpose: the global `modded SCR_CharacterControllerComponent` (player
// marker route + 1 Hz tick) and the player-authored marker route (owner: weapon does not
// auto-receive the player marker). The lab-only WeaponAnimationComponent subclass replaces
// the EXISTING inherited {60B4EA76EB15F6E0} instance (no second component added).
//
// The only write is the explicit owner-invoked action's SetAmmoCount(old+1) on the
// installed lab magazine. Everything else is getter-only. No detach/replace/spawn, no
// donor, no inventory, no chamber/pump, no R/fire/Shift, no global modded hook, no input
// listener. Synthetic +1 only: not a gameplay reload, not authority/replication proof.
//
// Revision after owner review (Issue #34 comment 5972157499) and the merge task
// (comment 5972248499):
//   * probe lookup on the weapon ENTITY + owner cross-check (was `not-lab-weapon` x36);
//   * bounded baseline gate retries until the installed magazine exists; strict read-back
//     (baselineDone only if got==start && sameMagazine && non-null same owner); failed
//     read-back -> `baseline-readback-mismatch` and +1 blocked, no retry;
//   * one-shot latch BEFORE SetAmmoCount; post-write verdict; `null==null` never counts
//     as sameOwner; muzzle supply and chamber flag reported separately.
// ============================================================================

// ----------------------------------------------------------------------------
// Lab-only WeaponAnimationComponent subclass (replaces the inherited instance by its
// own instance GUID {60B4EA76EB15F6E0}; the production graph/ASI are inherited unchanged).
// ----------------------------------------------------------------------------
class ARMST_T4B_WeaponAnimationComponentClass : WeaponAnimationComponentClass
{
}

class ARMST_T4B_WeaponAnimationComponent : WeaponAnimationComponent
{
	protected AnimationEventID m_evtBlendIn = -1;
	protected AnimationEventID m_evtBlendOut = -1;
	protected AnimationEventID m_evtEnableFire = -1;
	protected AnimationEventID m_evtRackBolt = -1;
	protected AnimationEventID m_evtSpawn = -1;
	protected AnimationEventID m_evtAttach = -1;
	protected AnimationEventID m_evtRelease = -1;
	protected AnimationEventID m_evtDetach = -1;
	protected AnimationEventID m_evtDespawn = -1;
	protected int m_iEvt = 0;
	protected int m_iCmd = 0;
	protected const int T4B_EVT_CAP = 400;

	ARMST_T4B_WeaponProbe T4BProbe()
	{
		IEntity o = GetOwner();
		if (!o)
			return null;
		return ARMST_T4B_WeaponProbe.Cast(o.FindComponent(ARMST_T4B_WeaponProbe));
	}

	// Returns the significant event name, or "" for events we deliberately do not log.
	string T4BEventName(AnimationEventID id)
	{
		if (m_evtBlendIn < 0)
			m_evtBlendIn = GameAnimationUtils.RegisterAnimationEvent("BlendIn");
		if (m_evtBlendOut < 0)
			m_evtBlendOut = GameAnimationUtils.RegisterAnimationEvent("BlendOut");
		if (m_evtEnableFire < 0)
			m_evtEnableFire = GameAnimationUtils.RegisterAnimationEvent("Weapon_EnableFire");
		if (m_evtRackBolt < 0)
			m_evtRackBolt = GameAnimationUtils.RegisterAnimationEvent("Weapon_Rack_Bolt");
		if (m_evtSpawn < 0)
			m_evtSpawn = GameAnimationUtils.RegisterAnimationEvent("Weapon_SpawnMagazine");
		if (m_evtAttach < 0)
			m_evtAttach = GameAnimationUtils.RegisterAnimationEvent("Weapon_AttachMagazine");
		if (m_evtRelease < 0)
			m_evtRelease = GameAnimationUtils.RegisterAnimationEvent("Weapon_MagRelease");
		if (m_evtDetach < 0)
			m_evtDetach = GameAnimationUtils.RegisterAnimationEvent("Weapon_DetachMagazine");
		if (m_evtDespawn < 0)
			m_evtDespawn = GameAnimationUtils.RegisterAnimationEvent("Weapon_DespawnMagazine");

		if (id == m_evtBlendIn) return "BlendIn";
		if (id == m_evtBlendOut) return "BlendOut";
		if (id == m_evtEnableFire) return "Weapon_EnableFire";
		if (id == m_evtRackBolt) return "Weapon_Rack_Bolt";
		if (id == m_evtSpawn) return "Weapon_SpawnMagazine";
		if (id == m_evtAttach) return "Weapon_AttachMagazine";
		if (id == m_evtRelease) return "Weapon_MagRelease";
		if (id == m_evtDetach) return "Weapon_DetachMagazine";
		if (id == m_evtDespawn) return "Weapon_DespawnMagazine";
		return "";
	}

	override void OnAnimationEvent(AnimationEventID animEventType, AnimationEventID animUserString, int intParam, float timeFromStart, float timeToEnd)
	{
		m_iEvt++;
		bool allow = (m_iEvt <= T4B_EVT_CAP);
		string name = T4BEventName(animEventType);
		bool significant = (name != "");
		ARMST_T4B_WeaponProbe probe = T4BProbe();

		if (allow && significant && probe)
			probe.T4BLog("EVT", "pre-super", name);

		super.OnAnimationEvent(animEventType, animUserString, intParam, timeFromStart, timeToEnd);

		if (allow && significant && probe)
		{
			probe.T4BLog("EVT", "post-super", name);
			if (animEventType == m_evtBlendOut)
				probe.T4BScheduleFinal();
		}
	}

	override void OnCharacterCommand(int commandID, int intValue, float floatValue)
	{
		super.OnCharacterCommand(commandID, intValue, floatValue);

		if (m_iCmd >= T4B_EVT_CAP)
			return;
		m_iCmd++;
		ARMST_T4B_WeaponProbe probe = T4BProbe();
		if (probe)
			probe.T4BLogCmd(commandID, intValue, floatValue);
	}
}

// ----------------------------------------------------------------------------
// Snapshot hub + installed-magazine baseline probe (lab weapon entity).
// ----------------------------------------------------------------------------
class ARMST_T4B_WeaponProbeClass : ScriptComponentClass
{
}

[BaseContainerProps()]
class ARMST_T4B_WeaponProbe : ScriptComponent
{
	protected bool m_bInitDone = false;
	protected bool m_bBaselineDone = false;
	protected bool m_bBaselineFailed = false;
	protected int m_iRetries = 0;
	protected int m_iSeq = 0;
	protected IEntity m_t4bWpnEntity;
	protected int m_t4bWpnTag = 0;
	protected int m_t4bNextWpnTag = 0;
	protected IEntity m_t4bMagEntity;
	protected int m_t4bMagTag = 0;
	protected int m_t4bNextMagTag = 0;

	// Baseline ammo for the ALREADY INSTALLED lab magazine (0..max). Default 0 so the
	// +1 test starts from 0/10; set to max to test the full-rejection case.
	[Attribute("0", UIWidgets.Slider, "T4b installed magazine baseline ammo", "0 15 1")]
	int m_iT4BStartAmmo;

	bool IsBaselineDone()
	{
		return m_bBaselineDone;
	}

	override void OnPostInit(IEntity owner)
	{
		super.OnPostInit(owner);
		if (m_bInitDone)
			return;
		m_bInitDone = true;
		T4BLog("INSTALLED", "init", "attach");
		T4BTryBaseline();
	}

	// Bounded gate: retry until the weapon AND its installed magazine both exist.
	void T4BTryBaseline()
	{
		if (m_bBaselineDone || m_bBaselineFailed)
			return;

		BaseWeaponComponent wpn = T4BWeapon();
		BaseMagazineComponent mag = null;
		if (wpn)
			mag = wpn.GetCurrentMagazine();

		if (!wpn || !mag)
		{
			m_iRetries++;
			if (m_iRetries <= 4)
				GetGame().GetCallqueue().CallLater(T4BTryBaseline, 250, false);
			else
				T4BLog("INSTALLED", "reject", "baseline-not-ready");
			return;
		}

		IEntity magEntBefore = mag.GetOwner();
		int start = m_iT4BStartAmmo;
		if (start < 0)
			start = 0;
		int mx = mag.GetMaxAmmoCount();
		if (start > mx)
			start = mx;

		mag.SetAmmoCount(start);

		// Strict read-back; baselineDone ONLY on full match.
		BaseWeaponComponent wpn2 = T4BWeapon();
		BaseMagazineComponent mag2 = null;
		IEntity magEntAfter = null;
		int got = -1;
		if (wpn2)
		{
			mag2 = wpn2.GetCurrentMagazine();
			if (mag2)
			{
				magEntAfter = mag2.GetOwner();
				got = mag2.GetAmmoCount();
			}
		}
		bool sameMagazine = (mag2 == mag);
		bool sameOwner = (magEntBefore != null && magEntAfter == magEntBefore);
		bool ok = (got == start) && sameMagazine && sameOwner;

		if (!ok)
		{
			m_bBaselineFailed = true;
			T4BLog("INSTALLED", "reject", "baseline-readback-mismatch");
			return;
		}

		m_bBaselineDone = true;
		T4BLog("INSTALLED", "baseline", "init");
	}

	BaseWeaponComponent T4BWeapon()
	{
		IEntity o = GetOwner();
		if (!o)
			return null;
		return BaseWeaponComponent.Cast(o.FindComponent(WeaponComponent));
	}

	string T4BB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	// Builds the shared state string and advances the identity tags.
	string T4BState()
	{
		BaseWeaponComponent wpn = T4BWeapon();
		string wep = "-";
		int wpnTag = -1;
		int ammo = -1;
		int mx = -1;
		string magRes = "-";
		int mzSupply = -1;
		int mzMax = -1;
		int barrel = -1;
		int chambered = -1;
		bool chNeed = false;
		bool chPoss = false;

		if (wpn)
		{
			IEntity we = wpn.GetOwner();
			if (we)
			{
				if (we != m_t4bWpnEntity)
				{
					m_t4bWpnEntity = we;
					m_t4bNextWpnTag++;
					m_t4bWpnTag = m_t4bNextWpnTag;
				}
				wpnTag = m_t4bWpnTag;
				if (we.GetPrefabData())
					wep = we.GetPrefabData().GetPrefabName();
			}

			BaseMagazineComponent mag = wpn.GetCurrentMagazine();
			IEntity me = null;
			if (mag)
				me = mag.GetOwner();
			if (me != m_t4bMagEntity)
			{
				m_t4bMagEntity = me;
				m_t4bNextMagTag++;
				m_t4bMagTag = m_t4bNextMagTag;
			}
			if (mag)
			{
				ammo = mag.GetAmmoCount();
				mx = mag.GetMaxAmmoCount();
			}
			if (me && me.GetPrefabData())
				magRes = me.GetPrefabData().GetPrefabName();

			BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
			if (muzzle)
			{
				mzSupply = muzzle.GetAmmoCount();
				mzMax = muzzle.GetMaxAmmoCount();
				barrel = muzzle.GetCurrentBarrelIndex();
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
				else
					chambered = 0;
			}
			chNeed = wpn.IsChamberingNecessary();
			chPoss = wpn.IsChamberingPossible();
		}

		string s = "wpnTag=W" + wpnTag.ToString();
		s = s + " wep=" + wep;
		s = s + " magTag=M" + m_t4bMagTag.ToString();
		s = s + " mag=" + magRes;
		s = s + " ammo=" + ammo.ToString() + "/" + mx.ToString();
		s = s + " muzzleSupply=" + mzSupply.ToString() + "/" + mzMax.ToString();
		s = s + " barrel=" + barrel.ToString();
		s = s + " chambered=" + chambered.ToString();
		s = s + " chNeed=" + T4BB(chNeed);
		s = s + " chPoss=" + T4BB(chPoss);
		s = s + " baselineDone=" + T4BB(m_bBaselineDone);
		return s;
	}

	void T4BLog(string channel, string phase, string evName)
	{
		m_iSeq++;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-" + channel + "] #" + m_iSeq.ToString()
			+ " phase=" + phase
			+ " ev=" + evName
			+ " srv=" + srv.ToString()
			+ " " + T4BState(), LogLevel.NORMAL);
	}

	void T4BLogCmd(int commandID, int intValue, float floatValue)
	{
		m_iSeq++;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-CMD] #" + m_iSeq.ToString()
			+ " phase=command"
			+ " commandID=" + commandID.ToString()
			+ " intValue=" + intValue.ToString()
			+ " floatValue=" + floatValue.ToString()
			+ " srv=" + srv.ToString()
			+ " " + T4BState(), LogLevel.NORMAL);
	}

	void T4BScheduleFinal()
	{
		GetGame().GetCallqueue().CallLater(T4BFinal, 250, false);
	}

	void T4BFinal()
	{
		T4BLog("INSTALLED", "final-250ms", "post-blendout");
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
		Print("[ARMST_T4B-INSTALLED] #0 phase=action-init ev=useraction reason=register srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		outName = "T4b: +1 into installed mag";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Lab API test: SetAmmoCount(old+1) on the installed magazine; rejects when full, already used or baseline not ready.";
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

		BaseWeaponComponent wpn = T4BActionWeapon();
		if (!wpn)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=no-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// The probe is a SIBLING component on the weapon ENTITY (not on the component).
		IEntity weaponEnt = wpn.GetOwner();
		if (!weaponEnt)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=no-weapon-entity srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (m_t4bWeaponEntity == null || weaponEnt != m_t4bWeaponEntity)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=wrong-weapon-owner srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		ARMST_T4B_WeaponProbe probe = ARMST_T4B_WeaponProbe.Cast(weaponEnt.FindComponent(ARMST_T4B_WeaponProbe));
		if (!probe)
		{
			Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
				+ " phase=reject ev=not-lab-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (!probe.IsBaselineDone())
		{
			probe.T4BLog("INSTALLED", "reject", "baseline-not-ready");
			return;
		}

		BaseMagazineComponent magPre = wpn.GetCurrentMagazine();
		if (!magPre)
		{
			probe.T4BLog("INSTALLED", "reject", "no-installed-magazine");
			return;
		}

		IEntity magEntPre = magPre.GetOwner();
		int a = magPre.GetAmmoCount();
		int mx = magPre.GetMaxAmmoCount();
		BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
		int mzSupplyPre = -1;
		int barrelPre = -1;
		bool chamberedPre = false;
		if (muzzle)
		{
			mzSupplyPre = muzzle.GetAmmoCount();
			barrelPre = muzzle.GetCurrentBarrelIndex();
			chamberedPre = muzzle.IsCurrentBarrelChambered();
		}

		probe.T4BLog("INSTALLED", "pre", "invoked");

		if (m_bUsed)
		{
			probe.T4BLog("INSTALLED", "reject", "already-used");
			return;
		}
		if (a >= mx)
		{
			probe.T4BLog("INSTALLED", "reject", "full");
			return;
		}
		if (a < 0)
		{
			probe.T4BLog("INSTALLED", "reject", "bad-ammo");
			return;
		}

		int want = a + 1;

		// Strict one-shot: latch BEFORE the write.
		m_bUsed = true;
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
		BaseMuzzleComponent muzzle2 = wpn.GetCurrentMuzzle();
		int mzSupplyPost = -1;
		int barrelPost = -1;
		bool chamberedPost = false;
		if (muzzle2)
		{
			mzSupplyPost = muzzle2.GetAmmoCount();
			barrelPost = muzzle2.GetCurrentBarrelIndex();
			chamberedPost = muzzle2.IsCurrentBarrelChambered();
		}

		bool sameMagazine = (magPost == magPre);
		bool sameOwner = (magEntPre != null && magEntPost == magEntPre);
		bool gotOk = (a2 == want);
		bool chamberUnchanged = (chamberedPre == chamberedPost);
		bool muzzleSupplySame = (mzSupplyPre == mzSupplyPost);
		bool verdictOk = gotOk && sameMagazine && sameOwner && chamberUnchanged;

		string verdict = "mismatch";
		if (verdictOk)
			verdict = "ok";

		probe.T4BLog("INSTALLED", "post", "write");
		Print("[ARMST_T4B-INSTALLED] #" + m_iSeq.ToString()
			+ " verdict=" + verdict
			+ " want=" + want.ToString()
			+ " got=" + a2.ToString()
			+ " sameMagazine=" + T4BB(sameMagazine)
			+ " sameOwner=" + T4BB(sameOwner)
			+ " gotOk=" + T4BB(gotOk)
			+ " chamberedBefore=" + T4BB(chamberedPre)
			+ " chamberedAfter=" + T4BB(chamberedPost)
			+ " chamberUnchanged=" + T4BB(chamberUnchanged)
			+ " muzzleSupplyBefore=" + mzSupplyPre.ToString()
			+ " muzzleSupplyAfter=" + mzSupplyPost.ToString()
			+ " muzzleSupplySame=" + T4BB(muzzleSupplySame)
			+ " barrelBefore=" + barrelPre.ToString()
			+ " barrelAfter=" + barrelPost.ToString()
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
}
