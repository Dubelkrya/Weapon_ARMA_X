# Weapon_ARMA_X — project-wide knowledge audit and research backlog (2026-10-04)

**Status:** repository structure + representative source/document audit; read-only on all gameplay resources. This is **not** a claim to have opened all 2,244 tracked paths, inspected unavailable local addons, independently compiled scripts, or run Workbench. Complementary evidence/official links: [ENFUSION_WEAPON_SOURCE_ATLAS_2026-10-04.md](ENFUSION_WEAPON_SOURCE_ATLAS_2026-10-04.md). For the MP-133-specific G4-A route assessment see [MP133_G4A_RELOAD_SWAP_ROUTE_AUDIT.md](MP133_G4A_RELOAD_SWAP_ROUTE_AUDIT.md).

**Repository / research branch:** `Dubelkrya/Weapon_ARMA_X`, `t4b/installed-mag-probe`. Investigation started from source checkpoint `4807dfd7244c27a263b83e10f8f5ade07f1f87ae`; during the investigation the concurrently active G4-A agent published `ad89a18195c669b060d0707750ef73615b15e8e0` (G4-A report + sync/index update). The source atlas was added afterward in a separate documentation-only commit. **No preexisting report, sync/index file, catalog, gameplay file or open PR was overwritten.**

## 1. Inventory and ownership

The Git tree at the stated 4807dfd checkpoint returned **2,244 tracked entries (files plus directories)**. This is a repository-tree count, **not a file count**. Main knowledge areas:

