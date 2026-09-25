# 9×39 weapon family

> [!NOTE]
> **Status: GENERATED SNAPSHOT.** Membership is based on explicit 9×39 magazine paths, not weapon names or folder names.

Current matching catalog entries: **10**.

The current snapshot does not resolve one common handling baseline across every 9×39 entry.

Detailed balance layer: [9×39 balance comparison](../balance/CALIBER_9X39_BALANCE.md).

## Current catalog comparison

| Entry | Role | Parent | Magazine | RPM | Velocity coef | Dispersion | Slots | Warnings |
|---|---|---|---|---:|---:|---|---:|---:|
| [`armst_rifle_9a91`](../../catalog/weapons/armst_rifle_9a91.json) | leaf | `armst_Rifle_9a91_base.et` | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_9a91_base`](../../catalog/weapons/armst_rifle_9a91_base.json) | base | `Rifle_AK74_short_base.et` | `armst_Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_groza`](../../catalog/weapons/armst_rifle_groza.json) | leaf | `armst_Rifle_Groza_base.et` | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | 750 | — | D=0.058, R=100, 1.994 MOA | 0 | 0 |
| [`armst_rifle_groza_base`](../../catalog/weapons/armst_rifle_groza_base.json) | base | `Rifle_Base.et` | `armst_Magazine_9x39_Groza_20rnd_SP5.et` | 750 | — | D=0.058, R=100, 1.994 MOA | 0 | 0 |
| [`armst_rifle_val`](../../catalog/weapons/armst_rifle_val.json) | leaf | `armst_Rifle_val_base.et` | `armst_Magazine_9x39_30rnd_val_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_val_base`](../../catalog/weapons/armst_rifle_val_base.json) | base | `Rifle_AK74_short_base.et` | `armst_Magazine_9x39_30rnd_val_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_vsk94`](../../catalog/weapons/armst_rifle_vsk94.json) | leaf | `armst_Rifle_VSK94_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_vsk94_base`](../../catalog/weapons/armst_rifle_vsk94_base.json) | base | `Rifle_AK74_short_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_vss`](../../catalog/weapons/armst_rifle_vss.json) | leaf | `armst_Rifle_vss_base.et` | `armst_Magazine_9x39_20rnd_vss_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |
| [`armst_rifle_vss_base`](../../catalog/weapons/armst_rifle_vss_base.json) | base | `Rifle_AK74_short_base.et` | `armst_Magazine_9x39_20rnd_vss_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 1 | 0 |

The current catalog shows two magazine-well families: `MagazineWell9x39` and `MagazineWell9x39_9a91`. Treat that compatibility distinction separately from shared ballistic/handling values.

`Oc_Groza` is intentionally excluded because its current generated magazine path is 7.62×39, despite its location under the VAL source tree.
