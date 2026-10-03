// ============================================================================
// ARMST MP-133 T4b - G3B1 inventory-donor consume test (DIAGNOSTIC ONLY)
// ----------------------------------------------------------------------------
// Existing addon ARMSTMP133T4B_InstalledMagProbe. G3-B1 scope: deduct exactly ONE round
// from ONE genuine, directly carried inventory magazine (donor), and observe persistence
// + inventory display. NO transfer into the weapon, NO installed-mag/chamber change,
// NO donor deletion, NO automatic retry/rollback. G3-B2 is not authorized.
//
// Activation: the action is intended to be mounted on the G3B1 CHILD test weapon prefab
// (Prefabs/Test/ARMST_T4B_G3B1_TestWeapon.et), which inherits the verified T4b lab weapon
// and adds only this action; the decorative DonorDevice prefab is historical/unused.
//
// Review corrections (Issue #34 comment 5973159457, incorporated):
//   * server-only mutation: !Replication.IsServer() -> REJECT, no write;
//   * actor context (pUserEntity + inventory) retained for the delayed samples;
//   * immediate prewrite gates: donor component entity == item, inv.Contains(item),
//     valid parent slot, ammo>0 -> else REJECT (no write);
//   * strict ammo-type contract: empty/unknown reference -> REJECT; donor GetAmmoType(0)
//     must be non-empty and equal to the reference;
//   * exactly ONE compatible root donor required; >1 -> `ambiguous-donor` (no write);
//   * one-shot latch set BEFORE the setter.
//
// Installed-SDK API only: SCR_InventoryStorageManagerComponent.GetAllRootItems / Contains,
// BaseMagazineComponent.Get/SetAmmoCount/GetMaxAmmoCount/GetOwner/GetAmmoType,
// InventoryItemComponent.GetParentSlot, CharacterControllerComponent.GetWeaponManagerComponent.
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

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-G3B1] #0 op=0 phase=action-init ev=register srv=" + srv.ToString(), LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		outName = "G3B1: consume 1 from inventory donor";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		outName = "Lab G3B1: deduct one round from exactly one carried inventory magazine; no weapon transfer.";
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

	// Reference ammo type: explicit attribute first, else the equipped weapon's magazine.
	ResourceName T4BRefAmmoType(IEntity user)
	{
		if (m_sG3b1ExpectedAmmoType != "")
			return m_sG3b1ExpectedAmmoType;
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

	// Counts root magazines and returns the exactly-one compatible donor, if any.
	// outCompat: number of compatible donors; outWithMag / outWithAmmo for reject reasons.
	int T4BFindDonor(SCR_InventoryStorageManagerComponent inv, ResourceName refType, out IEntity outItem, out BaseMagazineComponent outMag, out int outWithMag, out int outWithAmmo, out int outCompat)
	{
		outItem = null;
		outMag = null;
		outWithMag = 0;
		outWithAmmo = 0;
		outCompat = 0;
		if (!inv)
			return 0;

		array<IEntity> items = new array<IEntity>();
		int count = inv.GetAllRootItems(items);
		if (count <= 0)
			return 0;

		IEntity found = null;
		BaseMagazineComponent foundMag = null;
		foreach (IEntity it : items)
		{
			BaseMagazineComponent mag = T4BMagOf(it);
			if (!mag)
				continue;
			outWithMag++;
			int a = mag.GetAmmoCount();
			if (a <= 0)
				continue;
			outWithAmmo++;
			ResourceName at = mag.GetAmmoType(0);
			if (at.IsEmpty() || at != refType)
				continue;
			outCompat++;
			found = it;
			foundMag = mag;
		}
		if (outCompat == 1)
		{
			outItem = found;
			outMag = foundMag;
		}
		return outCompat;
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

		// Server-only mutation.
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

		SCR_InventoryStorageManagerComponent inv = SCR_InventoryStorageManagerComponent.Cast(user.FindComponent(SCR_InventoryStorageManagerComponent));
		if (!inv)
		{
			T4BReject(seq, opId, "no-inventory", srv);
			return;
		}

		if (m_bUsed)
		{
			T4BReject(seq, opId, "already-used", srv);
			return;
		}

		ResourceName refType = T4BRefAmmoType(user);
		if (refType.IsEmpty())
		{
			T4BReject(seq, opId, "unknown-ammo-type", srv);
			return;
		}

		IEntity donorItem = null;
		BaseMagazineComponent donorMag = null;
		int withMag = 0;
		int withAmmo = 0;
		int compat = 0;
		compat = T4BFindDonor(inv, refType, donorItem, donorMag, withMag, withAmmo, compat);

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
			Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
				+ " phase=reject ev=" + reason
				+ " withMag=" + withMag.ToString() + " withAmmo=" + withAmmo.ToString()
				+ " compat=" + compat.ToString()
				+ " refAmmoType=" + refType
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// Immediate prewrite gates.
		IEntity donorOwner = donorMag.GetOwner();
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
		int mx = donorMag.GetMaxAmmoCount();

		Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
			+ " phase=pre ev=invoked refAmmoType=" + refType
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, donorItem, donorMag), LogLevel.NORMAL);

		// Strict one-shot: latch BEFORE the write.
		m_bUsed = true;
		donorMag.SetAmmoCount(a - 1);

		int a2 = donorMag.GetAmmoCount();
		IEntity donorOwner2 = donorMag.GetOwner();
		bool sameMag = (donorOwner2 == donorOwner);
		bool ownerSame = (donorMag.GetOwner() == donorItem);
		bool member = inv.Contains(donorItem);
		bool gotOk = (a2 == a - 1);
		bool setterReadbackOk = gotOk && sameMag && ownerSame;

		Print("[ARMST_T4B-G3B1] " + seq + " op=" + opId.ToString()
			+ " phase=post ev=consume want=" + (a - 1).ToString()
			+ " got=" + a2.ToString()
			+ " setter_readback_ok=" + T4BB(setterReadbackOk)
			+ " gotOk=" + T4BB(gotOk)
			+ " sameMag=" + T4BB(sameMag)
			+ " ownerSame=" + T4BB(ownerSame)
			+ " member=" + T4BB(member)
			+ " gameplay_effect=UNVERIFIED"
			+ " srv=" + srv.ToString()
			+ " " + T4BDonorState(inv, donorItem, donorMag), LogLevel.NORMAL);

		// Passive delayed persistence samples using the RETAINED actor context.
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
