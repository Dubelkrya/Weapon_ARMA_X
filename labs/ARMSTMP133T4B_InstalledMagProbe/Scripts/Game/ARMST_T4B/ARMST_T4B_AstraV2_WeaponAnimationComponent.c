// Isolated animation-only prototype. No input hooks, subscriptions or ammo writes.
[ComponentEditorProps(category: "ARMST/Astra", description: "Shell animation diagnostic only")]
class ARMST_T4B_AstraV2_WeaponAnimationComponentClass : ARMST_T4B_WeaponAnimationComponentClass
{
}

class ARMST_T4B_AstraV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComponent
{
	protected static int s_iNextInstance;
	protected int m_iInstance;
	protected int m_iSequence;
	protected int m_iCycle;
	protected int m_iStage; // 0 idle, 1 start, 2 grab, 3 insert, 4 check, 5 end
	protected bool m_bCandidate;
	protected IEntity m_Magazine;
	protected int m_iMagazineTag;

	void ARMST_T4B_AstraV2_WeaponAnimationComponent()
	{
		s_iNextInstance++;
		m_iInstance = s_iNextInstance;
		Print("[ARMST-T4B-ASTRA] component_constructed instance=" + m_iInstance.ToString(), LogLevel.NORMAL);
	}

	override void OnAnimationEvent(AnimationEventID animEventType, AnimationEventID animUserString, int intParam, float timeFromStart, float timeToEnd)
	{
		super.OnAnimationEvent(animEventType, animUserString, intParam, timeFromStart, timeToEnd);
		string name = GameAnimationUtils.GetEventString(animEventType);
		if (!name.StartsWith("ASTRA_Shell"))
			return;

		// Both suffixes are logged on THIS receiver. A _P name does not prove
		// delivery to a character callback. Only _W may arm a candidate.
		string result = "observed";
		if (name == "ASTRA_Shell_StartReload_W" && m_iStage == 0)
			m_iStage = 1;
		if (name == "ASTRA_Shell_GrabShell_W" && (m_iStage == 1 || m_iStage == 4))
		{
			m_iCycle++;
			m_bCandidate = false;
			m_iStage = 2;
		}
		if (name == "ASTRA_Shell_InsertShell_W" && m_iStage == 2)
			m_iStage = 3;
		if (name == "ASTRA_ShellInsertCommit_W")
		{
			result = "rejected_out_of_order_or_duplicate";
			if (m_iStage == 3 && !m_bCandidate)
			{
				m_bCandidate = true;
				result = "diagnostic_candidate_no_transfer";
			}
		}
		if (name == "ASTRA_Shell_CheckContinue_W" && m_iStage == 3)
			m_iStage = 4;
		if (name == "ASTRA_Shell_EndReload_W")
		{
			if (m_iStage == 1 || m_iStage == 2)
			{
				result = "ended_before_insert_no_candidate";
				m_iStage = 5;
			}
			else if (m_iStage == 4)
				m_iStage = 5;
			else
				result = "rejected_end_out_of_order";
		}
		// ReturnReady is a clip marker, not proof of the enclosing graph's Idle.
		if (name == "ASTRA_Shell_ReturnReady_W" && m_iStage == 5)
			m_iStage = 0;

		m_iSequence++;
		string line = "[ARMST-T4B-ASTRA] receiver=weapon seq=" + m_iSequence.ToString();
		line += " instance=" + m_iInstance.ToString();
		line += " cycle=" + m_iCycle.ToString() + " stage=" + m_iStage.ToString();
		line += " event=" + name + " result=" + result;
		line += " from=" + timeFromStart.ToString() + " to=" + timeToEnd.ToString();
		Print(line, LogLevel.NORMAL);
		AstraSnapshot();
	}

	protected void AstraSnapshot()
	{
		IEntity owner = GetOwner();
		if (!owner)
			return;
		BaseWeaponComponent weapon = BaseWeaponComponent.Cast(owner.FindComponent(WeaponComponent));
		if (!weapon)
			weapon = BaseWeaponComponent.Cast(owner.FindComponent(BaseWeaponComponent));
		if (!weapon)
		{
			Print("[ARMST-T4B-ASTRA] snapshot=weapon_unresolved", LogLevel.WARNING);
			return;
		}
		BaseMagazineComponent magazine = weapon.GetCurrentMagazine();
		IEntity entity;
		int ammo = -1;
		int capacity = -1;
		if (magazine)
		{
			entity = magazine.GetOwner();
			ammo = magazine.GetAmmoCount();
			capacity = magazine.GetMaxAmmoCount();
		}
		if (entity != m_Magazine)
		{
			m_Magazine = entity;
			m_iMagazineTag++;
		}
		string line = "[ARMST-T4B-ASTRA] snapshot seq=" + m_iSequence.ToString();
		line += " instance=" + m_iInstance.ToString();
		bool magPresent = entity != null;
		line += " magPresent=" + magPresent.ToString();
		line += " magTag=" + m_iMagazineTag.ToString();
		line += " ammo=" + ammo.ToString() + "/" + capacity.ToString();
		line += " chamberNeeded=" + weapon.IsChamberingNecessary().ToString();
		line += " chamberPossible=" + weapon.IsChamberingPossible().ToString();
		BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
		if (muzzle)
		{
			line += " chambered=" + muzzle.IsCurrentBarrelChambered().ToString();
			line += " barrel=" + muzzle.GetCurrentBarrelIndex().ToString();
		}
		Print(line, LogLevel.NORMAL);
	}
}