| Area | Main paths | Content/authority |
|---|---|---|
| Agent policy and safety | [AGENTS.md](../AGENTS.md), [PRIMARY_MOD_POLICY.md](../agent/PRIMARY_MOD_POLICY.md), [SAFE_PREFAB_EDITOR.md](../agent/SAFE_PREFAB_EDITOR.md), [CURRENT_AI_SYNC.md](../docs/sync/CURRENT_AI_SYNC.md) | Startup, addon-root validation, GUID/meta preservation, non-destructive Git workflow; policies outrank old narrative reports. |
| Scanner and generated references | `agent/scripts/scan_build.py`, `et_parser.py`, `base_game_snapshot.py`, `agent/scan_state.json`; `catalog/`, `indexes/`, `reports/scan_summary.*` | Snapshots of primary addon / vanilla references, not authoritative live or animation-source inventories. |
| Data model and quality | `schema/*.json`, `agent/scripts/check_data_quality.py`, [DATA_QUALITY.md](DATA_QUALITY.md), [unresolved references](unresolved_references.md), `.github/workflows/repository-integrity.yml` | Detect explicit contradictions vs unresolved coverage; hosted CI is not Workbench/runtime proof. |
| Weapon families and balance | `reports/families/AK_FAMILY.md`, `CALIBER_9X39.md`, `SHOTGUNS.md`, `reports/balance/CALIBER_9X39_BALANCE.md` | Generated comparisons whose validity depends on scan date and source inheritance. |
| Prefab and config authoring | [PREFAB_AUTHORING_GUIDE.md](PREFAB_AUTHORING_GUIDE.md), [CONFIG_AUTHORING_GUIDE.md](CONFIG_AUTHORING_GUIDE.md), [SCRIPT_MODULE_AUTHORING_GUIDE.md](SCRIPT_MODULE_AUTHORING_GUIDE.md) | Authoring guidance; distinguish Workbench-backed rules from general recommendations. |
| Optics and attachments | [OPTICS_COMPATIBILITY_SYSTEM_V2.md](OPTICS_COMPATIBILITY_SYSTEM_V2.md), `indexes/script_reference/optic_compatibility_policy_v2.json`, [nested RIS audit](NESTED_DOVETAIL_RIS_STORAGE_AUDIT_2026-09-21.md) | Approved gameplay compatibility vs separate physical attachment geometry and research-only nested storage. |
| Ammunition | [AMMO_AP_BP_POLICY.md](AMMO_AP_BP_POLICY.md), `indexes/ammunition_reference/`, `indexes/config_reference/`, `indexes/generated_config_reference/` | Gameplay role AP/BP, magazine loaded mapping, available projectiles and actual ballistic reference must remain separate dimensions. |
| MP-133 research | [MP133_INDEX.md](MP133_INDEX.md), [Issue #27](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27), [Issue #34](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34), more than 25 distinct versioned MP-133 reports | G0–G3 experiments and current G4-A route design coexist with frozen V1/V2 history; read latest owner observations. |
| Published game-lab source | `labs/ARMSTMP133T4A_SetProbe/`, `labs/ARMSTMP133T4B_InstalledMagProbe/`, manifests | Git-published lab **copies**; owner-loaded local addon is independent and may diverge. |
| Core / external Chungus | [Issue #33](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/33), [V2.7 Core study](MP133_ANIMATION_LAB_V27_C2_TRACE_AND_CORE_ISOLATION.md), [V2.8 Chungus comparison](MP133_ANIMATION_LAB_V28_REFERENCE_COMPARISON.md) | Historical excerpts and local-audit task; do not relabel as fresh access to actual current external addons. |

**Primary source boundary:** `Weapon_ARMA_X` is a knowledge/tools repo, **not the live `ARMST-PLATFORM---Weapons` addon**. Never use Git's catalog as grounds to mutate live weapons, Core, worlds/layers or user-local untracked work. Project reads must verify `addon.gproj` ID rather than locating a superficially similar sibling folder.

## 2. Snapshot freshness: actionable documentation debt

**Found in checked-in source:**
- `agent/scan_state.json` and `reports/scan_summary.md` say **2026-10-03**, **181 entities**; classifications include **68 weapons**, **53 magazines**, **22 ammunition**, **12 optics**, **12 attachments**; scan root is a **temporary extracted path** `...AppData/Local/Temp/opencode/mp133_head2/wpn`, not the authoritative current live addon root. A past legitimate extraction can inform research, but this scan does not establish the owner's live-addon state on 2026-10-04.
- [DATA_QUALITY.md](DATA_QUALITY.md) explicitly labels its **0 errors / 55 warnings / 32 informational findings** as the **2026-09-24 checker snapshot** and says original catalogs were not fully regenerated with improved `AmmoMapping` / AmmoConfig extraction. Do **not** propagate these figures as current CI output.
- `indexes/config_reference/manifest.json` says generated **2026-09-15** from `Weapons.zip`/`Configs.zip` plus later TT supplemental evidence; counts were **not recomputed** after that update. `indexes/generated_config_reference/` is a different, scanner-created coverage surface.
- [KNOWLEDGE_STATUS.md](KNOWLEDGE_STATUS.md) says that live Workbench source wins and documents newer case-specific deviations from older optic `DovetailRU` snapshot (nested adapter research). Preserve this precedence.
- [MP133_INDEX.md](MP133_INDEX.md), [CURRENT_AI_SYNC.md](../docs/sync/CURRENT_AI_SYNC.md) and [G3B2 design](MP133_V3_G3B2_TRANSACTION_DESIGN.md) contain historical earlier-stage paragraphs such as `G3-B2 DESIGN ONLY` or `owner compile pending`; those **are not the present state**. New G4-A pointers were published during this research, but old descriptions inside the documents remain valuable as historical chronology and can confuse a new agent if not dated.
- The active G3B2 source state is two retained **inventory-wide OFF and WRITE-ON** laboratory weapon fixtures and one real 3-cap `Tube3Mag`, **not** the several historical, since-deleted disposable G3B2 weapon variants.

**Recommended maintenance (not automatically performed due to overlap with [PR #31](https://github.com/Dubelkrya/Weapon_ARMA_X/pull/31)):** add a short **dated current-status section at the very top** of MP133_INDEX and CURRENT_AI_SYNC, explicitly superseding historical sections; maintain an audit link to Issue #34 and the new G4-A report; avoid overwriting the earlier timeline. Reconcile any concurrent agent changes before editing those files.

## 3. Present MP-133 evidence and the actual blocker

| Gate / claim | Evidence | Correct status |
|---|---|---|
| Clean production MP-133 ordinary short R, multiple shots, hold inspection | [Owner T0](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/27#issuecomment-5967911774), Weapons-only addon | **OWNER-RUNTIME FUNCTIONAL PASS** for that baseline, not full mag-instance/MP proof |
| T4b synthetic target +1, manual feed and a shot | [Current sync](../docs/sync/CURRENT_AI_SYNC.md), [T4b study](MP133_V3_T4B_INSTALLED_MAG_PROBE.md) | **OWNER-RUNTIME offline PASS** for its specific test |
| Real donor decrement | [G3 donor research](MP133_V3_G3_REAL_DONOR_PHASE_A.md), Issue #34 history | **OWNER-RUNTIME offline PASS**, not transaction atomicity |
| One real donor→target transfer; delayed checks | [Issue #34](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5975205409), [G3B2 script](../labs/ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/ARMST_T4B_G3B2_Transfer.c) | **Six successful owner-observed transfers** over two fill cycles; same target, donor conservation, +250/+1000, busy/full rejection |
| Physical capacity exactly 3 in tested lab fixture | [Current Tube3Mag](../labs/ARMSTMP133T4B_InstalledMagProbe/Prefabs/Test/ARMST_T4B_G3B2_Tube3Mag.et) and owner log | **SOURCE + OWNER-RUNTIME PASS** for physically installed 3-cap starting fixture |
| No stock tube replacement | [Owner empty R / double-R repro](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5975348824) | **FAIL / confirmed blocker:** native whole-mag swap can install 10-cap donor |
| G4-A lab-only sanitized graph/clip route | [Fresh G4-A audit](MP133_G4A_RELOAD_SWAP_ROUTE_AUDIT.md) | **Design candidate only**; no owner compilation/implementation/runtime PASS |
| G4-B staged per-shell animation, interruption, normal R integration | [Variant A architecture](MP133_V3_VARIANT_A_ARCHITECTURE.md) | **NOT IMPLEMENTED / NOT VALIDATED** |
| Multiplayer, network UI, atomic donor/target transfer, damage/hit | No corresponding controlled owner evidence in these reviewed sources | **UNVERIFIED** |

**Important distinction:** a 3-cap `MagazineTemplate` plus `SetAmmoCount` target cap check prevents an invalid **G3B2 transfer** after native mag swap; it does **not** globally prevent weapon swapping magazines in the vanilla `MagazineWell12g`. Do not “fix” G3B2 by relaxing target-capacity guard; inspect the native reload path.

## 4. Core and Chungus: evidence, not cargo-cult code

**Core:** owner has stated legacy SHIFT+R reload is not functional. [Issue #33](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/33) requires direct read-only validation of *current* Core and identification of source-present vs prefabs-referenced vs tested vs inactive. This pass did not have access to current private `romzet/ARMST-PLATFORM---Core` or the owner's local source (GitHub connector returned 404), so **CORE_SOURCE_UNAVAILABLE**. The historical `ARMST_SCR_PlayerMagRepacks.c` candidate and the earlier SHIFT+R code are not a validated installed-magazine transfer backend.

**Chungus:** current raw BC/Ithaca files were not found via accessible current GitHub sources in this pass. Historical V2.8 excerpts describe staged animation, pump commands and stop/continue; their existence in reported source does not prove behavior in the owner's current Chungus version. Reuse the **design pattern only** after version-matched direct source inspection; do not copy dummy-round insertion, automatic magazine spawning, implicit native `ReloadWeapon()` assumptions or third-party assets.

**Global input risk:** historical owner P2 A/B found that excluding the old global `modded SCR_CharacterCommandHandlerComponent` file restored ordinary R on other pumps. An apparently weapon-gated global override is therefore not a proven harmless shortcut. Prefer dedicated lab-bound graph/prefab approaches unless a separately scoped input experiment proves otherwise.

## 5. Research backlog for the **whole weapon project**, ranked by impact

| Priority | Work item and required evidence | Output / do-not-cross boundary |
|---|---|---|
| P0 | **G4-A route verification**: passive owner evidence for empty single R and rapid double R: exact command ID+float, same/different mag instance, clip events, chamber and carried donor before/after. | One narrow trace/report. No speculative input hooking, no code mutations before separate G4-A implementation authorization. |
| P0 | **Knowledge-status reconciliation**: latest G3B2 3-cap offline PASS, unwanted R-swap FAIL, G4A design candidate. Resolve [PR #31](https://github.com/Dubelkrya/Weapon_ARMA_X/pull/31) conflicts before editing the same index/sync sections. | A dated status header and versioned links; never erase experiment history. |
| P1 | **Official API cross-version matrix**: public docs generated 1.13.2 vs installed SDK 1.8.0.13; confirm exact signatures of magazine, muzzle, current weapon, input, action, inventory, replication and animation callbacks. | One normalized reference of **VERIFIED_INSTALLED**, **PUBLIC_ONLY**, **UNRESOLVED** with exact SDK paths; no guessed API. |
| P1 | **Native/Chungus/Core comparative mechanisms**: get exact versioned local Chungus files and Core; map input, server authority, magazine lifecycle, serialized graph/source events, prefab references, reuse risks. | Separate read-only provenance-backed reports. Do not copy third-party game assets, do not modify Core. |
| P1 | **Owner-generated canonical scan freshness**: scan the current authoritative production Weapons addon with `agent/scripts/addon_path.py` identity checks; compare to 2026-10-03 temp-extract baseline, record changes and rerun quality checks. | New snapshot with explicit `scan_date`, `mod_root`/addon ID, HEAD, provenance, counts and unresolved; **owner / separately authorized local agent only**. |
| P2 | **Ammo/config coverage**: regenerate `AmmoMapping` nested values, AmmoConfig reference completeness and projectile/AI ballistic table relationships. Distinguish allowed ammo from actually loaded projectile and primary damage from tracer/incendiary. | Refresh generated coverage *via generator*, never hand-edit catalog JSON or infer values from file names. |
| P2 | **Shotgun family audit**: the generated 10-item explicit shotgun list shares `MagazineWell12g`/template despite different real-world mechanisms. Check each real prefab/muzzle, animation graph, bolt/chamber rules and magazine semantics separately; compare RIS variant. | Source-backed per-weapon exceptions, not broad rules based only on a shared parent. |
| P2 | **Optics/attachments audit**: distinguish active `DovetailRU` gameplay policy from real mount compatibility and physical pivot/slot ownership. Reconcile unresolved nested Dovetail→RIS research with actual Workbench evidence. | Explicit compatibility + placement matrix, no speculative nested-prefab workaround. |
| P2 | **CI and catalog quality**: rerun current integrity and quality scripts in a verified local checkout; update documented counts by *that actual run*. Investigate warning classes rather than labelling unresolved values zero. | Command, environment, version, actual output and diff; green checks do not prove engine gameplay. |
| P3 | **G4-B shell animation** after G4-A runtime gate: staged Chungus-inspired insert, reliable player→weapon event bridge, exactly-once G3B2 commit, safe stop during/after commit and last shell. | Lab-only implementation subject to new explicit authorization. |
| P3 | **G5 multiplayer** after offline G4: master authority, client inventory UI consistency, interrupted RPC, dropped/reordered ack, duplicate events, weapon switching, low FPS, ammo conservation/damage. | Controlled owner runtime with exact test matrix; no auto-promotion to production. |

## 6. Repeatable research and indexing protocol

Every new reference entry should minimally contain:
1. **Entity:** prefab/class/method/command/GUID; literal names, not intuitive aliases.
2. **Source:** precise repo/path/branch/commit or official URL + stated generated SDK version.
3. **Evidence class:** source, owner-runtime, official publication, inference, unavailable.
4. **Scope/conditions:** addon and prefab, single-player vs MP, write-enabled vs disabled, actor/storage, date and game version.
5. **Known negative or contradiction:** competing older report, owner correction or failure path.
6. **Next falsifiable check:** exactly which log/compile/owner action will confirm or reject the claim.
7. **Safe reuse/license:** link external material; no unapproved code/media imports.

Recommended workflow for future AI sessions: read `AGENTS.md` → current `CURRENT_AI_SYNC.md` and recent Issue #34 → the appropriate curated source atlas and report → actual current source/SDK → propose smallest separate gate. **Never** deduce new implementation authorization from a report that merely proposes an option.

## 7. Limitations and validation of this report

- Reviewed GitHub tree structure, AGENTS.md, current sync/index, KNOWLEDGE_STATUS, DATA_QUALITY, scanner state, shotguns family, manifests, representative T4b/G3B2 lab sources, related MP-133 audits/issues and a range of official Bohemia docs/samples. **Did not exhaustively inspect all tracked file contents or raw `catalog/` entities.**
- GitHub-only access **cannot prove or hash the current local live Weapons/Core/Chungus working trees** or inspect Workbench binary ANM. Do not report `GAMEPLAY_FILES_CHANGED=0` as a full local hash result; no gameplay write was issued via this session.
- This report is a **separate additive knowledge document**. Existing generated snapshots, owner's local repos, production/Core, active lab code and open documentation PR are left unchanged. No Workbench/game or actual transfer was run.

**Next highest-value action:** collect the minimal passive two-trigger G4-A runtime trace and independently review the now-published G4-A audit before allowing any lab animation graph/code implementation. In parallel, use the source atlas to enrich SDK citations and prepare a canonical owner-side snapshot-quality refresh as a separate task.
