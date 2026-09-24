# ARMST Optics Compatibility System v1

> [!WARNING]
> **Status: HISTORICAL / SUPERSEDED POLICY.** Use `OPTICS_COMPATIBILITY_SYSTEM_V2.md` and `KNOWLEDGE_STATUS.md` for current authoring decisions.

## Engine rule

Arma Reforger attachment compatibility is directional. The inventory predicate reads the module's `WeaponAttachmentAttributes -> AttachmentType` and tests whether the module type inherits the type required by the weapon slot:

```text
moduleType.IsInherited(slotType)
```

This means a broad type on a weapon slot accepts all descendant module types, while a broad parent type on a module does not automatically fit a narrower child slot.

Bohemia's dovetail hierarchy is:

```text
AttachmentOptics
└─ AttachmentOpticsDovetail
   └─ AttachmentOpticsDovetailAKSVD
      ├─ AttachmentOpticsDovetailAK
      └─ AttachmentOpticsDovetailSVD
```

## Current ARMST findings

- `Optic_PSO1.et` uses `AttachmentOpticsDovetailAK`.
- AKM, VSS, VAL, 9A91, VSK94 and `armst_SVD` currently request that same `AttachmentOpticsDovetailAK` type. Therefore an AK-typed optic can cross all six families.
- `Optic_PSO1_ak.et` uses the parent `AttachmentOpticsDovetailAKSVD`. Under the actual inheritance check this parent does not satisfy narrower AK or SVD slots; in the supplied snapshot it has no local compatible slot.
- `Rifle_SOC94.et` already uses `AttachmentOpticsDovetailSVD`, showing that a narrower SVD family is available.
- G36 already follows the correct proprietary pattern with `AttachmentOpticsG36`.
- Groza uses standardized RIS1913. Keep RIS standardized, but select the correct rail-length class deliberately.

## Proposed closed ARMST dovetail namespace

Create organizational and leaf marker types:

```c
class AttachmentOpticsARMST_DovetailClass {}
AttachmentOpticsARMST_DovetailClass AttachmentOpticsARMST_DovetailSource;
class AttachmentOpticsARMST_Dovetail : AttachmentOptics
{
};

class AttachmentOpticsARMST_AKClass {}
AttachmentOpticsARMST_AKClass AttachmentOpticsARMST_AKSource;
class AttachmentOpticsARMST_AK : AttachmentOpticsARMST_Dovetail
{
};

class AttachmentOpticsARMST_SVDClass {}
AttachmentOpticsARMST_SVDClass AttachmentOpticsARMST_SVDSource;
class AttachmentOpticsARMST_SVD : AttachmentOpticsARMST_Dovetail
{
};

class AttachmentOpticsARMST_VSSVALClass {}
AttachmentOpticsARMST_VSSVALClass AttachmentOpticsARMST_VSSVALSource;
class AttachmentOpticsARMST_VSSVAL : AttachmentOpticsARMST_Dovetail
{
};

class AttachmentOpticsARMST_9A91VSKClass {}
AttachmentOpticsARMST_9A91VSKClass AttachmentOpticsARMST_9A91VSKSource;
class AttachmentOpticsARMST_9A91VSK : AttachmentOpticsARMST_Dovetail
{
};
```

`AttachmentOpticsARMST_Dovetail` is organizational only. Never serialize that parent directly into a final weapon slot or final optic prefab.

## Weapon slot policy

Use leaf family types:

```text
AKM family -> AttachmentOpticsARMST_AK
SVD / approved SVD-family -> AttachmentOpticsARMST_SVD
VSS / VAL -> AttachmentOpticsARMST_VSSVAL
9A91 / VSK94 -> AttachmentOpticsARMST_9A91VSK
G36 -> AttachmentOpticsG36
standard Picatinny -> AttachmentOpticsRIS1913* hierarchy
```

Do not solve compatibility by widening the weapon slot.

## Optic prefab policy

Separate optical body/mechanics from mount compatibility. Example:

```text
Optic_PSO1_Base.et
├─ Optic_PSO1_AK.et  -> AttachmentOpticsARMST_AK
└─ Optic_PSO1_SVD.et -> AttachmentOpticsARMST_SVD
```

If one optical body supports more than one mount family, create a thin child wrapper prefab for each family. The child changes only mount-specific data such as `AttachmentType` and, when necessary, validated mount geometry. Do not assign a broad parent type to make one prefab universal.

## RIS1913 policy

Reuse Bohemia's existing hierarchy:

```text
AttachmentOpticsRIS1913
└─ AttachmentOpticsRIS1913Medium
   └─ AttachmentOpticsRIS1913Short
      └─ AttachmentOpticsRIS1913VeryShort
```

The hierarchy encodes rail-length restrictions. Use the narrowest rail type justified by the weapon. A broad RIS slot intentionally accepts more descendant optics.

## Adapters

Bridge incompatible mount families through explicit adapter modules instead of broad weapon slots. Conceptually:

```text
AK dovetail slot
-> AK-to-RIS adapter typed for ARMST_AK
-> adapter exposes RIS1913 optic slot
-> standard RIS optic
```

This keeps native compatibility strict and makes every cross-standard connection explicit.

## Pivot contract

Compatibility and physical placement are separate concerns. Standardize mount geometry:

- weapon-side mount pivot: documented `slot_optics` contract;
- module-side snap pivot: one documented snap pivot per mount family;
- arbitrary offsets are calibrated exceptions, not compatibility logic;
- adapters own geometry conversion between mount standards.

A correct `AttachmentType` cannot fix a wrong pivot or offset.

## Static validation / CI

Build a source-derived matrix before Workbench:

1. Parse script inheritance (`class Child : Parent`).
2. Parse every weapon `AttachmentSlotComponent -> AttachmentType`.
3. Parse every final optic `WeaponAttachmentAttributes -> AttachmentType`.
4. Compute transitive `moduleType.IsInherited(slotType)` compatibility.
5. Emit a weapon × optic matrix.
6. Fail CI when:
   - a proprietary/dovetail weapon slot uses `AttachmentOptics`, `AttachmentOpticsDovetail` or `AttachmentOpticsDovetailAKSVD`;
   - a final dovetail optic uses an organizational parent rather than a leaf;
   - an optic has zero compatible slots;
   - an optic becomes compatible with an unapproved family;
   - a weapon optic slot has zero approved optics;
   - a mount family has an undocumented pivot contract;
   - a RIS rail uses a broader length class than policy allows.

Keep deliberate cross-family pairs in an explicit allowlist.

## Migration order

1. Add new marker types; do not delete current ones.
2. Create mount-specific PSO wrapper prefabs.
3. Migrate AK family.
4. Migrate SVD/SOC94.
5. Migrate VSS/VAL.
6. Migrate 9A91/VSK94.
7. Generate the compatibility matrix and run static checks.
8. Validate in Workbench.
9. Only then retire obsolete broad mappings.

## Public sources

- Compatibility predicate: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Inventory/SCR_InventoryStorageManagerComponent.c
- Attachment slot API: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/generated/Weapon/AttachmentSlotComponent.c
- Optic/RIS/dovetail hierarchy: https://github.com/BohemiaInteractive/Arma-Reforger-Script-Diff/blob/3d77cc212d5cda9922daf5f45635c7300d2d4cce/scripts/Game/Weapon/Attachments/Attachments_optics.c
