// ============================================================================
// ARMST MP-133 T4a - disposable SetAmmoCount semantics probe (DIAGNOSTIC ONLY)
// ----------------------------------------------------------------------------
// Isolated lab. The disposable, non-production test magazine prefab
// (Prefabs/Test/ARMST_T4A_TestMagazine.et) carries:
//   * ARMST_T4A_SetterProbe        - sets a baseline ammo on ITS OWN magazine on init;
//   * ActionsManagerComponent      - with one standard, range-limited, per-entity
//                                    context action:
//   * ARMST_T4A_AddRoundUserAction - shown as "T4a: add 1 test round"; on activation it
//                                    performs ONE guarded SetAmmoCount(current+1) on the
//                                    magazine it belongs to.
//
// The action is a ScriptedUserAction child of the specific magazine entity, so the
// standard interaction menu targets ONLY the magazine the player is interacting with.
// No global input listener, no keybinding, no cross-instance effect.
//
// Guards (no write on reject): missing magazine, already used, or full. One write per
// action instance. NO transfer, NO donor, NO player inventory, NO weapon/chamber
// mutation, NO production/Core edits, NO global modded hook, NO auto-trigger.
// Installed-SDK API only: BaseMagazineComponent.Get/SetAmmoCount()/GetMaxAmmoCount()/
// GetOwner(); ScriptedUserAction.P/CanBeShownScript/CanBePerformedScript/
// GetActionNameScript/Init(owner, manager).
//
// This proves whether SetAmmoCount is a usable write primitive on a disposable entity;
// it does NOT validate an installed magazine or engine replication.
// ============================================================================

class ARMST_T4A_SetterProbeClass : ScriptComponentClass
{
}

[BaseContainerProps()]
class ARMST_T4A_SetterProbe : ScriptComponent
{
	protected bool m_bInitDone = false;
	protected int m_t4aTag = 0;

	// Owner-controlled baseline for the disposable test magazine (0..max). Applied once
	// on init so the full-rejection case can be tested (set to max) as well as the +1 case.
	[Attribute("0", UIWidgets.Slider, "T4a disposable initial ammo", "0 15 1")]
	int m_iT4AStartAmmo;

	override void OnPostInit(IEntity owner)
	{
		super.OnPostInit(owner);
		if (m_bInitDone)
			return;
		m_bInitDone = true;
		if (m_t4aTag == 0)
			m_t4aTag = 1;

		int srv = 0;
		if (Replication.IsServer())
			srv = 1;

		Print("[ARMST_T4A-SETTER] #0 phase=init ev=component reason=attach"
			+ " " + T4AProbeState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		BaseMagazineComponent mag = T4AProbeMag();
		if (!mag)
			return;

		int start = m_iT4AStartAmmo;
		if (start < 0)
			start = 0;
		int mx = mag.GetMaxAmmoCount();
		if (start > mx)
			start = mx;
		mag.SetAmmoCount(start);
		Print("[ARMST_T4A-SETTER] #0 phase=baseline ev=component reason=init start=" + start.ToString()
			+ " " + T4AProbeState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	BaseMagazineComponent T4AProbeMag()
	{
		IEntity o = GetOwner();
		if (!o)
			return null;
		BaseMagazineComponent m = BaseMagazineComponent.Cast(o.FindComponent(MagazineComponent));
		if (!m)
			m = BaseMagazineComponent.Cast(o.FindComponent(BaseMagazineComponent));
		return m;
	}

	string T4AProbeState()
	{
		BaseMagazineComponent mag = T4AProbeMag();
		string magRes = "-";
		int a = -1;
		int mx = -1;
		if (mag)
		{
			a = mag.GetAmmoCount();
			mx = mag.GetMaxAmmoCount();
			IEntity me = mag.GetOwner();
			if (me && me.GetPrefabData())
				magRes = me.GetPrefabData().GetPrefabName();
		}
		string s = "entTag=E" + m_t4aTag.ToString();
		s = s + " mag=" + magRes;
		s = s + " ammo=" + a.ToString() + "/" + mx.ToString();
		return s;
	}
}

// ----------------------------------------------------------------------------
// Standard context interaction: shows in the player's interaction menu when near /
// looking at the disposable test magazine; targets ONLY that entity's magazine.
// ----------------------------------------------------------------------------
class ARMST_T4A_AddRoundUserAction : ScriptedUserAction
{
	protected bool m_bUsed = false;
	protected int m_iSeq = 0;
	protected IEntity m_t4aEntity;
	protected int m_t4aTag = 0;

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		m_t4aEntity = pOwnerEntity;
		if (m_t4aTag == 0)
			m_t4aTag = 1;

		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4A-SETTER] #0 phase=action-init ev=useraction reason=register"
			+ " " + T4AActionState()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		outName = "T4a: add 1 test round";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Disposable API test: SetAmmoCount(+1); rejects when full or already used.";
		return true;
	}

	// Always shown and always "performable" so the guards run AND log the reject reason
	// (otherwise a disabled action would not be invocable and the reject would be silent).
	override bool CanBeShownScript(IEntity user)
	{
		return true;
	}

	override bool CanBePerformedScript(IEntity user)
	{
		return true;
	}

	// Server-authoritative, broadcast (project-proven ScriptedUserAction pattern).
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

		BaseMagazineComponent mag = T4AActionMag();
		if (!mag)
		{
			Print("[ARMST_T4A-SETTER] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=no-magazine srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		int a = mag.GetAmmoCount();
		int mx = mag.GetMaxAmmoCount();
		Print("[ARMST_T4A-SETTER] #" + m_iSeq.ToString()
			+ " phase=pre ev=useraction reason=invoked"
			+ " " + T4AActionState()
			+ " used=" + T4AB(m_bUsed)
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		if (m_bUsed)
		{
			Print("[ARMST_T4A-SETTER] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=already-used " + T4AActionState(), LogLevel.NORMAL);
			return;
		}

		if (a >= mx)
		{
			Print("[ARMST_T4A-SETTER] #" + m_iSeq.ToString()
				+ " phase=reject ev=useraction reason=full " + T4AActionState(), LogLevel.NORMAL);
			return;
		}

		int want = a + 1;
		mag.SetAmmoCount(want);
		int a2 = mag.GetAmmoCount();
		bool sameEntity = (mag.GetOwner() == m_t4aEntity);
		m_bUsed = true;

		Print("[ARMST_T4A-SETTER] #" + m_iSeq.ToString()
			+ " phase=post ev=useraction reason=write want=" + want.ToString()
			+ " " + T4AActionState()
			+ " sameIdentity=" + T4AB(sameEntity)
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	string T4AB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	BaseMagazineComponent T4AActionMag()
	{
		IEntity o = GetOwner();
		if (!o)
			return null;
		BaseMagazineComponent m = BaseMagazineComponent.Cast(o.FindComponent(MagazineComponent));
		if (!m)
			m = BaseMagazineComponent.Cast(o.FindComponent(BaseMagazineComponent));
		return m;
	}

	string T4AActionState()
	{
		BaseMagazineComponent mag = T4AActionMag();
		string magRes = "-";
		int a = -1;
		int mx = -1;
		if (mag)
		{
			a = mag.GetAmmoCount();
			mx = mag.GetMaxAmmoCount();
			IEntity me = mag.GetOwner();
			if (me && me.GetPrefabData())
				magRes = me.GetPrefabData().GetPrefabName();
		}
		string s = "entTag=E" + m_t4aTag.ToString();
		s = s + " mag=" + magRes;
		s = s + " ammo=" + a.ToString() + "/" + mx.ToString();
		return s;
	}
}
