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
//   * T3-style snapshots (identity tags, ammo, muzzle supply, barrel, chamber flag)
//                                                              -> [ARMST_T4B-INSTALLED]
// NOT ported on purpose: the global `modded SCR_CharacterControllerComponent` (player
// marker route + 1 Hz tick) and the player-authored marker route. The lab-only
// WeaponAnimationComponent subclass replaces the EXISTING inherited {60B4EA76EB15F6E0}
// instance (no second component added).
//
// The only write is the explicit owner-invoked action's SetAmmoCount(old+1) on the
// installed lab magazine. Everything else is getter-only. No detach/replace/spawn, no
// donor, no inventory, no chamber/pump, no R/fire/Shift, no global modded hook, no input
// listener. Synthetic +1 only: not a gameplay reload, not authority/replication proof.
//
// Revision after independent review (Issue #34 comment 5972318337):
//   1. DELAYED PERSISTENCE SAMPLES after the +1: ~250 ms and ~1 s relative to THIS setter
//      invocation, comparing the same intended magazine component + owning entity and the
//      expected value; distinguishes still-installed / replaced / missing. No re-issue, no
//      polling. (The separate post-BlendOut sampler is retained for native animation tests.)
//   2. Immediate result no longer claimed as a real round: `setter_readback_ok` /
//      `immediate_consistency` are logged, persistence is logged separately, and
//      `gameplay_effect=UNVERIFIED`. A single shared probe operation id (`op=`) links
//      pre / post / delayed / owner observation.
//   3. Event cap counts only SIGNIFICANT logged events, so unrelated callbacks can no
//      longer silence later Weapon_*Magazine / rack / BlendOut events. `super` always runs.
//
// Equip observation: NOT implemented here. `BaseItemAnimationComponent.SyncWithCharacter` /
// `RemoveSyncReference` are `proto external` (engine-implemented) and CANNOT be script
// overridden - declaring them caused `Multiple declaration of function` (owner compile log at
// 449e52c). A valid equip/pickup observable is under separate read-only API research.
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
	protected int m_iSigEvt = 0;
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
		string name = T4BEventName(animEventType);
		bool significant = (name != "");
		bool allow = false;
		if (significant && m_iSigEvt < T4B_EVT_CAP)
		{
			m_iSigEvt++;
			allow = true;
		}

		ARMST_T4B_WeaponProbe probe = T4BProbe();
		if (allow && probe)
			probe.T4BLog("EVT", "pre-super", name);

		super.OnAnimationEvent(animEventType, animUserString, intParam, timeFromStart, timeToEnd);

		if (allow && probe)
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
// Snapshot hub + installed-magazine baseline probe + delayed persistence sampler.
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
	protected int m_iOpId = 0;
	protected IEntity m_t4bWpnEntity;
	protected int m_t4bWpnTag = 0;
	protected int m_t4bNextWpnTag = 0;
	protected IEntity m_t4bMagEntity;
	protected int m_t4bMagTag = 0;
	protected int m_t4bNextMagTag = 0;

	// Delayed persistence sample state (captured at the +1 invocation).
	protected int m_delayedOp = 0;
	protected BaseMagazineComponent m_delayedMag;
	protected IEntity m_delayedMagEnt;
	protected int m_delayedWant = -1;

	// Baseline ammo for the ALREADY INSTALLED lab magazine (0..max). Default 0 so the
	// +1 test starts from 0/10; set to max to test the full-rejection case.
	[Attribute("0", UIWidgets.Slider, "T4b installed magazine baseline ammo", "0 15 1")]
	int m_iT4BStartAmmo;

	bool IsBaselineDone()
	{
		return m_bBaselineDone;
	}

	// Shared test/operation id correlating pre / post / delayed samples / owner observation.
	int T4BBeginOp()
	{
		m_iOpId++;
		return m_iOpId;
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

	void T4BLog(string channel, string phase, string evName, int opId = 0)
	{
		m_iSeq++;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-" + channel + "] #" + m_iSeq.ToString()
			+ " op=" + opId.ToString()
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

	// Passive post-BlendOut sampler (native animation tests), retained separately.
	void T4BScheduleFinal()
	{
		GetGame().GetCallqueue().CallLater(T4BFinal, 250, false);
	}

	void T4BFinal()
	{
		T4BLog("INSTALLED", "final-blendout-250ms", "post-blendout");
	}

	// ---- delayed persistence sampling after the synthetic +1 ------------------
	void T4BSchedulePostWrite(int opId, BaseMagazineComponent mag, IEntity magEnt, int want)
	{
		m_delayedOp = opId;
		m_delayedMag = mag;
		m_delayedMagEnt = magEnt;
		m_delayedWant = want;
		GetGame().GetCallqueue().CallLater(T4BDelayed250, 250, false);
		GetGame().GetCallqueue().CallLater(T4BDelayed1000, 1000, false);
	}

	void T4BDelayed250()
	{
		T4BDelayedSample(250);
	}

	void T4BDelayed1000()
	{
		T4BDelayedSample(1000);
	}

	// Reads the CURRENT installed magazine and compares to the captured intent.
	// Never re-issues SetAmmoCount; never polls.
	void T4BDelayedSample(int ms)
	{
		if (m_delayedOp <= 0)
			return;

		BaseWeaponComponent wpn = T4BWeapon();
		BaseMagazineComponent magNow = null;
		if (wpn)
			magNow = wpn.GetCurrentMagazine();
		IEntity ownerNow = null;
		int ammoNow = -1;
		if (magNow)
		{
			ownerNow = magNow.GetOwner();
			ammoNow = magNow.GetAmmoCount();
		}

		bool stillInstalled = (magNow == m_delayedMag);
		bool sameOwner = (m_delayedMagEnt != null && ownerNow == m_delayedMagEnt);
		bool replaced = (magNow != null && magNow != m_delayedMag);
		bool missing = (magNow == null);
		bool persistAmmo = (ammoNow == m_delayedWant);

		int srv = 0;
		if (Replication.IsServer())
			srv = 1;

		Print("[ARMST_T4B-INSTALLED] op=" + m_delayedOp.ToString()
			+ " phase=delayed+" + ms.ToString() + "ms"
			+ " ev=post-write"
			+ " expected=" + m_delayedWant.ToString()
			+ " got=" + ammoNow.ToString()
			+ " persistAmmo=" + T4BB(persistAmmo)
			+ " stillInstalled=" + T4BB(stillInstalled)
			+ " sameOwner=" + T4BB(sameOwner)
			+ " replaced=" + T4BB(replaced)
			+ " missing=" + T4BB(missing)
			+ " srv=" + srv.ToString()
			+ " " + T4BState(), LogLevel.NORMAL);
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
		Print("[ARMST_T4B-INSTALLED] #0 op=0 phase=action-init ev=useraction reason=register srv=" + srv.ToString(), LogLevel.NORMAL);
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
			Print("[ARMST_T4B-INSTALLED] phase=reject ev=no-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// The probe is a SIBLING component on the weapon ENTITY (not on the component).
		IEntity weaponEnt = wpn.GetOwner();
		if (!weaponEnt)
		{
			Print("[ARMST_T4B-INSTALLED] phase=reject ev=no-weapon-entity srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (m_t4bWeaponEntity == null || weaponEnt != m_t4bWeaponEntity)
		{
			Print("[ARMST_T4B-INSTALLED] phase=reject ev=wrong-weapon-owner srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		ARMST_T4B_WeaponProbe probe = ARMST_T4B_WeaponProbe.Cast(weaponEnt.FindComponent(ARMST_T4B_WeaponProbe));
		if (!probe)
		{
			Print("[ARMST_T4B-INSTALLED] phase=reject ev=not-lab-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
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

		int opId = probe.T4BBeginOp();

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

		probe.T4BLog("INSTALLED", "pre", "invoked", opId);

		if (m_bUsed)
		{
			probe.T4BLog("INSTALLED", "reject", "already-used", opId);
			return;
		}
		if (a >= mx)
		{
			probe.T4BLog("INSTALLED", "reject", "full", opId);
			return;
		}
		if (a < 0)
		{
			probe.T4BLog("INSTALLED", "reject", "bad-ammo", opId);
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

		// Immediate consistency ONLY (not proof of a real round).
		bool setterReadbackOk = gotOk && sameMagazine && sameOwner && chamberUnchanged;
		string imm = "mismatch";
		if (setterReadbackOk)
			imm = "ok";

		probe.T4BLog("INSTALLED", "post", "write", opId);
		Print("[ARMST_T4B-INSTALLED] op=" + opId.ToString()
			+ " phase=post-detail ev=write"
			+ " setter_call=1"
			+ " setter_readback_ok=" + T4BB(setterReadbackOk)
			+ " immediate_consistency=" + imm
			+ " gotOk=" + T4BB(gotOk)
			+ " sameMagazine=" + T4BB(sameMagazine)
			+ " sameOwner=" + T4BB(sameOwner)
			+ " want=" + want.ToString()
			+ " got=" + a2.ToString()
			+ " chamberedBefore=" + T4BB(chamberedPre)
			+ " chamberedAfter=" + T4BB(chamberedPost)
			+ " chamberUnchanged=" + T4BB(chamberUnchanged)
			+ " muzzleSupplyBefore=" + mzSupplyPre.ToString()
			+ " muzzleSupplyAfter=" + mzSupplyPost.ToString()
			+ " muzzleSupplySame=" + T4BB(muzzleSupplySame)
			+ " barrelBefore=" + barrelPre.ToString()
			+ " barrelAfter=" + barrelPost.ToString()
			+ " gameplay_effect=UNVERIFIED"
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		// Passive delayed persistence samples relative to THIS setter invocation.
		probe.T4BSchedulePostWrite(opId, magPre, magEntPre, want);
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
