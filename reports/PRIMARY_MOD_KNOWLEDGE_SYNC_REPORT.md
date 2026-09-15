# PRIMARY MOD KNOWLEDGE SYNC REPORT

- Branch: `agent/primary-mod-knowledge-sync`
- Base SHA before study: `9d2961a9369a221e728c140cd3ec636564eca648`
- Authoritative primary addon root (READ ONLY for this pass):
  `C:\Users\Muroy\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST-PLATFORM---Weapons`
- Repository: `C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X`
- Scanner command:
  `python agent/scripts/scan_build.py` with `MOD_ROOT=<primary addon>` and `REPO_ROOT=C:\Users\Muroy\Documents\Default Project\Weapon_ARMA_X\snapshots\primary_candidate`
- Source hash check: **PASS** (923 source files `.et/.conf/.meta/.c`; SHA256 identical before and after the isolated scan)
- Scanner exit code: 0

## Entity counts — before / candidate

| Category | Canonical (before) | Candidate | Delta |
|---|---:|---:|---:|
| entities | 124 | 125 | +1 |
| weapon | 55 | 55 | 0 |
| magazine | 32 | 32 | 0 |
| ammunition | 14 | 14 | 0 |
| optics | 3 | 3 | 0 |
| attachment | 7 | 7 | 0 |
| grenade | 4 | 4 | 0 |
| tripod | 3 | 3 | 0 |
| core | 4 | 4 | 0 |
| particle | 2 | 2 | 0 |
| misc | 0 | 1 | +1 |
| warnings | 0 | 1 | +1 |
| graph edges | 261 | 263 | +2 |
| source files indexed | — | 1964 | — |
| text resources parsed | — | 922 | — |

## Source change summary

The primary addon changed since the last canonical scan exactly as follows:

1. **REMOVED from our comparison**: none meaningful; no tracked entity resource was removed.
2. **ADDED source resource**: `armst_Optic_PSO1_DovetailRU.et` (addon root), a thin child of
   `{C850A33226B8F9C1}Prefabs/Weapons/Attachments/Optics/Optic_PSO1.et`
   also now present.
   - Serialized content is only a `WeaponAttachmentAttributes -> AttachmentType` override:
     `AttachmentOpticsARMST_DovetailRU "{5D0CCDD0615C597D}"`.
   - Instance IDs: `InventoryItemComponent {52627A1F45CD4EB6}`, `SCR_ItemAttributeCollection {52627A1EBB0698FD}`,
     `WeaponAttachmentAttributes {5284D858FFF9BE66}`, `AttachmentType {5D0CCDD0615C597D}`.
3. **ADDED non-entity file**: `Prefabs/Weapons/Handguns/armst_TT_prefab_balance_profile.et`
   is a JSON balance-profile document, not an Enfusion prefab (line 1 is `{`).
   The scanner correctly reports it as a PARSE warning (anomaly), not as an entity.

Nothing else changed in the primary addon during this pass (source hash guard PASS).

## New / removed / changed entities

- **New entity**: `catalog/misc/armst_optic_pso1_dovetailru.json` (`armst_Optic_PSO1_DovetailRU.et`, classified `misc`, `used_as_base_by` of `Optic_PSO1.et`). This is the newly present thin ARMST PSO-1 child following the documented DovetailRU authoring pattern.
- **Removed entities**: none.
- **Changed generated catalog entries** (compared canonical `catalog/` vs candidate `catalog/`, 10 files):

| File | Reason |
|---|---|
| `optics/optic_pso1.json` | `used_as_base_by` now includes `armst_Optic_PSO1_DovetailRU.et` (source-backed) |
| `weapons/armst_m9.json` | scanner extraction difference (candidate resolves chain shorter; see limitations) |
| `weapons/armst_pm.json` | scanner extraction difference |
| `weapons/armst_tt.json` | scanner extraction difference |
| 6× `ammunition/*` | candidate loses populate enrichments (references/warnings/derived) — canonical preserved |

## New / changed inheritance facts

- `armst_Optic_PSO1_DovetailRU.et` → `Optic_PSO1.et` → `Optic_PSO1/Optic_PSO1_base.et` (external tail).
  Reference-graph edges 261 → 263: the new entity and its `inherits` edge to `Optic_PSO1.et` were added.
