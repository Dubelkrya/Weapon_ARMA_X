# ARMST Optics Compatibility System v2

> [!IMPORTANT]
> **Status: CURRENT GAMEPLAY POLICY.** Applies to the documented DovetailRU policy; newer live experimental research can supersede it for a specific research branch when `KNOWLEDGE_STATUS.md` says so.

## Final gameplay rule

ARMST keeps two separate layers:

- **RealCompatibility** — researched real-world compatibility.
- **GameplayCompatibility** — what the game intentionally permits.

For Russian/Soviet side-rail optics we use one gameplay family: `DovetailRU`.

All approved weapons with that side-rail gameplay interface and all approved Russian side-rail optics use `AttachmentOpticsARMST_DovetailRU`.

Therefore PSO-family optics may be mounted on every ARMST weapon deliberately marked as `DovetailRU`.

## Script

```c
class AttachmentOpticsARMST_DovetailRUClass
{
};

AttachmentOpticsARMST_DovetailRUClass AttachmentOpticsARMST_DovetailRUSource;

class AttachmentOpticsARMST_DovetailRU : AttachmentOptics
{
};
```

The class contains no optic behavior. It only defines the compatibility family.

## Weapon side

Use `AttachmentOpticsARMST_DovetailRU` on weapon optic slots that ARMST intentionally groups into the Russian side-rail gameplay family.

Current supplied snapshot candidates: AKM, VSS, VAL, 9A91, VSK94, SVD and SOC94.

Current Workbench-validated project example: the AEK-971 prototype based on `Rifle_AK74N_base.et`, where only the inherited optic `AttachmentType` was changed while slot geometry remained inherited.

This is a gameplay simplification, not a claim that every real mount is mechanically identical.

## Optic side

PSO-family optics and other approved Russian side-rail optics use the same `AttachmentOpticsARMST_DovetailRU` type.

When the source optic should otherwise stay unchanged, prefer a **thin child prefab** rather than editing the original Bohemia/ARMST source asset. Override only `WeaponAttachmentAttributes -> AttachmentType` and preserve inherited model, reticle, zeroing, animation and geometry.

Workbench validation confirmed this with `armst_Optic_PSO1_DovetailRU.et`: the child PSO-1 mounted successfully on the AEK-971 DovetailRU slot.

Different child prefabs are still allowed when geometry, model, reticle, eye relief, pivot, zeroing or another actual property differs.

## Two-sided compatibility contract

A weapon-side slot alone is not sufficient.

- weapon: `AttachmentSlotComponent -> AttachmentType`
- optic/module: `WeaponAttachmentAttributes -> AttachmentType`

The module type must equal or inherit the type required by the weapon slot. If only the weapon side is migrated, the slot can exist visually while rejecting the intended optic.

## Geometry is separate

Changing compatibility type does not require rewriting physical placement.

Keep inherited `PivotID`, `ChildPivotID`, offsets, angles, helper prefabs and snap geometry unless there is an independent geometry problem. A correct `AttachmentType` cannot repair a bad pivot, and a pivot change does not create compatibility.

## Interfaces kept separate

- RIS1913/Picatinny keeps the Bohemia `AttachmentOpticsRIS1913` hierarchy.
- G36 keeps `AttachmentOpticsG36`.
- Adapters bridge interfaces explicitly rather than broadening the native slot.

## Realism database

Every researched module keeps both `RealCompatibility` and `GameplayCompatibility`.

Example:

```text
PSO-1
RealCompatibility: specific real-world side-rail / bracket variants
GameplayCompatibility: DovetailRU
GameplaySimplification: allowed on every ARMST weapon marked DovetailRU
```

## Validation rules

Fail authoring validation when:

1. A DovetailRU weapon still uses an old AK/SVD local compatibility type as its intended gameplay type.
2. A DovetailRU optic still uses a different local side-rail type.
3. Only one side of the weapon/module compatibility contract was migrated.
4. RIS1913 or G36 is accidentally assigned DovetailRU.
5. A module has no GameplayCompatibility classification.
6. RealCompatibility is overwritten by the gameplay simplification.
7. Pivot/snap data are missing or inconsistent where geometry is locally authored.
8. A compatibility-only child unnecessarily duplicates inherited geometry or optic behavior.

Attachment compatibility and physical positioning remain separate checks.
