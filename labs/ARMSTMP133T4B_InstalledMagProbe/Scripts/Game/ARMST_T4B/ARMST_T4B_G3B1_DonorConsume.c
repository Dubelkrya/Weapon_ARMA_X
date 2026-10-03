// ============================================================================
// ARMST MP-133 T4b - G3B1 inventory-donor consume test (DIAGNOSTIC ONLY)
// ----------------------------------------------------------------------------
// Existing addon ARMSTMP133T4B_InstalledMagProbe. G3-B1 scope: deduct exactly ONE round
// from ONE genuine, directly carried inventory magazine (donor), and observe persistence
// + inventory display. NO transfer into the weapon, NO installed-mag/chamber change,
// NO donor deletion, NO automatic retry/rollback. G3-B2 is not authorized.
//
// Activation: mounted on the G3B1 CHILD test weapon prefab
// (Prefabs/Test/ARMST_T4B_G3B1_TestWeapon.et). The decorative DonorDevice is historical.
//
// Revision 3 (Issue #34 comment 5973339846): the donor enumeration now walks the player's
// ACTUAL reachable inventory (GetStorages + SCR_InventoryStorageManagerComponent.GetAllItems
// per storage, i.e. nested clothing/vest/bag storage), not only root items, with bounded
// read-only CLASSIFICATION logging. The decrement WRITE is gated by `m_bG3b1WriteEnabled`
// (default false) so the first owner run is read-only.
//
// Corrections retained: server-only; actor context; installed-magazine exclusion by identity;
// weapon-context binding; immediate ownership/slot/identity gates; strict ammo-type; exactly one
// donor; one-shot latch before setter.
//
// Installed-SDK API only: SCR_InventoryStorageManagerComponent.GetAllRootItems / GetAllItems /
// GetStorages / Contains, BaseMagazineComponent.Get/SetAmmoCount/GetMaxAmmoCount/GetOwner/
// GetAmmoType, InventoryItemComponent.GetParentSlot/GetStorage,
// CharacterControllerComponent.GetWeaponManagerComponent.
// ============================================================================

class ARMST_T4B_G3B1_ConsumeAction : ScriptedUserAction
{
	protected bool m_bUsed = false;
	protected int m_iSeq = 0;
	protected int m_iOp = 0;
	protected int m_t4bItemTag = 0;
	protected int m_t4bNextItemTag = 0;
	protected int m_t4bMagTag = 0;
	protected int m_t4bNextMagTag = 0;
	protected IEntity m_lastItem;
	protected BaseMagazineComponent m_lastMag;

	// Retained actor context for the delayed samples.
	protected int m_delayedOp = 0;
	protected IEntity m_delayedUser;
	protected SCR_InventoryStorageManagerComponent m_delayedInv;
	protected BaseMagazineComponent m_delayedMag;
	protected IEntity m_delayedItem;
	protected int m_delayedWant = -1;

	// Optional explicit reference ammo type (ResourceName). Empty = use the equipped
	// weapon magazine's GetAmmoType(0). Required to be non-empty for any write.
	[Attribute("", UIWidgets.EditBox, "G3B1 expected donor ammo type ResourceName (empty = equipped weapon mag type)")]
	string m_sG3b1ExpectedAmmoType;

