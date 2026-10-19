// Server-side R path for native double-barrel reloads.
// Ammo is moved into a real 2-round magazine BEFORE giving that entity to the engine.
// Cancellation never credits donors: the prepared magazine retains the reserved rounds.
[BaseContainerProps()]
modded class ARMST_ShotgunReloadComponent
{
	protected bool m_DBBusy;
	protected bool m_DBQuarantined;
	protected int m_DBGeneration;
	protected int m_DBTicks;
	protected bool m_DBSawReload;
	protected SCR_CharacterControllerComponent m_DBController;
	protected SCR_InventoryStorageManagerComponent m_DBInventory;
	protected BaseWeaponComponent m_DBWeapon;
	protected BaseMagazineComponent m_DBOld;
	protected BaseMagazineComponent m_DBPrepared;
	protected IEntity m_DBPreparedEntity;
	protected int m_DBOldAmmo;
	protected bool m_DBChambered;
	protected ResourceName m_DBSelectedAmmoType;
	protected bool m_DBRequestRejectedLogged;
	protected SCR_PlayerController m_DBRequester;

	protected ResourceName DBMagazineForType(ResourceName ammoType)
	{
		if (ammoType == "{862E8EB633CED07D}Prefabs/Weapons/Shootgun/Ammo/12g/armst_Ammo_12ga.et")
			return "{29B12AC67C564ED1}Prefabs/Weapons/Shootgun/Magazines/12ga/ARMST_DB_Buckshot2.et";
		if (ammoType == "{9F7537128778361F}Prefabs/Weapons/Shootgun/Ammo/12g/armst_Ammo_12ga_shell.et")
			return "{B98C070C4C2B470E}Prefabs/Weapons/Shootgun/Magazines/12ga/ARMST_DB_Slug2.et";
		return "";
	}

	// Only known homogeneous packs/internal magazines may fund a transfer.
	protected bool DBKnownDonor(IEntity item)
	{
		if (!item || !item.GetPrefabData())
			return false;
		ResourceName prefab = item.GetPrefabData().GetPrefabName();
		return prefab == "{B0DFDF7AAA9C5D39}Prefabs/Weapons/Shootgun/Magazines/12ga/armst_12ga_Buckshot.et"
			|| prefab == "{9F9380F5E2ECAF59}Prefabs/Weapons/Shootgun/Magazines/12ga/12ga_Buckshot_base.et"
			|| prefab == "{0346C78F29531C70}Prefabs/Weapons/Shootgun/Magazines/12ga/armst_12ga_Shell.et"
			|| prefab == "{29B12AC67C564ED1}Prefabs/Weapons/Shootgun/Magazines/12ga/ARMST_DB_Buckshot2.et"
			|| prefab == "{B98C070C4C2B470E}Prefabs/Weapons/Shootgun/Magazines/12ga/ARMST_DB_Slug2.et";
	}

	protected ResourceName DBSelectAmmoType(int total)
	{
		ResourceName preferred = m_DBKnownAmmoType;
		if (m_DBOld)
			preferred = m_DBOld.GetAmmoType(0);
		if (total > 0)
		{
			if (DBMagazineForType(preferred).IsEmpty())
				return "";
			return preferred;
		}
		array<IEntity> available = {};
		m_DBInventory.GetItems(available);
		bool hasBuckshot = false;
		bool hasSlug = false;
		foreach (IEntity candidate : available)
		{
			if (!DBKnownDonor(candidate) || !DBCarriedPack(candidate))
				continue;
			BaseMagazineComponent pack = BaseMagazineComponent.Cast(candidate.FindComponent(MagazineComponent));
			if (!pack || pack == m_DBOld || pack.GetAmmoCount() <= 0)
				continue;
			ResourceName kind = pack.GetAmmoType(0);
			if (DBMagazineForType(kind).IsEmpty())
				continue;
			if (kind == preferred)
				return kind;
			if (kind == "{862E8EB633CED07D}Prefabs/Weapons/Shootgun/Ammo/12g/armst_Ammo_12ga.et")
				hasBuckshot = true;
			else
				hasSlug = true;
		}
		if (hasBuckshot)
			return "{862E8EB633CED07D}Prefabs/Weapons/Shootgun/Ammo/12g/armst_Ammo_12ga.et";
		if (hasSlug)
			return "{9F7537128778361F}Prefabs/Weapons/Shootgun/Ammo/12g/armst_Ammo_12ga_shell.et";
		return "";
	}

	protected bool DBIdentity()
	{
		if (!m_DBController || !m_DBInventory || !m_DBWeapon || !GetOwner())
			return false;
		BaseWeaponManagerComponent manager = m_DBController.GetWeaponManagerComponent();
		return manager && manager.GetCurrentWeapon() == m_DBWeapon && m_DBWeapon.GetOwner() == GetOwner();
	}

	// Reject ground items and magazines installed in any weapon (including nested storage).
	protected bool DBCarriedPack(IEntity item)
	{
		if (!item || !m_DBInventory || !m_DBInventory.Contains(item))
			return false;
		IEntity node = item;
		for (int depth = 0; depth < 16; depth++)
		{
			if (node == m_DBController.GetOwner())
				return true;
			if (node.FindComponent(WeaponComponent))
				return false;
			InventoryItemComponent itemComponent = InventoryItemComponent.Cast(node.FindComponent(InventoryItemComponent));
			if (!itemComponent || !itemComponent.GetParentSlot())
				return false;
			BaseInventoryStorageComponent storage = itemComponent.GetParentSlot().GetStorage();
			if (!storage || !storage.GetOwner() || storage.GetOwner() == node)
				return false;
			node = storage.GetOwner();
		}
		return false;
	}

	void DBRequestNative(SCR_CharacterControllerComponent controller, SCR_PlayerController requester)
	{
		if (!Replication.IsServer() || !m_bNativeDoubleBarrelReload || m_DBBusy || m_DBQuarantined || !controller || controller.IsReloading())
			return;
		m_DBController = controller;
		if (!requester || requester.GetControlledEntity() != controller.GetOwner())
			return;
		m_DBRequester = requester;
		m_DBInventory = SCR_InventoryStorageManagerComponent.Cast(controller.GetOwner().FindComponent(SCR_InventoryStorageManagerComponent));
		m_DBWeapon = T4BWeapon();
		if (!DBIdentity())
			return;
		// A rejected/interrupted native request already reserved real ammunition.
		// Reuse that exact carried item; never spawn or debit another reservation.
		if (m_DBPrepared && m_DBPreparedEntity && m_DBPrepared.GetAmmoCount() > 0
			&& m_DBWeapon.GetCurrentMagazine() != m_DBPrepared)
		{
			if (!DBCarriedPack(m_DBPreparedEntity))
				return;
			m_DBGeneration++;
			DBStartPreparedNative(m_DBGeneration);
			return;
		}
		BaseMuzzleComponent muzzle = m_DBWeapon.GetCurrentMuzzle();
		if (!muzzle || muzzle.GetBarrelsCount() != 1)
			return;
		m_DBOld = m_DBWeapon.GetCurrentMagazine();
		m_DBOldAmmo = 0;
		if (m_DBOld)
			m_DBOldAmmo = m_DBOld.GetAmmoCount();
		m_DBChambered = muzzle.IsCurrentBarrelChambered();
		int chamber = 0;
		if (m_DBChambered)
			chamber = 1;
		int total = m_DBOldAmmo + chamber;
		if (m_DBOldAmmo < 0 || total != muzzle.GetAmmoCount() || total < 0 || total >= ShotgunLoadedLimit(m_DBOld))
		{
			{ /* Diagnostic output removed. */ }
			return;
		}
		m_DBSelectedAmmoType = DBSelectAmmoType(total);
		ResourceName preparedPrefab = DBMagazineForType(m_DBSelectedAmmoType);
		if (preparedPrefab.IsEmpty())
		{
			{ /* Diagnostic output removed. */ }
			return;
		}
		{ /* Diagnostic output removed. */ }
		Resource resource = Resource.Load(preparedPrefab);
		if (!resource)
			return;
		EntitySpawnParams parameters = new EntitySpawnParams();
		parameters.TransformMode = ETransformMode.WORLD;
		parameters.Transform[3] = controller.GetOwner().GetOrigin();
		m_DBPreparedEntity = GetGame().SpawnEntityPrefab(resource, GetGame().GetWorld(), parameters);
		if (!m_DBPreparedEntity)
			return;
		m_DBPrepared = BaseMagazineComponent.Cast(m_DBPreparedEntity.FindComponent(MagazineComponent));
		if (!m_DBPrepared)
		{
			SCR_EntityHelper.DeleteEntityAndChildren(m_DBPreparedEntity);
			return;
		}
		// Spawned ammo is never funding: erase it before exposing the item to inventory.
		m_DBPrepared.SetAmmoCount(0);
		if (m_DBPrepared.GetAmmoCount() != 0 || m_DBPrepared.GetMaxAmmoCount() != 2 || m_DBPrepared.GetAmmoType(0) != m_DBSelectedAmmoType)
		{
			SCR_EntityHelper.DeleteEntityAndChildren(m_DBPreparedEntity);
			return;
		}
		m_DBBusy = true;
		m_DBGeneration++;
		m_DBTicks = 0;
		if (!m_DBInventory.TryInsertItem(m_DBPreparedEntity))
		{
			DBAbandonEmpty("no-inventory-space");
			return;
		}
		GetGame().GetCallqueue().CallLater(DBPrepare, 50, false, m_DBGeneration);
	}

	protected void DBAbandonEmpty(string reason)
	{
		// Only our freshly spawned, still-empty item can be cleaned up here.
		if (m_DBPrepared && m_DBPrepared.GetAmmoCount() == 0 && m_DBWeapon && m_DBWeapon.GetCurrentMagazine() != m_DBPrepared)
		{
			if (m_DBInventory && m_DBInventory.Contains(m_DBPreparedEntity))
				m_DBInventory.TryDeleteItem(m_DBPreparedEntity);
			else
				SCR_EntityHelper.DeleteEntityAndChildren(m_DBPreparedEntity);
		}
		{ /* Diagnostic output removed. */ }
		m_DBBusy = false;
	}

	void DBPrepare(int generation)
	{
		if (!Replication.IsServer() || generation != m_DBGeneration || !m_DBBusy)
			return;
		if (!DBIdentity() || m_DBController.IsReloading() || !m_DBPrepared || m_DBPrepared.GetAmmoCount() != 0)
		{
			DBAbandonEmpty("identity-or-state-changed");
			return;
		}
		if (!DBCarriedPack(m_DBPreparedEntity))
		{
			m_DBTicks++;
			if (m_DBTicks < 40)
				GetGame().GetCallqueue().CallLater(DBPrepare, 50, false, generation);
			else
			{
				// Async insertion ownership is uncertain: no debit or deletion on timeout.
				m_DBQuarantined = true;
				Print("[ARMST-DB-RELOAD] quarantine=inventory-insert-timeout ammo-not-debited", LogLevel.ERROR);
			}
			return;
		}
		BaseMuzzleComponent muzzle = m_DBWeapon.GetCurrentMuzzle();
		if (!muzzle || m_DBWeapon.GetCurrentMagazine() != m_DBOld || muzzle.IsCurrentBarrelChambered() != m_DBChambered)
		{
			DBAbandonEmpty("magazine-or-chamber-changed");
			return;
		}
		if (m_DBOld && m_DBOld.GetAmmoCount() != m_DBOldAmmo)
		{
			DBAbandonEmpty("old-ammo-changed");
			return;
		}
		ResourceName ammoType = m_DBPrepared.GetAmmoType(0);
		{ /* Diagnostic output removed. */ }
		ResourceName retainedType = m_DBKnownAmmoType;
		if (m_DBOld)
			retainedType = m_DBOld.GetAmmoType(0);
		bool hasRetainedRounds = m_DBOldAmmo > 0 || m_DBChambered;
		if (ammoType.IsEmpty() || ammoType != m_DBSelectedAmmoType || (hasRetainedRounds && retainedType != ammoType))
		{
			DBAbandonEmpty("ammo-type-mismatch");
			return;
		}
		int chamber = 0;
		if (m_DBChambered)
			chamber = 1;
		int needed = ShotgunLoadedLimit(m_DBOld) - chamber - m_DBOldAmmo;
		// Recheck after async insertion, before any source ammunition is debited.
		if (m_DBOldAmmo < 0 || needed <= 0 || muzzle.GetAmmoCount() != m_DBOldAmmo + chamber)
		{
			DBAbandonEmpty("loaded-limit-or-total-changed");
			return;
		}
		array<IEntity> items = {};
		array<BaseMagazineComponent> donors = {};
		array<int> before = {};
		array<int> take = {};
		m_DBInventory.GetItems(items);
		int reserved = 0;
		foreach (IEntity item : items)
		{
			if (item == m_DBPreparedEntity || !DBKnownDonor(item) || !DBCarriedPack(item))
				continue;
			BaseMagazineComponent donor = BaseMagazineComponent.Cast(item.FindComponent(MagazineComponent));
			// Read-only evidence: do not infer the physical round from the UI label.
			if (donor && donor != m_DBOld && donor.GetAmmoCount() > 0 && item.GetPrefabData())
			{
				string ammoEvidence = "[ARMST-DB-AMMO] donorPrefab=" + item.GetPrefabData().GetPrefabName();
				ammoEvidence += " count=" + donor.GetAmmoCount().ToString();
				ammoEvidence += " ammoType0=" + donor.GetAmmoType(0);
				{ /* Diagnostic output removed. */ }
			}
			if (!donor || donor == m_DBOld || donor.GetAmmoType(0) != ammoType || donor.GetAmmoCount() <= 0 || donors.Find(donor) >= 0)
				continue;
			int amount = Math.Min(needed - reserved, donor.GetAmmoCount());
			donors.Insert(donor);
			before.Insert(donor.GetAmmoCount());
			take.Insert(amount);
			reserved += amount;
			if (reserved == needed)
				break;
		}
		if (reserved <= 0)
		{
			DBAbandonEmpty("no-compatible-ammo");
			return;
		}
		// Synchronous conservation transaction; no yield between debit and credit.
		if (m_DBOld)
			m_DBOld.SetAmmoCount(0);
		for (int i = 0; i < donors.Count(); i++)
			donors[i].SetAmmoCount(before[i] - take[i]);
		// Never create credited rounds when a source setter failed.
		bool debited = !m_DBOld || m_DBOld.GetAmmoCount() == 0;
		for (int sourceIndex = 0; sourceIndex < donors.Count(); sourceIndex++)
		{
			if (donors[sourceIndex].GetAmmoCount() != before[sourceIndex] - take[sourceIndex])
				debited = false;
		}
		if (!debited)
		{
			m_DBQuarantined = true;
			Print("[ARMST-DB-RELOAD] quarantine=debit-readback-mismatch credit-not-issued", LogLevel.ERROR);
			return;
		}
		m_DBPrepared.SetAmmoCount(m_DBOldAmmo + reserved);
		bool verified = m_DBPrepared.GetAmmoCount() == m_DBOldAmmo + reserved;
		if (m_DBOld && m_DBOld.GetAmmoCount() != 0)
			verified = false;
		for (int j = 0; j < donors.Count(); j++)
		{
			if (donors[j].GetAmmoCount() != before[j] - take[j])
				verified = false;
		}
		if (!verified)
		{
			m_DBQuarantined = true;
			Print("[ARMST-DB-RELOAD] quarantine=transfer-readback-mismatch", LogLevel.ERROR);
			return;
		}
		{ /* Diagnostic output removed. */ }
		m_DBTicks = 0;
		m_DBSawReload = false;
		DBStartPreparedNative(generation);
	}

	protected void DBStartPreparedNative(int generation)
	{
		if (!Replication.IsServer() || generation != m_DBGeneration || !DBIdentity())
			return;
		if (!m_DBPrepared || !m_DBPreparedEntity || m_DBPrepared.GetAmmoCount() <= 0
			|| !DBCarriedPack(m_DBPreparedEntity) || m_DBController.IsReloading())
			return;
		m_DBBusy = true;
		m_DBTicks = 0;
		m_DBSawReload = false;
		if (!m_DBRequester || !m_DBRequester.WAXDispatchDoubleBarrelReload(m_DBController.GetOwner(), GetOwner(), m_DBPreparedEntity))
		{
			// Rounds remain in the carried prepared magazine: do NOT refund them twice.
			m_DBBusy = false;
			if (!m_DBRequestRejectedLogged)
			{
				Print("[ARMST-DB-RELOAD] native-request-rejected prepared-ammo-retained-for-retry", LogLevel.WARNING);
				m_DBRequestRejectedLogged = true;
			}
			return;
		}
		m_DBRequestRejectedLogged = false;
		GetGame().GetCallqueue().CallLater(DBWatchNative, 50, false, generation);
	}

	void DBWatchNative(int generation)
	{
		if (!Replication.IsServer() || generation != m_DBGeneration || !m_DBBusy)
			return;
		m_DBTicks++;
		bool running = m_DBController && m_DBController.IsReloading();
		if (running)
			m_DBSawReload = true;
		if (!running && (m_DBSawReload || m_DBTicks >= 40))
		{
			m_DBBusy = false;
			if (m_DBWeapon && m_DBWeapon.GetCurrentMagazine() == m_DBPrepared)
				DBTraceNative("controlled-reload-complete");
			else
				Print("[ARMST-DB-RELOAD] native-interrupted no-refund-reserved-ammo-remains-in-magazine", LogLevel.WARNING);
			return;
		}
		if (m_DBTicks >= 600)
		{
			m_DBQuarantined = true;
			Print("[ARMST-DB-RELOAD] quarantine=native-timeout no-refund", LogLevel.ERROR);
			return;
		}
		GetGame().GetCallqueue().CallLater(DBWatchNative, 50, false, generation);
	}
}

