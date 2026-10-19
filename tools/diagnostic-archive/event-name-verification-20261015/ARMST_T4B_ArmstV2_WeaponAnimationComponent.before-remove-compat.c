// Isolated animation-only prototype. No input hooks, subscriptions or ammo writes.
// Compile fix (owner WB log 2026-10-04): the parameterless script constructor on the
// derived component was rejected ("Overloaded function ... not compatible"). Enfusion
// instantiates prefab components engine-side; the BaseItemAnimationComponent family
// (complete inherited-member list, installed 1.8.0.13 API docs) exposes no script
// constructor and no OnInit/OnPostInit, only animation/character callbacks. The former
// constructor is replaced by a lazy once-only init driven by OnAnimationEvent.
//
// Weapon-local observer of the inert reload command via
// BaseItemAnimationComponent.OnCharacterCommand(int,int,float). Observation only.
//
// STAGED ADDITION (source prep only): native mag-event correlation. OnAnimationEvent is
// extended to log ANY `Weapon_*` event with a magazine/muzzle snapshot, so the runtime
// order `cmd5 -> first reload event -> physical mutation -> cmd3` can be measured.
// Passive only: no writers, no Update, no handler, no timers, no graph change.
[ComponentEditorProps(category: "ARMST/Armst", description: "Shell animation diagnostic only")]
class ARMST_T4B_ArmstV2_WeaponAnimationComponentClass : ARMST_T4B_WeaponAnimationComponentClass
{
}

class ARMST_T4B_ArmstV2_WeaponAnimationComponent : ARMST_T4B_WeaponAnimationComponent
{
	protected int m_WAXRawWeaponEvents;
	protected static int s_iNextInstance;
	protected int m_iInstance;
	protected int m_iSequence;
	protected int m_iCycle;
	protected int m_iStage; // 0 idle, 1 start, 2 grab, 3 insert, 4 check, 5 end
	protected bool m_bCandidate;
	protected IEntity m_Magazine;
	protected int m_iMagazineTag;
	// Lazy once-only instance init. A scripted constructor is NOT supported on a
	// component subclass (the engine instantiates prefab components), so the
	// former `component_constructed` ctor is replaced by an engine-driven,
	// event-triggered init that runs exactly once per created instance.
	protected bool m_bInstanceInitLogged;

	// passive native mag-event correlation counter
	protected int m_iMagEvtSeq;

	// O1 PHASE 1C W-local request propagation probe (weapon-local setters only).
	protected bool m_bWPropBound;
	protected int m_iWPropReq = -1;
	protected int m_iWPropElig = -1;
	protected int m_iWPropRep = -1;
	protected int m_iWPropStop = -1;
	protected int m_iWPropSession;
	protected bool m_bWPropActive;
	protected bool m_bWPropSawP;
	protected bool m_bWPropSawW;

	protected void ArmstEnsureInstanceInit()
	{
		if (m_bInstanceInitLogged)
			return;
		m_bInstanceInitLogged = true;
		s_iNextInstance++;
		m_iInstance = s_iNextInstance;
		{ /* Diagnostic output removed. */ }
	}

	// O1 PHASE 1C — bind the CURRENT graph's shell request variables on THIS weapon
	// instance. Source-proven engine API on the AnimationControllerComponent family
	// (EnfusionScriptAPI interfaceBaseAnimationControllerComponent.html):
	//   proto external int  BindBoolVariable(string varName)
	//   proto external void SetBoolVariable(int varId, bool value)
	//   proto external bool GetBoolVariable(int varId)
	protected void T4BWPropBind()
	{
		if (m_bWPropBound)
			return;
		m_bWPropBound = true;
		m_iWPropReq = BindBoolVariable("ARMST_ShellRequest");
		m_iWPropElig = BindBoolVariable("ARMST_ShellEligible");
		m_iWPropRep = BindBoolVariable("ARMST_ShellRepeat");
		m_iWPropStop = BindBoolVariable("ARMST_ShellStop");
		{ /* Diagnostic output removed. */ }
	}