	// Safety gate: keep false for the read-only classification run; must be reviewed before true.
	[Attribute("false", UIWidgets.CheckBox, "G3B1 enable donor decrement (keep false for read-only classification)")]
	bool m_bG3b1WriteEnabled = false;

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-G3B1] #0 op=0 phase=action-init ev=register writeEnabled=" + T4BB(m_bG3b1WriteEnabled) + " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		outName = "G3B1: classify / consume 1 from inventory donor";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Lab G3B1: read-only inventory classification (default); deducts one round only when the write gate is enabled.";
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

	// ---- helpers ------------------------------------------------------------
	string T4BB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	int T4BItemTag(IEntity item)
	{
		if (item != m_lastItem)
		{
			m_lastItem = item;
			m_t4bNextItemTag++;
			m_t4bItemTag = m_t4bNextItemTag;
		}
		return m_t4bItemTag;
	}

	int T4BMagTag(BaseMagazineComponent mag)
	{
		if (mag != m_lastMag)
		{
			m_lastMag = mag;
			m_t4bNextMagTag++;
			m_t4bMagTag = m_t4bNextMagTag;
		}
		return m_t4bMagTag;
	}

	BaseMagazineComponent T4BMagOf(IEntity item)
	{
		if (!item)
			return null;
		BaseMagazineComponent m = BaseMagazineComponent.Cast(item.FindComponent(MagazineComponent));
		if (!m)
			m = BaseMagazineComponent.Cast(item.FindComponent(BaseMagazineComponent));
		return m;
	}

	BaseWeaponComponent T4BWeaponOf(IEntity e)
	{
		if (!e)
			return null;
		return BaseWeaponComponent.Cast(e.FindComponent(WeaponComponent));
	}

	BaseWeaponComponent T4BCurrentWeapon(IEntity user)
	{
		if (!user)
			return null;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(user.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl)
			return null;
		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
		if (!wm)
			return null;
		return wm.GetCurrentWeapon();
	}

	ResourceName T4BRefAmmoType(IEntity user)
	{
		if (m_sG3b1ExpectedAmmoType != "")
			return m_sG3b1ExpectedAmmoType;
		BaseWeaponComponent wpn = T4BCurrentWeapon(user);
		if (!wpn)
			return ResourceName.Empty;
		BaseMagazineComponent mag = wpn.GetCurrentMagazine();
		if (!mag)
			return ResourceName.Empty;
		return mag.GetAmmoType(0);
	}

	void T4BAddUnique(array<IEntity> items, IEntity it)
	{
		if (!it)
			return;
		foreach (IEntity x : items)
		{
			if (x == it)
				return;
		}
		items.Insert(it);
	}

	// Enumerate the player's ACTUAL reachable inventory: root items + every storage's items
	// (nested clothing/vest/bag included). Deduplicated by reference.
	void T4BCollect(SCR_InventoryStorageManagerComponent inv, out array<IEntity> items)
	{
		items = new array<IEntity>();
		if (!inv)
			return;

		array<IEntity> root = new array<IEntity>();
		inv.GetAllRootItems(root);
		foreach (IEntity it : root)
			T4BAddUnique(items, it);

		array<BaseInventoryStorageComponent> storages = new array<BaseInventoryStorageComponent>();
		inv.GetStorages(storages, EStoragePurpose.PURPOSE_ANY);
		foreach (BaseInventoryStorageComponent st : storages)
		{
			if (!st)
				continue;
			array<IEntity> part = new array<IEntity>();
			inv.GetAllItems(part, st);
			foreach (IEntity it : part)
				T4BAddUnique(items, it);
		}
	}

	string T4BStorageOf(IEntity item)
	{
		if (!item)
			return "-";
		InventoryItemComponent iic = InventoryItemComponent.Cast(item.FindComponent(InventoryItemComponent));
		if (!iic)
			return "-";
		InventoryStorageSlot slot = iic.GetParentSlot();
		if (!slot)
			return "-";
		BaseInventoryStorageComponent st = slot.GetStorage();
		string s = "slot" + slot.GetID().ToString();
		if (st)
		{
			IEntity se = st.GetOwner();
			if (se && se.GetPrefabData())
				s = se.GetPrefabData().GetPrefabName() + "/" + s;
		}
		return s;
	}

	string T4BDonorState(SCR_InventoryStorageManagerComponent inv, IEntity item, BaseMagazineComponent mag)
	{
		string itemPrefab = "-";
		int ammo = -1;
		int mx = -1;
		string ammoType = "-";
		int member = 0;
		int slotId = -1;
		if (item && item.GetPrefabData())
			itemPrefab = item.GetPrefabData().GetPrefabName();
		if (mag)
		{
			ammo = mag.GetAmmoCount();
			mx = mag.GetMaxAmmoCount();
			ammoType = mag.GetAmmoType(0);
		}
		if (inv && item && inv.Contains(item))
			member = 1;
		InventoryItemComponent iic = null;
		if (item)
			iic = InventoryItemComponent.Cast(item.FindComponent(InventoryItemComponent));
		if (iic)
		{
			InventoryStorageSlot slot = iic.GetParentSlot();
			if (slot)
				slotId = slot.GetID();
		}
		string s = "itemTag=I" + T4BItemTag(item).ToString();
		s = s + " item=" + itemPrefab;
		s = s + " magTag=M" + T4BMagTag(mag).ToString();
		s = s + " ammo=" + ammo.ToString() + "/" + mx.ToString();
		s = s + " ammoType=" + ammoType;
		s = s + " member=" + member.ToString();
		s = s + " slotId=" + slotId.ToString();
		s = s + " storage=" + T4BStorageOf(item);
		return s;
	}

	// Bounded read-only classification of magazine items (no writes).
	void T4BClassify(SCR_InventoryStorageManagerComponent inv, ResourceName refType, BaseMagazineComponent installedMag, IEntity installedItem, out int outWithMag, out int outWithAmmo, out int outCompat, out int outTargetSkipped)
	{
		outWithMag = 0;
		outWithAmmo = 0;
		outCompat = 0;
		outTargetSkipped = 0;

		array<IEntity> items = new array<IEntity>();
		T4BCollect(inv, items);
		Print("[ARMST_T4B-G3B1] phase=classify-start ev=items total=" + items.Count().ToString()
			+ " refAmmoType=" + refType, LogLevel.NORMAL);

		int shown = 0;
		foreach (IEntity it : items)
		{
			BaseMagazineComponent mag = T4BMagOf(it);
			if (!mag)
				continue;
			outWithMag++;
			bool isTarget = (mag == installedMag) || (installedItem != null && it == installedItem);
			if (isTarget)
			{
				outTargetSkipped++;
				shown++;
				Print("[ARMST_T4B-G3B1] phase=classify ev=target-excluded " + T4BDonorState(inv, it, mag), LogLevel.NORMAL);
				continue;
			}
			int a = mag.GetAmmoCount();
			if (a > 0)
				outWithAmmo++;
			ResourceName at = mag.GetAmmoType(0);
			bool typeOk = (!at.IsEmpty() && at == refType);
			if (a > 0 && typeOk)
				outCompat++;
			if (shown < 40)
			{
				shown++;
				Print("[ARMST_T4B-G3B1] phase=classify ev=magazine typeOk=" + T4BB(typeOk) + " " + T4BDonorState(inv, it, mag), LogLevel.NORMAL);
			}
		}

		Print("[ARMST_T4B-G3B1] phase=classify-done ev=magazines withMag=" + outWithMag.ToString()
			+ " withAmmo=" + outWithAmmo.ToString()
			+ " compat=" + outCompat.ToString()
			+ " targetSkipped=" + outTargetSkipped.ToString(), LogLevel.NORMAL);
	}

	void T4BReject(string seq, int opId, string reason, int srv)
	{
		Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
			+ " phase=reject ev=" + reason + " srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	// ---- action -------------------------------------------------------------
	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
	{
		m_iSeq++;
		m_iOp++;
		int opId = m_iOp;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		string seq = m_iSeq.ToString();

		if (!Replication.IsServer())
		{
			T4BReject(seq, opId, "not-server", srv);
			return;
		}

		IEntity user = pUserEntity;
		if (!user)
		{
			T4BReject(seq, opId, "no-user", srv);
			return;
		}

		IEntity actionOwner = pOwnerEntity;
		if (!actionOwner)
			actionOwner = GetOwner();
		BaseWeaponComponent actionWpn = T4BWeaponOf(actionOwner);
		if (!actionWpn)
		{
			T4BReject(seq, opId, "not-action-weapon", srv);
			return;
		}
		BaseWeaponComponent currentWpn = T4BCurrentWeapon(user);
		if (!currentWpn || currentWpn != actionWpn)
		{
			T4BReject(seq, opId, "wrong-weapon-context", srv);
			return;
		}

		SCR_InventoryStorageManagerComponent inv = SCR_InventoryStorageManagerComponent.Cast(user.FindComponent(SCR_InventoryStorageManagerComponent));
		if (!inv)
		{
			T4BReject(seq, opId, "no-inventory", srv);
			return;
		}

		// Installed weapon magazine (must never be a donor).
		BaseMagazineComponent installedMag = currentWpn.GetCurrentMagazine();
		IEntity installedItem = null;
		if (installedMag)
			installedItem = installedMag.GetOwner();

		ResourceName refType = T4BRefAmmoType(user);

		// Read-only classification of the actual reachable inventory.
		int withMag = 0;
		int withAmmo = 0;
		int compat = 0;
		int targetSkipped = 0;
		T4BClassify(inv, refType, installedMag, installedItem, withMag, withAmmo, compat, targetSkipped);

		// Read-only gate (default): no writes until the candidate is identified + reviewed.
		if (!m_bG3b1WriteEnabled)
		{
			Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
				+ " phase=readonly ev=classification-only writeEnabled=0"
				+ " withMag=" + withMag.ToString() + " withAmmo=" + withAmmo.ToString()
				+ " compat=" + compat.ToString() + " targetSkipped=" + targetSkipped.ToString()
				+ " refAmmoType=" + refType
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		if (refType.IsEmpty())
		{
			T4BReject(seq, opId, "unknown-ammo-type", srv);
			return;
		}
		if (m_bUsed)
		{
			T4BReject(seq, opId, "already-used", srv);
			return;
		}
		if (compat != 1)
		{
			string reason = "no-donor";
			if (withMag <= 0)
				reason = "no-donor-magazine";
			else if (withAmmo <= 0)
				reason = "zero-ammo";
			else if (compat <= 0)
				reason = "incompatible-ammo";
			else if (compat > 1)
				reason = "ambiguous-donor";
			T4BReject(seq, opId, reason, srv);
			return;
		}

		// Re-resolve the exactly-one compatible donor and revalidate immediately before the write.
		array<IEntity> items = new array<IEntity>();
		T4BCollect(inv, items);
		IEntity donorItem = null;
		BaseMagazineComponent donorMag = null;
		int found = 0;
		foreach (IEntity it : items)
		{
			BaseMagazineComponent mag = T4BMagOf(it);
			if (!mag)
				continue;
			if (mag == installedMag || (installedItem != null && it == installedItem))
				continue;
			if (mag.GetAmmoCount() <= 0)
				continue;
			ResourceName at = mag.GetAmmoType(0);
			if (at.IsEmpty() || at != refType)
				continue;
			found++;
			donorItem = it;
			donorMag = mag;
		}
		if (found != 1)
		{
			T4BReject(seq, opId, "donor-changed", srv);
			return;
		}

		IEntity donorOwner = donorMag.GetOwner();
		if (donorItem == installedItem || donorMag == installedMag)
		{
			T4BReject(seq, opId, "installed-magazine-excluded", srv);
			return;
		}
		if (donorOwner != donorItem || !inv.Contains(donorItem))
		{
			T4BReject(seq, opId, "not-owned", srv);
			return;
		}
		InventoryItemComponent iic = InventoryItemComponent.Cast(donorItem.FindComponent(InventoryItemComponent));
		InventoryStorageSlot slot = null;
		if (iic)
			slot = iic.GetParentSlot();
		if (!slot)
		{
			T4BReject(seq, opId, "no-slot", srv);
			return;
		}
		int a = donorMag.GetAmmoCount();
		if (a <= 0)
		{
			T4BReject(seq, opId, "zero-ammo", srv);
			return;
		}

		Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
			+ " phase=pre ev=invoked refAmmoType=" + refType
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, donorItem, donorMag), LogLevel.NORMAL);

		m_bUsed = true;
		donorMag.SetAmmoCount(a - 1);

		int a2 = donorMag.GetAmmoCount();
		bool gotOk = (a2 == a - 1);
		bool sameMag = (donorMag.GetOwner() == donorOwner);
		bool notInstalled = (donorMag != installedMag) && (installedItem == null || donorItem != installedItem);
		bool member = inv.Contains(donorItem);
		bool setterReadbackOk = gotOk && sameMag && notInstalled;

		Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
			+ " phase=post ev=consume want=" + (a - 1).ToString()
			+ " got=" + a2.ToString()
			+ " setter_readback_ok=" + T4BB(setterReadbackOk)
			+ " gotOk=" + T4BB(gotOk)
			+ " sameMag=" + T4BB(sameMag)
			+ " notInstalled=" + T4BB(notInstalled)
			+ " member=" + T4BB(member)
			+ " gameplay_effect=UNVERIFIED"
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, donorItem, donorMag), LogLevel.NORMAL);

		m_delayedOp = opId;
		m_delayedUser = user;
		m_delayedInv = inv;
		m_delayedMag = donorMag;
		m_delayedItem = donorItem;
		m_delayedWant = a - 1;
		GetGame().GetCallqueue().CallLater(T4BDelayed250, 250, false);
		GetGame().GetCallqueue().CallLater(T4BDelayed1000, 1000, false);
	}

	void T4BDelayed250()
	{
		T4BDelayedSample(250);
	}

	void T4BDelayed1000()
	{
		T4BDelayedSample(1000);
	}

	void T4BDelayedSample(int ms)
	{
		if (m_delayedOp <= 0)
			return;

		int ammoNow = -1;
		IEntity ownerNow = null;
		if (m_delayedMag)
		{
			ammoNow = m_delayedMag.GetAmmoCount();
			ownerNow = m_delayedMag.GetOwner();
		}
		bool actorValid = (m_delayedUser != null && m_delayedInv != null);
		bool stillSame = (ownerNow != null && ownerNow == m_delayedItem);
		bool member = false;
		if (m_delayedInv && m_delayedItem && m_delayedInv.Contains(m_delayedItem))
			member = true;
		bool persistAmmo = (ammoNow == m_delayedWant);

		int srv = 0;
		if (Replication.IsServer())
			srv = 1;

		Print("[ARMST_T4B-G3B1] op=" + m_delayedOp.ToString()
			+ " phase=delayed+" + ms.ToString() + "ms ev=post-consume"
			+ " expected=" + m_delayedWant.ToString()
			+ " got=" + ammoNow.ToString()
			+ " persistAmmo=" + T4BB(persistAmmo)
			+ " stillSame=" + T4BB(stillSame)
			+ " member=" + T4BB(member)
			+ " actorValid=" + T4BB(actorValid)
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(m_delayedInv, m_delayedItem, m_delayedMag), LogLevel.NORMAL);
	}
}
