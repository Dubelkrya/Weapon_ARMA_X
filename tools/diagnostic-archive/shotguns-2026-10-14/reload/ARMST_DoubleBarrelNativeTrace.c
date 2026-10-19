// Native reload observation and server-side last magazine type cache.
// No ammo, chamber, inventory or graph writes.
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
		Print(line, LogLevel.NORMAL);
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
