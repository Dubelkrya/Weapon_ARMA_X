# Selective review — resolver-v2 and weapon-intelligence-v1

> Status: CURRENT REVIEW NOTE. This document records what may be borrowed from the two remaining research branches. It does not authorize a wholesale merge of either branch.

Reviewed against current `main` after canonical rescan PR #8 and scan-policy hardening.

## Decision summary

### agent/resolver-v2

**TAKE NOW / adapted into `agent/scanner-coverage-hardening`:**

- colon-aware serialized block parsing so inherited declarations such as
  `BaseFireMode "{INSTANCE}" : "{GUID}FireMode.conf"` keep the instance ID and template/resource reference separate;
- normalization of config-root self ResourceName so a config's own GUID/path is not mistaken for an instance identifier or inheritance reference;
- array extraction concept used for serialized `AmmoMapping` element children;
- regression tests for parser/config identity and source-backed array extraction;
- GUID-aware identity principle for relocated magazine references;
- CI execution of focused scanner/parser regression tests.

These changes are small enough to validate independently and do not introduce resolver-v2's alternate repository architecture.

**ADAPT LATER, not merged in this pass:**

- functional-component scoring when duplicate `WeaponComponent`, `MuzzleComponent` or `MagazineComponent` instances exist;
- origin-aware ARMST + read-only vanilla resolution;
- strict GUID collision/origin pinning;
- config inheritance hydration across roots;
- exact Workbench materialization guards;
- architecture indexing/package tooling.

These need a dedicated integration branch and current canonical scan evidence. They must not be copied as one block.

**SKIP / DO NOT MERGE WHOLESALE:**

- resolver-v2 generated catalog/report replacements;
- alternate repository layout that removes or sidelines current canonical indexes/reports/schema;
- old generated AI/jsonl outputs as an authority source;
- any change that makes materialized vanilla editable;
- any large scan result produced before the current canonical 2026-09-24 snapshot.

### agent/weapon-intelligence-v1

**Potentially useful, keep for a later bounded extraction:**

- `WAX_WeaponResourceScannerPlugin.c`: read-only mounted vanilla weapon prefab/config inventory;
- `WAX_BaseGameScriptScannerPlugin.c`: read-only mounted vanilla script visibility diagnostics.

These are unique diagnostics and are not required for the current ARMST canonical scanner.

**Superseded / do not take from this branch:**

- its base-game source materializer is older than the hardened materialization/resolution work on `resolver-v2`;
- its standalone-addon architecture and `addon.gproj` should not be merged into current `main` merely to obtain diagnostics;
- generated vanilla intelligence output is evidence/debug data, not canonical ARMST weapon truth.

## Scanner debt addressed by the current hardening branch

### AmmoMapping

The current scanner previously read `AmmoMapping.value`. Serialized arrays are represented by child `__elem__` nodes, so the extractor could emit an empty mapping even when the live prefab serialized slots.

The hardening branch reads array element children explicitly. When `MaxAmmo` is absent but a non-empty mapping is serialized, capacity is derived from the mapping length. This is direct source evidence and does not infer capacity from the filename.

### AmmoConfig coverage

The historical `indexes/config_reference/ammo_configs.json` is supplied-snapshot coverage and should not be the only index used for current live ARMST configs.

The hardening branch adds a scanner-generated live index:

`indexes/generated_config_reference/ammo_configs.json`

It is regenerated from current primary-addon `.conf` resources and kept separate from supplied/reference snapshots.

### Relocated magazine references

Some current weapon prefabs still serialize historical magazine paths while preserving the resource GUID. The canonical scanner already resolves those references by GUID to relocated local targets.

`check_data_quality.py` previously compared only the serialized path, producing four false `WEAPON_MAGAZINE_NOT_CATALOGED` warnings. The hardening branch accepts a matching catalog GUID or the scanner's resolved local target.

This is a checker correction only. No weapon prefab is rewritten.

## Required validation sequence

1. Run Python regression tests in CI.
2. Run repository integrity and existing generated-page checks.
3. Confirm the current checked-in snapshot no longer reports false relocated-magazine warnings.
4. Merge scanner/checker hardening only after CI is green.
5. Run a new read-only canonical rescan against:
   `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`
6. Review generated diff for AmmoMapping, derived capacity and live AmmoConfig coverage changes.
7. Re-run data-quality scan and record before/after counts.
8. Do not claim Workbench/runtime validation from this static scanner work.

## Branch retention

Keep both research branches until the hardening/rescan cycle is complete:

- `agent/resolver-v2` — retained for later selective resolver/origin work;
- `agent/weapon-intelligence-v1` — retained only until a decision is made on the two unique read-only Workbench diagnostic scanners.

After selective extraction decisions are complete, close obsolete research PRs and remove their branches rather than merging them wholesale.
