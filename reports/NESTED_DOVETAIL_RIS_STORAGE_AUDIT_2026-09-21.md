# Nested Dovetail → RIS attachment/storage audit

Date: 2026-09-21

Status: **research checkpoint / no production migration**

This report records the current live-addon and Arma Reforger 1.8.0.13 evidence for the desired hierarchy:

```
AK weapon
└─ dovetail adapter      # separate inventory item
   └─ RIS collimator     # separate inventory item
```

The hard gameplay requirement is that the adapter and collimator remain **separate items**, while the collimator can stay physically attached to the adapter when the adapter is removed from the weapon, dropped, stored, picked up and reinstalled.

## Authority and scope

Authority order remains:

1. current live addon / Workbench / runtime;
2. current engine-script evidence;
3. this report;
4. older generated indexes and policy snapshots.

Authoritative live addon:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

The repo contains older optics-policy snapshots that still describe `AttachmentOpticsARMST_DovetailRU`. For the **current live AKDovetail research path**, the effective live type is `AttachmentOpticsDovetailAK`. Do not revert the live project to the older repo snapshot from this report.

Official script evidence used here:

- `BohemiaInteractive/Arma-Reforger-Script-Diff`
- commit `3d77cc212d5cda9922daf5f45635c7300d2d4cce`
- Arma Reforger `1.8.0.13`

## Current production resources

Production adapter:

- `Prefabs/Weapons/Attachments/Optics/AKDovetailMount/armst_Optic_AKDovetailMount.et`
- GUID `D71FD2BD68AC4B31`
- parent `{0A9CD090EE3440E7}Prefabs/Weapons/Core/WeaponPart_Base.et`
- outer type: `AttachmentOpticsDovetailAK`
- model: `{18C9F66F09FF1531}Assets/addons/Dovetail/AKDovetailMount.xob`
- adapter pivots: `snap_weapon`, `snap_ris`
- inherited child slot instance: `BB6000C24BAA468F`
- child slot type: `AttachmentOpticsRIS1913`
- child slot geometry: `PivotID snap_ris`, `ChildPivotID snap_weapon`

Production collimator:

- `Prefabs/Weapons/Attachments/Optics/armst_Optic_Collimator.et`
- GUID `28DE12055E70E762`
- model: `{AE4FFD4A3655A0C4}Assets/addons/Dovetail/coll.xob`
- effective attachment type: `AttachmentOpticsRIS1913`
- model is currently frozen; no further XOB/pivot edits should be proposed without new direct evidence.

## Current single test resource

All prior Dovetail/Collimator diagnostic prefabs and the temporary custom-action script were deleted. The research branch now has one test host only:

- `Prefabs/Weapons/Attachments/Optics/Diagnostic/armst_Optic_AKDovetail_Nested_SINGLE_TEST.et`
- GUID `29B016F2EFCB883B`
- thin child of production adapter
- only architectural local addition: `SCR_WeaponAttachmentsStorageComponent`
- inherited RIS slot remains `BB6000C24BAA468F`
- no custom actions
- no test collimator
- no fake weapon-side RIS slot
- no dependency mechanism
- no fixed `SlotManager` child

The test physical profile was corrected to the Workbench-proven manual profile on the same inherited `ItemPhysicalAttributes` instance `5618897B0A38800A`:

- Weight `0.5`
- `SizeSetupStrategy Manual`
- `ItemDimensions 10 10 10`
- `ItemVolume 100`
- `RestingUP Up`
- `RestingAdditiveRotationLS 0 0 0`

Do not reopen this physical-profile issue unless runtime evidence directly implicates it.

## Proven engine facts

### 1. RIS1913 inheritance compatibility is proven

The 1.8.0.13 type hierarchy includes:

```
AttachmentOpticsRIS1913
└─ AttachmentOpticsRIS1913Medium
   └─ AttachmentOpticsRIS1913Short
      └─ AttachmentOpticsRIS1913VeryShort
```

Stock compatibility uses typename inheritance semantics. Therefore a module typed `AttachmentOpticsRIS1913Short` is compatible with a slot requiring `AttachmentOpticsRIS1913`.

