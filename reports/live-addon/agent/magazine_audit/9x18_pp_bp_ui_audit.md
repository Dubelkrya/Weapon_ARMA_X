# 9x18 PP/BP Magazine UI + Localization Audit (READ ONLY)

## Current effective display identity
| mag | item Name | item Description | edit Name | missing keys |
|---|---|---|---|---|
| PM_PP | `#AR-Magazine_PM_Name` | `#AR-ARMST_Magazine_armst_Magazine_9x18_PM_8rnd_Ball_Description` | `#AR-Magazine_PM_Name` | none |
| PM_BP | `#AR-Magazine_PM_Name` | `#AR-ARMST_Magazine_armst_Magazine_9x18_PM_8rnd_Ball_Description` | `#AR-Magazine_PM_Name` | none |
| APB_PP | `APB Magazine` | `#AR-ARMST_Magazine_armst_Magazine_9x18_APB_20rnd_Ball_Description` | `APB Magazine` | none |
| APB_BP | `APB Magazine` | `#AR-ARMST_Magazine_armst_Magazine_9x18_APB_20rnd_Ball_Description` | `APB Magazine` | none |
| PP91_PP | `PP-91 Magazine` | `#AR-ARMST_Magazine_armst_Magazine_9x18_PP91_30rnd_Ball_Description` | `PP-91 Magazine` | none |
| PP91_BP | `PP-91 Magazine` | `#AR-ARMST_Magazine_armst_Magazine_9x18_PP91_30rnd_Ball_Description` | `PP-91 Magazine` | none |

## 9x19 reference convention
- M9 PP desc key: `#AR-ARMST_Magazine_armst_Magazine_9x19_M9_15rnd_Ball_Description`
- M9 BP desc key: `#AR-ARMST_Magazine_armst_Magazine_9x19_M9_15rnd_Ball_BP_Description`
- Same physical Name; distinct PP/BP Description keys.

## Issues
- PP/BP pairs share identical display Name and identical Description key (no PP/BP distinction).
- BP magazines lack dedicated *_Ball_BP_Description keys (9x19 convention uses distinct PP/BP description keys).
- PM PP/BP reuse the legacy shared ARMST PM description key; wording is Ball-only and does not state PP/BP.
- APB/PP91 descriptions are Ball-only; no loaded-ammunition role suffix.

## Recommended identities (proposal only)
- PM_PP: Name `#AR-Magazine_PM_Name`, desc `#AR-ARMST_Magazine_armst_Magazine_9x18_PM_8rnd_Ball_Description`
  - RU: Магазин на 8 патронов для пистолета Макарова под 9×18 мм. Снаряжён боеприпасами ARMST PP.
  - EN: 8-round magazine for the Makarov pistol, chambered for 9x18 mm. Loaded with ARMST PP ammunition.
- PM_BP: Name `#AR-Magazine_PM_Name`, desc `#AR-ARMST_Magazine_armst_Magazine_9x18_PM_8rnd_Ball_BP_Description`
  - RU: Магазин на 8 патронов для пистолета Макарова под 9×18 мм. Снаряжён боеприпасами ARMST BP.
  - EN: 8-round magazine for the Makarov pistol, chambered for 9x18 mm. Loaded with ARMST BP ammunition.
- APB_PP: Name `APB Magazine`, desc `#AR-ARMST_Magazine_armst_Magazine_9x18_APB_20rnd_Ball_Description`
  - RU: Магазин на 20 патронов для АПБ под 9×18 мм. Снаряжён боеприпасами ARMST PP.
  - EN: 20-round magazine for the APB, chambered for 9x18 mm. Loaded with ARMST PP ammunition.
- APB_BP: Name `APB Magazine`, desc `#AR-ARMST_Magazine_armst_Magazine_9x18_APB_20rnd_Ball_BP_Description`
  - RU: Магазин на 20 патронов для АПБ под 9×18 мм. Снаряжён боеприпасами ARMST BP.
  - EN: 20-round magazine for the APB, chambered for 9x18 mm. Loaded with ARMST BP ammunition.
- PP91_PP: Name `PP-91 Magazine`, desc `#AR-ARMST_Magazine_armst_Magazine_9x18_PP91_30rnd_Ball_Description`
  - RU: Магазин на 30 патронов для ПП-91 под 9×18 мм. Снаряжён боеприпасами ARMST PP.
  - EN: 30-round magazine for the PP-91, chambered for 9x18 mm. Loaded with ARMST PP ammunition.
- PP91_BP: Name `PP-91 Magazine`, desc `#AR-ARMST_Magazine_armst_Magazine_9x18_PP91_30rnd_Ball_BP_Description`
  - RU: Магазин на 30 патронов для ПП-91 под 9×18 мм. Снаряжён боеприпасами ARMST BP.
  - EN: 30-round magazine for the PP-91, chambered for 9x18 mm. Loaded with ARMST BP ammunition.

## Localization changes required
- NEW key #AR-ARMST_Magazine_armst_Magazine_9x18_PM_8rnd_Ball_BP_Description
- NEW key #AR-ARMST_Magazine_armst_Magazine_9x18_APB_20rnd_Ball_BP_Description
- NEW key #AR-ARMST_Magazine_armst_Magazine_9x18_PP91_30rnd_Ball_BP_Description

## Out of scope confirmed
- AmmoConfig/AmmoMapping/capacity/MagazineWell/model/GUID unchanged; SR-2M untouched.

LIVE_FILES_CHANGED: NONE
