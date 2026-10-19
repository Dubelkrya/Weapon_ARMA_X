// ============================================================================
// ARMST MP-133 T4b - Task #1, PLAYER/CHARACTER-SIDE native mag-event observer
// (STAGED, source prep only).
//
// Purpose: close the observation gap. The weapon-side observer
// (BaseItemAnimationComponent.OnAnimationEvent) did NOT see any Weapon_*Magazine
// event, yet the installed magazine disappeared between cmd5 and cmd3. The prior
// T3 audit left open whether the magazine events are visible on a character/player
// animation receiver at all. This observer logs the SAME events on the character
// side so the question can be answered.
//
// Original diagnostics remain passive. The armed lab-only P commit bridge below
// now delegates one transfer to the unchanged G3B2 transaction; W never writes.
// Original observation scope:
//   - subscribes to the character controller's existing animation-event invoker
//     (GetOnAnimationEvent) and logs Weapon_* events + a magazine/muzzle snapshot;
//   - gated to the lab weapon (ARMST_ShotgunReloadComponent) to avoid global spam;
//   - NO writers, NO reload interference, NO input listeners, NO Update/timers,
//     NO HandleWeaponReloading, NO graph/prefab change.
//
// NOTE: this is a global `modded class SCR_CharacterControllerComponent` (the only
// documented way to receive character-side animation events). It is observe-only
// and does NOT touch the reload command flow. If the native rack ever regresses
// with this file present, remove it first (it is the only character-global file).
// ============================================================================
modded class SCR_CharacterControllerComponent
{
	protected int m_WAXRawCharacterEvents;
	// LOCAL PLAYER PROTOTYPE: decorative only, no inventory, ammo or replication writes.
	protected IEntity m_T4BVisualShell;
	protected IEntity m_T4BVisualShellWeapon;
	protected int m_T4BVisualShellTicks;

	protected void T4BHideVisualShell()
	{
		GetGame().GetCallqueue().Remove(T4BWatchVisualShell);
		if (m_T4BVisualShell)
			SCR_EntityHelper.DeleteEntityAndChildren(m_T4BVisualShell);
		m_T4BVisualShell = null;
		m_T4BVisualShellWeapon = null;
	}

	protected void T4BWatchVisualShell()
	{
		PlayerController local = GetGame().GetPlayerController();
		BaseWeaponManagerComponent manager = GetWeaponManagerComponent();
		BaseWeaponComponent current;
		if (manager)
			current = manager.GetCurrentWeapon();
		m_T4BVisualShellTicks++;
		if (!m_T4BVisualShell || !local || local.GetControlledEntity() != GetOwner() || IsDead() || !current || current.GetOwner() != m_T4BVisualShellWeapon || m_T4BVisualShellTicks >= 40)
		{
			T4BHideVisualShell();
			return;
		}
		if (Replication.IsServer() && (!m_T4BArmedPTransfer || !m_T4BArmedPTransfer.IsPSessionActive()))
		{
			T4BHideVisualShell();
			return;
		}
		GetGame().GetCallqueue().CallLater(T4BWatchVisualShell, 50, false);
	}

	protected void T4BShowVisualShell(IEntity weapon)
	{
		PlayerController local = GetGame().GetPlayerController();
		if (!local || local.GetControlledEntity() != GetOwner() || IsDead())
			return;
		if (m_T4BVisualShell && m_T4BVisualShellWeapon == weapon)
			return;
		T4BHideVisualShell();
		int bone = GetOwner().GetBoneIndex("LeftHandProp");
		if (bone < 0)
		{
			Print("[ARMST-SHELL-VISUAL] missing LeftHandProp", LogLevel.WARNING);
			return;
		}
		Resource res = Resource.Load("{E426D5918A73BC02}Prefabs/Weapons/Shootgun/MP133/ARMST_MP133_VisualShell.et");
		if (!res)
			return;
		EntitySpawnParams params = new EntitySpawnParams();
		params.TransformMode = ETransformMode.WORLD;
		params.Transform[3] = GetOwner().GetOrigin();
		m_T4BVisualShell = GetGame().SpawnEntityPrefab(res, GetOwner().GetWorld(), params);
		if (!m_T4BVisualShell)
			return;
		GetOwner().AddChild(m_T4BVisualShell, bone);
		if (m_T4BVisualShell.GetParent() != GetOwner())
		{
			T4BHideVisualShell();
			return;
		}
		vector transform[4];
		transform[0] = "1 0 0";
		transform[1] = "0 1 0";
		transform[2] = "0 0 1";
		transform[3] = "0 0 0";
		m_T4BVisualShell.SetLocalTransform(transform);
		m_T4BVisualShell.SetFlags(EntityFlags.VISIBLE);
		m_T4BVisualShellWeapon = weapon;
		m_T4BVisualShellTicks = 0;
		{ /* Diagnostic output removed. */ }
		GetGame().GetCallqueue().CallLater(T4BWatchVisualShell, 50, false);
	}

	// Bounded, read-only visual-prop audit. Does not prove absence of engine-internal visuals.
	protected int m_T4BVisualProbeSamples;

	protected void T4BVisualTree(IEntity entity, int depth, inout int budget)
	{
		// Passive diagnostic disabled in normal runtime.
	}

	protected void T4BVisualSnapshot(IEntity expectedWeapon, string phase)
	{
		// Passive diagnostic disabled in normal runtime.
	}

	protected ARMST_T4B_PCommitTransferAction m_T4BArmedPTransfer;

	void T4BReleasePTransfer(ARMST_T4B_PCommitTransferAction expected)
	{
		// Never detach another weapon's newly armed session.
		if (m_T4BArmedPTransfer != expected)
			return;
		m_T4BArmedPTransfer = null;
		T4BHideVisualShell();
	}

	bool T4BArmPTransfer(BaseWeaponComponent weapon, SCR_PlayerController requester)
	{
		if (!weapon || !weapon.GetOwner())
			return false;
		ARMST_ShotgunReloadComponent probe = ARMST_ShotgunReloadComponent.Cast(weapon.GetOwner().FindComponent(ARMST_ShotgunReloadComponent));
		if (!probe || !probe.m_T4BPTransferAction)
			return false;
		if (!probe.m_T4BPTransferAction.ArmP(GetOwner(), weapon, requester))
			return false;
		m_T4BArmedPTransfer = probe.m_T4BPTransferAction;
		return true;
	}
	protected bool m_bT4BLateAttachmentBindAttempted;
	protected bool m_bT4BPHostSampled;

	protected void T4BPHostReadOnly()
	{
		// Passive diagnostic disabled in normal runtime.
	}
	protected int m_iT4BCharEvtSeq;
	protected int m_iT4BCharMagTag;
	protected IEntity m_T4BCharMagRef;

	override void OnInit(IEntity owner)
	{
		super.OnInit(owner);

		ScriptInvoker onAnim = GetOnAnimationEvent();
		if (onAnim)
			onAnim.Insert(T4BOnCharAnimationEvent);
	}

	protected void T4BOnCharAnimationEvent(AnimationEventID animEventType, AnimationEventID animUserString, int intParam, float timeFromStart, float timeToEnd, SCR_CharacterControllerComponent controller)
	{
		string name = GameAnimationUtils.GetEventString(animEventType);
		if (m_WAXRawCharacterEvents < 96 && name.Contains("Shell"))
		{
			m_WAXRawCharacterEvents++;
			PrintFormat("[WAX-RAW-EVENT] side=P server=%1 name=%2", Replication.IsServer(), name);
		}
		// Compatibility until compiled clips are re-exported with ARMST event names.
		name.Replace("ASTRA", "ARMST");
		if (name == "ARMST_ShellVisual_Hide_P" || name == "ARMST_Shell_EndReload_P" || name == "ARMST_Shell_Stop_P" || name == "ARMST_Shell_ReturnReady_P")
			T4BHideVisualShell();
		// Captured action receives events before the current-weapon diagnostic gate.
		if (m_T4BArmedPTransfer)
			m_T4BArmedPTransfer.ReceiveP(GetOwner(), name);
		// Passive observation of native weapon and custom shell events on character.
		if (!name.StartsWith("Weapon_") && !name.StartsWith("ARMST_Shell"))
			return;

		// Lab gate: only when the current weapon carries the T4B probe.
		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		BaseWeaponComponent wpn = null;
		if (wm)
			wpn = wm.GetCurrentWeapon();
		if (!wpn)
			return;
		IEntity we = wpn.GetOwner();
		if (!we)
			return;
		if (!we.FindComponent(ARMST_ShotgunReloadComponent))
			return;
		ARMST_ShotgunReloadComponent nativeReload = ARMST_ShotgunReloadComponent.Cast(we.FindComponent(ARMST_ShotgunReloadComponent));
		if (name == "ARMST_ShellVisual_Show_P" && nativeReload && !nativeReload.m_bNativeDoubleBarrelReload)
			T4BShowVisualShell(we);
		if (nativeReload && !nativeReload.m_bNativeDoubleBarrelReload && m_T4BVisualProbeSamples < 12)
		{
			if (name == "ARMST_Shell_GrabShell_P")
				T4BVisualSnapshot(we, "grab-before-spawn");
			if (name == "Weapon_SpawnMagazine" || name == "Weapon_AttachMagazine")
			{
				T4BVisualSnapshot(we, name);
				GetGame().GetCallqueue().CallLater(T4BVisualSnapshot, 50, false, we, "delayed-" + name);
			}
		}
		if (nativeReload && nativeReload.m_bNativeDoubleBarrelReload)
		{
			nativeReload.DBTraceNative(name);
			GetGame().GetCallqueue().CallLater(nativeReload.DBTraceNative, 1, false, "after-" + name);
		}
		if (name == "ARMST_Shell_StartReload_P" && !m_bT4BPHostSampled)
		{
			m_bT4BPHostSampled = true;
			T4BPHostReadOnly();
		}

		if (name == "Weapon_Safety_Toggle_Off" && !m_bT4BLateAttachmentBindAttempted)
		{
			ARMST_T4B_ArmstV2_WeaponAnimationComponent component = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(we.FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
			if (component && component.GetOwner() == we)
			{
				m_bT4BLateAttachmentBindAttempted = true;
				GetGame().GetCallqueue().CallLater(T4BLateAttachmentBindOnly, 100, false, we, component);
			}
		}

		m_iT4BCharEvtSeq++;

		IEntity magEnt = null;
		int ammo = -1;
		int maxAmmo = -1;
		BaseMagazineComponent mag = wpn.GetCurrentMagazine();
		if (mag)
		{
			magEnt = mag.GetOwner();
			ammo = mag.GetAmmoCount();
			maxAmmo = mag.GetMaxAmmoCount();
		}
		if (magEnt != m_T4BCharMagRef)
		{
			m_T4BCharMagRef = magEnt;
			m_iT4BCharMagTag++;
		}

		int supply = -1;
		int barrel = -1;
		int chambered = -1;
		BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
		if (muzzle)
		{
			supply = muzzle.GetAmmoCount();
			barrel = muzzle.GetCurrentBarrelIndex();
			chambered = 0;
			if (muzzle.IsCurrentBarrelChambered())
				chambered = 1;
		}

		string side = "CL";
		if (Replication.IsServer())
			side = "SV";
		bool magPresent = magEnt != null;

		{ /* Diagnostic output removed. */ }
	}

	// One sample after an observed equip-related event; timing is not P readiness proof.
	protected void T4BLateAttachmentBindOnly(IEntity expectedWeapon, ARMST_T4B_ArmstV2_WeaponAnimationComponent expectedComponent)
	{
		BaseWeaponManagerComponent manager = GetWeaponManagerComponent();
		if (!manager || !expectedWeapon || !expectedComponent)
			return;
		BaseWeaponComponent currentWeapon = manager.GetCurrentWeapon();
		if (!currentWeapon || currentWeapon.GetOwner() != expectedWeapon)
			return;
		ARMST_T4B_ArmstV2_WeaponAnimationComponent component = ARMST_T4B_ArmstV2_WeaponAnimationComponent.Cast(expectedWeapon.FindComponent(ARMST_T4B_ArmstV2_WeaponAnimationComponent));
		if (!component)
			return;
		if (component != expectedComponent || component.GetOwner() != expectedWeapon)
			return;
		IEntity actor = GetOwner();
		if (!actor)
			return;
		CharacterAnimationComponent characterAnim = CharacterAnimationComponent.Cast(actor.FindComponent(CharacterAnimationComponent));
		if (!characterAnim)
		{
			{ /* Diagnostic output removed. */ }
			return;
		}
		TAnimGraphVariable characterRequestId = characterAnim.BindVariableBool("ARMST_ShellRequest");
		{ /* Diagnostic output removed. */ }
		int attachmentId = component.BindAttachment("Weapon");
		int variableId = component.BindAttBoolVariable(attachmentId, "ARMST_ShellRequest");
		{ /* Diagnostic output removed. */ }
	}
}
