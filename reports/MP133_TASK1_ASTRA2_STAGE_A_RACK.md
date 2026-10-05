# MP-133 Task #1 — ASTRA2 Stage A: rack routing (old_pa → ASTRA2)

Статус: **ASTRA2_STAGE_A_RACK_PORTED_OWNER_WB_VERIFY_PENDING**
Дата: 2026-10-05
Задание: Issue #34 [#5998463700](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5998463700) (supersedes Astra3 plan).
**SOURCE = old_pa** (`Assets/MP133_AstraShellGraph_test/old_pa/`). **TARGET = ASTRA2** (`Assets/MP133_AstraShellGraph_test/`, `MP133_Astra2.*` + `astra2.aw`).
Режим: локальная правка при закрытом Workbench. **Только AGF** изменён.

---

## 0. ASTRA2 known-good snapshot (до Stage A)

`MP133_Astra2.ast` `3A1C9BB0…`, `MP133_Astra2.agf` `665E4203…`, `MP133_Astra2.agr` `8E8BAB37…`, `astra2.aw` `0D25975B…`, `MP133_Astra2_player.asi` `9F850CE7…`, `MP133_Astra2_weapon.asi` `77E2887E…`.

---

## 1. Stage A — что перенесено (только `MP133_Astra2.agf`)

Из old_pa добавлены (семантический донор):
- `AnimSrcNodeStateMachine ReloadRouteSTM` — состояние `Bolt` (Tag `TagRackBolt`, `StartCondition "GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(CMD_Weapon_Reload) == 0.0"`) → `Child "RackStanceSTM"`.
- `AnimSrcNodeStateMachine RackStanceSTM` — `ErcCro` (`Stance != 2`) → `RackErcG`; `Pne` (`Stance == 2`) → `RackPneG`.
- `AnimSrcNodeGroupSelect RackErcG` — `Group "Reload"`, `Column "Erc"`, `Child "RackBoltAnim"`.
- `AnimSrcNodeGroupSelect RackPneG` — `Group "Reload"`, `Column "Pne"`, `Child "RackBoltAnim"`.

Изменено:
- `IdleReloadSTM.Reload`: `Child "Blend T 1"` → `Child "ReloadRouteSTM"` (старый `Blend T 1`/native-ветка становятся недостижимыми, но НЕ удаляются — Stage D).
- Условия входа `Idle → Buffer3` и `WeaponInspection → Buffer3` приведены к CMD1-only (как в old_pa): `IsCommand(CMD_Weapon_Reload) && GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(CMD_Weapon_Reload) == 0.0`.

Использован существующий ASTRA2 `RackBoltAnim` (`Source "Reload.ReloadActionBolt"`) — дубликат не создавался.

## 2. Что НЕ трогалось
AST, обе ASI, AGR, AW, все `.meta`, GUID, 10 P/W назначений `Reload/Erc`, `ShellReloadSTM`/`AstraShellErcG`, native-ноды (пока orphan), fire/safety/inspection/IK/modes, G3B2, ORIGINAL.

## 3. Статическая проверка (PASS)
- `ReloadRouteSTM=1 RackStanceSTM=1 RackErcG=1 RackPneG=1`; `Reload.Child=ReloadRouteSTM`; `Blend T 1` orphan (0 refs).
- native `WeaponReloadSTM/MagReloadSTM/WeaponReloadStanceSTM` присутствуют (orphan) — удаление в Stage D.
- `ShellReloadSTM`/`AstraShellErcG` на месте.
- **0** неразрешённых `Child`-ссылок; скобки 319/319.
- **ASTRA2 P/W phase rows = 5/5** (не изменялись).
- live == labs для `MP133_Astra2.agf`.

Размер AGF: 33843 → 34881 (+4 узла).

## 4. Ворота проверки владельцем (STOP при первом провале)
1. Открыть `astra2.aw` (Animation Editor), проверить Errors: **ноль новых** ошибок.
2. Убедиться: 5/5 P и 5/5 W в `Reload/Erc` присутствуют.
3. **Save → Close → Reopen**; проверить, что десять строк **остались** в обеих `.asi` на диске.
4. Если строки исчезли или появились ошибки — это граница причины; **revert только Stage A**, предыдущие доказанные состояния не трогать. Прислать точный список ошибок + post-save состояние.

Дальше по плану: Stage B (shell STM/cancel), C (CMD2-6 isolation), D (удаление legacy graph nodes), E (удаление legacy AST/ASI mag-строк), F (AGR cleanup) — каждый со своей проверкой.

## 5. Git
Коммит Stage A отдельный (для биссекции): `labs/.../MP133_AstraShellGraph_test/` переведён на фактический ASTRA2-набор; старые pre-Astra2 `MP133_Astra.*` удалены из labs. Игровой R/CMD4/5/6 не запускался.