// Native request runs on the owning character. Only the server prepares ammo.
modded class SCR_PlayerController
{
	protected int m_WAXDBSendSequence;
	protected int m_WAXDBOwnerSequence;

	bool WAXDispatchDoubleBarrelReload(IEntity actor, IEntity weapon, IEntity prepared)
	{
		if (!Replication.IsServer() || !actor || !weapon || !prepared || GetControlledEntity() != actor)
			return false;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(actor.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl)
			return false;
		BaseWeaponManagerComponent manager = ctrl.GetWeaponManagerComponent();
		if (!manager || !manager.GetCurrentWeapon() || manager.GetCurrentWeapon().GetOwner() != weapon)
			return false;
		RplComponent weaponRpl = RplComponent.Cast(weapon.FindComponent(RplComponent));
		RplComponent preparedRpl = RplComponent.Cast(prepared.FindComponent(RplComponent));
		if (!weaponRpl || !preparedRpl)
			return false;
		if (GetGame().GetPlayerController() == this)
			return ctrl.ReloadWeaponWith(prepared, true);
		m_WAXDBSendSequence++;
		Rpc(RpcDo_WAXDBReload, weaponRpl.Id(), preparedRpl.Id(), m_WAXDBSendSequence);
		return true; // Dispatched, not proof of successful native completion.
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Owner)]
	protected void RpcDo_WAXDBReload(RplId weaponId, RplId preparedId, int sequence)
	{
		if (Replication.IsServer() || GetGame().GetPlayerController() != this || sequence <= m_WAXDBOwnerSequence)
			return;
		m_WAXDBOwnerSequence = sequence;
		WAXDBTryOwnerReload(weaponId, preparedId, sequence, 0);
	}

	void WAXDBTryOwnerReload(RplId weaponId, RplId preparedId, int sequence, int attempt)
	{
		if (Replication.IsServer() || GetGame().GetPlayerController() != this || sequence != m_WAXDBOwnerSequence)
			return;
		IEntity actor = GetControlledEntity();
		if (!actor)
			return;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(actor.FindComponent(SCR_CharacterControllerComponent));
		SCR_InventoryStorageManagerComponent inventory = SCR_InventoryStorageManagerComponent.Cast(actor.FindComponent(SCR_InventoryStorageManagerComponent));
		if (!ctrl || !inventory || ctrl.IsReloading())
			return;
		BaseWeaponManagerComponent manager = ctrl.GetWeaponManagerComponent();
		if (!manager || !manager.GetCurrentWeapon())
			return;
		BaseWeaponComponent current = manager.GetCurrentWeapon();
		IEntity weapon = current.GetOwner();
		if (!weapon)
			return;
		RplComponent weaponRpl = RplComponent.Cast(weapon.FindComponent(RplComponent));
		ARMST_ShotgunReloadComponent reload = ARMST_ShotgunReloadComponent.Cast(weapon.FindComponent(ARMST_ShotgunReloadComponent));
		if (!weaponRpl || weaponRpl.Id() != weaponId || !reload || !reload.m_bNativeDoubleBarrelReload)
			return;
		array<IEntity> items = {};
		inventory.GetItems(items);
		foreach (IEntity item : items)
		{
			if (!item)
				continue;
			RplComponent itemRpl = RplComponent.Cast(item.FindComponent(RplComponent));
			if (!itemRpl || itemRpl.Id() != preparedId)
				continue;
			BaseMagazineComponent magazine = BaseMagazineComponent.Cast(item.FindComponent(MagazineComponent));
			if (!magazine || magazine.GetAmmoCount() <= 0 || current.GetCurrentMagazine() == magazine)
				return;
			if (!ctrl.ReloadWeaponWith(item, true))
				Print("[ARMST-DB-RELOAD] owner-native-request-rejected prepared-ammo-retained", LogLevel.WARNING);
			return;
		}
		// Inventory replication may arrive shortly after the reliable request.
		if (attempt < 20)
			GetGame().GetCallqueue().CallLater(WAXDBTryOwnerReload, 50, false, weaponId, preparedId, sequence, attempt + 1);
		else
			Print("[ARMST-DB-RELOAD] owner-prepared-item-unavailable no-ammo-write", LogLevel.WARNING);
	}
}