	// Read-only W-host attachment lookup. IDs are rebound per qualified request;
	// nonnegative is provisional only, not proof of P-instance ownership.
	// Immediate reversible diagnostic only. Attachment IDs may be signed hashes;
	// the variable bind, not the sign of the attachment ID, gates access.
	bool T4BPRepeatPulse()
	{
		int attachment = BindAttachment("Weapon");
		int repeat = BindAttBoolVariable(attachment, "ARMST_ShellRepeat");
		{ /* Diagnostic output removed. */ }
		if (repeat == -1)
		{
			{ /* Diagnostic output removed. */ }
			return true;
		}
		bool original = GetAttBoolVariable(attachment, repeat);
		float pulse = 1.0;
		if (original)
			pulse = 0.0;
		SetAttBoolVariable(attachment, repeat, pulse);
		bool observed = GetAttBoolVariable(attachment, repeat);
		float restore = 0.0;
		if (original)
			restore = 1.0;
		SetAttBoolVariable(attachment, repeat, restore);
		bool restored = GetAttBoolVariable(attachment, repeat);
		{ /* Diagnostic output removed. */ }
		{ /* Diagnostic output removed. */ }
		return restored == original;
	}

	protected void T4BPAttachmentReadonly()
	{
		int att = BindAttachment("Weapon");
		{ /* Diagnostic output removed. */ }
		if (att < 0)
			return;

		int req = BindAttBoolVariable(att, "ARMST_ShellRequest");
		int elig = BindAttBoolVariable(att, "ARMST_ShellEligible");
		int rep = BindAttBoolVariable(att, "ARMST_ShellRepeat");
		int stop = BindAttBoolVariable(att, "ARMST_ShellStop");
		{ /* Diagnostic output removed. */ }
		if (req < 0 || elig < 0 || rep < 0 || stop < 0)
		{
			{ /* Diagnostic output removed. */ }
			return;
		}

		bool rbReq = GetAttBoolVariable(att, req);
		bool rbElig = GetAttBoolVariable(att, elig);
		bool rbRep = GetAttBoolVariable(att, rep);
		bool rbStop = GetAttBoolVariable(att, stop);
		{ /* Diagnostic output removed. */ }
	}

	// Animation-only, one-cycle shell request originated on the WEAPON side.
	// No ammo/mag/chamber writes, no native reload command, no P-side setter.
	// Repeat is forced false. Only current graph variables are bound.
	bool T4BWPropRequest()
	{
		T4BPAttachmentReadonly();
		T4BWPropBind();
		// NOTE: the < 0 invalid-sentinel is a bounded assumption (engine bind docs do
		// not publish the sentinel); the readback below is the authoritative signal.
		if (m_iWPropReq < 0 || m_iWPropElig < 0 || m_iWPropRep < 0 || m_iWPropStop < 0)
		{
			m_bWPropActive = false;
			{ /* Diagnostic output removed. */ }
			return false;
		}
		// R2: deterministic manual abort (no timer). A second qualified R while the
		// previous session never produced ReturnReady_W means W-local propagation did
		// NOT run; reset to safe defaults instead of opening a second session.
		if (m_bWPropActive)
		{
			SetBoolVariable(m_iWPropReq, false);
			SetBoolVariable(m_iWPropElig, false);
			bool abortReqRb = GetBoolVariable(m_iWPropReq);
			bool abortEligRb = GetBoolVariable(m_iWPropElig);
			{ /* Diagnostic output removed. */ }
			m_bWPropActive = false;
			return false;
		}
		m_iWPropSession++;
		m_bWPropSawP = false;
		m_bWPropSawW = false;
		SetBoolVariable(m_iWPropElig, true);
		SetBoolVariable(m_iWPropRep, false);
		SetBoolVariable(m_iWPropStop, false);
		SetBoolVariable(m_iWPropReq, true);
		bool reqRb = GetBoolVariable(m_iWPropReq);
		bool eligRb = GetBoolVariable(m_iWPropElig);
		bool repRb = GetBoolVariable(m_iWPropRep);
		bool stopRb = GetBoolVariable(m_iWPropStop);
		m_bWPropActive = reqRb;
		if (!reqRb)
		{
			// A failed / non-observable write must not leave the session marked active.
			SetBoolVariable(m_iWPropReq, false);
			SetBoolVariable(m_iWPropElig, false);
			{ /* Diagnostic output removed. */ }
			return false;
		}
		{ /* Diagnostic output removed. */ }
		return reqRb;
	}