This is no longer an unresolved compatibility question.

### 2. Stock weapon attachment actions are weapon-centric

`SCR_AttachItemFromInventoryAction` and `SCR_EquipWeaponAttachment` resolve the current weapon and operate on storage attached to the weapon entity.

Therefore adding more normal attachment actions to the adapter does **not** make the adapter's child slot the standard action target.

This is why further `ActionsManager` patching is not the correct first response to a nested-host failure.

### 3. No vanilla attachment-host prefab was found

A full scan of the available vanilla attachment snapshot found no proven stock prefab that is simultaneously:

- a normal inventory weapon attachment; and
- a host for another weapon attachment.

Vanilla attachment prefabs found in the snapshot behave as leaves. Proven attachment hosting is on weapon entities.

This proves **absence of a known stock prefab pattern**, not impossibility in the engine.

### 4. `SCR_WeaponAttachmentsStorageComponent` does not script-create slots

The script-side `SCR_WeaponAttachmentsStorageComponent` adds:

- required/obstructed attachment-type checks;
- active-type tracking;
- add/remove callbacks;
- dependency cleanup via `RemoveNestedAttachments()`.

Its script body does not show slot construction. Slot ownership/discovery remains native.

### 5. Stock dependency behavior is real but is not the desired product model

`SCR_WeaponAttachmentObstructionAttributes` provides:

- required attachment types;
- obstructed attachment types.

`SCR_WeaponAttachmentsStorageComponent` tracks active types and can remove dependent attachments when a required type disappears.

This supports a stock **weapon-side sibling-slot dependency** model, but that model was rejected for this feature because the desired result is true adapter → collimator nesting.

### 6. Inspection UI is not the target architecture

The inventory UI method:

```
CanInspectItemInInventory(item, iic)
```

checks whether the item has an `SCR_WeaponAttachmentsStorageComponent`.

`InspectWeapon()` then builds `SCR_InventoryGearInspectionPointUI` from the storage's slots.

This explains the weapon inspection view, but inspection UI/context is not the gameplay contract we need. The required nested relationship must work even without treating the adapter as a small weapon UI.

### 7. `InventoryStorageSlot` is a physical slot object

This is the most important correction to the earlier “generic storage is grid-only” conclusion.

In 1.8.0.13:

```
InventoryStorageSlot : EntitySlotInfo
```

and `EntitySlotInfo` exposes physical slot behavior including:

- `GetAttachedEntity()`
- `AttachEntity(IEntity)`
- `DetachEntity(...)`
- local/world transform access
- pivot/node information

Official weapon sample serialization also uses:

```
AttachmentSlotComponent
└─ AttachmentSlot InventoryStorageSlot
   ├─ PivotID "slot_optics"
   └─ ChildPivotID "..."
```

Therefore an inventory slot can participate in real parent/child transform semantics. It is not merely a UI grid cell.

### 8. Storage slot registration hooks are proven to exist

`BaseInventoryStorageComponent` derives from `InventoryItemComponent` and exposes protected native hooks:

```
SetupSlotHooks(InventoryStorageSlot ownedSlot, int slotID)
ReleaseSlotHooks(InventoryStorageSlot ownedSlot)
```

It also exposes the script extension points:

```
GetSlotsCountScr()
GetSlotScr(int slotID)
GetEmptySlotForItem(...)
CanStoreItem(...)
InsertItem(...)
RemoveItem(...)
```

These APIs strongly indicate that a custom storage can register owned `InventoryStorageSlot` instances, but the exact construction/serialization pattern for one custom pivot-bearing slot is still not demonstrated by a source example.

## Corrected conclusions

The following statements are **not** safe to treat as proven:

- “nested physical attachment is impossible in stock Enfusion”;
- “generic storage can only store and can never physically attach”;
- “`WeaponComponent` is mandatory for any storage/slot physical relationship”;
- “a root-level `AttachmentSlotComponent` can never be registered to a custom storage”.

What is proven is narrower:

- there is no known vanilla attachment-host prefab example;
- stock weapon actions target the weapon;
- stock weapon attachment storage slot discovery is native;
- our current single test did not produce the desired user-facing behavior;
- `InventoryStorageSlot` itself has physical entity-slot semantics;
- custom storage slot registration hooks exist.

