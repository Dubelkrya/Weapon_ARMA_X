# Weapon_ARMA_X

Workbench-native intelligence addon for Arma Reforger weapon resources.

## Architecture

`Weapon_ARMA_X` is an independent Workbench addon whose only project dependency is the base game (`58D0FB3206B6F859`). It is not built on top of ARMST and does not require the ARMST weapon mod to scan vanilla data.

The addon reads mounted Arma Reforger resources and writes local derived evidence under this addon:

- `Generated/VanillaWeaponIntelligence/` — `.et/.conf` resource inventory and prefab component metadata;
- `Generated/BaseGameScripts/` — Workbench-visible `.c` file index;
- `Imported/VanillaSources/` — optional local materialized copies of selected `.et/.conf` resources.

`Generated/` and `Imported/` are intentionally gitignored so vanilla source content is not committed to the public repository.

## Workbench plugins

Resource Manager:

- `Weapon ARMA X -> WAX: Scan Vanilla Weapon Resources`
- `Weapon ARMA X -> WAX: Materialize Selected Vanilla Sources`

Script Editor:

- `Weapon ARMA X -> WAX: Scan Base Game Scripts`

## Installation

Place/clone this repository as a Workbench addon and open `addon.gproj` with Arma Reforger Tools. The project depends directly on the base game.

See `docs/WEAPON_INTELLIGENCE_V1.md` for the current scope and validation boundary.