- Verified AEK-971 chain in the primary mod source: `armst_AEK971...` presence was tested via the workaddon; the primary mod itself currently contains NO AEK-971 prefab (control point remains the `Armst_Work` prototype / AEK971_TEST docs).
  - PSO-1 / PSO-1_ak both inherit `Optic_PSO1/Optic_PSO1_base.et` (external) and there is a local root-level `armst_Optic_PSO1_DovetailRU.et` thin child.
- TT / 7.63×25 chain resolved: `Ammo_763x25.conf` ({9379B9A38F29D508}) → `Ammo_763x25_Ball.et`; TT magazine `Magazine_763x25_TT_8rnd_Ball.et` inherits PM mag base and maps 8 × `Ammo_763x25_Ball`.

## Ammo / config / projectile knowledge delta

All source values below are verified from the primary addon; gameplay classification remains a separate layer.

- Projectiles in the addon (14): 5.45 7N6, 5.56 M193, 7.62×39 57N231, 9×18 57N181, 9×19 M882, 7.63×25 Ball, 7.63×25 (LPS-based orphan), 9×39 SP5, 9×39 SP6, 12ga family (Ammo_12ga, Ammo_12ga_shell, Ammo_12ga_shell_test, Ammo_Buckshot_pellet), VOG25 grenade.
- Present batteries: `Ammo_9x39.conf` [SP5, SP6], `Ammo_763x25.conf` [763x25_Ball], `Ammo_12g.conf` [12ga, 12ga_shell, 12ga_shell_test]; vanilla-family configs referenced from magazines (545x39, 556x45, 762x39, 762x54, 9x18Mak, 9x19).
- Deltas / notes:
  - The six `ball` copies (7N6/M193/57N231/57N181/M882) are pure `Ammo_Bullet_Base` inherits: InitSpeed 750, Mass 0.01, Diameter 8, kinetic DamageValue 50, ballistic table `AIBT_Bullet_Base.conf`.
  - 9×39 SP5 (290 m/s, 19.59 g, kinetic 130) vs SP6 (305 m/s, 25.59 g, kinetic **150** local). The source SP6 already has a *higher kinetic damage* than SP5 — the desired AP/BP trade-off is NOT yet enforced by current source values, consistent with the policy note that 9×39 is a first-validation family.
  - 7.63×25 Ball: InitSpeed 430 (±15), Mass 0.00804, Diameter 9.1, Length 15.5, PenetrationDepth 20, PenetrationDensity 0.65, PenetrationSpeed 355, kinetic DamageValue 50 (inherited), ballistic table `AIBT_9x19_Ball_M882.conf`. Separate legacy `Ammo_763x25.et` (LPS-based) is NOT in the resolved TT chain.
  - 5.45/5.56/7.62×39/9×18/9×19 currently have ball-only ARMMST projectiles; AP/BP variants are not present in the primary addon source.
- Magazine loaded mappings verified (primary mod magazines): PM 8rnd → 57N181×8; APB → 57N181×20 (PM pattern); PP91/SR2 30rnd → 57N181×30; TT → 763x25_Ball×8; M9 → M882×15; SVD (Sniper and 7BZ3API mags) → both resolve to 57N323S×10 (the “7BZ3API” mag actually carries LPS); PK 250 → 57N323S×250; 5.45 AK 30rnd and STANAG mags → loading binding NOT resolvable from available sources (see open items); 9×39 30rnd/20rnd SP5/SP6 mags → map to their SP5/SP6 projectiles; 12ga shell mixes slug + buckshot by mapping; 12ga buckshot maps pellet + shell.
- Tracer/incendiary effects remain separate from primary kinetic (7T3/M856/M196 0.75 incendiary; 57T231P/7T2; 7BZ3 additive 3) — preserved, not merged.

## Attachment / optic compatibility delta

