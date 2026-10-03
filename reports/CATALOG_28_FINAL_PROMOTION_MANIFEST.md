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

---

## G. Final provisions (owner message 2026-10-03)

**G.1 Scanner classification fixed (committed, `ca4c870`).** `classify()` now checks
`/grenades/` **before** the `WeaponComponent` heuristic, so `armst_Smoke_ANM8HC/RDG2`
(which inherit `SmokeGrenade_Base.et`) classify as **grenade**. Regression tests added
(grenade-with-WeaponComponent → grenade; weapon-with-WeaponComponent → weapon). Final
candidate: weapons **70 → 68**, grenades **2 → 4**, **0 smoke under `weapons/`**.

**G.2 MP-133 ← M21 inheritance (checked, no action).** The chain is the **pre-existing
ARMST design**: `armst_Shotgun_mp_133.et` → `armst_shotgun_base.et` →
`{B31929F65F0D0279}Prefabs/Weapons/Rifles/M14/Rifle_M21.et` (vanilla base). The catalog
resolves it correctly (and now deeper via `base_game_snapshot`). Not a scan artifact, not
introduced by #28.

**G.3 Review of the 106 `data`-changed entries (finished).**
- Dominant class: newly **resolved base-game inheritance** — `attachment_slots`,
  `fire_modes`, `sights`, `ballistic_table`, `effects`, inherited `Mass`/dispersion
  previously empty, now populated from `base_game_snapshot`.
- **Genuine value changes** (provenance excluded): **52 entries**, concentrated in
  **ammunition** (`armst_ammo_9x39_sp5/sp6`, `763x25`, `12ga`, buckshot pellet:
  `Mass`/`InitSpeed`/`PenetrationDepth`/`PenetrationSpeed`/`ballistic_table`) and
  **magazines** (`ammo_mapping` length/content corrected to the source) — reflecting the
  current restored addon vs the 2026-09-25 snapshot, not a scanner defect.
- Flagged anomaly: **`Assets/Toz/1.et` → `catalog/weapons/1.json`** — an oddly-named
  prefab in the addon; not a scanner bug, but worth renaming/reviewing.

**G.4 Final candidate (isolated, rebuilt with the fix).** **181 entities** (68 weapons /
53 magazines / 22 ammunition / 12 optics / 12 attachments / 4 grenades / 2 tripods /
4 core / 2 particles / 2 misc), 1 warning. `build_weapon_index/family_pages/
balance_pages --check` = **0**, `check_data_quality` = **0**. Dirty worktree == committed
HEAD catalog (0 diff). Corpus 1,404 files preserved (aggregate SHA `15380703…`).

**G.5 Publication.** The 30 `SOURCE_ABSENT_AT_HEAD` entries are approved for exclusion
from the active catalog (game resources are not deleted). Canonical generated files are
still **not published** by the agent; the reviewed promotion set is ready and awaits the
explicit publish go-ahead, followed by a fresh hosted CI run. The scanner fix is a
separate committed source change (`ca4c870`).

---

## G.6 Pre-push gate results (2026-10-03) — PUBLICATION PAUSED

Frozen input verified: Weapons committed HEAD `b88bc537b8fb0b14aeecda9856b7cce1e17448d8`
(unchanged), ID `ARMSTPLATFORMWeapons`. Isolated HEAD-based candidate rebuilt with the
current scripts (`%TEMP%\opencode\mp133_head2`).

**PASS**
- HEAD2 catalog == dirty-final catalog (0 diff); **181 entities** exactly
  (68/53/22/12/12/4/2/4/2/2); 0 smoke under `weapons/`, grenades correct.
- MP-133 GUID `63FF6FDCA4E7E735` present; template/animation consistent with source.
- determinism: generated-set hash stable across a re-run.
- `build_weapon_index/family_pages/balance_pages --check` = 0; `check_data_quality` = 0.
- corpus **1,404** files aggregate SHA `153807035686AE3FEB9F9A55CA16986FFC61E33A033EABAB1420344A28789B4E`
  identical (HEAD2 == working repo); authored docs unchanged.

**BLOCKER 1 — new test failure once the catalog is promoted**
- `agent/tests/test_balance_report_regressions.test_9x39_narrative_tracks_current_catalog`
  asserts the OLD snapshot values `` `armst_Ammo_9x39_SP6_Ball.et`: InitSpeed=305 `` and
  `PenetrationDepth=5.55`; the promoted catalog's source-truth narrative yields
  `InitSpeed=290` and `PenetrationDepth=6` (the source changed between the 2026-09-25
  snapshot and now). Publishing the catalog without a minimal test update makes CI fail.
- **Proposed minimal update** (2 expected values: 305→290, 5.55→6) — requires owner
  approval; it is a source/test change, not part of the generated-only manifest.

**BLOCKER 2 — integrity gate NOT RUN locally**
- `check_repository_integrity.py` requires `jsonschema`; no locally available Python has
  it (Rizom / Blender 4.5 / Blender 5.2 / Adobe; `pip` unavailable). Reported **NOT RUN**,
  not PASS. Hosted CI installs `jsonschema`, but the owner's pre-push gate asks for it
  locally.

**STATUS:** `#28_PUBLICATION_BLOCKED_PENDING_TEST_UPDATE_AND_JSONSCHEMA_DECISION`.
**No canonical generated file was published**; the working repo catalog is unchanged.

---

## H. Addendum — owner decisions in flight

- Owner authorized the catalog publication subject to the pre-push gates
  (comment 5968616207). Gates are **not all satisfiable** (Blocker 1/2 above) ⇒ the
  promotion is on hold pending the two decisions.
- `Assets/Toz/1.et` left unchanged; tracked separately in issue #30.
- T2a preparation is authorized to start only **after** the #28 promotion is published
  and its fresh hosted CI is inspected; if CI is red, pause T2 until #28/#29 are
  dispositioned.

---

## I. Publication result (2026-10-03) — PUBLISHED, CI GREEN

Owner approved the two remaining items (test update; `jsonschema` gate deferred to
hosted CI). The reviewed **generated-only** promotion was published as **one commit**:

- **`5c443a94ff0f53b839e7a1909c4f11e382825e47`** (push `8070340..5c443a9`, no force).
- Staged exactly the manifest: **177 modified / 119 deleted / 30 added**
  generated+derived files, plus the approved `test_balance_report_regressions.py` 9x39
  SP6 update (`InitSpeed=305→290`, `PenetrationDepth=5.55→6`), asserted against the
  specific SP6 line. No corpus/authored/live-addon files staged.
- **Local:** 82 tests OK; index/family/balance `--check` = 0; data-quality = 0;
  `git diff --check` clean; corpus **1,404** files SHA `15380703…` preserved;
  `check_repository_integrity.py` **NOT RUN** locally (jsonschema) — deferred to CI.
- **Hosted CI run [37119940835](https://github.com/Dubelkrya/Weapon_ARMA_X/actions/runs/37119940835):**
  `validate` job = **success**, every step green (scanner/parser regressions, repository
  integrity, weapon index/family/balance freshness, catalog data-quality) ⇒
  **`CI_ALL_CHECKS_PASS`**.
- Frozen input `b88bc53` unchanged; `Assets/Toz/1.et` unchanged (issue #30). T2a is now
  unblocked.
