// ============================================================================
// ARMST MP-133 T4b - G3B2 one-round transfer action (LAB, WRITE-DISABLED BY DEFAULT)
// ----------------------------------------------------------------------------
// Existing addon ARMSTMP133T4B_InstalledMagProbe, branch t4b/installed-mag-probe.
// G3-B2 scope: ONE manual, lab-only, no-R operation that moves exactly one round from ONE
// genuine carried donor magazine into the SAME already-installed MP-133 magazine, with a
// one-shot transaction state machine, quarantined partial failure and correlated telemetry.
//
// Source of truth: reports/MP133_V3_G3B2_TRANSACTION_DESIGN.md (rev 2, approved) plus review
// conditions in Issue #34 comments 5973770796 and 5973836821.
//
// SAFETY: this file is additive; it does NOT modify or subclass-override the verified G3-B1
// setter action or the T4b +1 action. The B2 write gate `m_bG3B2WriteEnabled` defaults FALSE and
// the published child prefab does not enable it. With the gate OFF the action runs the SAME
// read-only preflight as the write path and calls NO B2 setter. The donor-storage whitelist
// defaults EMPTY and therefore rejects every donor until the owner authorizes one exact
// storage-owner prefab (and optionally slot). No global `modded` hook, no input listener,
// no R / CMD_Weapon_Reload, no animation/RPC, no spawn/attach/detach/TryDeleteItem.
//
// NOTE ON SETUP MUTATION: the unchanged T4b probe (ARMST_T4B_WeaponProbe, reused on this lab
// weapon) performs ONE initialization baseline `SetAmmoCount(m_iT4BStartAmmo)` in its own
// `T4BTryBaseline()`. That is a known SETUP mutation, separate from the B2 action; it is not
// performed by this script and must not be conflated with the B2 transaction.
//
// Canonical serialized property spelling (P0 fix): `m_bG3B2WriteEnabled`,
// `m_sG3B2AllowedStorageOwner`, `m_iG3B2AllowedStorageSlot` - identical in script and prefab.
//
// Installed-SDK API used: SCR_InventoryStorageManagerComponent.GetAllRootItems / GetAllItems /
// GetStorages / Contains; BaseInventoryStorageComponent; InventoryItemComponent.GetParentSlot;
// InventoryStorageSlot.GetStorage / GetID; BaseMagazineComponent.GetAmmoCount / GetMaxAmmoCount /
// GetAmmoType(0) / GetOwner / SetAmmoCount; BaseWeaponComponent.GetCurrentMagazine /
// GetCurrentMuzzle / GetOwner; BaseWeaponManagerComponent.GetCurrentWeapon / GetWeapons;
// BaseMuzzleComponent.GetAmmoCount / GetMaxAmmoCount / GetBarrelsCount / GetCurrentBarrelIndex /
// IsCurrentBarrelChambered; CharacterControllerComponent.GetWeaponManagerComponent;
// Replication.IsServer.
// ============================================================================

class ARMST_T4B_G3B2_TransferAction : ScriptedUserAction
{
	// ---- per-instance one-shot state ----
	protected bool m_b2Latch = false;        // set immediately BEFORE the first B2 setter
	protected bool m_b2Quarantined = false;  // terminal; only a newly spawned instance clears it
	protected int m_i2OpId = 0;
	protected int m_i2Seq = 0;

	// ---- correlation tags (aids only; identity is the actual entity/component reference) ----
	protected IEntity m_lastItem;
	protected int m_t4bItemTag = 0;
	protected int m_t4bNextItemTag = 0;
	protected BaseMagazineComponent m_lastMag;
	protected int m_t4bMagTag = 0;
	protected int m_t4bNextMagTag = 0;

	// ---- last classification/selection results ----
	protected IEntity m_selItem;
	protected BaseMagazineComponent m_selMag;
	protected int m_cWithMag = 0;
	protected int m_cTargetSkipped = 0;
	protected int m_cInstalledExcluded = 0;
	protected int m_cWithAmmo = 0;
	protected int m_cTypeOk = 0;
	protected int m_cStorageRejected = 0;
	protected int m_cCompat = 0;

	// ---- delayed (read-only) samples: captured actual references, not just tags ----
	protected int m_dOp = 0;
	protected IEntity m_dActor;
	protected SCR_InventoryStorageManagerComponent m_dInv;
	protected BaseWeaponComponent m_dWeapon;
	protected BaseMagazineComponent m_dDonorMag;
	protected IEntity m_dDonorItem;
	protected int m_dDonorWant = -1;
	protected BaseInventoryStorageComponent m_dDonorStorage;
	protected IEntity m_dDonorStorageOwner;
	protected int m_dDonorSlotId = -1;
	protected BaseMagazineComponent m_dTargetMag;
	protected IEntity m_dTargetEnt;
	protected int m_dTargetWant = -1;
	protected BaseMuzzleComponent m_dMuzzle;
	protected bool m_dChambered = false;
	protected int m_dBarrel = -1;
	protected int m_dBarrels = -1;
	protected ResourceName m_dRefType;

	// ========================================================================
	// Attributes (canonical spelling shared with the prefab)
	// ========================================================================

	// Write gate. MUST stay false for the dry-run / published prefab.
	[Attribute("false", UIWidgets.CheckBox, "G3B2 enable the two-sided transfer writes (keep false for the read-only dry-run)")]
	bool m_bG3B2WriteEnabled = false;

