# ARMST architecture passport — Arma Reforger

Status: descriptive architecture map. This document does **not** authorize reorganizing, renaming, moving or refactoring files inside the addon.

## 1. Project boundary

Authoritative weapon addon:

`C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`

Engine/editor context: **Arma Reforger / Enfusion / Arma Reforger Workbench**.

The physical addon layout is treated as intentional and human-oriented. Knowledge tooling must adapt to the addon; the addon must not be reorganized merely to satisfy scanners, catalogs or naming conventions.

Current primary scan/study baseline on branch `agent/primary-mod-knowledge-sync`:

- 923 source text resources guarded by SHA-256 during the study pass;
- 125 discovered entities in the candidate inventory;
- 55 weapons;
- 32 magazines;
- 14 ammunition/projectile entities;
- 3 scanner-classified optics plus one root-level thin PSO child currently misclassified by the scanner as `misc`;
- 7 attachments;
- 4 grenades;
- 3 tripods;
- 4 core entities;
- 2 particle entities.

Counts are scanner inventory facts, not a statement that every gameplay dependency is locally resolvable.

## 2. Core architectural principle

The addon is inheritance-driven. A final weapon is normally a composition of several layers rather than one self-contained file.

Conceptual chain:

```text
Enfusion/base-game parent
        ↓
ARMST core/family base
        ↓
ARMST concrete weapon
        ↓
optional equipped/full/variant child
```

The exact number of local levels differs by family.

### Fully local chain example — AKM

Observed local chain:

```text
Prefabs/Weapons/Core/Weapon_Base.et
└─ Prefabs/Weapons/Core/Rifle_Base.et
   └─ Prefabs/Weapons/Rifles/AKM/Rifle_AKM_base.et
      └─ Prefabs/Weapons/Rifles/AKM/Rifle_AKM.et
         └─ Rifle_AKM_full.et
```

This family demonstrates the cleanest local pattern: common weapon base → rifle base → family base → concrete weapon → optional equipped variant.

### External-tail example — VAL

Observed local chain:

```text
base-game Rifle_AK74_short_base.et
└─ ARMST Rifle_val_base.et
   └─ ARMST Rifle_VAL.et
      └─ ARMST Oc_Groza.et
```

The ARMST local chain ends at `Rifle_val_base.et`; the next parent is external to the addon. External inheritance is normal and must be represented as such rather than guessed or treated as missing authoring.

### Thin local overlay example — AK-74M

Observed local chain:

```text
base-game Rifle_AK74N_base.et
└─ armst_AK74N.et
   └─ armst_AK74M.et
      └─ armst_AK74M_full.et
```

The local ARMST children are intentionally thin and may mainly add materials, attachment choices or other local overrides while substantial mechanics remain external/inherited.

## 3. Functional layers of the mod

For authoring and analysis, treat the addon as six interacting systems.

### 3.1 Weapon hierarchy

Responsible for:

- weapon entity inheritance;
- fire modes;
- weapon-side velocity coefficient;
- dispersion;
- recoil/sway overrides;
- UI identity;
- physical properties;
- magazine well selection;
- attachment slots;
- animation references.

Key rule: a child prefab should be interpreted relative to its inheritance chain. Absence of a field in the child does not mean the feature/value is absent.

### 3.2 Magazine system

Conceptual flow:

```text
Weapon
→ MagazineWell type
→ magazine prefab
→ MagazineComponent / ammo binding
→ AmmoConfig
→ AmmoMapping / loaded projectile
```

The magazine is the bridge between a weapon family and ammunition resources.

Known magazine-well classes observed in the primary addon include:

- `MagazineWell12g`
- `MagazineWell763x25`
- `MagazineWell9x39`
- `MagazineWell9x39_9a91`
- `MagazineWellAPB`
- `MagazineWellPP91`
- `MagazineWellVZ58_762`
- `MagazineWellM9Beretta`
- `MagazineWellStanag556`

This list is descriptive and may not be exhaustive for every external/base-game chain.

### 3.3 Ammunition/config system

Conceptual flow:

```text
AmmoConfig
→ allowed projectile resources
→ projectile prefab
→ kinetic damage / penetration / ballistics
```

Project rules:

- `AmmoResourceArray` = allowed ammunition resources;
- `AmmoMapping` = what is actually loaded;
- projectile kinetic damage is separate from tracer/incendiary/explosive secondary effects;
- use the projectile's actually referenced ballistic table;
- weapon-side `BulletInitSpeedCoef` is a weapon modifier, not projectile lethality.

Confirmed local TT chain:

```text
armst_TT.et
→ MagazineWell763x25
→ Magazine_763x25_TT_8rnd_Ball.et
→ Ammo_763x25.conf
→ Ammo_763x25_Ball.et
```

The separate legacy `Ammo_763x25.et` is not the projectile selected by the resolved TT config chain.

### 3.4 Attachment compatibility system

Treat compatibility and geometry as two separate contracts.

```text
Attachment slot
├─ compatibility type
└─ physical mount geometry
   ├─ pivot
   ├─ child pivot
   ├─ translation
   └─ rotation
```

Compatibility is two-sided:

- weapon side: `AttachmentSlotComponent -> AttachmentType`;
- module/optic side: `WeaponAttachmentAttributes -> AttachmentType`.

Physical pivots/snap points are independent of type compatibility.

Current primary-mod source state for the custom Russian side-rail family:

- marker class `AttachmentOpticsARMST_DovetailRU` exists;
- `armst_Optic_PSO1_DovetailRU.et` uses it on the optic/module side;
- no surveyed primary-mod weapon slot currently requests the custom type;
- therefore the primary addon is currently **module-side-only** for this custom family.

This source state does not cancel the project policy that a finished migration requires both sides.

### 3.5 Presentation/resources

Includes:

- `.xob` models;
- materials;
- particles;
- sounds;
- animation graphs and instances;
- UI names/descriptions.

These references may be local or external. Their location should not be used as evidence for gameplay inheritance.

### 3.6 Knowledge/tooling layer

Lives outside gameplay authoring logic and must adapt to the addon structure.

Includes:

- scanner;
- catalogs;
- reference graph;
- authoring guides;
- compatibility policies;
- ammo AP/BP policy;
- Workbench-validated samples.

Tooling must never force physical addon reorganization.

## 4. Family patterns observed

The following family/group relationships are source-backed examples from the current inventory. This table is descriptive, not a complete taxonomy of every weapon.

| Family / group | Observed structure | Notes |
|---|---|---|
| AKM | `Weapon_Base -> Rifle_Base -> Rifle_AKM_base -> Rifle_AKM -> full variant` | Strong local family hierarchy |
| AK-74 local overlays | base-game `Rifle_AK74N_base -> armst_AK74N -> armst_AK74M -> armst_AK74M_full` | Significant inherited mechanics remain external |
| VAL | base-game AK74-short parent -> `Rifle_val_base -> Rifle_VAL` | Local 9×39 family layered over external rifle base |
| VSS | local VSS family resources are present; 9×39 magazine families exist | Keep distinct from VAL where source uses distinct bases/wells |
| 9A91 / VSK94 | local family resources and `MagazineWell9x39_9a91` exist | Related caliber does not imply identical magazine family |
| Groza | local Groza resources exist and some inherit from existing ARMST rifle structures | Treat exact parent chain per prefab, not by name only |
| PM-derived handguns | PM base is reused by local handgun work | TT currently reuses parts of this chain |
| TT | `armst_TT -> armst_PM -> PM base / Handgun base` plus dedicated `MagazineWell763x25` and TT magazine | Good example of mechanics reuse plus caliber-specific magazine/ammo override |
| Shotguns | local 12ga family plus dedicated `MagazineWell12g` and 12ga ammo/config resources | Pellet/slug handling needs separate ammo interpretation |

## 5. Caliber architecture view

A caliber family should be documented independently from individual weapons.

Passport fields per caliber:

```text
Caliber
AmmoConfig
Local projectile resources
External/config-only projectile resources
Primary gameplay role candidates
Tracer / incendiary / subsonic / precision tags
Magazine families
MagazineWell classes
Compatible weapon families
Resolved AmmoMapping chains
Unresolved bindings
Workbench validation status
```

Current source-backed local projectile inventory includes:

- 5.45×39 `7N6` local ball projectile;
- 5.56×45 `M193` local ball projectile;
- 7.62×39 `57N231` local ball projectile;
- 7.63×25 `Ammo_763x25_Ball` plus a separate non-default legacy projectile;
- 9×18 `57N181` local ball projectile;
- 9×19 `M882` local ball projectile;
- 9×39 SP5 and SP6 local projectiles;
- 12ga projectile family;
- VOG25 projectile.