- The primary mod **contains** the `AttachmentOpticsARMST_DovetailRU` marker class (script market excerpt in `agent/SAFE_PREFAB_EDITOR.md`), and exactly **one** surveyed usage: the new thin-child optic `armst_Optic_PSO1_DovetailRU.et` (module side only).
- Nevertheless, **no ARMST weapon slot in the primary addon currently requests `AttachmentOpticsARMST_DovetailRU`** — weapon-side slots still serialize legacy/built-in classes: `AttachmentOpticsDovetailAK` (AKM slot `{65AE4CB5E23C0F61}`, 9a91/VAL/VSS/VSK94 slot `{60AAE435165C80B8}`, SVD `{58E2BCF926D50DE5}`), `AttachmentOpticsDovetailSVD` (SOC94 stock rail `{65AE4CB5E23C0F7D}`), `AttachmentOpticsG36` (G36 `{6A0470709BAE058B}`), RIS1913 (Groza, slots disabled).
- This is a **module-side-only** state: the DovetailRU compatibility family is present on the optic side but not yet wired to weapon slots in the primary mod (authoring policy requires migrating both sides). Confirmed as a knowledge delta, not an error to auto-fix.
- Magazine wells active in the primary mod: `MagazineWell12g`, `MagazineWell763x25`, `MagazineWell9x39`, `MagazineWell9x39_9a91`, `MagazineWellAPB`, `MagazineWellPP91`, `MagazineWellVZ58_762`, `MagazineWellM9Beretta`, `MagazineWellStanag556`, stock/handguard/underbarrel/muzzle slots as documented per family.

## AEK / PSO / TT control-point findings

- **AEK-971**: not present as an entity in the primary mod catalog; the validated AEK-971 prototype lives in `Armst_Work` (`armst_AEK971_test_v12_NAME_DESCRIPTION.et`) and as `reports/samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et`. Primary addon remains the source of truth for component IDs used by AEK (e.g. `Rifle_AK74N_base` external parent `{EAE9A298979C4721}`, FireMode confs).
- **PSO-1 / DovetailRU**: primary addon now ships the DovetailRU thin child (`armst_Optic_PSO1_DovetailRU.et`) and the marker class; optic mounts per active policy; weapon slots not yet migrated in the primary addon.
- **TT / 7.63×25**: confirmed resolution `Ammo_763x25.conf → Ammo_763x25_Ball.et`; TT magazine loads `Ammo_763x25_Ball`; values match the supplemental `Configs(1).zip` knowledge.

## AP/BP candidate map discovered from the primary addon source

Gameplay-candidate classification only; NOT a claim about real-world cartridges.

| Caliber | АП / anti_personnel candidate (higher kinetic, softer) | БП / armor-piercing candidate (penetrator) | Source-backed? |
|---|---|---|---|
| 9×39 | `Ammo_9x39_SP5_Ball.et` (290, 19.59 g, kinetic 130) | `Ammo_9x39_SP6_Ball.et` (305, 25.59 g, kinetic 150, deeper idea) | both exist as distinct local projectiles; current values do not yet enforce the intended damage-vs-penetration trade-off |
| 7.63×25 | custom soft/incendiary child not present | existing `Ammo_763x25_Ball.et` (higher-penetration baseline candidate) | only Ball exists in resolved config |
| 12ga | `Ammo_12ga` buckshot (BP-ish per policy wording; kept as its own family) | `Ammo_12ga_shell` (slug-style 720 m/s, 100 dmg, PenDensity 3.36) | both exist |
| 5.45×39 / 5.56×45 / 7.62×39 / 9×18 / 9×19 | ball rounds present | AP/BP variants **not present** in primary addon source | ball-only; candidate pairs must come from later authoring |
| 7.62×51 / 7.62×54R / 12.7×99 / 12.7×108 / 14.5×114 / 25×137 | not part of the primary addon entity set in this snapshot | not present in this snapshot | known from supplied Config snapshots only |

## Unresolved external dependencies / open items

- **Magazine binding for 5.45 AK-30rnd and 5.56 STANAG magazines**: chains resolve through `Core/Magazine_Base.et` whose addon copy only contains `ARMST_ITEMS_STATS_COMPONENTS` + `InventoryMagazineComponent` — no `MagazineComponent`/`AmmoConfig`/`AmmoMapping` in any available source. Treat as unbound in source until a runtime/PBO verification or an addon authoring fix; acknowledge in `reports/KNOWLEDGE_STATUS.md` debt.
- `armst_TT_prefab_balance_profile.et` is a JSON document with a `.et` extension → scanner PARSE warning (harmless; not an entity).
- Numerous weapons/ammo inherit from base-game prefabs absent on disk (AK74 bases, Handgun_Base, Rifle_M16A2, Optic_PSO1_base, etc.). Values resolved only where local authoring exists; external values marked external/unknown.

