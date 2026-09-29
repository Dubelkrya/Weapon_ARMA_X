# AKM Stock Slot Audit (READ ONLY)

- AKM_STOCK_SLOT: instance `65AE4CB5E23C0F63`, AttachmentType `AttachmentStockVz58`, PivotID `slot_barrel_muzzle`, Enabled 1, origin LOCAL_ADDITION, no default at base.
- Parent chain `Rifle_Base.et` -> `Weapon_Base.et` exposes no attachment slots => LOCAL_ADDITION (not override).
- Matching attachment prefab: `Prefabs/Weapons/Attachments/Stocks/armst_Stock_akm.et` (GUID B0E764B069F6A153, outer `AttachmentStockVz58`, inherits Stock_VZ58_base).
- CHILD_VARIANT_USAGE: AKM.et (default armst_Stock_akm.et), AKMS.et (default Stock_VZ58_folding.et), VPO136.et (default Stock_akm.et); SOC94 override frozen.
- ACTION_CONTEXT_USAGE: none tied to the stock slot (contexts: 4 unnamed core + bayonet on `slot_barrel_muzzle`).
- PHYSICAL_ROLE: VALID_AKM_STOCK_INTERFACE (base model `akm_weapons_nonstock.xob`; stock is an attachable part actively defaulted by base AKM variants).
- SLOT_CLASSIFICATION: KEEP (KEEP_VARIANT_HOOK) — removal candidate criteria fail because children override the instance and set defaults.
- Anomalies: pivot mis-assignment + VZ58-borrowed type naming (informational; no mutation).

LIVE_FILES_CHANGED: NONE
