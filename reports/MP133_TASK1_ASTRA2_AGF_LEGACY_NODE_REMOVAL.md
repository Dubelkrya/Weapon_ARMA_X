# MP-133 Task #1 — ASTRA2: удаление 9 legacy AGF-нод (AGF-only cleanup)

Статус: **ASTRA2_LEGACY_AGF_NODES_REMOVED_OWNER_WB_VERIFY_PENDING**
Дата: 2026-10-05
Авторизация: Issue #34 [#5999306498](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5999306498).
Target: `Assets/MP133_AstraShellGraph_test/MP133_Astra2.agf` (единственный изменённый файл).
Workbench/Animation Editor/Game: **закрыты** перед правкой (проверено).

---

## 1. Удалённые 9 нод (отключённый native magazine-reload кластер)

`Blend T 1`, `WeaponReloadStanceSTM`, `ReloadErcCroG`, `ReloadPneG`, `WeaponReloadSTM`, `MagReloadSTM`, `InsertMagAnim`, `RemoveMagAnim`, `IdleFinger_1`.

Вместе с state machines удалены их внутренние transitions (brace-aware удаление блоков).

## 2. AGF до/после

| | SHA-256 | Размер |
|---|---|---|
| до | `447E206B60F0C84CBD96936BAD11F70C66C6B66C47FF28D83CF8C97451E04CBC` | 34881 |
| после | `55570DE07550E4BE7E41A4FB63D807672701ED42FBBAA71F7C40E27127EA71E8` | 30631 |

## 3. `RackBoltAnim` сохранён — активный CMD1-маршрут

```
MasterControl → IdleReloadSTM → Reload → ReloadRouteSTM → RackStanceSTM → RackErcG / RackPneG → RackBoltAnim
```
`RackBoltAnim` присутствует (3 вхождения), `Source "Reload.ReloadActionBolt"` не изменён. Сохранены также `ReloadRouteSTM`, `RackStanceSTM`, `RackErcG`, `RackPneG`, `ShellReloadSTM`, `AstraShellErcG`, пять `Astra*` Source-нод, весь `IdleReloadSTM`, fire/safety/inspection/IK/modes.

## 4. Protected files — до/после (не изменялись)

| Файл | SHA-256 | unchanged |
|---|---|---|
| `MP133_Astra2.ast` | `3A1C9BB03E0DAEB0506C988B03467D2C5B5131DACA5C58321462129F8163234B` | True |
| `MP133_Astra2_player.asi` | `9F850CE79AAF31D33BFB614BFD87961E5ABA511BB462161AF52A333C0546901D` | True |
| `MP133_Astra2_weapon.asi` | `77E2887EE57175D697C226308D6E9349FB53673691AC06E9C9268637D319A72E` | True |
| `MP133_Astra2.agr` | `8E8BAB3771E0691F5A116AB917A1F506E407245C6CC7E5C8B1DF1ECFCB730FF2` | True |
| `astra2.aw` | `0D25975B66679B607852E3751DAB54D2483C35991085D2C36A3D685518E05DDC` | True |

Все `.meta` не изменялись. `Reload_InsertMag`/`Reload_RemoveMag` в AST/ASI **не удалялись** (остаются инертными).

## 5. Проверки после удаления (PASS)

- 9 целевых нод = **0** (удалены ровно они).
- **0** неразрешённых `Child`/`Child0`/`Child1`.
- Скобки: **287/287**.
- `IdleReloadSTM.Reload.Child = ReloadRouteSTM`.
- CMD1-условие `GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(CMD_Weapon_Reload) == 0.0` присутствует.
- P ASI `Reload.Erc.<phase>` = **5/5**; W ASI = **5/5** (не редактировались).
- 10 исходных P/W ANM GUID — неизменны.

## 6. Git

Один узкий commit: только `MP133_Astra2.agf` (+ отчёт). Синхронизирован только изменённый AGF в `labs/`. Другие файлы/этапы не смешивались. Commit SHA: см. ниже.

## 7. Ворота владельца (STOP)

Владелец: открыть `astra2.aw` → **Errors** (ноль новых) → 5/5 P → 5/5 W → **Save → Close → Reopen** → повторная проверка, что десять строк сохранились. Игровой `R/CMD4/5/6` и ammo-записи не запускать. Следующие этапы не начинаю.