## Historical POC results

### Composite assembly

A fixed-child `SlotManager` POC proved structurally that the dovetail mount and collimator can behave as one item.

This path is **not acceptable for production** because separate item identity is a hard requirement.

### Weapon-side RIS + dependency

A weapon-side sibling-slot POC using `SCR_WeaponAttachmentObstructionAttributes` validated statically.

This remains a technically valid stock fallback, but it is **not the desired model** because the collimator is not actually stored on the adapter.

### Adapter-owned `SCR_WeaponAttachmentsStorageComponent`

The current single test adds this storage to the adapter while keeping the inherited RIS `AttachmentSlotComponent`.

Static structure is valid, but slot ownership/discovery on a non-weapon host is not proven. Do not infer success or impossibility from the component merely appearing in Workbench.

## Current architectural target

Because separate item identity is mandatory, the most promising target is now a **custom one-slot adapter storage**:

```
AK weapon storage
└─ adapter item
   └─ adapter-owned storage
      └─ InventoryStorageSlot
         └─ collimator item
```

Required properties:

- adapter remains an `AttachmentOpticsDovetailAK` item;
- collimator remains a separate RIS item;
- nested slot accepts only RIS1913-family optics;
- parent pivot: `snap_ris`;
- child pivot: `snap_weapon`;
- child remains the same entity when inserted/removed;
- removing/moving/dropping the adapter preserves the child relation;
- no weapon-side fake RIS slot;
- no composite/fixed child;
- no dependency workaround.

## Main unresolved technical question

The decisive unknown is **slot ownership/construction**, not compatibility.

We still need a proven pattern for one of these two shapes:

### Shape A — storage owns a pivot-bearing InventoryStorageSlot directly

```
ARMST_DovetailOpticStorageComponent
└─ InventoryStorageSlot
   ├─ PivotID snap_ris
   └─ ChildPivotID snap_weapon
```

### Shape B — existing AttachmentSlotComponent remains the slot holder

```
adapter
├─ ARMST_DovetailOpticStorageComponent
└─ AttachmentSlotComponent
   └─ AttachmentSlot InventoryStorageSlot
      ├─ PivotID snap_ris
      └─ ChildPivotID snap_weapon
```

and the custom storage registers that slot with `SetupSlotHooks(slot, 0)`.

Shape B is closer to the proven weapon serialization, but script access to the nested `InventoryStorageSlot` instance must be proven before implementation.

## IIC-derived component warning

`BaseInventoryStorageComponent` derives from `InventoryItemComponent`.

The production adapter already has the canonical WeaponPart-family IIC:

`557E85EEE1B60313`

Therefore a custom storage component may introduce a second IIC-derived effective component role.

Before implementing a custom storage, explicitly verify whether this multi-IIC-derived pattern is valid in vanilla container items or whether the storage component must replace/reuse the primary item identity.

Do not add a custom storage blindly and then hide one component with `Enabled 0`.

## Do not do next

Until the slot-ownership question is answered, do **not**:

- edit the XOBs;
- change `snap_weapon` or `snap_ris`;
- add more `ActionsManager` actions;
- add `WeaponComponent` just to imitate a weapon;
- create another test collimator;
- create another test weapon;
- restore the deleted POC branch;
- force exact RIS1913 when RIS1913Short inheritance is already valid;
- mass-change current optics compatibility policy from this experiment.

## Recommended next audit/POC gate

Before any new live edit, find or prove the exact slot-construction pattern for a custom `BaseInventoryStorageComponent`:

1. look for a source class implementing `GetSlotsCountScr` / `GetSlotScr`;
2. look for a source class calling `SetupSlotHooks`;
3. determine how its `InventoryStorageSlot` instance is constructed or obtained;
4. determine whether pivot and child-pivot data can be serialized/configured for that owned slot;
5. determine whether the existing `AttachmentSlotComponent` can expose/reuse its internal `InventoryStorageSlot` to a custom storage.

Only after one of these is proven should the single test prefab be modified again.

## Current verdict

