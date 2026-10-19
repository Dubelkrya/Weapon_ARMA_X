// Native reload observation and server-side last magazine type cache.
// No ammo, chamber, inventory or graph writes.
// Temporary state sampler: at most 240 reads / 80 changed-state lines per player.
modded class SCR_PlayerController
{
	protected float m_WAXDBSampleElapsed;
	protected int m_WAXDBSampleCount;
	protected int m_WAXDBStateLines;
	protected string m_WAXDBLastState;

	override void OnUpdate(float timeSlice)
	{
		super.OnUpdate(timeSlice);
		if (m_WAXDBSampleCount >= 240 || m_WAXDBStateLines >= 80)
			return;
		if (!Replication.IsServer() && GetGame().GetPlayerController() != this)
			return;
		m_WAXDBSampleElapsed += timeSlice;
		if (m_WAXDBSampleElapsed < 0.25)
			return;
		m_WAXDBSampleElapsed = 0;
		IEntity actor = GetControlledEntity();
		if (!actor)
			return;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(actor.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl)
			return;
		BaseWeaponManagerComponent manager = ctrl.GetWeaponManagerComponent();
		if (!manager || !manager.GetCurrentWeapon())
			return;
		BaseWeaponComponent weapon = manager.GetCurrentWeapon();
		IEntity entity = weapon.GetOwner();
		if (!entity)
			return;
		ARMST_ShotgunReloadComponent reload = ARMST_ShotgunReloadComponent.Cast(entity.FindComponent(ARMST_ShotgunReloadComponent));
		if (!reload || !reload.m_bNativeDoubleBarrelReload)
			return;
		m_WAXDBSampleCount++;
		string state = "weapon=unreplicated";
		RplComponent weaponRpl = RplComponent.Cast(entity.FindComponent(RplComponent));
		if (weaponRpl)
			state = string.Format("weapon=%1", weaponRpl.Id());
		BaseMagazineComponent magazine = weapon.GetCurrentMagazine();
		if (magazine)
		{
			RplComponent magRpl = RplComponent.Cast(magazine.GetOwner().FindComponent(RplComponent));
			if (magRpl)
				state += string.Format(" magazine=%1", magRpl.Id());
			state += string.Format(" ammo=%1 max=%2", magazine.GetAmmoCount(), magazine.GetMaxAmmoCount());
		}
		else
			state += " magazine=none";
		BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
		if (muzzle)
			state += string.Format(" total=%1 chambered=%2", muzzle.GetAmmoCount(), muzzle.IsCurrentBarrelChambered());
		state += string.Format(" reloading=%1", ctrl.IsReloading());
		if (state == m_WAXDBLastState)
			return;
		m_WAXDBLastState = state;
		m_WAXDBStateLines++;
		PrintFormat("[WAX-DB-STATE] player=%1 server=%2 sample=%3 %4", GetPlayerId(), Replication.IsServer(), m_WAXDBSampleCount, state);
	}
}

[BaseContainerProps()]
modded class ARMST_ShotgunReloadComponent
{
	protected BaseMagazineComponent m_DBNativeLastMagazine;

	void DBTraceNative(string phase)
	{
		if (!m_bNativeDoubleBarrelReload || !Replication.IsServer())
			return;
		BaseWeaponComponent weapon = T4BWeapon();
		if (!weapon)
			return;
		BaseMagazineComponent mag = weapon.GetCurrentMagazine();
		BaseMuzzleComponent muzzle = weapon.GetCurrentMuzzle();
		int ammo = -1;
		int capacity = -1;
		int previousAmmo = -1;
		int supply = -1;
		bool chambered = false;
		if (mag)
		{
			ammo = mag.GetAmmoCount();
			capacity = mag.GetMaxAmmoCount();
			m_DBKnownAmmoType = mag.GetAmmoType(0);
		}
		if (m_DBNativeLastMagazine)
			previousAmmo = m_DBNativeLastMagazine.GetAmmoCount();
		if (muzzle)
		{
			supply = muzzle.GetAmmoCount();
			chambered = muzzle.IsCurrentBarrelChambered();
		}
		bool changed = mag != m_DBNativeLastMagazine;
		string line = "[ARMST-DB-NATIVE] phase=" + phase;
		line += " ammo=" + ammo.ToString() + "/" + capacity.ToString();
		line += " supply=" + supply.ToString() + " chambered=" + chambered.ToString();
		line += " magazineChanged=" + changed.ToString() + " previousAmmo=" + previousAmmo.ToString();
		if (mag)
		{
			line += " ammoType0=" + mag.GetAmmoType(0);
			IEntity magazineOwner = mag.GetOwner();
			if (magazineOwner && magazineOwner.GetPrefabData())
				line += " magazinePrefab=" + magazineOwner.GetPrefabData().GetPrefabName();
		}
		{ /* Diagnostic output removed. */ }
		if (mag)
			m_DBNativeLastMagazine = mag;
	}
}

modded class SCR_CharacterControllerComponent
{
	override protected void OnReloaded(IEntity owner, BaseWeaponComponent weapon)
	{
		super.OnReloaded(owner, weapon);
		if (!weapon || !weapon.GetOwner())
			return;
		ARMST_ShotgunReloadComponent reload = ARMST_ShotgunReloadComponent.Cast(weapon.GetOwner().FindComponent(ARMST_ShotgunReloadComponent));
		if (reload && reload.m_bNativeDoubleBarrelReload)
			reload.DBTraceNative("reload-complete");
	}
}
