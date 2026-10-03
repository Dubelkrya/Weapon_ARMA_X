// ============================================================================
// ARMST MP-133 T4b - G3B1 isolated inventory-donor consume test (DIAGNOSTIC ONLY)
// ----------------------------------------------------------------------------
// Existing addon ARMSTMP133T4B_InstalledMagProbe. Adds a SEPARATE, clearly named G3B1
// device prefab + this action. The verified T4b weapon prefab, probe, action and script
// are NOT touched.
//
// G3-B1 scope: deduct EXACTLY ONE round from a disposable, directly held compatible
// magazine in the acting user's inventory, and observe persistence + inventory display.
// It does NOT transfer anything into the weapon, does NOT touch the installed magazine or
// the chamber, and does NOT run G3-B2.
//
// Invocation: a single explicit non-R context action on the G3B1 device (server-
// authoritative, one-shot latch). Passive pre/post/+250ms/+1s snapshots of the donor
// magazine component identity, owning item entity, inventory membership, slot and
// ammo/max. No global modded, no input listener, no per-frame polling, no re-issue.
//
// Installed-SDK API only: SCR_InventoryStorageManagerComponent.GetAllRootItems /
// GetItems / Contains, BaseMagazineComponent.Get/SetAmmoCount/GetMaxAmmoCount/GetOwner/
// GetAmmoType, BaseInventoryStorageComponent / InventoryItemComponent.GetParentSlot.
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

	// Delayed persistence sample state (captured at the consume invocation).
	protected int m_delayedOp = 0;
	protected BaseMagazineComponent m_delayedMag;
	protected IEntity m_delayedItem;
	protected int m_delayedWant = -1;

	// Reference tags for the donor identity (stable per reference, not per prefab).
	protected IEntity m_lastItem;
	protected BaseMagazineComponent m_lastMag;

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-G3B1] #0 op=0 phase=action-init ev=register srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		outName = "G3B1: consume 1 from inventory donor mag";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Lab G3B1: deduct one round from a disposable directly held compatible inventory magazine; no weapon transfer.";
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

	IEntity T4BUser(IEntity pUserEntity)
	{
		if (pUserEntity)
			return pUserEntity;
		return SCR_PlayerController.GetLocalControlledEntity();
	}

	SCR_InventoryStorageManagerComponent T4BInv(IEntity user)
	{
		if (!user)
			return null;
		return SCR_InventoryStorageManagerComponent.Cast(user.FindComponent(SCR_InventoryStorageManagerComponent));
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

	// Reference ammo type from the user's equipped weapon magazine (may be null).
	ResourceName T4BRefAmmoType(IEntity user)
	{
		if (!user)
			return ResourceName.Empty;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(user.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl)
			return ResourceName.Empty;
		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
		if (!wm)
			return ResourceName.Empty;
		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn)
			return ResourceName.Empty;
		BaseMagazineComponent mag = wpn.GetCurrentMagazine();
		if (!mag)
			return ResourceName.Empty;
		return mag.GetAmmoType(0);
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
		return s;
	}

	// Finds the first eligible donor: a root inventory item with a magazine component and
	// ammo>=1, compatible with the equipped weapon's magazine ammo type (if known).
	int T4BFindDonor(SCR_InventoryStorageManagerComponent inv, ResourceName refType, out IEntity outItem, out BaseMagazineComponent outMag)
	{
		outItem = null;
		outMag = null;
		if (!inv)
			return 0;

		array<IEntity> items = new array<IEntity>();
		int count = inv.GetAllRootItems(items);
		if (count <= 0)
			return 0;

		int seenMag = 0;
		int seenAmmo = 0;
		int seenCompat = 0;
		foreach (IEntity it : items)
		{
			BaseMagazineComponent mag = T4BMagOf(it);
			if (!mag)
				continue;
			seenMag++;
			int a = mag.GetAmmoCount();
			if (a <= 0)
				continue;
			seenAmmo++;
			ResourceName at = mag.GetAmmoType(0);
			if (!refType.IsEmpty() && at != refType)
				continue;
			seenCompat++;
			outItem = it;
			outMag = mag;
			break;
		}

		if (outMag)
			return 1;
		if (seenMag <= 0)
			return -1; // no magazine item
		if (seenAmmo <= 0)
			return -2; // magazine(s) but all empty
		if (seenCompat <= 0)
			return -3; // ammo present but type mismatch
		return 0;
	}

	// ---- action -------------------------------------------------------------
	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
	{
		m_iSeq++;
		m_iOp++;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		int opId = m_iOp;

		IEntity user = T4BUser(pUserEntity);
		if (!user)
		{
			Print("[ARMST_T4B-G3B1] " + m_iSeq.ToString() + " op=" + opId.ToString()
				+ " phase=reject ev=no-user srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		SCR_InventoryStorageManagerComponent inv = T4BInv(user);
		if (!inv)
		{
			Print("[ARMST_T4B-G3B1] " + m_iSeq.ToString() + " op=" + opId.ToString()
				+ " phase=reject ev=no-inventory srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		if (m_bUsed)
		{
			Print("[ARMST_T4B-G3B1] " + m_iSeq.ToString() + " op=" + opId.ToString()
				+ " phase=reject ev=already-used srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		ResourceName refType = T4BRefAmmoType(user);
		IEntity donorItem = null;
		BaseMagazineComponent donorMag = null;
		int found = T4BFindDonor(inv, refType, donorItem, donorMag);

		if (found != 1)
		{
			string reason = "no-donor";
			if (found == -1)
				reason = "no-donor-magazine";
			else if (found == -2)
				reason = "zero-ammo";
			else if (found == -3)
				reason = "incompatible-ammo";
			Print("[ARMST_T4B-G3B1] " + m_iSeq.ToString() + " op=" + opId.ToString()
				+ " phase=reject ev=" + reason
				+ " refAmmoType=" + refType
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		IEntity donorOwner = donorMag.GetOwner();
		int a = donorMag.GetAmmoCount();
		int mx = donorMag.GetMaxAmmoCount();

		Print("[ARMST_T4B-G3B1] " + m_iSeq.ToString() + " op=" + opId.ToString()
			+ " phase=pre ev=invoked refAmmoType=" + refType
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, donorItem, donorMag), LogLevel.NORMAL);

		// Strict one-shot: latch BEFORE the write.
		m_bUsed = true;
		donorMag.SetAmmoCount(a - 1);

		int a2 = donorMag.GetAmmoCount();
		IEntity donorOwner2 = donorMag.GetOwner();
		bool sameMag = (donorOwner2 == donorOwner);
		bool member = (inv.Contains(donorItem) != false);
		bool gotOk = (a2 == a - 1);
		bool setterReadbackOk = gotOk && sameMag;

		Print("[ARMST_T4B-G3B1] " + m_iSeq.ToString() + " op=" + opId.ToString()
			+ " phase=post ev=consume want=" + (a - 1).ToString()
			+ " got=" + a2.ToString()
			+ " setter_readback_ok=" + T4BB(setterReadbackOk)
			+ " gotOk=" + T4BB(gotOk)
			+ " sameMag=" + T4BB(sameMag)
			+ " member=" + T4BB(member)
			+ " gameplay_effect=UNVERIFIED"
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, donorItem, donorMag), LogLevel.NORMAL);

		// Passive delayed persistence samples relative to THIS invocation.
		m_delayedOp = opId;
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

		IEntity user = SCR_PlayerController.GetLocalControlledEntity();
		SCR_InventoryStorageManagerComponent inv = T4BInv(user);

		int ammoNow = -1;
		IEntity ownerNow = null;
		if (m_delayedMag)
		{
			ammoNow = m_delayedMag.GetAmmoCount();
			ownerNow = m_delayedMag.GetOwner();
		}
		bool stillSame = (ownerNow != null && ownerNow == m_delayedItem);
		bool member = (inv && m_delayedItem && inv.Contains(m_delayedItem));
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
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, m_delayedItem, m_delayedMag), LogLevel.NORMAL);
	}
}
