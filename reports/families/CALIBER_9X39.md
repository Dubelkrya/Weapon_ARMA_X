# 9×39 weapon family

> [!NOTE]
> **Status: GENERATED SNAPSHOT.** Membership is based on explicit 9×39 magazine paths, not weapon names or folder names.

Current matching catalog entries: **9**.

In the current snapshot all 9 matching entries resolve to **700 RPM**, velocity coefficient **0.835**, dispersion **0.4 / 200** and approximately **6.875 MOA**.

## Current catalog comparison

| Entry | Role | Parent | Magazine | RPM | Velocity coef | Dispersion | Slots | Warnings |
|---|---|---|---|---:|---:|---|---:|---:|
| [`rifle_9a91`](../../catalog/weapons/rifle_9a91.json) | leaf | `Rifle_9a91_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_9a91_base`](../../catalog/weapons/rifle_9a91_base.json) | base | `Rifle_AK74_short_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_9a91_suppressor`](../../catalog/weapons/rifle_9a91_suppressor.json) | leaf | `Rifle_9a91_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_val`](../../catalog/weapons/rifle_val.json) | base | `Rifle_val_base.et` | `Magazine_9x39_30rnd_val_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_val_base`](../../catalog/weapons/rifle_val_base.json) | base | `Rifle_AK74_short_base.et` | `Magazine_9x39_30rnd_val_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_vsk94`](../../catalog/weapons/rifle_vsk94.json) | leaf | `Rifle_VSK94_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_vsk94_base`](../../catalog/weapons/rifle_vsk94_base.json) | base | `Rifle_AK74_short_base.et` | `Magazine_9x39_20rnd_9a91_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_vss`](../../catalog/weapons/rifle_vss.json) | leaf | `Rifle_vss_base.et` | `Magazine_9x39_20rnd_vss_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |
| [`rifle_vss_base`](../../catalog/weapons/rifle_vss_base.json) | base | `Rifle_AK74_short_base.et` | `Magazine_9x39_20rnd_vss_SP5.et` | 700 | 0.835 | D=0.4, R=200, 6.875 MOA | 2 | 0 |

The current catalog shows two magazine-well families: `MagazineWell9x39` and `MagazineWell9x39_9a91`. Treat that compatibility distinction separately from shared ballistic/handling values.

`Oc_Groza` is intentionally excluded because its current generated magazine path is 7.62×39, despite its location under the VAL source tree.
