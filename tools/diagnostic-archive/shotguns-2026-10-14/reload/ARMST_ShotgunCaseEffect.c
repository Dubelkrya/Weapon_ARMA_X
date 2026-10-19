// Cosmetic only: no magazine, chamber or ammunition writes.
class ARMST_ShotgunCaseEffectClass : MuzzleEffectComponentClass
{
}

class ARMST_ShotgunCaseEffect : MuzzleEffectComponent
{
	[Attribute("", UIWidgets.Object, "Spent case ejection position")]
	ref PointInfo m_CasePosition;

	[Attribute("-1", UIWidgets.EditBox, "Manual mode index; -1 means all modes are manual")]
	int m_iManualModeIndex;

	[Attribute("0", UIWidgets.CheckBox, "Allow immediate ejection outside the manual mode (SPAS only)")]
	bool m_bAllowImmediateEjection = false;

	protected bool m_bSpentCasePending;

	override void OnInit(IEntity owner)
	{
		super.OnInit(owner);
		Print(string.Format("[ARMST-CASE] init owner=%1 point=%2", owner, m_CasePosition));
		if (m_CasePosition)
			m_CasePosition.Init(owner);
	}

	// The empty native ParticleEffect does not deliver OnFired in the tested setup.
	// Receive the shot from the existing muzzle-flash component instead.
	void NotifyWeaponFired(BaseMuzzleComponent muzzle)
	{
		Print(string.Format("[ARMST-CASE] fired muzzle=%1", muzzle));
		if (!muzzle)
			return;
		// SPAS opts in explicitly. Its semi mode has UIName "Auto" in the prefab.
		// Do not infer pump/semi from array indices: inherited safety shifts them.
		BaseFireMode fireMode = muzzle.GetCurrentFireMode();
		string modeName = "";
		if (fireMode)
			modeName = fireMode.GetUIName();
		bool immediateEjection = m_bAllowImmediateEjection && modeName == "Auto";
		Print(string.Format("[ARMST-CASE] mode=%1 name=%2 allowImmediate=%3 emitNow=%4", muzzle.GetFireModeIndex(), modeName, m_bAllowImmediateEjection, immediateEjection));
		if (!immediateEjection)
		{
			m_bSpentCasePending = true;
			return;
		}
		// SPAS in semi-automatic mode ejects immediately.
		m_bSpentCasePending = false;
		EmitCase();
	}

	void EjectPendingCase()
	{
		Print(string.Format("[ARMST-CASE] rack pending=%1", m_bSpentCasePending));
		if (!m_bSpentCasePending)
			return;
		m_bSpentCasePending = false;
		EmitCase();
	}

	protected void EmitCase()
	{
		if (!m_CasePosition)
		{
			Print("[ARMST-CASE] spawn blocked: no point");
			return;
		}
		ParticleEffectEntitySpawnParams params = new ParticleEffectEntitySpawnParams();
		params.TransformMode = ETransformMode.WORLD;
		m_CasePosition.GetWorldTransform(params.Transform);
		params.DeleteWhenStopped = true;
		ParticleEffectEntity effect = ParticleEffectEntity.SpawnParticleEffect("{3E62CF528279BC22}Particles/Weapon/Casing_12ga.ptc", params);
		Print(string.Format("[ARMST-CASE] spawn result=%1 position=%2", effect, params.Transform[3]));
	}
}

modded class SCR_MuzzleEffectComponent
{
	override void OnFired(IEntity effectEntity, BaseMuzzleComponent muzzle, IEntity projectileEntity)
	{
		super.OnFired(effectEntity, muzzle, projectileEntity);
		if (!muzzle)
			return;
		IEntity weapon = muzzle.GetOwner();
		if (!weapon)
			return;
		ARMST_ShotgunCaseEffect caseEffect = ARMST_ShotgunCaseEffect.Cast(weapon.FindComponent(ARMST_ShotgunCaseEffect));
		if (caseEffect)
			caseEffect.NotifyWeaponFired(muzzle);
	}
}