Other resources known from supplied config snapshots remain valid knowledge, but their provenance must be marked `supplied snapshot` rather than `present local projectile` when absent from the primary addon source.

## 6. Per-weapon passport record

Every weapon entry in the future architecture passport should contain the same normalized record:

```text
Weapon ID / display name
Source resource
Local parent chain
External parent tail
Family
Role in family: base / concrete / equipped variant / leaf
WeaponComponent source
Fire-mode source(s)
Recoil source(s)
Dispersion source
BulletInitSpeedCoef source
MagazineWell
Default magazine/template
Resolved AmmoConfig
Resolved loaded projectile(s)
Optic slot type
Muzzle slot type
Other attachment slots
Physical pivots where relevant
Animation graph / instance source
Local model/material dependencies
External dependencies
Known scanner limitations
Workbench validation status
```

Do not fill a field from naming conventions when the source chain does not prove it.

## 7. Per-family passport record

Each family should also have one higher-level record:

```text
Family name
Functional family base
External base-game parent, if any
Concrete weapons
Equipped/full variants
Shared fire-mode policy
Shared recoil source
Shared magazine well(s)
Shared attachment interfaces
Shared animation family
Known exceptions
Safe authoring layer for common changes
Safe authoring layer for per-weapon changes
```

This is the layer that will tell us whether a future change belongs in a family base, a concrete weapon, a magazine, an ammo config or a projectile.

## 8. Known structural quirks — document, do not reorganize

### Root-level PSO child

`armst_Optic_PSO1_DovetailRU.et` is physically located at addon root. The scanner currently labels it `misc` because classification is folder-biased, even though its inheritance clearly identifies it as an optic child.

Action: fix knowledge tooling/classification. **Do not move the addon file solely for scanner convenience.**

### TT balance profile with `.et` extension

`Prefabs/Weapons/Handguns/armst_TT_prefab_balance_profile.et` contains JSON-style balance documentation rather than an Enfusion prefab and therefore generates a parse warning.

Action: record as a known non-prefab resource / scanner exception. Do not rename or move it without an explicit authoring decision by the mod owner.

### 5.45 AK and 5.56 STANAG magazine binding

The current local source set does not fully expose a resolvable `MagazineComponent / AmmoConfig / AmmoMapping` binding for the surveyed inherited magazine chains.

Action: mark unresolved from available local source. Do not infer the loaded projectile from filenames.

### External base-game inheritance

Several weapons inherit from Arma Reforger/base-game resources not physically present in this addon tree.

Action: retain an explicit `external parent` boundary and never synthesize inherited values.

## 9. Safe improvements — knowledge/tooling only

The addon itself remains untouched. Improvements should target our analysis layer:

1. Build a machine-readable family index connecting `family -> base -> weapons -> variants`.
2. Add explicit provenance values such as `local`, `external/base-game`, `supplied-config-snapshot`, `Workbench-validated`, `unknown`.
3. Improve scanner classification using inheritance/components in addition to folders.
4. Separate scanner `source_root` from `output_root` in metadata.
5. Generate per-weapon architecture records from the source graph.
6. Generate per-caliber records linking weapon families -> magazine wells -> magazines -> AmmoConfig -> projectiles.
7. Track unresolved bindings explicitly instead of filling them from names.
8. Keep gameplay policy data (DovetailRU, AP/BP) separate from raw source inventory.

## 10. Non-goals

This passport does **not** propose:

- moving folders;
- renaming existing prefabs;
- consolidating author-created directories;
- replacing existing family structures;
- converting the addon to a different layout;
- changing gameplay values;
- changing attachments;
- changing ammo;
- changing GUIDs or instance IDs.

The goal is to make the existing human-friendly addon understandable to ChatGPT, the local agent and future tooling without disturbing how the author works with it in Workbench.

## 11. Next knowledge step

Build two derived knowledge views without touching the addon:

1. `ARMST_FAMILY_MAP` — family/base/concrete/variant inheritance graph.
2. `ARMST_CALIBER_MAP` — caliber -> magazine well -> magazines -> config -> projectiles -> weapon families.

Together with this passport, those two maps become the navigation layer for all later authoring work.