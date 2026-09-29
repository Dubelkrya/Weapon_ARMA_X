# ARMST Variant Materialization / Direct Base Normalization

## Result: NOT APPLIED (safety gate)

Queries show that for every target the new base introduces or changes fields not present in the current effective state; those cannot be canceled by local overrides, so exact zero-diff materialization is not achievable.

| target | current parent | target parent | missing_in_new | extra_in_new | result |
|---|---|---|---|---|---|
| AK74N | `VanillaSources Rifle_AK74N_base.et (external)` | `armst_AK74_base.et` | 3 | 1 | REVIEW_REQUIRED |
| AK74M | `armst_AK74N.et (concrete)` | `armst_AK74_base.et` | 3 | 1 | NOT_ATTEMPTED |
| AKS | `armst_AK74N.et (concrete)` | `armst_AK74_base.et` | 3 | 1 | NOT_ATTEMPTED |
| AK74M_full | `armst_AK74M.et (concrete)` | `armst_AK74_base.et` | 7 | 1 | NOT_ATTEMPTED |
| AKM_full | `armst_Rifle_AKM.et (concrete)` | `armst_Rifle_AKM_base.et` | 51 | 57 | REVIEW_REQUIRED |

## Why
- Direct reparent to the `*_base` changes effective state: the base chain differs from the current (external vanilla or concrete-sibling) chain. Differences include added/changed fields that cannot be unset locally.
- Per the safety gate, no mutation was performed.

## Current final graph (unchanged)
- AK74: `armst_AK74_base` <- AK105 (direct); AK74N/AK74M/AKS/AK74M_full still on concrete/external parents
- AKM: `armst_Rifle_AKM_base` <- AKM/AKMS/SOC94/VPO136 (direct); AKM_full still via concrete AKM

GUID_CHANGES: 0 ; DANGLING_REFS: 0 ; UNRELATED_GAMEPLAY_CHANGES: 0
LIVE_FILES_CHANGED: NONE