```
SEPARATE_ITEM_REQUIREMENT: HARD
COMPOSITE_PATH: REJECTED_FOR_PRODUCT
WEAPON_SIDE_DEPENDENCY: VALID_FALLBACK_BUT_REJECTED_FOR_PRODUCT
STOCK_ATTACHMENT_HOST_PATTERN: NOT_FOUND
NESTED_ATTACHMENT_IMPOSSIBLE: NOT_PROVEN
INVENTORYSTORAGESLOT_PHYSICAL_SEMANTICS: PROVEN
SETUPSLOOTHOOKS_API: PROVEN
CUSTOM_ONE_SLOT_STORAGE: MOST_PROMISING, NOT YET PROVEN
CURRENT_SINGLE_TEST: KEEP
PRODUCTION_FILES_CHANGED_BY_THIS_AUDIT: NONE
```

The next useful work is source/API archaeology around custom slot ownership, not another broad prefab experiment.

---

## Forensics update (same day — InventoryStorageSlot access/construction)

A follow-up read-only pass tightened the gate and produced a concrete route classification.

**Classified routes:**

- **ROUTE A** — custom storage directly owns a serialized `InventoryStorageSlot` → **UNRESOLVED** (no source/prefab example of that serialization).
- **ROUTE B** — create `InventoryStorageSlot` in script → **UNRESOLVED** (no proven constructor / `CreateInstance` path).
- **ROUTE C** — register the existing `AttachmentSlotComponent`'s internal slot → **UNRESOLVED** (no public getter of the internal `InventoryStorageSlot`; `EntitySlotInfo.GetSlotInfo(child)` is circular for registration).
- **ROUTE D** — `MultiSlotConfiguration` creating a pivot-bearing slot → **UNRESOLVED** (`SlotTemplate` absent from the game DB; no pivot-field slot-config evidence).

**Decision: D — NO_PUBLIC_ROUTE_PROVEN.**

Framing (important, do not overstate): this is **not** "the engine forbids nested attach". It is narrower — no public/proven way has yet been found to obtain or construct a pivot-bearing `InventoryStorageSlot` for a script-defined storage. Every other piece is proven present (`InventoryStorageSlot : EntitySlotInfo` with physical attach, `SetupSlotHooks`/`ReleaseSlotHooks`, `GetSlotsCountScr`/`GetSlotScr`).

**Concrete unblock files (all confirmed present in the installed game resource DB):**

- `scripts/Game/generated/InventorySystem/InventoryStorageSlot.c`
- `scripts/Game/generated/InventorySystem/MultiSlotConfiguration.c`
- `scripts/Game/generated/InventorySystem/BaseInventoryStorageComponent.c`
- `scripts/Game/Inventory/ScriptedBaseInventoryStorageComponent.c`
- `scripts/Game/Inventory/SCR_UniversalInventoryStorageComponent.c`
- `scripts/GameCode/Components/InventorySystem/UniversalInventoryStorageComponent.c`
- `scripts/GameCode/Weapon/BaseAttachmentSlotComponent.c`

**Cheapest next test before writing any custom code:** confirm whether a `ScriptAndConfig`-derived component can declare a serialized `ref InventoryStorageSlot` / `ref EntitySlotInfo` member with `PivotID`/`ChildPivotID` in Workbench.
- If YES → Route A/B opens (one-file custom storage + one slot).
- If NO → separate-item nested attach requires a deeper custom bridge, and the stock fallbacks remain: composite (one assembly) or weapon-side dependency.

Live addon unchanged by this forensics pass.

---

## Route E staging status (2026-09-22)

Route E: adapter-owned `EquipmentStorageComponent` (equipment storage slot) instead of a script-declared `InventoryStorageSlot`.

### External evidence used (shape only)

- `SCR_UniversalInventoryStorageComponent { components { SCR_EquipmentStorageComponent { InitialStorageSlots { SCR_EquipmentStorageSlot <Name> { PivotID ... ChildPivotID ... } } } } }`
  - proven serialization identifiers: `InitialStorageSlots`, `SCR_EquipmentStorageSlot`, `PivotID`, `Offset`, `Enabled`, `Prefab`, `AllowedItemTypes`, `ChildPivotID`.
