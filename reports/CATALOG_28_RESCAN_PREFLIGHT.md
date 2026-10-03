# Catalog rescan #28 — Phase A preflight + isolated candidate (READ-ONLY)

**Status:** `RESCAN_PREFLIGHT_PASS; ISOLATED_CANDIDATE_STATUS = COMPLETED / DIVERGES SUBSTANTIALLY / PUBLICATION NOT READY`. Source: Issue #28 + comment 5968124784. The working repo was **not modified**; the scan ran in an isolated copy (`%TEMP%\opencode\mp133_rescan\repo`).

## Source / Git evidence

- addon root resolved + validated: `...\ARMST-PLATFORM---Weapons`, `ID "ARMSTPLATFORMWeapons"`, `GUID "6A70E400C54051DC"`.
- knowledge repo: `main` `7d645f3` (+ untracked CI #29 report).
- Weapons repo: `main` `b88bc53`, **dirty** (SPAS-12 anims + MP-133 `.meta`) — read-only, untouched.
- live addon has **no** `Prefabs/Weapons/Rifles/` directory (reorganized to `Russian`/`Western`).

## Output allowlist (exact, from scan_build.py)

- deleted/regenerated: `catalog/{weapons,magazines,ammunition,optics,attachments,grenades,tripods,core,particles,misc}/*.json`; `indexes/{weapons,magazines,ammunition,optics,attachments,references,reference_graph}.json`; `indexes/generated_config_reference/ammo_configs.json`; `reports/{scan_summary,unresolved_references,inheritance_issues,anomalies}.{json,md}`; `reports/weapon_ballistics.json`; `schema/{entity,weapon,magazine,ammunition}.schema.json`; `agent/scan_state.json`; `agent/scripts/working_tables/entities.json`.
- preserved: `catalog/**/*.et|.conf|.meta`, supplied reference indexes, curated reports, authored docs, unrelated schemas.

## Safety evidence (preflight PASS)

- `REPO_ROOT` redirects catalog/index/report/schema outputs; `BASE_GAME_SNAPSHOT_ROOT` defaults to the candidate catalog; `dump_working_tables` writes to `SCRIPT_DIR/working_tables` — hence the full isolated copy.
- no writes to the working repos: knowledge `git status` shows only the untracked #29 report; Weapons dirty set unchanged.
- **preservation:** `catalog/**/*.et|.conf|.meta` = 1404 files, aggregate SHA-256 `153807035686AE3FEB9F9A55CA16986FFC61E33A033EABAB1420344A28789B4E` — identical before/after in the isolated tree (and to the original).
- authored docs unchanged: `docs/sync/CURRENT_AI_SYNC.md`, `AGENTS.md`, `reports/README.md`, `reports/KNOWLEDGE_STATUS.md`, `agent/scripts/scan_build.py`, `agent/scripts/addon_path.py`.
- **determinism:** identical stdout across two runs; generated-set hash unchanged after a third run (`gen_hash_changed=False`).

## Candidate vs current main

- generated files: orig **292** → candidate **203** (NEW **32**, DELETED **121**, CHANGED **169**, UNCHANGED **2**).
- candidate scan summary: **181 entities** (70 weapons / 53 magazines / 22 ammunition / 12 optics / 12 attachments / 2 grenades / 2 tripods / 4 core / 2 particles / 2 misc); 1 warning.
- current generated catalog JSON: 270 → candidate 181.

## Stale `Prefabs/Weapons/Rifles/` counts (heuristic)

| scope | current | candidate |
|---|---:|---:|
| catalog/**/*.json | 1455 | 972 |
| indexes/** | 178 | 196 |
| reports/** | 1670 | 2178 |

**Not all are defects.** Sampled candidate refs are legitimate external base-game paths (`"defined_in": "base_game_snapshot:Prefabs/Weapons/Rifles/M14/Rifle_M21_base.et"`) and **supplied** reference indexes (`shard_03/04.json`, `slot_and_sight_summary.json`) that the scanner does not own. The heuristic counts stale-looking strings, not broken references.

## Tests / checks

- NOT RUN by the agent: Workbench/game (forbidden).
- NOT RUN: `check_repository_integrity.py` on this station (jsonschema missing); hosted CI installs it.
- The isolated candidate is **not** published; no canonical generated file was written to the working repo.

## Risks / publication readiness

- The candidate **diverges substantially** (121 deleted, 32 new, 169 changed). This must be diff-reviewed; many deletions/new names likely reflect the live addon reorganisation and the restored baseline, but that is **not** assumed.
- The live addon is **dirty** (SPAS-12 anims + MP-133 `.meta`); the candidate reflects that state. Re-run after the owner confirms the intended source state.
- The stale-count metric must be redefined (separate scanner-owned refs from external/supplied ones) before drawing conclusions.
- **PUBLICATION NOT READY**: requires owner diff review per Issue #28.

## Appendix — full generated-file diff

### NEW (candidate only) — 32

- `catalog/ammunition/armst_ammo_545x39_bp.json`
- `catalog/ammunition/armst_ammo_545x39_pp.json`
- `catalog/ammunition/armst_ammo_grenade_hedp_m433.json`
- `catalog/attachments/armst_bayonet_6kh4.json`
- `catalog/attachments/armst_bayonet_m9.json`
- `catalog/attachments/armst_suppressor_m16.json`
- `catalog/attachments/armst_suppressor_pbs4.json`
- `catalog/attachments/armst_ugl_m203_long.json`
- `catalog/attachments/armst_ugl_m203_short.json`
- `catalog/magazines/armst_box_556x45_m249_200rnd_4ball_1tracer.json`
- `catalog/magazines/armst_box_762x51_m60_100rnd_4ball_1tracer.json`
- `catalog/magazines/armst_box_762x54_pk_100rnd_4ball_1tracer.json`
- `catalog/magazines/armst_box_762x54_uk59_50rnd_4ball_1tracer.json`
- `catalog/magazines/armst_magazine_545x39_ak_30rnd_bp.json`
- `catalog/magazines/armst_magazine_545x39_ak_30rnd_pp.json`
- `catalog/magazines/armst_magazine_545x39_rpk_45rnd_bp.json`
- `catalog/magazines/armst_magazine_545x39_rpk_45rnd_pp.json`
- `catalog/magazines/armst_magazine_762x51_m14_20rnd_bp.json`
- `catalog/magazines/armst_magazine_762x51_m14_20rnd_pp.json`
- `catalog/misc/armst_shotgun_ris_mount.json`
- `catalog/misc/asphaltpavement_decal_base.json`
- `catalog/optics/armst_collim_ap2k.json`
- `catalog/optics/armst_okp.json`
- `catalog/optics/armst_optic_4x20.json`
- `catalog/optics/armst_optic_artii.json`
- `catalog/weapons/armst_mgun_m249.json`
- `catalog/weapons/armst_mgun_m60.json`
- `catalog/weapons/armst_mgun_uk59.json`
- `catalog/weapons/armst_rifle_m21.json`
- `catalog/weapons/armst_shotgun_mp_133_ris.json`
- `catalog/weapons/armst_smoke_anm8hc.json`
- `catalog/weapons/armst_smoke_rdg2.json`

### DELETED (current only) — 121

- `catalog/ammunition/ammo_12ga.json`
- `catalog/ammunition/ammo_12ga_shell.json`
- `catalog/ammunition/ammo_12ga_shell_test.json`
- `catalog/ammunition/ammo_545x39_ball_7n6.json`
- `catalog/ammunition/ammo_556x45_ball_m193.json`
- `catalog/ammunition/ammo_762x39_ball_57n231.json`
- `catalog/ammunition/ammo_763x25.json`
- `catalog/ammunition/ammo_763x25_ball.json`
- `catalog/ammunition/ammo_9x18_ball_57n181.json`
- `catalog/ammunition/ammo_9x19_ball_m882.json`
- `catalog/ammunition/ammo_9x39_sp5_ball.json`
- `catalog/ammunition/ammo_9x39_sp6_ball.json`
- `catalog/ammunition/ammo_buckshot_pellet.json`
- `catalog/ammunition/ammo_grenade_he_vog25.json`
- `catalog/attachments/handguard_ak74m.json`
- `catalog/attachments/handguard_ak74m2.json`
- `catalog/attachments/handguard_aks.json`
- `catalog/attachments/stock_akm.json`
- `catalog/attachments/suppressor_9a91.json`
- `catalog/attachments/suppressor_pbs4_base.json`
- `catalog/attachments/ugl_gp25.json`
- `catalog/grenades/armst_smoke_anm8hc.json`
- `catalog/grenades/armst_smoke_rdg2.json`
- `catalog/grenades/grenade_m67.json`
- `catalog/grenades/grenade_rgd5.json`
- `catalog/grenades/smoke_anm8hc.json`
- `catalog/grenades/smoke_rdg2.json`
- `catalog/magazines/12ga_buckshot.json`
- `catalog/magazines/12ga_shell.json`
- `catalog/magazines/12ga_shell_test.json`
- `catalog/magazines/armst_magazine_545x39_ak_30rnd_ball.json`
- `catalog/magazines/armst_magazine_545x39_ak_30rnd_tracer.json`
- `catalog/magazines/armst_magazine_545x39_rpk_45rnd_ball.json`
- `catalog/magazines/armst_magazine_545x39_rpk_45rnd_tracer.json`
- `catalog/magazines/box_762x54_pk_250rnd_ball.json`
- `catalog/magazines/magazine_545x39_ak_30rnd_ball.json`
- `catalog/magazines/magazine_545x39_ak_30rnd_base.json`
- `catalog/magazines/magazine_545x39_ak_30rnd_tracer.json`
- `catalog/magazines/magazine_545x39_rpk_45rnd_ball.json`
- `catalog/magazines/magazine_545x39_rpk_45rnd_tracer.json`
- `catalog/magazines/magazine_556x45_stanag_30rnd_m193_ball.json`
- `catalog/magazines/magazine_556x45_stanag_30rnd_m196_tracer.json`
- `catalog/magazines/magazine_556x45_stanag_30rnd_m855_ball.json`
- `catalog/magazines/magazine_556x45_stanag_30rnd_m856_tracer.json`
- `catalog/magazines/magazine_762x39_akm_10rnd_ball.json`
- `catalog/magazines/magazine_762x39_akm_30rnd_ball.json`
- `catalog/magazines/magazine_762x39_akm_30rnd_tracer.json`
- `catalog/magazines/magazine_762x54_svd_10rnd_7bz3api.json`
- `catalog/magazines/magazine_762x54_svd_10rnd_sniper.json`
- `catalog/magazines/magazine_763x25_tt_8rnd_ball.json`
- `catalog/magazines/magazine_9x18_apb_20rnd_ball.json`
- `catalog/magazines/magazine_9x18_pm_8rnd_ball.json`
- `catalog/magazines/magazine_9x18_pp91_30rnd_ball.json`
- `catalog/magazines/magazine_9x18_sr2_30rnd_ball.json`
- `catalog/magazines/magazine_9x19_m9_15rnd_ball.json`
- `catalog/magazines/magazine_9x39_20rnd_9a91_sp5.json`
- `catalog/magazines/magazine_9x39_20rnd_9a91_sp6.json`
- `catalog/magazines/magazine_9x39_20rnd_vss_sp5.json`
- `catalog/magazines/magazine_9x39_20rnd_vss_sp6.json`
- `catalog/magazines/magazine_9x39_30rnd_val_sp5.json`
- `catalog/magazines/magazine_9x39_30rnd_val_sp6.json`
- `catalog/optics/optic_4x20.json`
- `catalog/optics/optic_pso1.json`
- `catalog/optics/optic_pso1_ak.json`
- `catalog/tripods/tripod_6t5.json`
- `catalog/tripods/tripod_6t5_pkm.json`
- `catalog/tripods/tripod_6t7_nsv.json`
- `catalog/weapons/armst_ak105.json`
- `catalog/weapons/armst_ak74.json`
- `catalog/weapons/armst_ak74m.json`
- `catalog/weapons/armst_ak74m_full.json`
- `catalog/weapons/armst_ak74n.json`
- `catalog/weapons/armst_aks.json`
- `catalog/weapons/armst_aks74u.json`
- `catalog/weapons/armst_aks74un.json`
- `catalog/weapons/armst_apb.json`
- `catalog/weapons/armst_groza1.json`
- `catalog/weapons/armst_izh_27.json`
- `catalog/weapons/armst_m9.json`
- `catalog/weapons/armst_mp_133.json`
- `catalog/weapons/armst_mp_153.json`
- `catalog/weapons/armst_pkm.json`
- `catalog/weapons/armst_pm.json`
- `catalog/weapons/armst_pp91.json`
- `catalog/weapons/armst_remington_870.json`
- `catalog/weapons/armst_rpk74.json`
- `catalog/weapons/armst_spas_12.json`
- `catalog/weapons/armst_sr_2.json`
- `catalog/weapons/armst_svd.json`
- `catalog/weapons/armst_toz_66.json`
- `catalog/weapons/armst_toz_66_pantera.json`
- `catalog/weapons/armst_toz_66_saw.json`
- `catalog/weapons/armst_tt.json`
- `catalog/weapons/armst_vz58p_base.json`
- `catalog/weapons/armst_vz58v_base.json`
- `catalog/weapons/groza_base.json`
- `catalog/weapons/handgun_knife_base.json`
- `catalog/weapons/oc_groza.json`
- `catalog/weapons/rifle_9a91.json`
- `catalog/weapons/rifle_9a91_base.json`
- `catalog/weapons/rifle_9a91_suppressor.json`
- `catalog/weapons/rifle_akm.json`
- `catalog/weapons/rifle_akm_base.json`
- `catalog/weapons/rifle_akm_full.json`
- `catalog/weapons/rifle_akms.json`
- `catalog/weapons/rifle_hk_g36.json`
- `catalog/weapons/rifle_hkg33.json`
- `catalog/weapons/rifle_l85.json`
- `catalog/weapons/rifle_m16a2.json`
- `catalog/weapons/rifle_m16a2_carbine.json`
- `catalog/weapons/rifle_sig550.json`
- `catalog/weapons/rifle_soc94.json`
- `catalog/weapons/rifle_val.json`
- `catalog/weapons/rifle_val_base.json`
- `catalog/weapons/rifle_vpo136.json`
- `catalog/weapons/rifle_vsk94.json`
- `catalog/weapons/rifle_vsk94_base.json`
- `catalog/weapons/rifle_vss.json`
- `catalog/weapons/rifle_vss_base.json`
- `catalog/weapons/shotgun_base.json`
- `catalog/weapons/slr.json`

### CHANGED — 169

- `agent/scan_state.json`
- `catalog/ammunition/armst_ammo_12ga.json`
- `catalog/ammunition/armst_ammo_12ga_shell.json`
- `catalog/ammunition/armst_ammo_12ga_shell_test.json`
- `catalog/ammunition/armst_ammo_556x45_bp.json`
- `catalog/ammunition/armst_ammo_556x45_pp.json`
- `catalog/ammunition/armst_ammo_762x39_bp.json`
- `catalog/ammunition/armst_ammo_762x39_pp.json`
- `catalog/ammunition/armst_ammo_762x51_bp.json`
- `catalog/ammunition/armst_ammo_762x51_pp.json`
- `catalog/ammunition/armst_ammo_763x25.json`
- `catalog/ammunition/armst_ammo_763x25_ball.json`
- `catalog/ammunition/armst_ammo_9x18_bp.json`
- `catalog/ammunition/armst_ammo_9x18_pp.json`
- `catalog/ammunition/armst_ammo_9x19_bp.json`
- `catalog/ammunition/armst_ammo_9x19_pp.json`
- `catalog/ammunition/armst_ammo_9x39_sp5_ball.json`
- `catalog/ammunition/armst_ammo_9x39_sp6_ball.json`
- `catalog/ammunition/armst_ammo_buckshot_pellet.json`
- `catalog/ammunition/armst_ammo_grenade_he_vog25.json`
- `catalog/attachments/armst_handguard_ak74m.json`
- `catalog/attachments/armst_handguard_ak74m2.json`
- `catalog/attachments/armst_handguard_aks.json`
- `catalog/attachments/armst_stock_akm.json`
- `catalog/attachments/armst_suppressor_9a91.json`
- `catalog/attachments/armst_ugl_gp25.json`
- `catalog/core/grenade_base.json`
- `catalog/core/magazine_base.json`
- `catalog/core/rifle_base.json`
- `catalog/core/weapon_base.json`
- `catalog/grenades/armst_grenade_m67.json`
- `catalog/grenades/armst_grenade_rgd5.json`
- `catalog/magazines/12ga_buckshot_base.json`
- `catalog/magazines/armst_12ga_buckshot.json`
- `catalog/magazines/armst_12ga_shell.json`
- `catalog/magazines/armst_12ga_shell_test.json`
- `catalog/magazines/armst_magazine_556x45_hkg36.json`
- `catalog/magazines/armst_magazine_556x45_hkg36_bp.json`
- `catalog/magazines/armst_magazine_556x45_sig_550.json`
- `catalog/magazines/armst_magazine_556x45_sig_550_bp.json`
- `catalog/magazines/armst_magazine_556x45_stanag_30rnd_m193_ball.json`
- `catalog/magazines/armst_magazine_556x45_stanag_30rnd_m193_ball_bp.json`
- `catalog/magazines/armst_magazine_556x45_stanag_30rnd_m855_ball.json`
- `catalog/magazines/armst_magazine_556x45_stanag_30rnd_m855_ball_bp.json`
- `catalog/magazines/armst_magazine_762x39_akm_10rnd_ball.json`
- `catalog/magazines/armst_magazine_762x39_akm_10rnd_ball_bp.json`
- `catalog/magazines/armst_magazine_762x39_akm_30rnd_ball.json`
- `catalog/magazines/armst_magazine_762x39_akm_30rnd_ball_bp.json`
- `catalog/magazines/armst_magazine_762x51_hk3_20_m80_ball.json`
- `catalog/magazines/armst_magazine_762x51_hk3_20_m80_ball_bp.json`
- `catalog/magazines/armst_magazine_762x51_l1a1_20_m80_ball.json`
- `catalog/magazines/armst_magazine_762x51_l1a1_20_m80_ball_bp.json`
- `catalog/magazines/armst_magazine_762x51_l1a1_30_m80_ball.json`
- `catalog/magazines/armst_magazine_762x51_l1a1_30_m80_ball_bp.json`
- `catalog/magazines/armst_magazine_762x54_svd_10rnd_7bz3api.json`
- `catalog/magazines/armst_magazine_763x25_tt_8rnd_ball.json`
- `catalog/magazines/armst_magazine_9x18_apb_20rnd_ball.json`
- `catalog/magazines/armst_magazine_9x18_apb_20rnd_ball_bp.json`
- `catalog/magazines/armst_magazine_9x18_pm_8rnd_ball.json`
- `catalog/magazines/armst_magazine_9x18_pm_8rnd_ball_bp.json`
- `catalog/magazines/armst_magazine_9x18_pm_8rnd_ball_pp.json`
- `catalog/magazines/armst_magazine_9x18_pp91_30rnd_ball.json`
- `catalog/magazines/armst_magazine_9x18_pp91_30rnd_ball_bp.json`
- `catalog/magazines/armst_magazine_9x18_sr2_30rnd_ball.json`
- `catalog/magazines/armst_magazine_9x19_m9_15rnd_ball.json`
- `catalog/magazines/armst_magazine_9x19_m9_15rnd_ball_bp.json`
- `catalog/magazines/armst_magazine_9x39_20rnd_9a91_sp5.json`
- `catalog/magazines/armst_magazine_9x39_20rnd_9a91_sp6.json`
- `catalog/magazines/armst_magazine_9x39_20rnd_vss_sp5.json`
- `catalog/magazines/armst_magazine_9x39_20rnd_vss_sp6.json`
- `catalog/magazines/armst_magazine_9x39_30rnd_val_sp5.json`
- `catalog/magazines/armst_magazine_9x39_30rnd_val_sp6.json`
- `catalog/magazines/armst_magazine_9x39_groza_20rnd_sp5.json`
- `catalog/magazines/armst_magazine_9x39_groza_20rnd_sp6.json`
- `catalog/magazines/magazine_556x45_stanag_30rnd_base.json`
- `catalog/optics/armst_hkg36_carryhandle_optic.json`
- `catalog/optics/armst_hkg36_carryhandle_picatinny.json`
- `catalog/optics/armst_l85_carryhandle.json`
- `catalog/optics/armst_optic_1p29.json`
- `catalog/optics/armst_optic_akdovetailmount.json`
- `catalog/optics/armst_optic_collimator.json`
- `catalog/optics/armst_optic_pso1.json`
- `catalog/optics/weaponoptic_base.json`
- `catalog/particles/bullet_case_12ga.json`
- `catalog/particles/bullet_case_12ga_blue.json`
- `catalog/tripods/armst_tripod_6t5.json`
- `catalog/tripods/armst_tripod_6t5_pkm.json`
- `catalog/weapons/1.json`
- `catalog/weapons/armst_handgun_knife_base.json`
- `catalog/weapons/armst_mgun_pkm.json`
- `catalog/weapons/armst_mgun_rpk74.json`
- `catalog/weapons/armst_pistol_apb.json`
- `catalog/weapons/armst_pistol_apb_base.json`
- `catalog/weapons/armst_pistol_m9.json`
- `catalog/weapons/armst_pistol_pm.json`
- `catalog/weapons/armst_pistol_pp91.json`
- `catalog/weapons/armst_pistol_pp91_base.json`
- `catalog/weapons/armst_pistol_sr_2.json`
- `catalog/weapons/armst_pistol_sr_2_base.json`
- `catalog/weapons/armst_pistol_tt.json`
- `catalog/weapons/armst_pistol_tt_base.json`
- `catalog/weapons/armst_rifle_9a91.json`
- `catalog/weapons/armst_rifle_9a91_base.json`
- `catalog/weapons/armst_rifle_aek971.json`
- `catalog/weapons/armst_rifle_aek971_base.json`
- `catalog/weapons/armst_rifle_ak105.json`
- `catalog/weapons/armst_rifle_ak74.json`
- `catalog/weapons/armst_rifle_ak74m.json`
- `catalog/weapons/armst_rifle_ak74m_full.json`
- `catalog/weapons/armst_rifle_ak74n.json`
- `catalog/weapons/armst_rifle_akm.json`
- `catalog/weapons/armst_rifle_akm_base.json`
- `catalog/weapons/armst_rifle_akm_full.json`
- `catalog/weapons/armst_rifle_akms.json`
- `catalog/weapons/armst_rifle_aks.json`
- `catalog/weapons/armst_rifle_aks74u.json`
- `catalog/weapons/armst_rifle_groza.json`
- `catalog/weapons/armst_rifle_groza_base.json`
- `catalog/weapons/armst_rifle_hkg33.json`
- `catalog/weapons/armst_rifle_hkg33_base.json`
- `catalog/weapons/armst_rifle_hkg36.json`
- `catalog/weapons/armst_rifle_hkg36_base.json`
- `catalog/weapons/armst_rifle_l85.json`
- `catalog/weapons/armst_rifle_l85_base.json`
- `catalog/weapons/armst_rifle_m16a2.json`
- `catalog/weapons/armst_rifle_m4_carbine.json`
- `catalog/weapons/armst_rifle_sig550.json`
- `catalog/weapons/armst_rifle_sig550_base.json`
- `catalog/weapons/armst_rifle_soc94.json`
- `catalog/weapons/armst_rifle_svd.json`
- `catalog/weapons/armst_rifle_val.json`
- `catalog/weapons/armst_rifle_val_base.json`
- `catalog/weapons/armst_rifle_vpo136.json`
- `catalog/weapons/armst_rifle_vsk94.json`
- `catalog/weapons/armst_rifle_vsk94_base.json`
- `catalog/weapons/armst_rifle_vss.json`
- `catalog/weapons/armst_rifle_vss_base.json`
- `catalog/weapons/armst_shotgun_base.json`
- `catalog/weapons/armst_shotgun_izh_27.json`
- `catalog/weapons/armst_shotgun_mp_133.json`
- `catalog/weapons/armst_shotgun_mp_153.json`
- `catalog/weapons/armst_shotgun_remington_870.json`
- `catalog/weapons/armst_shotgun_spas_12.json`
- `catalog/weapons/armst_shotgun_toz_66.json`
- `catalog/weapons/armst_shotgun_toz_66_pantera.json`
- `catalog/weapons/armst_shotgun_toz_66_saw.json`
- `catalog/weapons/armst_slr.json`
- `catalog/weapons/armst_slr_base.json`
- `catalog/weapons/armst_vz58p.json`
- `catalog/weapons/armst_vz58v.json`
- `indexes/ammunition.json`
- `indexes/attachments.json`
- `indexes/generated_config_reference/ammo_configs.json`
- `indexes/magazines.json`
- `indexes/optics.json`
- `indexes/reference_graph.json`
- `indexes/references.json`
- `indexes/weapons.json`
- `reports/inheritance_issues.json`
- `reports/inheritance_issues.md`
- `reports/scan_summary.json`
- `reports/scan_summary.md`
- `reports/unresolved_references.json`
- `reports/unresolved_references.md`
- `reports/weapon_ballistics.json`
- `schema/ammunition.schema.json`
- `schema/entity.schema.json`
- `schema/magazine.schema.json`
- `schema/weapon.schema.json`