	// Latch cancellation until CheckContinue observes it. A one-frame command
	// can be consumed while the weapon is still in GrabShell or InsertShell.
	void T4BWPropRequestStop()
	{
		T4BWPropBind();
		if (m_iWPropStop < 0)
			return;
		SetBoolVariable(m_iWPropStop, true);
		{ /* Diagnostic output removed. */ }
	}

	// Deterministic reset driven by the existing W ReturnReady marker (no timer).
	protected void T4BWPropReset()
	{
		if (m_iWPropSession <= 0)
			return;
		SetBoolVariable(m_iWPropReq, false);
		SetBoolVariable(m_iWPropElig, false);
		bool reqRb = GetBoolVariable(m_iWPropReq);
		bool eligRb = GetBoolVariable(m_iWPropElig);
		m_bWPropActive = false;
		{ /* Diagnostic output removed. */ }
	}

	// Weapon-local observer: does the handler-emitted inert reload command reach this
	// equipped lab weapon receiver? Route is proven ONLY when BOTH the reload command
	// type (commandID) AND intValue==ARMST_T4B_INERT_RELOAD_CMD match — never on intValue
	// alone. Observation only.
	override void OnCharacterCommand(int commandID, int intValue, float floatValue)
	{
		super.OnCharacterCommand(commandID, intValue, floatValue);
		bool isReloadCommand = (commandID == ARMST_T4B_RELOAD_COMMAND_ID);
		bool isInert = isReloadCommand && (intValue == ARMST_T4B_INERT_RELOAD_CMD);
		{ /* Diagnostic output removed. */ }
	}

	override void OnAnimationEvent(AnimationEventID animEventType, AnimationEventID animUserString, int intParam, float timeFromStart, float timeToEnd)
	{
		ArmstEnsureInstanceInit();
		super.OnAnimationEvent(animEventType, animUserString, intParam, timeFromStart, timeToEnd);
		string name = GameAnimationUtils.GetEventString(animEventType);
		if (m_WAXRawWeaponEvents < 96 && name.Contains("Shell"))
		{
			m_WAXRawWeaponEvents++;
			PrintFormat("[WAX-RAW-EVENT] side=W server=%1 name=%2", Replication.IsServer(), name);
		}
		if (name == "ARMST_CaseEject" || name == "Weapon_Rack_Bolt")
		{
			ARMST_ShotgunCaseEffect caseEffect = ARMST_ShotgunCaseEffect.Cast(GetOwner().FindComponent(ARMST_ShotgunCaseEffect));
			{ /* Diagnostic output removed. */ }
			if (caseEffect)
				caseEffect.EjectPendingCase();
		}
		// Compatibility until compiled clips are re-exported with ARMST event names.
		name.Replace("ASTRA", "ARMST");
		ARMST_ShotgunReloadComponent repeatProbe = ARMST_ShotgunReloadComponent.Cast(GetOwner().FindComponent(ARMST_ShotgunReloadComponent));
		if (repeatProbe && repeatProbe.m_T4BPTransferAction)
			repeatProbe.m_T4BPTransferAction.ReceiveW(name);

		// --- passive native reload mag-event correlation (read-only) ---
		if (name.StartsWith("Weapon_"))
		{
			T4BMagEventSnapshot(name, intParam, timeFromStart, timeToEnd);
			return;
		}

		if (!name.StartsWith("ARMST_Shell"))
			return;

		// --- O1 PHASE 1C WPROP: P/W marker-family classification + W-authored reset ---
		// P files (P_Armst_*.txa) contain only *_P markers; W files only *_W markers
		// (statical classification). Observing both families here is the probe's
		// "both sides executed" evidence; gameplay authority stays W-only.
		if (m_iWPropSession > 0)
		{
			bool familyP = name.EndsWith("_P");
			bool familyW = name.EndsWith("_W");
			if (familyP && !m_bWPropSawP)
			{
				m_bWPropSawP = true;
				{ /* Diagnostic output removed. */ }
			}
			if (familyW && !m_bWPropSawW)
			{
				m_bWPropSawW = true;
				{ /* Diagnostic output removed. */ }
			}
		}
		// R3: PACT reset lifecycle. P ReturnReady is authoritative; W ReturnReady resets
		// only when no P family was observed (W-only / no-P fallback). If P started but
		// never reaches P ReturnReady, PACT stays active so the second-R manual abort
		// remains available. No timer.
		if (name == "ARMST_Shell_ReturnReady_P")
		{
			// The captured server session owns lifecycle cleanup, never the global local player.
		}
		else if (name == "ARMST_Shell_ReturnReady_W")
		{
			if (!m_bWPropSawP)
			{
				// W-only fallback remains diagnostic; it must not reset another actor's controller.
			}

			if (m_iWPropSession > 0)
			{
				{ /* Diagnostic output removed. */ }
				T4BWPropReset();
			}
		}

		// Both suffixes are logged on THIS receiver. A _P name does not prove
		// delivery to a character callback. Only _W may arm a candidate.
		string result = "observed";
		if (name == "ARMST_Shell_StartReload_W" && m_iStage == 0)
			m_iStage = 1;
		if (name == "ARMST_Shell_GrabShell_W" && (m_iStage == 1 || m_iStage == 4))
		{
			m_iCycle++;
			m_bCandidate = false;
			m_iStage = 2;
		}
		if (name == "ARMST_Shell_InsertShell_W" && m_iStage == 2)
			m_iStage = 3;
		if (name == "ARMST_ShellInsertCommit_W")
		{
			result = "rejected_out_of_order_or_duplicate";
			if (m_iStage == 3 && !m_bCandidate)
			{
				m_bCandidate = true;
				result = "diagnostic_candidate_no_transfer";
			}
		}
		if (name == "ARMST_Shell_CheckContinue_W" && m_iStage == 3)
			m_iStage = 4;
		if (name == "ARMST_Shell_EndReload_W")
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
		if (name == "ARMST_Shell_ReturnReady_W" && m_iStage == 5)
			m_iStage = 0;

		m_iSequence++;
		string line = "[ARMST-T4B-ARMST] receiver=weapon seq=" + m_iSequence.ToString();
		line += " instance=" + m_iInstance.ToString();
		line += " cycle=" + m_iCycle.ToString() + " stage=" + m_iStage.ToString();
		line += " event=" + name + " result=" + result;
		line += " from=" + timeFromStart.ToString() + " to=" + timeToEnd.ToString();
		{ /* Diagnostic output removed. */ }
		ArmstSnapshot();
	}

