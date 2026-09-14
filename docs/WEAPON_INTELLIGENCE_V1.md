# Weapon Intelligence V1

## Goal

Build a Workbench-native addon that reads mounted **base-game Arma Reforger** weapon resources and script visibility, then exports local AI-readable metadata for later comparison against ARMST or other mods.

The scanner is not built on an ARMST source directory. `Weapon_ARMA_X` itself is the addon and depends directly on the base game.

## Project dependency

`addon.gproj` contains only the Arma Reforger dependency:

```text
58D0FB3206B6F859
```

This is the same base-game dependency pattern used by the existing Reforger Workbench Toolkit project.

## Proven design sources

The implementation reuses already-tested RWTK ideas as architectural references:

1. `RWTK_ResourceCollector` / `RWTK_PrefabValidator` — discover registered `.et` resources through `SCR_WorkbenchHelper.SearchWorkbenchResources`, load them with `Resource.Load`, convert prefab resources to `IEntitySource`, and inspect component classes.
2. `RWTK_CodeIntelligenceScanner` — discover Workbench-visible `.c` files through `FileIO.FindFiles("scripts/", ".c")` and read them without requiring a Python daemon or unpacking game archives.
3. `RWTK_ParticleSourceExtractorPlugin` — physical-copy-first materialization with `BaseContainer` serialization fallback, while treating Workbench-native `Duplicate to addon` as the bridge when packed resources cannot be exposed directly.

## Plugins

### WAX: Scan Vanilla Weapon Resources

Workbench module: `ResourceManager`.

Current scan roots:

```text
$ArmaReforger:Prefabs/Weapons
$ArmaReforger:Configs/Weapons
```

Current outputs:

```text
$Weapon_ARMA_X:Generated/VanillaWeaponIntelligence/resources.tsv
$Weapon_ARMA_X:Generated/VanillaWeaponIntelligence/components.tsv
$Weapon_ARMA_X:Generated/VanillaWeaponIntelligence/manifest.tsv
$Weapon_ARMA_X:Generated/VanillaWeaponIntelligence/README.md
```

The first pass records:

- registered `ResourceName` identity;
- virtual resource path;
- loaded root class;
- top-level `IEntitySource` component count and component class names for `.et`;
- `BaseContainer` class availability for `.conf`;
- explicit load/serialization failures instead of guessed values.

It does **not** yet claim property-level extraction such as RPM, dispersion, magazine capacity, or full inherited effective values. Those must be added only after Workbench evidence confirms the correct property-access/materialization path.

### WAX: Materialize Selected Vanilla Sources

Workbench module: `ResourceManager`.

Purpose: recover selected vanilla `.et/.conf` resources into the local WAX addon for inspection.

Order:

```text
selected ResourceName
-> Workbench.GetAbsolutePath physical source, when available
-> byte-for-byte physical copy
-> otherwise Resource.Load / GetResource / ToBaseContainer
-> BaseContainerTools.SaveContainer, when supported
-> RegisterResourceFile
```

If a packed resource cannot be represented through either path, the plugin reports the exact failed stage. Workbench `Duplicate to addon` remains the known safe staging bridge rather than direct `.pak` unpacking.

Local destination:

```text
$Weapon_ARMA_X:Imported/VanillaSources
```

### WAX: Scan Base Game Scripts

Workbench module: `ScriptEditor`.

Uses:

```text
FileIO.FindFiles("scripts/", ".c")
FileIO.OpenFile(...)
FileHandle.ReadLine(...)
```

V1 emits file/line metadata only. It deliberately does not commit/copy vanilla `.c` source bodies into Git.

Output:

```text
$Weapon_ARMA_X:Generated/BaseGameScripts/
```

## Data policy

`Generated/` and `Imported/` are gitignored.

Repository code is public; locally generated vanilla source/materialization evidence remains local unless a later task explicitly defines a safe derived-data publication format.

The future intended pipeline is:

```text
Arma Reforger base game
        ↓
Weapon_ARMA_X Workbench addon
        ↓
vanilla weapon/resource knowledge
        ↓
ARMST scan / comparison layer
        ↓
balance analysis and targeted mod changes
```

The base game is the reference corpus. ARMST is a later comparison target, not the parser host.

## Current validation boundary

Repository review can verify that the addon structure and API choices are derived from previously used RWTK patterns. It cannot prove this new WAX code compiles or that the exact `$ArmaReforger:` roots return the expected corpus.

Before merging V1, run in Arma Reforger Tools and record:

1. `addon.gproj` loads with only the base-game dependency;
2. WorkbenchGame compilation succeeds;
3. Resource Manager shows both WAX resource plugins;
4. Script Editor shows the WAX script scanner;
5. vanilla weapon prefab discovery count is non-zero;
6. vanilla weapon config discovery count is non-zero or the actual correct config root is identified;
7. `.et` resources successfully convert to `IEntitySource` for representative weapons/magazines/ammo prefabs;
8. `.conf` `BaseContainer` behavior is recorded from real evidence;
9. base-game `.c` discovery/read count is non-zero;
10. materialization is tested on one representative `.et` and one representative `.conf` without modifying source resources.

Until these checks are run, Workbench runtime status is **PENDING**.
