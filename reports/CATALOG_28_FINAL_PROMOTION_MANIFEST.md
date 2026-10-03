# Catalog #28 — final promotion preparation (isolated candidate, READ-ONLY)

**Status:** `CANDIDATE_PREPARATION_IN_PROGRESS; CANONICAL_PUBLICATION_BLOCKED`.
Source: Issue #28 + comment 5968408249. All work is in isolated copies; the working
repo and the live Weapons addon are **not** modified. `SOURCE_INTENTIONALLY_ABSENT` is
restated as **`SOURCE_ABSENT_AT_HEAD`** (no authorial-removal intent proven).

Candidate (current **dirty** addon worktree): `%TEMP%\opencode\mp133_rescan\repo`.
Committed-HEAD candidate: `%TEMP%\opencode\mp133_head\repo` (extracted with
`git archive HEAD`; the owner worktree was not reset/cleaned).

---

## A. Classification anomalies

**Two smoke grenades moved `grenade → weapon` — scanner classification defect (source-backed):**
- `9DB69176CEF0EE97`: old `catalog/grenades/smoke_anm8hc.json` (`Smoke_ANM8HC.et`,
  kind=grenade) → new `catalog/weapons/armst_smoke_anm8hc.json`
  (`Prefabs/Weapons/Grenades/armst_Smoke_ANM8HC.et`, kind=weapon).
- `77EAE5E07DC4678A`: old `catalog/grenades/smoke_rdg2.json` (`Smoke_RDG2.et`) → new
  `catalog/weapons/armst_smoke_rdg2.json` (`…/armst_Smoke_RDG2.et`, kind=weapon).
- Source check: `armst_Smoke_ANM8HC.et` inherits
  `Prefabs/Weapons/Core/SmokeGrenade_Base.et` — it is a grenade by source.
- Cause: `scan_build.classify()` checks `has_comp(resolved, "WeaponComponent")` (line
  468) **before** the `/grenades/` folder heuristic (line 474); the resolved chain
  includes a `WeaponComponent`, so the grenade is misclassified as a weapon.
- **Recommendation:** fix `classify()` ordering (grenade folder/`GrenadeComponent`
  before the generic weapon heuristic) — a **separate scanner diff**, not part of this
  promotion; do not silently accept smoke grenades as weapons.

**Other `role` changes (kind unchanged):** 10 entries flipped `leaf ↔ base` due to
inheritance re-resolution (e.g. `rifle_hkg33` → `armst_rifle_hkg33_base`,
`armst_tt` → `armst_pistol_tt_base`, `optic_pso1` → `armst_optic_pso1`). These are
renames + role recomputation, not gameplay reclassification.

## B. Field-level review of changed entries

- Catalog entries changed: **149** (`data` changed: **106**; `data` unchanged
  (inheritance/references/provenance churn only): **43**).
- Top-level sections touched: `inheritance` 149, `references` 109, `data` 106,
  `derived` 65, `classification` 4, `identity` 2, `source` 2.
- **MP-133** (GUID `63FF6FDCA4E7E735`, same relpath `catalog/weapons/armst_shotgun_mp_133.json`):
  18 differing leaf paths, all **additive resolution** from the base-game snapshot:
  - `inheritance.chain`: 2 → 7 entries (adds `armst_Rifle_M21.et`, `Rifle_M21_base`,
    `LongRangeRifle_Base`, `Rifle_Base`, `Weapon_Base` via `base_game_snapshot`);
    `external_parents`: 1 → 0; `chain_depth_base_game_snapshot = 4`.
  - newly resolved: `data.physical.Mass=3`, `data.ballistics.dispersion_diameter=0.4`,
    `data.sights.ranges` (10 ranges), `data.attachment_slots` (`AttachmentOpticsM21`),
    `derived.approx_moa`/`dispersion_m_per_m`, and additional `references`
    (FireModes/Recoil/TriggerEffects, `Muzzle_M21.ptc`).
  - **Core fields preserved:** `data.magazine.magazine_template` (`armst_12ga_Buckshot`),
    `data.animation.anim_graph`/`anim_instance`, `fire_modes` — **unchanged**.
  - The old path `Prefabs/Weapons/Rifles/Shotgun/armst_mp_133.et` (in old
    `armst_mp_133.json`) is the superseded relocation; identity is preserved by GUID.
- **High-impact review continues** for the 106 `data`-changed entries; the owner's list
  (weapon/magazine/ammunition relationships, `AmmoMapping`, references) is being checked
  entry-by-entry; unknown values are retained as unknown.

## C. The 30 `SOURCE_ABSENT_AT_HEAD` entries

