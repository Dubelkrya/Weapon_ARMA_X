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
// Passive only:
//   - subscribes to the character controller's existing animation-event invoker
//     (GetOnAnimationEvent) and logs Weapon_* events + a magazine/muzzle snapshot;
//   - gated to the lab weapon (ARMST_T4B_WeaponProbe) to avoid global spam;
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
		if (!name.StartsWith("Weapon_"))
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
		if (!we.FindComponent(ARMST_T4B_WeaponProbe))
			return;

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

		Print("[ARMST-T4B-CHAREVT] seq=" + m_iT4BCharEvtSeq.ToString()
			+ " side=" + side
			+ " event=" + name
			+ " intParam=" + intParam.ToString()
			+ " from=" + timeFromStart.ToString() + " to=" + timeToEnd.ToString()
			+ " magPresent=" + magPresent.ToString()
			+ " magTag=" + m_iT4BCharMagTag.ToString()
			+ " ammo=" + ammo.ToString() + "/" + maxAmmo.ToString()
			+ " muzzleSupply=" + supply.ToString()
			+ " barrel=" + barrel.ToString()
			+ " chambered=" + chambered.ToString(), LogLevel.NORMAL);
	}
}
