// ============================================================================
// ARMST MP-133 T4b - G3B2 one-round transfer action (LAB, WRITE-DISABLED BY DEFAULT)
// ----------------------------------------------------------------------------
// Existing addon ARMSTMP133T4B_InstalledMagProbe, branch t4b/installed-mag-probe.
// G3-B2 scope: ONE manual, lab-only, no-R operation that moves exactly one round from ONE
// genuine carried donor magazine into the SAME already-installed MP-133 magazine, with a
// one-act = one-round transaction state machine (repeatable per action; in-flight latch, quarantined
// partial failure and correlated telemetry).
//
// Source of truth: reports/MP133_V3_G3B2_TRANSACTION_DESIGN.md (rev 2, approved) plus review
// conditions in Issue #34 comments 5973770796, 5973836821, 5973901925 and 5973988068.
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
// COMPILER NOTE (rev 4): `PerformAction` was over the EnforceScript 64-local limit and the
// prewrite boundary was a single "Formula too complex" expression. The operation context now
// lives in member fields and the transaction runs in small named phases. Every boolean gate is
// combined sequentially (`ok = ok && ...`) instead of one large expression. All safety checks
// from the design and prior reviews are preserved.
//
// Canonical serialized property spelling: `m_bG3B2WriteEnabled`, `m_sG3B2AllowedStorageOwner`,
// `m_iG3B2AllowedStorageSlot` - identical in script and prefab.
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
	// ---- per-instance transaction state ----
	protected bool m_b2Latch = false;        // in-flight guard: set BEFORE the first B2 setter; cleared
	                                        // only after BOTH delayed samples pass for the same op
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

	// ---- operation context (captured once per invocation; keeps PerformAction small) ----
	protected IEntity m_opUser;
	protected IEntity m_opActionOwner;
	protected BaseWeaponComponent m_opWeapon;
	protected SCR_InventoryStorageManagerComponent m_opInv;
	protected BaseMagazineComponent m_opTargetMag;
	protected IEntity m_opTargetEnt;
	protected ResourceName m_opRefType;
	protected int m_opTAmmo = -1;
	protected int m_opTMax = -1;
	protected BaseMuzzleComponent m_opMuzzle;
	protected bool m_opCh = false;
	protected int m_opBarrel = -1;
	protected int m_opBarrels = -1;
	protected int m_opSupply = -1;
	protected int m_opSupplyMax = -1;
	protected string m_opRejectReason = "";
	protected bool m_opExactOwnerMatch = false;
	protected bool m_opInventoryOwnerValid = false;
	protected bool m_opStorageSnapshotValid = false;

	// ---- donor boundary snapshot (captured immediately before the first setter) ----
	protected IEntity m_opDonorItem;
	protected BaseMagazineComponent m_opDonorMag;
	protected int m_opDonorAmmo = -1;
	protected int m_opDonorMax = -1;
	protected InventoryStorageSlot m_opSlot;
	protected BaseInventoryStorageComponent m_opStorage;
	protected IEntity m_opStorageOwner;
	protected int m_opSlotId = -1;

	// ---- results ----
	protected int m_opDonorAfter = -1;
	protected int m_opTargetAfter = -1;

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
	// Repeatable-transfer state: the +250 ms sample result for the CURRENT captured op, the count of
	// accepted delayed samples, and the op id currently scheduled (guards stale/duplicate callbacks).
	protected bool m_dSample250Ok = false;
	protected int m_dSamples = 0;
	protected int m_dScheduledOp = 0;

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

	// Opt-in inventory-wide donor search (default OFF = legacy whitelist behavior). When true, the
	// whitelist/slot are ignored and any magazine that is GENUINELY owned by the invoking actor's
	// inventory (nested pouches/backpack included), with a valid slot/storage/owner, is accepted;
	// weapon-installed and weapon-storage magazines stay excluded. Write-ON for this mode is NOT
	// authorized in this task.
	[Attribute("false", UIWidgets.CheckBox, "G3B2INV search donors across the whole character inventory (ignores the whitelist/slot)")]
	bool m_bG3B2InventoryWide = false;

	// ========================================================================
	// Init / UI
	// ========================================================================

	override void Init(IEntity pOwnerEntity, GenericComponent pManagerComponent)
	{
		Print("[ARMST_T4B-G3B2] #0 op=0 phase=action-init ev=register writeEnabled=" + T4BB(m_bG3B2WriteEnabled)
			+ " inventoryWide=" + T4BB(m_bG3B2InventoryWide)
			+ " storagePolicy=" + T4B2StoragePolicy()
			+ " whitelist=" + T4B2WL() + " allowedSlot=" + m_iG3B2AllowedStorageSlot.ToString()
			+ " srv=" + T4B2Srv() + " note=t4b-probe-baseline-setammo-is-separate-setup", LogLevel.NORMAL);
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
			outName = "Lab G3B2: write ENABLED - performs one one-round donor->installed transfer per action with the transaction machine (repeatable after +1s verified).";
		else
			outName = "Lab G3B2: read-only preflight only; performs the one-round donor->installed transfer only when the write gate is enabled.";
		return true;
	}

	override bool CanBeShownScript(IEntity user)		{ return true; }
	override bool CanBePerformedScript(IEntity user)	{ return true; }
	override event bool HasLocalEffectOnlyScript()		{ return false; }
	override event bool CanBroadcastScript()			{ return true; }

	// ========================================================================
	// Small helpers
	// ========================================================================

	string T4BB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	string T4B2Srv()
	{
		if (Replication.IsServer())
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

	// Strips a leading "{GUID}" token so a "{GUID}path" and a bare "path" compare equal.
	string T4B2NormalizePrefab(string s)
	{
		if (s == "")
			return s;
		if (!s.StartsWith("{"))
			return s;
		int close = s.IndexOf("}");
		if (close < 0)
			return s;
		return s.Substring(close + 1, s.Length() - close - 1);
	}

	// Minimal syntactic GUID check: exactly 16 hex digits (both cases).
	bool T4B2IsHexGuid(string s)
	{
		if (s.Length() != 16)
			return false;
		string hex = "0123456789ABCDEFabcdef";
		for (int i = 0; i < 16; i++)
		{
			if (hex.IndexOf(s.Substring(i, 1)) < 0)
				return false;
		}
		return true;
	}

	// STRICT write-path identity: the whitelist value MUST be the full "{GUID}path" form with a
	// syntactically valid 16-hex-digit GUID and MUST equal the engine's actual storage-owner resource
	// string EXACTLY (GUID and path). Fail closed on empty/bare/malformed value, missing resource, or
	// uncertain API. Not used for OFF read-only diagnostics (which keep the lenient normalized match
	// in T4B2StorageAllowed).
	bool T4B2OwnerExactName(IEntity item)
	{
		if (item == null)
			return false;
		if (m_sG3B2AllowedStorageOwner == "")
			return false;
		if (!m_sG3B2AllowedStorageOwner.StartsWith("{"))
			return false;
		int close = m_sG3B2AllowedStorageOwner.IndexOf("}");
		if (close <= 1)
			return false;
		if (close + 1 >= m_sG3B2AllowedStorageOwner.Length())
			return false;
		if (!T4B2IsHexGuid(m_sG3B2AllowedStorageOwner.Substring(1, close - 1)))
			return false;
		BaseInventoryStorageComponent st = T4B2StorageOf(item);
		if (!st)
			return false;
		IEntity se = st.GetOwner();
		if (!se || !se.GetPrefabData())
			return false;
		string ownerRaw = se.GetPrefabData().GetPrefabName();
		if (ownerRaw != m_sG3B2AllowedStorageOwner)
			return false;
		return true;
	}

	string T4B2StoragePolicy()
	{
		if (m_bG3B2InventoryWide)
			return "inventory-wide";
		return "whitelist";
	}

	string T4B2ExactField()
	{
		if (m_bG3B2InventoryWide)
			return "N/A";
		return T4BB(m_opExactOwnerMatch);
	}

	// Inventory-wide ownership proof: the item is genuinely in THIS actor's inventory manager and
	// its slot/storage/owner resolve. World/vicinity/ground items are not contained by the actor's
	// inventory manager, so they fail closed here.
	bool T4B2InventoryOwnerValid(IEntity item)
	{
		if (!m_opInv || !item)
			return false;
		if (!m_opInv.Contains(item))
			return false;
		return T4B2StorageSnapshotValid(item);
	}

	bool T4B2StorageSnapshotValid(IEntity item)
	{
		if (!item)
			return false;
		InventoryStorageSlot slot = T4B2SlotOf(item);
		if (!slot)
			return false;
		BaseInventoryStorageComponent st = slot.GetStorage();
		if (!st)
			return false;
		IEntity se = st.GetOwner();
		if (!se)
			return false;
		return true;
	}

	// Storage gate. whitelist mode (default): exact storage-owner path + optional slot (fail-closed on
	// empty whitelist). inventory-wide mode: any resolvable slot/storage/owner is accepted here; the
	// actor-ownership and weapon-storage exclusions are enforced separately.
	bool T4B2StorageAllowed(IEntity item, out int outSlotId, out string outOwnerPrefab)
	{
		outSlotId = -1;
		outOwnerPrefab = "";
		if (!item)
			return false;
		if (!m_bG3B2InventoryWide && m_sG3B2AllowedStorageOwner == "")
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
		if (m_bG3B2InventoryWide)
			return true;
		if (T4B2NormalizePrefab(outOwnerPrefab) != T4B2NormalizePrefab(m_sG3B2AllowedStorageOwner))
			return false;
		if (m_iG3B2AllowedStorageSlot >= 0 && outSlotId != m_iG3B2AllowedStorageSlot)
			return false;
		return true;
	}

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

	void T4B2Quarantine(string reason, string opTag)
	{
		m_b2Quarantined = true;
		Print("[ARMST_T4B-G3B2] " + opTag + " phase=indeterminate ev=" + reason + " srv=" + T4B2Srv(), LogLevel.NORMAL);
		Print("[ARMST_T4B-G3B2] " + opTag + " phase=quarantine ev=stop-no-retry srv=" + T4B2Srv(), LogLevel.NORMAL);
	}

	// ========================================================================
	// Read-only classification + donor selection (NO setter)
	// ========================================================================
	void T4B2Scan()
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
		T4B2Collect(m_opInv, items);
		array<BaseMagazineComponent> instMags = new array<BaseMagazineComponent>();
		array<IEntity> instEnts = new array<IEntity>();
		T4B2InstalledSet(m_opUser, instMags, instEnts);

		Print("[ARMST_T4B-G3B2] phase=classify-start ev=items total=" + items.Count().ToString()
			+ " refAmmoType=" + m_opRefType
			+ " storagePolicy=" + T4B2StoragePolicy()
			+ " whitelist=" + T4B2WL()
			+ " allowedSlot=" + m_iG3B2AllowedStorageSlot.ToString(), LogLevel.NORMAL);

		int shown = 0;
		foreach (IEntity it : items)
		{
			BaseMagazineComponent mag = T4B2MagOf(it);
			if (!mag)
				continue;
			m_cWithMag++;
			if (mag == m_opTargetMag || it == m_opTargetEnt)
			{
				m_cTargetSkipped++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=target-excluded " + T4B2DonorState(m_opInv, it, mag), LogLevel.NORMAL);
				continue;
			}
			bool isInstalled = T4B2InMags(instMags, mag);
			isInstalled = isInstalled || T4B2InEnts(instEnts, it);
			if (isInstalled)
			{
				m_cInstalledExcluded++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=installed-in-weapon " + T4B2DonorState(m_opInv, it, mag), LogLevel.NORMAL);
				continue;
			}
			if (T4B2StorageIsWeapon(it))
			{
				m_cInstalledExcluded++;
				Print("[ARMST_T4B-G3B2] phase=classify ev=storage-in-weapon " + T4B2DonorState(m_opInv, it, mag), LogLevel.NORMAL);
				continue;
			}

			// Counters below are independent of the whitelist, so the reject reason is accurate.
			int a = mag.GetAmmoCount();
			if (a > 0)
				m_cWithAmmo++;
			ResourceName at = mag.GetAmmoType(0);
			bool typeOk = (!at.IsEmpty()) && (at == m_opRefType);
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
					Print("[ARMST_T4B-G3B2] phase=classify ev=storage-not-whitelisted typeOk=" + T4BB(typeOk) + " " + T4B2DonorState(m_opInv, it, mag), LogLevel.NORMAL);
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
				Print("[ARMST_T4B-G3B2] phase=classify ev=magazine typeOk=" + T4BB(typeOk) + " " + T4B2DonorState(m_opInv, it, mag), LogLevel.NORMAL);
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
	bool T4B2Preflight()
	{
		m_opRejectReason = "";
		m_opExactOwnerMatch = false;
		m_opInventoryOwnerValid = false;
		m_opStorageSnapshotValid = false;
		ARMST_T4B_WeaponProbe probe = null;
		if (m_opActionOwner)
			probe = ARMST_T4B_WeaponProbe.Cast(m_opActionOwner.FindComponent(ARMST_T4B_WeaponProbe));
		if (!probe || !probe.IsBaselineDone())
		{
			m_opRejectReason = "baseline-not-ready";
			return false;
		}
		if (m_opRefType.IsEmpty())
		{
			m_opRejectReason = "unknown-ammo-type";
			return false;
		}
		if (m_opTMax <= 0 || m_opTAmmo < 0)
		{
			m_opRejectReason = "target-invalid-or-full";
			return false;
		}
		if (m_opTAmmo >= m_opTMax)
		{
			m_opRejectReason = "target-invalid-or-full";
			return false;
		}
		if (m_cCompat != 1)
		{
			m_opRejectReason = T4B2CompatReason();
			if (m_opRejectReason == "")
				m_opRejectReason = "no-eligible-donor";
			return false;
		}
		IEntity donorItem = m_selItem;
		BaseMagazineComponent donorMag = m_selMag;
		if (!donorItem || !donorMag)
		{
			m_opRejectReason = "no-donor";
			return false;
		}
		if (donorMag == m_opTargetMag || donorItem == m_opTargetEnt)
		{
			m_opRejectReason = "donor-is-target";
			return false;
		}
		// Diagnostics: strict whitelist identity + inventory-wide ownership/storage proof.
		m_opExactOwnerMatch = T4B2OwnerExactName(donorItem);
		m_opInventoryOwnerValid = T4B2InventoryOwnerValid(donorItem);
		m_opStorageSnapshotValid = T4B2StorageSnapshotValid(donorItem);
		// Inventory-wide mode requires genuine actor-inventory ownership (fail closed).
		if (m_bG3B2InventoryWide && !m_opInventoryOwnerValid)
		{
			m_opRejectReason = "inventory-owner-unverified";
			return false;
		}
		int dMax = donorMag.GetMaxAmmoCount();
		int dAmmo = donorMag.GetAmmoCount();
		if (dMax <= 0 || dAmmo <= 0)
		{
			m_opRejectReason = "donor-bounds";
			return false;
		}
		if (dAmmo > dMax)
		{
			m_opRejectReason = "donor-bounds";
			return false;
		}
		if (donorMag.GetOwner() != donorItem)
		{
			m_opRejectReason = "not-owned";
			return false;
		}
		if (!m_opInv.Contains(donorItem))
		{
			m_opRejectReason = "not-owned";
			return false;
		}
		if (T4B2StorageIsWeapon(donorItem))
		{
			m_opRejectReason = "donor-installed-in-weapon";
			return false;
		}
		int sid = -1;
		string owner = "";
		if (!T4B2StorageAllowed(donorItem, sid, owner))
		{
			m_opRejectReason = "no-permitted-storage";
			return false;
		}
		array<BaseMagazineComponent> instMags = new array<BaseMagazineComponent>();
		array<IEntity> instEnts = new array<IEntity>();
		T4B2InstalledSet(m_opUser, instMags, instEnts);
		if (T4B2InMags(instMags, donorMag) || T4B2InEnts(instEnts, donorItem))
		{
			m_opRejectReason = "donor-installed-in-weapon";
			return false;
		}
		ResourceName donorType = donorMag.GetAmmoType(0);
		if (donorType.IsEmpty())
		{
			m_opRejectReason = "ammo-type-mismatch";
			return false;
		}
		if (donorType != m_opRefType)
		{
			m_opRejectReason = "ammo-type-mismatch";
			return false;
		}
		if (!m_opMuzzle)
		{
			m_opRejectReason = "no-barrel-component";
			return false;
		}
		if (m_opBarrel < 0 || m_opBarrels <= 0)
		{
			m_opRejectReason = "no-barrel-component";
			return false;
		}
		if (m_opBarrel >= m_opBarrels)
		{
			m_opRejectReason = "no-barrel-component";
			return false;
		}
		BaseWeaponComponent wpnNow = T4B2CurrentWeapon(m_opUser);
		if (!wpnNow)
		{
			m_opRejectReason = "weapon-context-changed";
			return false;
		}
		if (wpnNow != m_opWeapon)
		{
			m_opRejectReason = "weapon-context-changed";
			return false;
		}
		if (m_opWeapon.GetCurrentMagazine() != m_opTargetMag)
		{
			m_opRejectReason = "target-changed";
			return false;
		}
		if (m_opTargetMag.GetOwner() != m_opTargetEnt)
		{
			m_opRejectReason = "target-changed";
			return false;
		}
		if (m_opTargetMag.GetAmmoCount() != m_opTAmmo)
		{
			m_opRejectReason = "target-changed";
			return false;
		}
		return true;
	}

	// ========================================================================
	// Transaction phases (each small, sequential gates, no giant formulas)
	// ========================================================================

	// Read-only boundary immediately before the first setter. Named sequential gates.
	bool T4B2Boundary()
	{
		m_opRejectReason = "";
		m_opDonorItem = m_selItem;
		m_opDonorMag = m_selMag;
		m_opDonorAmmo = -1;
		m_opDonorMax = -1;
		m_opSlot = null;
		m_opStorage = null;
		m_opStorageOwner = null;
		m_opSlotId = -1;

		// Gate 1: authenticated donor storage/owner/slot + whitelist.
		string storageOwnerOut = "";
		bool allowed = T4B2StorageAllowed(m_opDonorItem, m_opSlotId, storageOwnerOut);
		InventoryStorageSlot slot = T4B2SlotOf(m_opDonorItem);
		BaseInventoryStorageComponent storage = T4B2StorageOf(m_opDonorItem);
		IEntity storageOwner = null;
		if (storage)
			storageOwner = storage.GetOwner();
		if (!allowed || slot == null || storage == null || storageOwner == null)
		{
			m_opRejectReason = "prewrite-storage";
			return false;
		}

		// Mode-specific storage identity at the prewrite boundary.
		if (m_bG3B2InventoryWide)
		{
			// Inventory-wide: require genuine actor-inventory ownership + captured snapshot.
			if (!T4B2InventoryOwnerValid(m_opDonorItem))
			{
				m_opRejectReason = "prewrite-storage-owner";
				return false;
			}
		}
		else
		{
			// Whitelist mode: require the full {GUID}path exact match (fail closed).
			if (!T4B2OwnerExactName(m_opDonorItem))
			{
				m_opRejectReason = "prewrite-storage-exact";
				return false;
			}
		}

		// Gate 2: donor identity + membership + not inside a weapon.
		m_opDonorAmmo = m_opDonorMag.GetAmmoCount();
		m_opDonorMax = m_opDonorMag.GetMaxAmmoCount();
		bool gateMember = (m_opDonorMag.GetOwner() == m_opDonorItem);
		gateMember = gateMember && m_opInv.Contains(m_opDonorItem);
		gateMember = gateMember && (T4B2MagOf(m_opDonorItem) == m_opDonorMag);
		gateMember = gateMember && (!T4B2StorageIsWeapon(m_opDonorItem));
		if (!gateMember)
		{
			m_opRejectReason = "prewrite-member";
			return false;
		}

		// Gate 3: donor/target ammo types.
		ResourceName donorType = m_opDonorMag.GetAmmoType(0);
		ResourceName targetType = m_opTargetMag.GetAmmoType(0);
		if (donorType.IsEmpty() || donorType != m_opRefType)
		{
			m_opRejectReason = "prewrite-type";
			return false;
		}
		if (targetType.IsEmpty() || targetType != m_opRefType)
		{
			m_opRejectReason = "prewrite-type";
			return false;
		}

		// Gate 4: donor ammo bounds.
		if (m_opDonorMax <= 0 || m_opDonorAmmo <= 0 || m_opDonorAmmo > m_opDonorMax)
		{
			m_opRejectReason = "prewrite-bounds";
			return false;
		}

		// Gate 5: same actor's currently-equipped (action) weapon.
		BaseWeaponComponent wpnB = T4B2CurrentWeapon(m_opUser);
		if (!wpnB || wpnB != m_opWeapon)
		{
			m_opRejectReason = "prewrite-weapon";
			return false;
		}

		// Gate 6: same captured muzzle.
		BaseMuzzleComponent muzzleB = null;
		if (m_opWeapon)
			muzzleB = m_opWeapon.GetCurrentMuzzle();
		if (!muzzleB || muzzleB != m_opMuzzle)
		{
			m_opRejectReason = "prewrite-muzzle";
			return false;
		}

		// Gate 7: same still-installed target.
		if (m_opWeapon.GetCurrentMagazine() != m_opTargetMag)
		{
			m_opRejectReason = "prewrite-target";
			return false;
		}
		if (m_opTargetMag.GetOwner() != m_opTargetEnt)
		{
			m_opRejectReason = "prewrite-target";
			return false;
		}
		if (m_opTargetMag.GetAmmoCount() != m_opTAmmo)
		{
			m_opRejectReason = "prewrite-target";
			return false;
		}

		m_opSlot = slot;
		m_opStorage = storage;
		m_opStorageOwner = storageOwner;
		return true;
	}

	// After donor-1: same donor component/owner/member, same storage component+owner+slot, type.
	bool T4B2AfterDonor()
	{
		m_opDonorAfter = m_opDonorMag.GetAmmoCount();
		bool countOk = (m_opDonorAfter == m_opDonorAmmo - 1);
		bool ownerOk = (m_opDonorMag.GetOwner() == m_opDonorItem);
		bool memberOk = m_opInv.Contains(m_opDonorItem);
		bool compOk = (T4B2MagOf(m_opDonorItem) == m_opDonorMag);
		BaseInventoryStorageComponent storageNow = T4B2StorageOf(m_opDonorItem);
		IEntity storageOwnerNow = null;
		if (storageNow)
			storageOwnerNow = storageNow.GetOwner();
		bool storageOk = (storageNow != null) && (storageNow == m_opStorage);
		storageOk = storageOk && (storageOwnerNow == m_opStorageOwner);
		InventoryStorageSlot slotNow = T4B2SlotOf(m_opDonorItem);
		bool slotOk = (slotNow != null) && (slotNow.GetID() == m_opSlotId);
		ResourceName typeNow = m_opDonorMag.GetAmmoType(0);
		bool typeOk = (!typeNow.IsEmpty()) && (typeNow == m_opRefType);

		bool ok = countOk;
		ok = ok && ownerOk;
		ok = ok && memberOk;
		ok = ok && compOk;
		ok = ok && storageOk;
		ok = ok && slotOk;
		ok = ok && typeOk;

		Print("[ARMST_T4B-G3B2] " + m_i2Seq.ToString() + " op=" + m_i2OpId.ToString()
			+ " phase=donor-post ev=set want=" + (m_opDonorAmmo - 1).ToString()
			+ " got=" + m_opDonorAfter.ToString()
			+ " donorOk=" + T4BB(ok)
			+ " compOk=" + T4BB(compOk)
			+ " storageOk=" + T4BB(storageOk)
			+ " slotOk=" + T4BB(slotOk)
			+ " typeOk=" + T4BB(typeOk)
			+ " srv=" + T4B2Srv()
			+ " " + T4B2DonorState(m_opInv, m_opDonorItem, m_opDonorMag), LogLevel.NORMAL);
		return ok;
	}

	// Between setters: same equipped weapon, target still installed, same muzzle/chamber, storage.
	bool T4B2Between()
	{
		BaseWeaponComponent wpnMid = T4B2CurrentWeapon(m_opUser);
		BaseMuzzleComponent muzzleMid = null;
		if (wpnMid)
			muzzleMid = wpnMid.GetCurrentMuzzle();
		if (!wpnMid || !muzzleMid)
			return false;

		bool wpnOk = (wpnMid == m_opWeapon);
		bool targetOk = (wpnMid.GetCurrentMagazine() == m_opTargetMag);
		targetOk = targetOk && (m_opTargetMag.GetOwner() == m_opTargetEnt);
		bool muzzleOk = (muzzleMid == m_opMuzzle);
		bool chamberOk = (muzzleMid.IsCurrentBarrelChambered() == m_opCh);
		chamberOk = chamberOk && (muzzleMid.GetCurrentBarrelIndex() == m_opBarrel);
		chamberOk = chamberOk && (muzzleMid.GetBarrelsCount() == m_opBarrels);
		bool countOk = (m_opTargetMag.GetAmmoCount() == m_opTAmmo);
		BaseInventoryStorageComponent storageMid = T4B2StorageOf(m_opDonorItem);
		bool storageOk = (storageMid != null) && (storageMid == m_opStorage);

		bool ok = wpnOk;
		ok = ok && targetOk;
		ok = ok && muzzleOk;
		ok = ok && chamberOk;
		ok = ok && countOk;
		ok = ok && storageOk;
		return ok;
	}

	// After target+1: same equipped weapon, target still installed, count, same muzzle.
	bool T4B2AfterTarget()
	{
		m_opTargetAfter = m_opTargetMag.GetAmmoCount();
		BaseWeaponComponent wpnEnd = T4B2CurrentWeapon(m_opUser);
		BaseMuzzleComponent muzzleEnd = null;
		if (wpnEnd)
			muzzleEnd = wpnEnd.GetCurrentMuzzle();
		bool wpnOk = (wpnEnd != null) && (wpnEnd == m_opWeapon);
		bool installed = wpnOk && (wpnEnd.GetCurrentMagazine() == m_opTargetMag);
		bool countOk = (m_opTargetAfter == m_opTAmmo + 1);
		bool ownerOk = (m_opTargetMag.GetOwner() == m_opTargetEnt);
		bool muzzleOk = (muzzleEnd != null) && (muzzleEnd == m_opMuzzle);

		bool ok = countOk;
		ok = ok && wpnOk;
		ok = ok && installed;
		ok = ok && ownerOk;
		ok = ok && muzzleOk;

		Print("[ARMST_T4B-G3B2] " + m_i2Seq.ToString() + " op=" + m_i2OpId.ToString()
			+ " phase=target-post ev=set want=" + (m_opTAmmo + 1).ToString()
			+ " got=" + m_opTargetAfter.ToString()
			+ " targetOk=" + T4BB(ok)
			+ " wpnOk=" + T4BB(wpnOk)
			+ " muzzleOk=" + T4BB(muzzleOk)
			+ " srv=" + T4B2Srv()
			+ " target=" + T4B2DonorState(m_opInv, m_opTargetEnt, m_opTargetMag), LogLevel.NORMAL);
		return ok;
	}

	// Final: live conservation + full donor re-check AFTER the second setter + target/chamber.
	bool T4B2Commit()
	{
		bool conserv = ((m_opDonorAmmo + m_opTAmmo) == (m_opDonorAfter + m_opTargetAfter));

		// Final donor re-check using LIVE values after the target write.
		BaseMagazineComponent donorMagNow = T4B2MagOf(m_opDonorItem);
		bool donorCompOk = (donorMagNow == m_opDonorMag);
		bool donorOwnerOk = (m_opDonorMag.GetOwner() == m_opDonorItem);
		bool donorMemberOk = m_opInv.Contains(m_opDonorItem);
		bool donorCountOk = (m_opDonorMag.GetAmmoCount() == m_opDonorAfter);
		ResourceName donorTypeNow = m_opDonorMag.GetAmmoType(0);
		bool donorTypeOk = (!donorTypeNow.IsEmpty()) && (donorTypeNow == m_opRefType);
		BaseInventoryStorageComponent donorStorageNow = T4B2StorageOf(m_opDonorItem);
		IEntity donorStorageOwnerNow = null;
		if (donorStorageNow)
			donorStorageOwnerNow = donorStorageNow.GetOwner();
		bool donorStorageOk = (donorStorageNow != null) && (donorStorageNow == m_opStorage);
		donorStorageOk = donorStorageOk && (donorStorageOwnerNow == m_opStorageOwner);
		InventoryStorageSlot donorSlotNow = T4B2SlotOf(m_opDonorItem);
		bool donorSlotOk = (donorSlotNow != null) && (donorSlotNow.GetID() == m_opSlotId);
		bool donorDistinct = (m_opDonorMag != m_opTargetMag) && (m_opDonorItem != m_opTargetEnt);

		// Target re-check.
		BaseWeaponComponent wpnEnd = T4B2CurrentWeapon(m_opUser);
		BaseMuzzleComponent muzzleEnd = null;
		if (wpnEnd)
			muzzleEnd = wpnEnd.GetCurrentMuzzle();
		bool wpnOk = (wpnEnd != null) && (wpnEnd == m_opWeapon);
		bool targetInstalled = wpnOk && (wpnEnd.GetCurrentMagazine() == m_opTargetMag);
		targetInstalled = targetInstalled && (m_opTargetMag.GetOwner() == m_opTargetEnt);
		ResourceName targetTypeNow = m_opTargetMag.GetAmmoType(0);
		bool targetTypeOk = (!targetTypeNow.IsEmpty()) && (targetTypeNow == m_opRefType);
		bool muzzleIdOk = (muzzleEnd != null) && (muzzleEnd == m_opMuzzle);
		bool chamberOk = false;
		if (muzzleEnd)
		{
			chamberOk = (muzzleEnd.IsCurrentBarrelChambered() == m_opCh);
			chamberOk = chamberOk && (muzzleEnd.GetCurrentBarrelIndex() == m_opBarrel);
			chamberOk = chamberOk && (muzzleEnd.GetBarrelsCount() == m_opBarrels);
		}

		bool ok = conserv;
		ok = ok && donorCompOk;
		ok = ok && donorOwnerOk;
		ok = ok && donorMemberOk;
		ok = ok && donorCountOk;
		ok = ok && donorTypeOk;
		ok = ok && donorStorageOk;
		ok = ok && donorSlotOk;
		ok = ok && donorDistinct;
		ok = ok && wpnOk;
		ok = ok && targetInstalled;
		ok = ok && targetTypeOk;
		ok = ok && muzzleIdOk;
		ok = ok && chamberOk;
		return ok;
	}

	void T4B2ScheduleDelayed()
	{
		m_dOp = m_i2OpId;
		m_dScheduledOp = m_i2OpId;
		m_dSamples = 0;
		m_dSample250Ok = false;
		m_dActor = m_opUser;
		m_dInv = m_opInv;
		m_dWeapon = m_opWeapon;
		m_dDonorMag = m_opDonorMag;
		m_dDonorItem = m_opDonorItem;
		m_dDonorWant = m_opDonorAfter;
		m_dDonorStorage = m_opStorage;
		m_dDonorStorageOwner = m_opStorageOwner;
		m_dDonorSlotId = m_opSlotId;
		m_dTargetMag = m_opTargetMag;
		m_dTargetEnt = m_opTargetEnt;
		m_dTargetWant = m_opTargetAfter;
		m_dMuzzle = m_opMuzzle;
		m_dChambered = m_opCh;
		m_dBarrel = m_opBarrel;
		m_dBarrels = m_opBarrels;
		m_dRefType = m_opRefType;
		GetGame().GetCallqueue().CallLater(T4B2Delayed250, 250, false, m_i2OpId);
		GetGame().GetCallqueue().CallLater(T4B2Delayed1000, 1000, false, m_i2OpId);
	}

	void T4B2Execute()
	{
		string opTag = m_i2Seq.ToString() + " op=" + m_i2OpId.ToString();
		if (!T4B2Boundary())
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=" + m_opRejectReason + " srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		// Single synchronous donor-first order. Latch BEFORE the first setter.
		m_b2Latch = true;
		m_opDonorMag.SetAmmoCount(m_opDonorAmmo - 1);

		if (!T4B2AfterDonor())
		{
			T4B2Quarantine("donor-post-mismatch", opTag);
			return;
		}
		if (!T4B2Between())
		{
			T4B2Quarantine("between-setters-changed", opTag);
			return;
		}

		m_opTargetMag.SetAmmoCount(m_opTAmmo + 1);

		if (!T4B2AfterTarget())
		{
			T4B2Quarantine("target-post-mismatch", opTag);
			return;
		}
		if (!T4B2Commit())
		{
			T4B2Quarantine("commit-check-failed", opTag);
			return;
		}

		int supplyAfter = -1;
		BaseMuzzleComponent muzzleEnd = m_opWeapon.GetCurrentMuzzle();
		if (muzzleEnd)
			supplyAfter = muzzleEnd.GetAmmoCount();
		Print("[ARMST_T4B-G3B2] " + opTag
			+ " phase=commit ev=committed"
			+ " donorBefore=" + m_opDonorAmmo.ToString() + " donorAfter=" + m_opDonorAfter.ToString()
			+ " targetBefore=" + m_opTAmmo.ToString() + " targetAfter=" + m_opTargetAfter.ToString()
			+ " conserved=" + T4BB((m_opDonorAmmo + m_opTAmmo) == (m_opDonorAfter + m_opTargetAfter))
			+ " chamberedBefore=" + T4BB(m_opCh)
			+ " barrelBefore=" + m_opBarrel.ToString()
			+ " supplyBefore=" + m_opSupply.ToString() + " supplyAfter=" + supplyAfter.ToString()
			+ " supplyTelemetry=1"
			+ " gameplay_effect=UNVERIFIED"
			+ " srv=" + T4B2Srv(), LogLevel.NORMAL);

		T4B2ScheduleDelayed();
	}

	// ========================================================================
	// Action
	// ========================================================================
	override void PerformAction(IEntity pOwnerEntity, IEntity pUserEntity)
	{
		m_i2Seq++;
		m_i2OpId++;
		string opTag = m_i2Seq.ToString() + " op=" + m_i2OpId.ToString();

		if (m_b2Quarantined)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=quarantined srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}
		if (m_b2Latch)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=busy srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}
		if (!Replication.IsServer())
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=not-server srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		IEntity user = pUserEntity;
		if (!user)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=no-user srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		// Strict action-owner binding: the entity passed in must be this action's own owner.
		IEntity actionOwner = GetOwner();
		if (!actionOwner)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=no-action-owner srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}
		if (pOwnerEntity && pOwnerEntity != actionOwner)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=action-owner-mismatch srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		BaseWeaponComponent actionWpn = T4B2WeaponOf(actionOwner);
		if (!actionWpn)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=not-action-weapon srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}
		BaseWeaponComponent currentWpn = T4B2CurrentWeapon(user);
		if (!currentWpn || currentWpn != actionWpn)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=wrong-weapon-context srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		SCR_InventoryStorageManagerComponent inv = T4B2Inv(user);
		if (!inv)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=no-inventory srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		BaseMagazineComponent targetMag = currentWpn.GetCurrentMagazine();
		IEntity targetEnt = null;
		if (targetMag)
			targetEnt = targetMag.GetOwner();
		if (!targetMag || !targetEnt)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=no-installed-magazine srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		// Capture the operation context once.
		m_opUser = user;
		m_opActionOwner = actionOwner;
		m_opWeapon = currentWpn;
		m_opInv = inv;
		m_opTargetMag = targetMag;
		m_opTargetEnt = targetEnt;
		m_opRefType = targetMag.GetAmmoType(0);
		m_opTAmmo = targetMag.GetAmmoCount();
		m_opTMax = targetMag.GetMaxAmmoCount();
		m_opMuzzle = currentWpn.GetCurrentMuzzle();
		m_opCh = T4B2ChamberedOf(m_opMuzzle);
		m_opBarrel = -1;
		m_opBarrels = -1;
		m_opSupply = -1;
		m_opSupplyMax = -1;
		if (m_opMuzzle)
		{
			m_opBarrel = m_opMuzzle.GetCurrentBarrelIndex();
			m_opBarrels = m_opMuzzle.GetBarrelsCount();
			m_opSupply = m_opMuzzle.GetAmmoCount();
			m_opSupplyMax = m_opMuzzle.GetMaxAmmoCount();
		}

		Print("[ARMST_T4B-G3B2] " + opTag
			+ " phase=pre ev=invoked writeEnabled=" + T4BB(m_bG3B2WriteEnabled)
			+ " refAmmoType=" + m_opRefType
			+ " srv=" + T4B2Srv()
			+ " target=" + T4B2DonorState(inv, targetEnt, targetMag)
			+ " muzzle=" + T4BB(m_opMuzzle != null)
			+ " chambered=" + T4BB(m_opCh)
			+ " barrel=" + m_opBarrel.ToString() + "/" + m_opBarrels.ToString()
			+ " supply=" + m_opSupply.ToString() + "/" + m_opSupplyMax.ToString(), LogLevel.NORMAL);

		// Read-only classification.
		T4B2Scan();

		// Read-only preflight (shared): the SAME validation used by the write path.
		bool pfEligible = T4B2Preflight();
		Print("[ARMST_T4B-G3B2] " + opTag
			+ " phase=preflight ev=checked preflightEligible=" + T4BB(pfEligible)
			+ " reason=" + m_opRejectReason
			+ " storagePolicy=" + T4B2StoragePolicy()
			+ " exactOwnerMatch=" + T4B2ExactField()
			+ " inventoryOwnerValid=" + T4BB(m_opInventoryOwnerValid)
			+ " storageSnapshotValid=" + T4BB(m_opStorageSnapshotValid)
			+ " compat=" + m_cCompat.ToString()
			+ " targetSkipped=" + m_cTargetSkipped.ToString()
			+ " installedExcluded=" + m_cInstalledExcluded.ToString()
			+ " storageRejected=" + m_cStorageRejected.ToString()
			+ " srv=" + T4B2Srv(), LogLevel.NORMAL);

		if (!m_bG3B2WriteEnabled)
		{
			Print("[ARMST_T4B-G3B2] " + opTag
				+ " phase=readonly ev=preflight-only writeEnabled=0"
				+ " preflightEligible=" + T4BB(pfEligible)
				+ " reason=" + m_opRejectReason
				+ " storagePolicy=" + T4B2StoragePolicy()
				+ " exactOwnerMatch=" + T4B2ExactField()
				+ " inventoryOwnerValid=" + T4BB(m_opInventoryOwnerValid)
				+ " storageSnapshotValid=" + T4BB(m_opStorageSnapshotValid)
				+ " refAmmoType=" + m_opRefType
				+ " srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		if (!pfEligible)
		{
			Print("[ARMST_T4B-G3B2] " + opTag + " phase=reject ev=" + m_opRejectReason + " srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		T4B2Execute();
	}

	// ========================================================================
	// Delayed read-only samples (NEVER write)
	// ========================================================================
	void T4B2Delayed250(int cbOp)
	{
		T4B2DelayedSample(250, cbOp);
	}

	void T4B2Delayed1000(int cbOp)
	{
		T4B2DelayedSample(1000, cbOp);
	}

	void T4B2DelayedSample(int ms, int cbOp)
	{
		// Immutable callback-correlation gate: BEFORE reading/updating any sample state, require that
		// this callback belongs to the CURRENT scheduled operation and that the in-flight latch is
		// still held. A stale/duplicate callback (old op id, or arriving after unlock) is dropped
		// without mutating state, so it can never unlock or quarantine a newer operation.
		if (m_dOp <= 0)
			return;
		if (cbOp != m_dScheduledOp)
			return;
		if (!m_b2Latch)
			return;
		if (m_dOp != cbOp)
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
		bool dSameEnt = (dOwnerNow != null) && (dOwnerNow == m_dDonorItem);
		bool dSameComp = (m_dDonorItem != null) && (m_dDonorMag != null);
		dSameComp = dSameComp && (T4B2MagOf(m_dDonorItem) == m_dDonorMag);
		bool member = (m_dInv != null) && (m_dDonorItem != null);
		member = member && m_dInv.Contains(m_dDonorItem);
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
		bool dStorageSame = (dStorageNow != null) && (dStorageNow == m_dDonorStorage);
		dStorageSame = dStorageSame && (dStorageOwnerNow == m_dDonorStorageOwner);
		dStorageSame = dStorageSame && (dSlotIdNow == m_dDonorSlotId);

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
		bool targetInstalled = wpnSame && (installedNow != null);
		targetInstalled = targetInstalled && (installedNow == m_dTargetMag);
		targetInstalled = targetInstalled && (tOwnerNow == m_dTargetEnt);
		bool muzzleSame = (muzzleNow != null) && (muzzleNow == m_dMuzzle);
		bool chamberSame = (T4B2ChamberedOf(muzzleNow) == m_dChambered);
		bool barrelSame = false;
		if (muzzleNow)
		{
			barrelSame = (muzzleNow.GetCurrentBarrelIndex() == m_dBarrel);
			barrelSame = barrelSame && (muzzleNow.GetBarrelsCount() == m_dBarrels);
		}

		// Ammo-type invariance (full delayed scope, not only count/location).
		ResourceName dTypeNow = ResourceName.Empty;
		ResourceName tTypeNow = ResourceName.Empty;
		if (m_dDonorMag)
			dTypeNow = m_dDonorMag.GetAmmoType(0);
		if (m_dTargetMag)
			tTypeNow = m_dTargetMag.GetAmmoType(0);
		bool typesSame = (!dTypeNow.IsEmpty()) && (dTypeNow == m_dRefType);
		typesSame = typesSame && (!tTypeNow.IsEmpty()) && (tTypeNow == m_dRefType);

		bool allOk = dPersist;
		allOk = allOk && tPersist;
		allOk = allOk && dSameEnt;
		allOk = allOk && dSameComp;
		allOk = allOk && member;
		allOk = allOk && dStorageSame;
		allOk = allOk && wpnSame;
		allOk = allOk && targetInstalled;
		allOk = allOk && muzzleSame;
		allOk = allOk && chamberSame;
		allOk = allOk && barrelSame;
		allOk = allOk && typesSame;

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
			+ " srv=" + T4B2Srv(), LogLevel.NORMAL);

		if (!allOk)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] op=" + m_dOp.ToString()
				+ " phase=late-quarantine ev=delayed-mismatch srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}

		// Positive sample accepted (read-only). Track each stage separately so duplicates cannot
		// satisfy the two-distinct-samples requirement. Never writes here.
		if (ms == 250)
		{
			if (!m_dSample250Ok)
			{
				m_dSample250Ok = true;
				m_dSamples++;
			}
			return;
		}

		// ms == 1000: sample accepted; require its own +250 ms sample for the SAME op.
		if (!m_dSample250Ok)
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] op=" + m_dOp.ToString()
				+ " phase=late-quarantine ev=unlock-not-verified missing250 srv=" + T4B2Srv(), LogLevel.NORMAL);
			return;
		}
		m_dSamples = 2;

		// Release the in-flight latch ONLY for the verified current op, no quarantine, server-side.
		bool sameOp = (m_dOp == m_dScheduledOp) && (m_dOp == cbOp);
		bool twoSamples = (m_dSamples >= 2);
		bool canUnlock = m_dSample250Ok;
		canUnlock = canUnlock && sameOp;
		canUnlock = canUnlock && twoSamples;
		canUnlock = canUnlock && (!m_b2Quarantined);
		canUnlock = canUnlock && Replication.IsServer();
		if (canUnlock)
		{
			m_b2Latch = false;
			m_dScheduledOp = 0;
			Print("[ARMST_T4B-G3B2] op=" + m_dOp.ToString()
				+ " phase=unlock ev=postcommit-verified samples=" + m_dSamples.ToString()
				+ " srv=" + T4B2Srv(), LogLevel.NORMAL);
		}
		else
		{
			m_b2Quarantined = true;
			Print("[ARMST_T4B-G3B2] op=" + m_dOp.ToString()
				+ " phase=late-quarantine ev=unlock-not-verified sample250ok=" + T4BB(m_dSample250Ok)
				+ " sameOp=" + T4BB(sameOp) + " samples=" + m_dSamples.ToString()
				+ " srv=" + T4B2Srv(), LogLevel.NORMAL);
		}
	}
}