## Scanner limitations discovered

- `scan_build.py` cannot parse `AmmoMapping`/config indirections for magazines that inherit a `Magazine_Base` shadowed copy; raw `.et` reads are required to derive loaded loads (already done above).
- The scanner classifies amber/JWT/particle assets oddly (the 12ga particle pair) and reports `attachment` counts inconsistently between `scan state` (7) and `scan_summary` (10) — same inconsistency already present in canonical data; left as scanner quirk.
- Reference resolution reports external parents richer in the candidate (explicit external parent GUID+raw), which caused the 3 weapon catalog diffs; canonical retained enriched handgun-derived data is intentionally preserved.

## Canonical files synchronized (this pass)

- `catalog/misc/armst_optic_pso1_dovetailru.json` (new)
- `catalog/optics/optic_pso1.json` (used_as_base_by updated)
- `indexes/references.json` (entity_count 124 → 125)
- `indexes/reference_graph.json` (edges 261 → 263, new entity)
- `agent/scan_state.json` (counts + warnings 1, source root unchanged)
- `reports/scan_summary.json` / `reports/scan_summary.md`
- `reports/anomalies.json` / `reports/anomalies.md` (records the new TT profile PARSE anomaly)
- `reports/inheritance_issues.json` / `reports/inheritance_issues.md` (adds the new DovetailRU entity entry)
- `snapshots/primary_candidate/` (isolated candidate snapshot retained with this commit for provenance)

## Manual / mixed-history files intentionally preserved (NOT overwritten)

- `reports/KNOWLEDGE_STATUS.md`, `reports/PREFAB_AUTHORING_GUIDE.md`, `reports/CONFIG_AUTHORING_GUIDE.md`,
  `reports/SCRIPT_MODULE_AUTHORING_GUIDE.md`, `reports/OPTICS_COMPATIBILITY_SYSTEM*.md`, `reports/AMMO_AP_BP_POLICY.md`,
  `reports/AEK971_TEST_CHECKPOINT_V8.md`, `reports/samples/*`
- `indexes/script_reference/*` (incl. `optic_compatibility_policy_v2.json`), `indexes/ammunition_reference/*`,
  `indexes/magazine_reference/*`, `indexes/config_reference/*`, `indexes/prefab_authoring*`
- `schema/compatibility.schema.json`
- `catalog/weapons/armst_m9.json`, `catalog/weapons/armst_pm.json`, `catalog/weapons/armst_tt.json` — canonical copies contain handgun-derived enrichment (fire modes, physical, magazine well, camera recoil IDs, derived single_rpm/moa) not re-extractable from the isolated primary-addon scan; marked as mixed manual+generated history.
- All 6 changed `catalog/ammunition/*` JSONs — canonical copies carry Configs.zip-supplement references, warnings and derived magazine-loading enrichments; candidate would silently drop them.

## STOP conditions / ambiguous items

- No STOP conditions triggered. One ambiguity is documented: the primary addon ships the DovetailRU marker and a DovetailRU module, but no weapon slot requests `AttachmentOpticsARMST_DovetailRU` yet — this is knowledge-state, not an error, and none of it was edited in the addon (addon READ ONLY).

## Validation status

- Primary addon source hashes: unchanged (PASS).
- Candidate JSON parses (script-validated; all changed files parse).
- Canonical files changed by sync parse (verified).
- No manual protected file unintentionally changed (git diff reviewed).
- No unexplained mass deletion.
- Active DovetailRU policy preserved (manual policy files untouched).
- AP/BP policy preserved as gameplay layer (report only, no source edits).
- TT supplemental knowledge not regressed (Ammo_763x25.conf → Ammo_763x25_Ball chain intact).
- Git diff contains only explainable knowledge-sync changes + this report.

**Recommendation: SAFE TO REVIEW**