- All 30 were already shown absent from the committed HEAD
  (`git cat-file -e HEAD:<resource>` → absent for 30/30).
- Candidate-reference scan: **9 are unreferenced anywhere** in the candidate
  (`optic_4x20`, `tripod_6t7_nsv`, `armst_groza1`, `oc_groza`, `rifle_9a91`,
  `rifle_9a91_suppressor`, `rifle_val`, `rifle_vsk94`, `rifle_vss`) → purely historical.
- **21 are referenced only by generated `indexes/config_reference/ammo_configs.json`
  and/or preserved historical `reports/live-addon/**`** — i.e. dangling external/config
  references and historical prose, **not cataloged entities** of the current snapshot.
  No current weapon/magazine/ammunition entity resolves them as a local source.
- **No unproved claim of intentional deletion.** They remain recoverable through Git.

## D. Committed-HEAD vs dirty candidate

`git archive HEAD` was extracted to a separate copy (`%TEMP%\opencode\mp133_head\wpn`) and
scanned with a separate knowledge copy; the owner worktree was **not** reset/cleaned.

- Generated catalog: **identical** — **181 entities** in both, `only-dirty = 0`,
  `only-head = 0`, `changed dirty-vs-head = 0`; stale counts identical (972 each).
- The dirty files (SPAS-12 `*.asi/*.agf`, MP-133 `*.meta`) **do not affect the generated
  catalog** (they are not `.et/.conf/.meta` inventory or the scanner normalises them).
- ⇒ Either the current dirty worktree or the committed HEAD is a valid frozen input for
  the catalog; the catalog content is source-state-independent for these dirty files.
  **Recommendation:** freeze the scan input as the **committed HEAD** for a reproducible
  promotion, while documenting that the owner's dirty files are non-catalog-affecting; if
  the owner prefers the dirty tree, the output is byte-identical either way.

## E. Derived pages + checks (isolated)

Regenerated in the dirty candidate (all exit 0): `WEAPON_INDEX.md`,
`reports/families/{AK_FAMILY,CALIBER_9X39,SHOTGUNS}.md`,
`reports/balance/CALIBER_9X39_BALANCE.md` — **5 changed, 0 added, 0 deleted**.

| check | result |
|---|---|
| `build_weapon_index.py --check` | **exit 0** (after regeneration) |
| `build_weapon_family_pages.py --check` | **exit 0** |
| `build_balance_pages.py --check` | **exit 0** |
| `check_data_quality.py` | **exit 0** (INFO-only) |
| `check_repository_integrity.py` | **NOT RUN** locally (jsonschema missing) |

Hosted CI currently fails on the **old catalog's** stale `WEAPON_INDEX.md`; the reviewed
promotion must include these regenerated pages so the check can pass (do not disable it).

## F. Final promotion manifest (PLAN; not applied; owner approval required)

| Scope | Action |
|---|---|
| `catalog/{10 dirs}/*.json` | replace generated set: 181 entities; 149 changed, 32 new; **91 relocations** = same-GUID replace; **30 `SOURCE_ABSENT_AT_HEAD`** = delete only as an owner-approved historical batch |
| `indexes/*.json`, `indexes/generated_config_reference/ammo_configs.json` | replace |
| generated `reports/*` (scan_summary/unresolved/inheritance/anomalies/weapon_ballistics) | replace |
| `schema/{entity,weapon,magazine,ammunition}.schema.json` | replace |
| `agent/scan_state.json` | replace |
| `WEAPON_INDEX.md`, `reports/families/*`, `reports/balance/*` | replace (5 files) |
| `catalog/**/*.et\|.conf\|.meta` (1,404) + hand-authored docs + `CURRENT_AI_SYNC.md` + supplied indexes | **preserve byte-identical** |
| `classify()` grenade ordering | **separate scanner diff** (not in this promotion) |

**Risk ranking:** (1) 30 `SOURCE_ABSENT_AT_HEAD` deletions — explicit batch approval;
(2) 106 `data`-changed entities — field review (MP-133 reviewed: additive only, core
fields preserved); (3) 32 new + smoke-grenade classification (separate fix);
(4) derived-page regeneration (verified `--check` 0).

**Eligibility:** preflight PASS, deterministic, corpus preserved, dirty==HEAD catalog,
checks pass after regeneration. **Canonical publication remains BLOCKED** pending the
owner's review of the manifest and batch approval of the 30 deletions.

## Tests / NOT RUN

- Not run by agent: Workbench/game. `check_repository_integrity.py` locally: NOT RUN
  (jsonschema missing) unless installed in the isolated env.
- Publication requires a fresh hosted CI run after promotion.