	// Donor-storage whitelist (fail-closed). Empty = reject every donor.
	[Attribute("", UIWidgets.EditBox, "G3B2 allowed donor storage-owner prefab path (exact match; empty = reject all donors)")]
	string m_sG3B2AllowedStorageOwner;

	[Attribute("-1", UIWidgets.Slider, "G3B2 allowed donor storage slot id inside that owner (-1 = any slot)", "-1 40 1")]
	int m_iG3B2AllowedStorageSlot = -1;

	// ========================================================================
	// Init / UI
	// ========================================================================

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-G3B2] #0 op=0 phase=action-init ev=register writeEnabled=" + T4BB(m_bG3B2WriteEnabled)
			+ " whitelist=" + T4B2WL() + " allowedSlot=" + m_iG3B2AllowedStorageSlot.ToString()
			+ " srv=" + srv.ToString()
			+ " note=t4b-probe-baseline-setammo-is-separate-setup", LogLevel.NORMAL);
	}

	override bool GetActionNameScript(out string outName)
	{
		if (m_bG3B2WriteEnabled)
			outName = "G3B2: transfer 1 (WRITE ENABLED)";
		else
			outName = "G3B2: transfer 1 (dry-run; write off)";
		return true;
	}

	override bool GetActionDescriptionScript(out string outName)
	{
		if (m_bG3B2WriteEnabled)
			outName = "Lab G3B2: write ENABLED - performs the one-round donor->installed transfer with the one-shot transaction machine.";
		else
			outName = "Lab G3B2: read-only preflight only; performs the one-round donor->installed transfer only when the write gate is enabled.";
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

	// ========================================================================
	// Small helpers
	// ========================================================================

	string T4BB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	string T4B2WL()
	{
		if (m_sG3B2AllowedStorageOwner == "")
			return "<empty>";
		return m_sG3B2AllowedStorageOwner;
	}

	int T4B2ItemTag(IEntity item)
	{
		if (item != m_lastItem)
		{
			m_lastItem = item;
			m_t4bNextItemTag++;
			m_t4bItemTag = m_t4bNextItemTag;
		}
		return m_t4bItemTag;
	}

	int T4B2MagTag(BaseMagazineComponent mag)
	{
		if (mag != m_lastMag)
		{
			m_lastMag = mag;
			m_t4bNextMagTag++;
			m_t4bMagTag = m_t4bNextMagTag;
		}
		return m_t4bMagTag;
	}

	BaseMagazineComponent T4B2MagOf(IEntity item)
	{
		if (!item)
			return null;
		BaseMagazineComponent m = BaseMagazineComponent.Cast(item.FindComponent(MagazineComponent));
		if (!m)
			m = BaseMagazineComponent.Cast(item.FindComponent(BaseMagazineComponent));
		return m;
	}

	BaseWeaponComponent T4B2WeaponOf(IEntity e)
	{
		if (!e)
			return null;
		return BaseWeaponComponent.Cast(e.FindComponent(WeaponComponent));
	}

	BaseWeaponComponent T4B2CurrentWeapon(IEntity user)
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

	SCR_InventoryStorageManagerComponent T4B2Inv(IEntity user)
	{
		if (!user)
			return null;
		return SCR_InventoryStorageManagerComponent.Cast(user.FindComponent(SCR_InventoryStorageManagerComponent));
	}

	void T4B2AddUnique(array<IEntity> items, IEntity it)
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

	// Root items + every storage's items (nested clothing/vest/bag), deduplicated by reference.
	void T4B2Collect(SCR_InventoryStorageManagerComponent inv, out array<IEntity> items)
	{
		items = new array<IEntity>();
		if (!inv)
			return;
		array<IEntity> root = new array<IEntity>();
		inv.GetAllRootItems(root);
		foreach (IEntity it : root)
			T4B2AddUnique(items, it);
		array<BaseInventoryStorageComponent> storages = new array<BaseInventoryStorageComponent>();
		inv.GetStorages(storages, EStoragePurpose.PURPOSE_ANY);
		foreach (BaseInventoryStorageComponent st : storages)
		{
			if (!st)
				continue;
			array<IEntity> part = new array<IEntity>();
			inv.GetAllItems(part, st);
			foreach (IEntity it : part)
				T4B2AddUnique(items, it);
		}
	}

	// Installed magazine component+entity set across ALL weapons of the acting user.
	void T4B2InstalledSet(IEntity user, out array<BaseMagazineComponent> outMags, out array<IEntity> outEnts)
	{
		outMags = new array<BaseMagazineComponent>();
		outEnts = new array<IEntity>();
		if (!user)
			return;
		SCR_CharacterControllerComponent ctrl = SCR_CharacterControllerComponent.Cast(user.FindComponent(SCR_CharacterControllerComponent));
		if (!ctrl)
			return;
		BaseWeaponManagerComponent wm = ctrl.GetWeaponManagerComponent();
		if (!wm)
			return;
		array<BaseWeaponComponent> ws = new array<BaseWeaponComponent>();
		wm.GetWeapons(ws);
		foreach (BaseWeaponComponent w : ws)
		{
			if (!w)
				continue;
			BaseMagazineComponent m = w.GetCurrentMagazine();
			if (!m)
				continue;
			outMags.Insert(m);
			IEntity e = m.GetOwner();
			if (e)
				outEnts.Insert(e);
		}
	}

	bool T4B2InMags(array<BaseMagazineComponent> mags, BaseMagazineComponent m)
	{
		foreach (BaseMagazineComponent x : mags)
		{
			if (x == m)
				return true;
		}
		return false;
	}

	bool T4B2InEnts(array<IEntity> ents, IEntity e)
	{
		foreach (IEntity x : ents)
		{
			if (x == e)
				return true;
		}
		return false;
	}

	InventoryStorageSlot T4B2SlotOf(IEntity item)
	{
		if (!item)
			return null;
		InventoryItemComponent iic = InventoryItemComponent.Cast(item.FindComponent(InventoryItemComponent));
		if (!iic)
			return null;
		return iic.GetParentSlot();
	}

	BaseInventoryStorageComponent T4B2StorageOf(IEntity item)
	{
		InventoryStorageSlot slot = T4B2SlotOf(item);
		if (!slot)
			return null;
		return slot.GetStorage();
	}

	// True when the item sits inside any weapon / weapon-attachment storage.
	bool T4B2StorageIsWeapon(IEntity item)
	{
		BaseInventoryStorageComponent st = T4B2StorageOf(item);
		if (!st)
			return true;
		IEntity se = st.GetOwner();
		if (!se)
			return true;
		if (se.FindComponent(WeaponComponent))
			return true;
		return false;
	}

	// Whitelist check (fail-closed): exact storage-owner prefab path, optional exact slot id.
	bool T4B2StorageAllowed(IEntity item, out int outSlotId, out string outOwnerPrefab)
	{
		outSlotId = -1;
		outOwnerPrefab = "";
		if (!item)
			return false;
		if (m_sG3B2AllowedStorageOwner == "")
			return false;
		InventoryStorageSlot slot = T4B2SlotOf(item);
		if (!slot)
			return false;
		outSlotId = slot.GetID();
		BaseInventoryStorageComponent st = slot.GetStorage();
		if (!st)
			return false;
		IEntity se = st.GetOwner();
		if (!se || !se.GetPrefabData())
			return false;
		outOwnerPrefab = se.GetPrefabData().GetPrefabName();
		if (outOwnerPrefab != m_sG3B2AllowedStorageOwner)
			return false;
		if (m_iG3B2AllowedStorageSlot >= 0 && outSlotId != m_iG3B2AllowedStorageSlot)
			return false;
		return true;
	}

	// Chamber / barrel invariant (NOT muzzle ammo count).
	bool T4B2ChamberedOf(BaseMuzzleComponent m)
	{
		if (!m)
			return false;
		return m.IsCurrentBarrelChambered();
	}

	string T4B2DonorState(SCR_InventoryStorageManagerComponent inv, IEntity item, BaseMagazineComponent mag)
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
		string oowner = "";
		InventoryStorageSlot slot = T4B2SlotOf(item);
		if (slot)
			slotId = slot.GetID();
		BaseInventoryStorageComponent st = T4B2StorageOf(item);
		if (st)
		{
			IEntity se = st.GetOwner();
			if (se && se.GetPrefabData())
				oowner = se.GetPrefabData().GetPrefabName();
		}
		string s = "itemTag=I" + T4B2ItemTag(item).ToString();
		s = s + " item=" + itemPrefab;
		s = s + " magTag=M" + T4B2MagTag(mag).ToString();
		s = s + " ammo=" + ammo.ToString() + "/" + mx.ToString();
		s = s + " ammoType=" + ammoType;
		s = s + " member=" + member.ToString();
		s = s + " slotId=" + slotId.ToString();
		s = s + " storageOwner=" + oowner;
		return s;
	}

	// ========================================================================
	// Read-only classification + donor selection (NO setter)
	// ========================================================================
	void T4B2Scan(SCR_InventoryStorageManagerComponent inv, IEntity user, BaseMagazineComponent targetMag, IEntity targetEnt, ResourceName refType)
	{
		m_selItem = null;
		m_selMag = null;
		m_cWithMag = 0;
		m_cTargetSkipped = 0;
		m_cInstalledExcluded = 0;
		m_cWithAmmo = 0;
		m_cTypeOk = 0;
		m_cStorageRejected = 0;
		m_cCompat = 0;

		array<IEntity> items = new array<IEntity>();
		T4B2Collect(inv, items);
		array<BaseMagazineComponent> instMags = new array<BaseMagazineComponent>();
		array<IEntity> instEnts = new array<IEntity>();
		T4B2InstalledSet(user, instMags, instEnts);

		Print("[ARMST_T4B-G3B2] phase=classify-start ev=items total=" + items.Count().ToString()
			+ " refAmmoType=" + refType
			+ " whitelist=" + T4B2WL()
			+ " allowedSlot=" + m_iG3B2AllowedStorageSlot.ToString(), LogLevel.NORMAL);

		int shown = 0;
		foreach (IEntity it : items)
		{
			BaseMagazineComponent mag = T4B2MagOf(it);
			if (!mag)
				continue;
			m_cWithMag++;
			if (mag == targetMag || it == targetEnt)
			{
				m_cTargetSkipped++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=target-excluded " + T4B2DonorState(inv, it, mag), LogLevel.NORMAL);
				continue;
			}
			if (T4B2InMags(instMags, mag) || T4B2InEnts(instEnts, it))
			{
				m_cInstalledExcluded++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=installed-in-weapon " + T4B2DonorState(inv, it, mag), LogLevel.NORMAL);
				continue;
			}
			if (T4B2StorageIsWeapon(it))
			{
				m_cInstalledExcluded++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=storage-in-weapon " + T4B2DonorState(inv, it, mag), LogLevel.NORMAL);
				continue;
			}

			// Counters below are independent of the whitelist, so the reject reason is accurate.
			int a = mag.GetAmmoCount();
			if (a > 0)
				m_cWithAmmo++;
			ResourceName at = mag.GetAmmoType(0);
			bool typeOk = (!at.IsEmpty() && at == refType);
			if (a > 0 && typeOk)
				m_cTypeOk++;

			int sid = -1;
			string owner = "";
			if (!T4B2StorageAllowed(it, sid, owner))
			{
				m_cStorageRejected++;
				if (shown < 40)
				{
					shown++;
					Print("[ARMST_T4B-G3B2] phase=classify ev=storage-not-whitelisted typeOk=" + T4BB(typeOk) + " " + T4B2DonorState(inv, it, mag), LogLevel.NORMAL);
				}
				continue;
			}
			if (a > 0 && typeOk)
			{
				m_cCompat++;
				m_selItem = it;
				m_selMag = mag;
			}
			if (shown < 40)
			{
				shown++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=magazine typeOk=" + T4BB(typeOk) + " " + T4B2DonorState(inv, it, mag), LogLevel.NORMAL);
			}
		}

		Print("[ARMST_T4B-G3B2] phase=classify-done ev=magazines withMag=" + m_cWithMag.ToString()
			+ " targetSkipped=" + m_cTargetSkipped.ToString()
			+ " installedExcluded=" + m_cInstalledExcluded.ToString()
			+ " withAmmo=" + m_cWithAmmo.ToString()
			+ " typeOk=" + m_cTypeOk.ToString()
			+ " storageRejected=" + m_cStorageRejected.ToString()
			+ " compat=" + m_cCompat.ToString(), LogLevel.NORMAL);
	}

	string T4B2CompatReason()
	{
		if (m_cWithMag <= 0)
			return "no-donor-magazine";
		if (m_cWithAmmo <= 0)
			return "zero-ammo";
		if (m_cTypeOk <= 0)
			return "incompatible-ammo";
		if (m_cCompat <= 0)
		{
			if (m_cStorageRejected > 0)
				return "no-permitted-storage";
			return "no-eligible-donor";
		}
		if (m_cCompat > 1)
			return "ambiguous-donor";
		return "";
	}

	// ========================================================================
	// Read-only preflight (shared by gate-off and gate-on). NEVER writes.
	// ========================================================================
	bool T4B2Preflight(IEntity user, IEntity actionOwner, BaseWeaponComponent wpn, SCR_InventoryStorageManagerComponent inv, BaseMagazineComponent targetMag, IEntity targetEnt, ResourceName refType, int tAmmo, int tMax, BaseMuzzleComponent muzzle, int barrel, int barrels, out string outReason)
	{
		outReason = "";
		ARMST_T4B_WeaponProbe probe = ARMST_T4B_WeaponProbe.Cast(actionOwner.FindComponent(ARMST_T4B_WeaponProbe));
		if (!probe || !probe.IsBaselineDone())
		{
			outReason = "baseline-not-ready";
			return false;
		}
		if (refType.IsEmpty())
		{
			outReason = "unknown-ammo-type";
			return false;
		}
		if (tMax <= 0 || tAmmo < 0 || tAmmo >= tMax)
		{
			outReason = "target-invalid-or-full";
			return false;
		}
		if (m_cCompat != 1)
		{
			outReason = T4B2CompatReason();
			if (outReason == "")
				outReason = "no-eligible-donor";
			return false;
		}
		IEntity donorItem = m_selItem;
		BaseMagazineComponent donorMag = m_selMag;
		if (!donorItem || !donorMag)
		{
			outReason = "no-donor";
			return false;
		}
		if (donorMag == targetMag || donorItem == targetEnt)
		{
			outReason = "donor-is-target";
			return false;
		}
		int dMax = donorMag.GetMaxAmmoCount();
		int dAmmo = donorMag.GetAmmoCount();
		if (dMax <= 0 || dAmmo <= 0 || dAmmo > dMax)
		{
			outReason = "donor-bounds";
			return false;
		}
		if (donorMag.GetOwner() != donorItem || !inv.Contains(donorItem))
		{
			outReason = "not-owned";
			return false;
		}
		if (T4B2StorageIsWeapon(donorItem))
		{
			outReason = "donor-installed-in-weapon";
			return false;
		}
		int sid = -1;
		string owner = "";
		if (!T4B2StorageAllowed(donorItem, sid, owner))
		{
			outReason = "no-permitted-storage";
			return false;
		}
		array<BaseMagazineComponent> instMags = new array<BaseMagazineComponent>();
		array<IEntity> instEnts = new array<IEntity>();
		T4B2InstalledSet(user, instMags, instEnts);
		if (T4B2InMags(instMags, donorMag) || T4B2InEnts(instEnts, donorItem))
		{
			outReason = "donor-installed-in-weapon";
			return false;
		}
		ResourceName donorType = donorMag.GetAmmoType(0);
		if (donorType.IsEmpty() || donorType != refType)
		{
			outReason = "ammo-type-mismatch";
			return false;
		}
		if (!muzzle || barrel < 0 || barrels <= 0 || barrel >= barrels)
		{
			outReason = "no-barrel-component";
			return false;
		}
		BaseWeaponComponent wpnNow = T4B2CurrentWeapon(user);
		if (!wpnNow || wpnNow != wpn)
		{
			outReason = "weapon-context-changed";
			return false;
		}
		if (wpn.GetCurrentMagazine() != targetMag || targetMag.GetOwner() != targetEnt || targetMag.GetAmmoCount() != tAmmo)
		{
			outReason = "target-changed";
			return false;
		}
		return true;
	}

	// ========================================================================
	// Action
	// ========================================================================
	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
	{
		m_i2Seq++;
		m_i2OpId++;
		int opId = m_i2OpId;
		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		string seq = m_i2Seq.ToString();

		if (m_b2Quarantined)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=quarantined srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (m_b2Latch)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=already-latched srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (!Replication.IsServer())
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=not-server srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		IEntity user = pUserEntity;
		if (!user)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=no-user srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// Strict action-owner binding: the entity passed in must be this action's own owner.
		IEntity actionOwner = GetOwner();
		if (!actionOwner)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=no-action-owner srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		if (pOwnerEntity && pOwnerEntity != actionOwner)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=action-owner-mismatch srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		BaseWeaponComponent actionWpn = T4B2WeaponOf(actionOwner);
		if (!actionWpn)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=not-action-weapon srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		BaseWeaponComponent currentWpn = T4B2CurrentWeapon(user);
		if (!currentWpn || currentWpn != actionWpn)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=wrong-weapon-context srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		SCR_InventoryStorageManagerComponent inv = T4B2Inv(user);
		if (!inv)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=no-inventory srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		BaseMagazineComponent targetMag = currentWpn.GetCurrentMagazine();
		IEntity targetEnt = null;
		if (targetMag)
			targetEnt = targetMag.GetOwner();
		if (!targetMag || !targetEnt)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=no-installed-magazine srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		ResourceName refType = targetMag.GetAmmoType(0);
		int tAmmo = targetMag.GetAmmoCount();
		int tMax = targetMag.GetMaxAmmoCount();
		BaseMuzzleComponent muzzle = currentWpn.GetCurrentMuzzle();
		bool chBefore = T4B2ChamberedOf(muzzle);
		int barrelBefore = -1;
		int barrelsBefore = -1;
		int supplyBefore = -1;
		int supplyMaxBefore = -1;
		if (muzzle)
		{
			barrelBefore = muzzle.GetCurrentBarrelIndex();
			barrelsBefore = muzzle.GetBarrelsCount();
			supplyBefore = muzzle.GetAmmoCount();
			supplyMaxBefore = muzzle.GetMaxAmmoCount();
		}

		Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
			+ " phase=pre ev=invoked writeEnabled=" + T4BB(m_bG3B2WriteEnabled)
			+ " refAmmoType=" + refType
			+ " srv=" + srv.ToString()
			+ " target=" + T4B2DonorState(inv, targetEnt, targetMag)
			+ " muzzle=" + T4BB(muzzle != null)
			+ " chambered=" + T4BB(chBefore)
			+ " barrel=" + barrelBefore.ToString() + "/" + barrelsBefore.ToString()
			+ " supply=" + supplyBefore.ToString() + "/" + supplyMaxBefore.ToString(), LogLevel.NORMAL);

		// Read-only classification.
		T4B2Scan(inv, user, targetMag, targetEnt, refType);

		// Read-only preflight (shared): the SAME validation used by the write path.
		string pfReason = "";
		bool pfEligible = T4B2Preflight(user, actionOwner, currentWpn, inv, targetMag, targetEnt, refType, tAmmo, tMax, muzzle, barrelBefore, barrelsBefore, pfReason);
		Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
			+ " phase=preflight ev=checked preflightEligible=" + T4BB(pfEligible)
			+ " reason=" + pfReason
			+ " compat=" + m_cCompat.ToString()
			+ " targetSkipped=" + m_cTargetSkipped.ToString()
			+ " installedExcluded=" + m_cInstalledExcluded.ToString()
			+ " storageRejected=" + m_cStorageRejected.ToString()
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		// ------------------------------------------------------------------
		// DRY-RUN (default): full preflight ran above; NO B2 setter / latch.
		// ------------------------------------------------------------------
		if (!m_bG3B2WriteEnabled)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
				+ " phase=readonly ev=preflight-only writeEnabled=0"
				+ " preflightEligible=" + T4BB(pfEligible)
				+ " reason=" + pfReason
				+ " refAmmoType=" + refType
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// ------------------------------------------------------------------
		// Gate ON: REJECTED here (before the first setter) is repeatable.
		// ------------------------------------------------------------------
		if (!pfEligible)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=reject ev=" + pfReason + " srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		IEntity donorItem = m_selItem;
		BaseMagazineComponent donorMag = m_selMag;
		int dAmmo = donorMag.GetAmmoCount();

		// Final fail-closed boundary immediately before the first setter: re-validate the ACTUAL
		// donor storage/slot/muzzle/ammo type and weapon context. Any uncertainty -> REJECTED
		// (no write, repeatable), never a partial transaction.
		int sidBefore = -1;
		string ownerPrefBefore = "";
		bool dAllowedBefore = T4B2StorageAllowed(donorItem, sidBefore, ownerPrefBefore);
		InventoryStorageSlot slotBefore = T4B2SlotOf(donorItem);
		BaseInventoryStorageComponent storageBefore = T4B2StorageOf(donorItem);
		IEntity storageOwnerBefore = null;
		if (storageBefore)
			storageOwnerBefore = storageBefore.GetOwner();
		BaseMuzzleComponent muzzleBefore = currentWpn.GetCurrentMuzzle();
		ResourceName donorTypeBefore = donorMag.GetAmmoType(0);
		ResourceName targetTypeBefore = targetMag.GetAmmoType(0);
		BaseWeaponComponent wpnBefore = T4B2CurrentWeapon(user);
		bool boundaryOk = dAllowedBefore && (slotBefore != null) && (storageBefore != null) && (storageOwnerBefore != null)
			&& (donorMag.GetOwner() == donorItem) && inv.Contains(donorItem) && (T4B2MagOf(donorItem) == donorMag)
			&& (!T4B2StorageIsWeapon(donorItem))
			&& (!donorTypeBefore.IsEmpty()) && (donorTypeBefore == refType)
			&& (!targetTypeBefore.IsEmpty()) && (targetTypeBefore == refType)
			&& (muzzleBefore != null) && (muzzleBefore == muzzle)
			&& (wpnBefore == currentWpn) && (currentWpn.GetCurrentMagazine() == targetMag)
			&& (targetMag.GetOwner() == targetEnt) && (targetMag.GetAmmoCount() == tAmmo)
			&& (dAmmo > 0);
		if (!boundaryOk)
		{
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
				+ " phase=reject ev=prewrite-boundary-failed"
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// ------------------------------------------------------------------
		// TRANSACTION (donor-first). Latch BEFORE the first setter.
		// ------------------------------------------------------------------
		m_b2Latch = true;

		donorMag.SetAmmoCount(dAmmo - 1);

		int dAfter = donorMag.GetAmmoCount();
		bool dSameOwner = (donorMag.GetOwner() == donorItem);
		bool dMember = inv.Contains(donorItem);
		bool dSameComponent = (T4B2MagOf(donorItem) == donorMag);
		BaseInventoryStorageComponent storageAfter = T4B2StorageOf(donorItem);
		IEntity storageOwnerAfter = null;
		if (storageAfter)
			storageOwnerAfter = storageAfter.GetOwner();
		bool storageSame = (storageAfter != null) && (storageAfter == storageBefore) && (storageOwnerAfter == storageOwnerBefore);
		InventoryStorageSlot slotAfter = T4B2SlotOf(donorItem);
		bool slotSame = (slotAfter != null) && (slotAfter.GetID() == sidBefore);
		ResourceName donorTypeAfter = donorMag.GetAmmoType(0);
		bool donorTypeSame = (!donorTypeAfter.IsEmpty()) && (donorTypeAfter == refType);
		bool donorOk = (dAfter == dAmmo - 1) && dSameOwner && dMember && dSameComponent && storageSame && slotSame && donorTypeSame;
		Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
			+ " phase=donor-post ev=set want=" + (dAmmo - 1).ToString()
			+ " got=" + dAfter.ToString()
			+ " donorOk=" + T4BB(donorOk)
			+ " sameComponent=" + T4BB(dSameComponent)
			+ " storageSame=" + T4BB(storageSame)
			+ " slotSame=" + T4BB(slotSame)
			+ " typeSame=" + T4BB(donorTypeSame)
			+ " srv=" + srv.ToString()
			+ " " + T4B2DonorState(inv, donorItem, donorMag), LogLevel.NORMAL);
		if (!donorOk)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=indeterminate ev=donor-post-mismatch srv=" + srv.ToString(), LogLevel.NORMAL);
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=quarantine ev=stop-no-retry srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// Between setters: still-equipped weapon, same target/chamber/muzzle, donor storage.
		BaseWeaponComponent wpnMid = T4B2CurrentWeapon(user);
		BaseMuzzleComponent muzzleMid = null;
		if (wpnMid)
			muzzleMid = wpnMid.GetCurrentMuzzle();
		if (!wpnMid || !muzzleMid)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=indeterminate ev=mid-weapon-or-muzzle-lost srv=" + srv.ToString(), LogLevel.NORMAL);
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=quarantine ev=stop-no-retry srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		bool wpnSameMid = (wpnMid == currentWpn);
		bool targetStill = (wpnMid.GetCurrentMagazine() == targetMag) && (targetMag.GetOwner() == targetEnt);
		bool muzzleSameMid = (muzzleMid == muzzle);
		bool chamberSameMid = (muzzleMid.IsCurrentBarrelChambered() == chBefore) && (muzzleMid.GetCurrentBarrelIndex() == barrelBefore) && (muzzleMid.GetBarrelsCount() == barrelsBefore);
		bool tCountSame = (targetMag.GetAmmoCount() == tAmmo);
		BaseInventoryStorageComponent storageMid = T4B2StorageOf(donorItem);
		bool storageSameMid = (storageMid != null) && (storageMid == storageBefore);
		if (!wpnSameMid || !targetStill || !muzzleSameMid || !chamberSameMid || !tCountSame || !storageSameMid)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
				+ " phase=indeterminate ev=between-setters-changed"
				+ " wpnSame=" + T4BB(wpnSameMid)
				+ " targetStill=" + T4BB(targetStill)
				+ " muzzleSame=" + T4BB(muzzleSameMid)
				+ " chamberSame=" + T4BB(chamberSameMid)
				+ " tCountSame=" + T4BB(tCountSame)
				+ " storageSame=" + T4BB(storageSameMid)
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=quarantine ev=stop-no-retry srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		targetMag.SetAmmoCount(tAmmo + 1);

		int tAfter = targetMag.GetAmmoCount();
		BaseWeaponComponent wpnEnd = T4B2CurrentWeapon(user);
		BaseMuzzleComponent muzzleEnd = null;
		if (wpnEnd)
			muzzleEnd = wpnEnd.GetCurrentMuzzle();
		bool wpnEndOk = (wpnEnd != null) && (wpnEnd == currentWpn);
		bool installedEnd = wpnEndOk && (wpnEnd.GetCurrentMagazine() == targetMag);
		bool targetOk = (tAfter == tAmmo + 1)
			&& wpnEndOk
			&& installedEnd
			&& (targetMag.GetOwner() == targetEnt);
		Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
			+ " phase=target-post ev=set want=" + (tAmmo + 1).ToString()
			+ " got=" + tAfter.ToString()
			+ " targetOk=" + T4BB(targetOk)
			+ " wpnEndOk=" + T4BB(wpnEndOk)
			+ " srv=" + srv.ToString()
			+ " target=" + T4B2DonorState(inv, targetEnt, targetMag), LogLevel.NORMAL);
		if (!targetOk)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=indeterminate ev=target-post-mismatch srv=" + srv.ToString(), LogLevel.NORMAL);
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=quarantine ev=stop-no-retry srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}
		// Guard the muzzle before any chamber/commit/diagnostic getter.
		if (!muzzleEnd)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=indeterminate ev=muzzle-lost-after-target srv=" + srv.ToString(), LogLevel.NORMAL);
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=quarantine ev=stop-no-retry srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		// Commit checks (all getters use the guarded muzzleEnd).
		bool conserv = ((dAmmo + tAmmo) == (dAfter + tAfter));
		ResourceName targetTypeAfter = targetMag.GetAmmoType(0);
		bool typesOk = (!targetTypeAfter.IsEmpty()) && (targetTypeAfter == refType) && donorTypeSame;
		bool chamberAfterOk = (muzzleEnd.IsCurrentBarrelChambered() == chBefore) && (muzzleEnd.GetCurrentBarrelIndex() == barrelBefore) && (muzzleEnd.GetBarrelsCount() == barrelsBefore);
		int supplyAfter = muzzleEnd.GetAmmoCount();
		bool committed = donorOk && targetOk && conserv && typesOk && chamberAfterOk
			&& (wpnEnd == currentWpn) && (muzzleEnd == muzzle)
			&& (wpnEnd.GetCurrentMagazine() == targetMag) && (targetMag.GetOwner() == targetEnt)
			&& (donorMag.GetOwner() == donorItem) && inv.Contains(donorItem)
			&& (T4B2MagOf(donorItem) == donorMag) && (T4B2StorageOf(donorItem) == storageBefore);

		if (!committed)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
				+ " phase=indeterminate ev=commit-check-failed"
				+ " conserv=" + T4BB(conserv)
				+ " typesOk=" + T4BB(typesOk)
				+ " chamberOk=" + T4BB(chamberAfterOk)
				+ " srv=" + srv.ToString(), LogLevel.NORMAL);
			Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString() + " phase=quarantine ev=stop-no-retry srv=" + srv.ToString(), LogLevel.NORMAL);
			return;
		}

		Print("[ARMST_T4B-G3B2] " + seq + " op=" + opId.ToString()
			+ " phase=commit ev=committed"
			+ " donorBefore=" + dAmmo.ToString() + " donorAfter=" + dAfter.ToString()
			+ " targetBefore=" + tAmmo.ToString() + " targetAfter=" + tAfter.ToString()
			+ " conserved=" + T4BB(conserv)
			+ " chamberedBefore=" + T4BB(chBefore) + " chamberedAfter=" + T4BB(T4B2ChamberedOf(muzzleEnd))
			+ " barrelBefore=" + barrelBefore.ToString() + " barrelAfter=" + muzzleEnd.GetCurrentBarrelIndex().ToString()
			+ " supplyBefore=" + supplyBefore.ToString() + " supplyAfter=" + supplyAfter.ToString()
			+ " supplyTelemetry=1"
			+ " gameplay_effect=UNVERIFIED"
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		m_dOp = opId;
		m_dActor = user;
		m_dInv = inv;
		m_dWeapon = currentWpn;
		m_dDonorMag = donorMag;
		m_dDonorItem = donorItem;
		m_dDonorWant = dAmmo - 1;
		m_dDonorStorage = storageBefore;
		m_dDonorStorageOwner = storageOwnerBefore;
		m_dDonorSlotId = sidBefore;
		m_dTargetMag = targetMag;
		m_dTargetEnt = targetEnt;
		m_dTargetWant = tAmmo + 1;
		m_dMuzzle = muzzle;
		m_dChambered = chBefore;
		m_dBarrel = barrelBefore;
		m_dBarrels = barrelsBefore;
		m_dRefType = refType;
		GetGame().GetCallqueue().CallLater(T4B2Delayed250, 250, false);
		GetGame().GetCallqueue().CallLater(T4B2Delayed1000, 1000, false);
	}

	// ========================================================================
	// Delayed read-only samples (NEVER write)
	// ========================================================================
	void T4B2Delayed250()
	{
		T4B2DelayedSample(250);
	}

	void T4B2Delayed1000()
	{
		T4B2DelayedSample(1000);
	}

	void T4B2DelayedSample(int ms)
	{
		if (m_dOp <= 0)
			return;

		int dNow = -1;
		IEntity dOwnerNow = null;
		if (m_dDonorMag)
		{
			dNow = m_dDonorMag.GetAmmoCount();
			dOwnerNow = m_dDonorMag.GetOwner();
		}
		int tNow = -1;
		IEntity tOwnerNow = null;
		if (m_dTargetMag)
		{
			tNow = m_dTargetMag.GetAmmoCount();
			tOwnerNow = m_dTargetMag.GetOwner();
		}

		bool dPersist = (dNow == m_dDonorWant);
		bool tPersist = (tNow == m_dTargetWant);
		bool dSameEnt = (dOwnerNow != null && dOwnerNow == m_dDonorItem);
		bool dSameComp = (m_dDonorItem != null && m_dDonorMag != null) && (T4B2MagOf(m_dDonorItem) == m_dDonorMag);
		bool member = (m_dInv != null && m_dDonorItem != null) && m_dInv.Contains(m_dDonorItem);
		BaseInventoryStorageComponent dStorageNow = null;
		IEntity dStorageOwnerNow = null;
		int dSlotIdNow = -1;
		if (m_dDonorItem)
		{
			dStorageNow = T4B2StorageOf(m_dDonorItem);
			if (dStorageNow)
				dStorageOwnerNow = dStorageNow.GetOwner();
			InventoryStorageSlot dSlotNow = T4B2SlotOf(m_dDonorItem);
			if (dSlotNow)
				dSlotIdNow = dSlotNow.GetID();
		}
		bool dStorageSame = (dStorageNow != null) && (dStorageNow == m_dDonorStorage) && (dStorageOwnerNow == m_dDonorStorageOwner) && (dSlotIdNow == m_dDonorSlotId);

		// The actor's CURRENTLY equipped weapon must still be the captured one, and the target must
		// still be its installed magazine (re-resolve from the actor, not only the captured ref).
		BaseWeaponComponent wpnNow = null;
		if (m_dActor)
			wpnNow = T4B2CurrentWeapon(m_dActor);
		bool wpnSame = (wpnNow != null) && (wpnNow == m_dWeapon);
		BaseMagazineComponent installedNow = null;
		BaseMuzzleComponent muzzleNow = null;
		if (wpnNow)
		{
			installedNow = wpnNow.GetCurrentMagazine();
			muzzleNow = wpnNow.GetCurrentMuzzle();
		}
		bool targetInstalled = wpnSame && (installedNow != null) && (installedNow == m_dTargetMag) && (tOwnerNow == m_dTargetEnt);
		bool muzzleSame = (muzzleNow != null) && (muzzleNow == m_dMuzzle);
		bool chamberSame = (T4B2ChamberedOf(muzzleNow) == m_dChambered);
		bool barrelSame = false;
		if (muzzleNow)
			barrelSame = (muzzleNow.GetCurrentBarrelIndex() == m_dBarrel) && (muzzleNow.GetBarrelsCount() == m_dBarrels);

		// Ammo-type invariance (full delayed scope, not only count/location).
		ResourceName dTypeNow = ResourceName.Empty;
		ResourceName tTypeNow = ResourceName.Empty;
		if (m_dDonorMag)
			dTypeNow = m_dDonorMag.GetAmmoType(0);
		if (m_dTargetMag)
			tTypeNow = m_dTargetMag.GetAmmoType(0);
		bool typesSame = (!dTypeNow.IsEmpty()) && (dTypeNow == m_dRefType) && (!tTypeNow.IsEmpty()) && (tTypeNow == m_dRefType);

		bool allOk = dPersist && tPersist && dSameEnt && dSameComp && member && dStorageSame && wpnSame && targetInstalled && muzzleSame && chamberSame && barrelSame && typesSame;

		int srv = 0;
		if (Replication.IsServer())
			srv = 1;
		Print("[ARMST_T4B-G3B2] op=" + m_dOp.ToString()
			+ " phase=delayed+" + ms.ToString() + "ms ev=post-commit"
			+ " donorWant=" + m_dDonorWant.ToString() + " donorGot=" + dNow.ToString()
			+ " targetWant=" + m_dTargetWant.ToString() + " targetGot=" + tNow.ToString()
			+ " donorPersist=" + T4BB(dPersist)
			+ " targetPersist=" + T4BB(tPersist)
			+ " donorSameEnt=" + T4BB(dSameEnt)
			+ " donorSameComp=" + T4BB(dSameComp)
			+ " member=" + T4BB(member)
			+ " donorStorageSame=" + T4BB(dStorageSame)
			+ " wpnSame=" + T4BB(wpnSame)
			+ " targetInstalled=" + T4BB(targetInstalled)
			+ " muzzleSame=" + T4BB(muzzleSame)
			+ " chamberSame=" + T4BB(chamberSame)
			+ " barrelSame=" + T4BB(barrelSame)
			+ " typesSame=" + T4BB(typesSame)
			+ " srv=" + srv.ToString(), LogLevel.NORMAL);

		if (!allOk)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] op=" + m_dOp.ToString()
				+ " phase=late-quarantine ev=delayed-mismatch srv=" + srv.ToString(), LogLevel.NORMAL);
		}
	}
}
