# ARMST Optics Compatibility System v2

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

This is a gameplay simplification, not a claim that every real mount is mechanically identical.

## Optic side

PSO-family optics and other approved Russian side-rail optics use the same `AttachmentOpticsARMST_DovetailRU` type.

Different child prefabs are still allowed when geometry, model, reticle, eye relief, pivot, zeroing or another actual property differs.

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

1. A DovetailRU weapon still uses an old AK/SVD local compatibility type.
2. A DovetailRU optic still uses a different local side-rail type.
3. RIS1913 or G36 is accidentally assigned DovetailRU.
4. A module has no GameplayCompatibility classification.
5. RealCompatibility is overwritten by the gameplay simplification.
6. Pivot/snap data are missing or inconsistent.

Attachment compatibility and physical positioning remain separate checks.
