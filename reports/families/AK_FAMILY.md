# AK / RPK family

> [!NOTE]
> **Status: GENERATED SNAPSHOT.** Missing values are unresolved/inherited in the current catalog, not zero.

Current matching catalog entries: **13**.

The AK74/AKS74U entries in this snapshot often contain only local overrides, so handling and magazine values may remain blank at this layer. The AKM branch is more fully resolved in the current generated catalog.

## Current catalog comparison

| Entry | Role | Parent | Magazine | RPM | Velocity coef | Dispersion | Slots | Warnings |
|---|---|---|---|---:|---:|---|---:|---:|
| [`armst_rifle_ak105`](../../catalog/weapons/armst_rifle_ak105.json) | leaf | `armst_Rifle_AK74N.et` | `—` | — | — | — | 2 | 0 |
| [`armst_rifle_ak74`](../../catalog/weapons/armst_rifle_ak74.json) | leaf | `Rifle_AK74_long_base.et` | `—` | — | — | — | 0 | 0 |
| [`armst_rifle_ak74m`](../../catalog/weapons/armst_rifle_ak74m.json) | base | `armst_Rifle_AK74N.et` | `—` | — | — | — | 1 | 0 |
| [`armst_rifle_ak74m_full`](../../catalog/weapons/armst_rifle_ak74m_full.json) | leaf | `armst_Rifle_AK74M.et` | `—` | — | — | — | 1 | 0 |
| [`armst_rifle_ak74n`](../../catalog/weapons/armst_rifle_ak74n.json) | base | `Rifle_AK74N_base.et` | `—` | — | — | — | 0 | 0 |
| [`armst_rifle_akm`](../../catalog/weapons/armst_rifle_akm.json) | base | `armst_Rifle_AKM_base.et` | `armst_Magazine_762x39_AKM_30rnd_Ball.et` | 800 | 0.986 | D=0.4, R=220, 6.25 MOA | 3 | 0 |
| [`armst_rifle_akm_base`](../../catalog/weapons/armst_rifle_akm_base.json) | base | `Rifle_Base.et` | `Magazine_762x39_Vz58_30rnd_Last_5Tracer.et` | 800 | 0.986 | D=0.4, R=220, 6.25 MOA | 3 | 0 |
| [`armst_rifle_akm_full`](../../catalog/weapons/armst_rifle_akm_full.json) | leaf | `armst_Rifle_AKM.et` | `armst_Magazine_762x39_AKM_30rnd_Ball.et` | 800 | 0.986 | D=0.4, R=220, 6.25 MOA | 3 | 0 |
| [`armst_rifle_akms`](../../catalog/weapons/armst_rifle_akms.json) | leaf | `armst_Rifle_AKM_base.et` | `Magazine_762x39_Vz58_30rnd_Last_5Tracer.et` | 800 | 0.986 | D=0.4, R=220, 6.25 MOA | 3 | 0 |
| [`armst_rifle_aks`](../../catalog/weapons/armst_rifle_aks.json) | leaf | `armst_Rifle_AK74N.et` | `—` | — | — | — | 1 | 0 |
| [`armst_rifle_aks74u`](../../catalog/weapons/armst_rifle_aks74u.json) | leaf | `Rifle_AKS74U_base.et` | `—` | — | — | — | 0 | 0 |
| [`armst_rifle_soc94`](../../catalog/weapons/armst_rifle_soc94.json) | leaf | `armst_Rifle_AKM_base.et` | `armst_Magazine_762x39_AKM_10rnd_Ball.et` | 800 | 0.986 | D=0.4, R=220, 6.25 MOA | 3 | 0 |
| [`armst_rifle_vpo136`](../../catalog/weapons/armst_rifle_vpo136.json) | leaf | `armst_Rifle_AKM_base.et` | `armst_Magazine_762x39_AKM_10rnd_Ball.et` | 800 | 0.986 | D=0.4, R=220, 6.25 MOA | 3 | 0 |

## Workbench control related to this family

The current AEK-971 prototype is **Workbench validated** and is based on `Rifle_AK74N_base.et`, but it is not present in the generated weapon catalog yet.

- Control: [`armst_AEK971_test_v12_NAME_DESCRIPTION.et`](../samples/armst_AEK971_test_v12_NAME_DESCRIPTION.et)
- Current status: [`KNOWLEDGE_STATUS.md`](../KNOWLEDGE_STATUS.md)

Do not copy unresolved AK74-family values from names or real-world memory; resolve them from the live primary addon or a refreshed canonical snapshot.
