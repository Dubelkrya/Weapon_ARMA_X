// ============================================================================
// ARMST MP-133 T4b - Task #1 Phase 2C - P->W variable-propagation PROBE.
//
// Purpose: answer ONE question - does setting ASTRA_ShellRequest on the
// invoking character's CharacterAnimationComponent reach THIS T4b injected
// weapon graph (IdleReloadSTM -> ShellReloadSTM)?
//
// Scope/limits (diagnostic only, per Issue #34 #5983798795):
//   * Default OFF: does nothing unless the owner explicitly invokes the action.
//   * Sets ONLY a graph bool on the character animation component; toggles
//     request on/off so the owner can observe then cleanly release.
//   * Never issues the native reload command or the engine reload API.
//   * Never touches ammo, magazine, chamber, donor, inventory or physical tube.
//   * Fail-closed on missing character / animation component / invalid handle.
//   * Distinct from the existing AddRound (+1), B1 and B2 actions; none of them
//     are called or modified.
//
// API (installed SDK docs, ArmaReforgerScriptAPIPublic):
//   CharacterAnimationComponent (BaseAnimPhysComponent):
//     TAnimGraphVariable BindVariableBool(string pVariableName)
//     void SetSharedVariableBool(TAnimGraphVariable varIdx, bool value, bool varHasOtherUsers)
//   ChimeraCharacter.GetAnimationComponent() -> CharacterAnimationComponent
//   SetSharedVariableBool is the character-scope method documented for a
//   variable also consumed by another (injected) animation user - hence 'true'.
// ============================================================================
class ARMST_T4B_AstraRequestProbeAction : ScriptedUserAction
{
	protected bool m_bRequested;

	override bool GetActionNameScript(out string outName)
	{
		outName = "ASTRA PROBE: ShellRequest ON/OFF";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Diagnostic only: toggles ASTRA_ShellRequest on the character animation component. No ammo/magazine/physical change.";
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
		ChimeraCharacter character = ChimeraCharacter.Cast(pUserEntity);
		if (!character)
		{
			Print("[ARMST-T4B-ASTRA-PROBE] phase=reject ev=no-character", LogLevel.NORMAL);
			return;
		}

		CharacterAnimationComponent anim = character.GetAnimationComponent();
		if (!anim)
		{
			Print("[ARMST-T4B-ASTRA-PROBE] phase=reject ev=no-character-anim-component", LogLevel.NORMAL);
			return;
		}

		TAnimGraphVariable v = anim.BindVariableBool("ASTRA_ShellRequest");
		if (v < 0)
		{
			Print("[ARMST-T4B-ASTRA-PROBE] phase=reject ev=bind-unavailable name=ASTRA_ShellRequest", LogLevel.NORMAL);
			return;
		}

		m_bRequested = !m_bRequested;
		anim.SetSharedVariableBool(v, m_bRequested, true);
		Print("[ARMST-T4B-ASTRA-PROBE] phase=write name=ASTRA_ShellRequest value=" + m_bRequested.ToString() + " idx=" + v.ToString(), LogLevel.NORMAL);
	}
}