	// Passive snapshot for native `Weapon_*` reload events. Read-only: mag entity
	// reference tag + ammo, muzzle supply, barrel, chambered. No mutation.
	protected void T4BMagEventSnapshot(string eventName, int intParam, float timeFromStart, float timeToEnd)
	{
		m_iMagEvtSeq++;

		IEntity owner = GetOwner();
		BaseWeaponComponent weapon = null;
		if (owner)
		{
			weapon = BaseWeaponComponent.Cast(owner.FindComponent(WeaponComponent));
			if (!weapon)
				weapon = BaseWeaponComponent.Cast(owner.FindComponent(BaseWeaponComponent));
		}

		IEntity magEnt = null;
		int ammo = -1;
		int maxAmmo = -1;
		if (weapon)
		{
			BaseMagazineComponent mag = weapon.GetCurrentMagazine();
			if (mag)
			{
				magEnt = mag.GetOwner();
				ammo = mag.GetAmmoCount();
				maxAmmo = mag.GetMaxAmmoCount();
			}
		}
		if (magEnt != m_Magazine)
		{
			m_Magazine = magEnt;
			m_iMagazineTag++;
		}

		int supply = -1;
		int barrel = -1;
		int chambered = -1;
		if (weapon)
		{
			BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
			if (muzzle)
			{
				supply = muzzle.GetAmmoCount();
				barrel = muzzle.GetCurrentBarrelIndex();
				chambered = 0;
				if (muzzle.IsCurrentBarrelChambered())
					chambered = 1;
			}
		}

		bool magPresent = magEnt != null;
		{ /* Diagnostic output removed. */ }
	}

	protected void ArmstSnapshot()
	{
		IEntity owner = GetOwner();
		if (!owner)
			return;
		BaseWeaponComponent weapon = BaseWeaponComponent.Cast(owner.FindComponent(WeaponComponent));
		if (!weapon)
			weapon = BaseWeaponComponent.Cast(owner.FindComponent(BaseWeaponComponent));
		if (!weapon)
		{
			Print("[ARMST-T4B-ARMST] snapshot=weapon_unresolved", LogLevel.WARNING);
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
		string line = "[ARMST-T4B-ARMST] snapshot seq=" + m_iSequence.ToString();
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
		{ /* Diagnostic output removed. */ }
	}
}