- Engine source (Script-Diff, 1.8.0.13):
  - `EquipmentStorageSlot : InventoryStorageSlot : EntitySlotInfo`
  - `SCR_EquipmentStorageComponent : EquipmentStorageComponent : BaseEquipmentStorageComponent : UniversalInventoryStorageComponent : BaseUniversalInventoryStorageComponent : ScriptedBaseInventoryStorageComponent : BaseInventoryStorageComponent : InventoryItemComponent`
  - `event bool CanStoreItem(IEntity item, int slotID)`; stock override form `override bool CanStoreItem(...)` + `super.CanStoreItem(...)` (see `SCR_FilteredInventoryStorageComponent`).
  - stock compatibility pattern `SCR_CompatibleAttachmentPredicate`: `InventoryItemComponent -> GetAttributes() -> FindAttribute(WeaponAttachmentAttributes) -> GetAttachmentType() -> .Type() -> IsInherited(attachmentType)`.
- Official sample `Arma-Reforger-Samples/SampleMod_NewWeapon` confirms: `AttachmentOpticsRIS1913`, `AttachmentOpticsRIS1913Short`, RIS-family attachment prefab, `AttachmentSlotComponent.Enabled`, `AttachmentSlot InventoryStorageSlot`, `PivotID` / `ChildPivotID`.

### Evidence limits (do not overstate)

- `AttachmentOpticsDovetailAK` is NOT proven vanilla by SampleMod_NewWeapon. It is only known as the live production adapter's effective type.
- SampleMod proves the RIS1913 optics family; it does not prove `DovetailAK` origin.

### Staging artifacts (non-authoritative)

- NEW `Scripts/Gamecode/ARMST_DovetailRISStorageComponent.c`:
  - `ARMST_DovetailRISStorageComponent : SCR_EquipmentStorageComponent`
  - `override bool CanStoreItem(IEntity item, int slotID)` filtering `IsInherited(AttachmentOpticsRIS1913)` via the stock `SCR_CompatibleAttachmentPredicate` pattern.
- `Prefabs/Weapons/Attachments/Optics/Diagnostic/armst_Optic_AKDovetail_Nested_SINGLE_TEST.et`:
  - removed experimental `SCR_WeaponAttachmentsStorageComponent {C396B32EED5A25B4}`;
  - neutralized inherited `AttachmentSlotComponent {BB6000C24BAA468F}` via `Enabled 0`;
  - added `ARMST_DovetailRISStorageComponent {908D32FA413D9AFB}` with
    `InitialStorageSlots { SCR_EquipmentStorageSlot RIS { PivotID "snap_ris" ChildPivotID "snap_weapon" } }`.
- `908D32FA413D9AFB = STAGING_ID_ONLY` (collision-checked locally, NOT Workbench-generated; not an authoritative component ID).
- Production adapter `armst_Optic_AKDovetailMount.et` and collimator `armst_Optic_Collimator.et`: UNCHANGED.

### Pending Workbench gates (first failure wins; do not expand)

- Gate 0 script/compiler -> `ROUTE_E_BLOCKED_AT_SCRIPT_COMPILE`
- Gate 1 prefab serialization -> `ROUTE_E_BLOCKED_AT_STORAGE_STRUCTURE`
- Gate 2 adapter item identity -> `ROUTE_E_BLOCKED_AT_ITEM_IDENTITY`
- Gate 3 child storage (production collimator) -> `ROUTE_E_BLOCKED_AT_CHILD_STORAGE`
- Gate 4 persistence -> only then `ROUTE_E_PROVEN`

If Workbench accepts the shape: delete the hand-serialized block, re-add `ARMST_DovetailRISStorageComponent` via the Workbench UI (Workbench-generated ID), configure one `SCR_EquipmentStorageSlot` (`snap_ris` / `snap_weapon`), save, diff, and confirm the production parent is unchanged. Do NOT auto-switch to the nested-under-`SCR_UniversalInventoryStorageComponent` variant; that would be a separate architectural iteration.

Current verdict: `ROUTE_E_PARTIAL` (staging built + static validation); runtime gates not yet executed.
