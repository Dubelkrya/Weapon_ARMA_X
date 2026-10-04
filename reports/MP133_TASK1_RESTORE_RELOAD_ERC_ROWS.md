# MP-133 Task #1 — восстановление десяти P/W строк в `Reload/Erc` (MP133_AstraShellGraph_test)

Статус: **PRE_ASTRA_PW_ROW_RESTORED_WORKBENCH_PERSISTENCE_PENDING**
Дата: 2026-10-05
Задание: Issue #34 [#5984487963](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5984487963).
База: `t4b/installed-mag-probe` @ `3e5c935`. Workbench полностью закрыт (проверено). Оригинал не изменялся.

---

## 0. Preflight

- Workbench/игра/писатели: **нет** (`Get-Process` пусто). Последнее сохранение Workbench — 00:20:23; после него файлы не менялись.
- Основа — **текущие live** файлы `Assets/MP133_AstraShellGraph_test/` (не старые версии). Эталон строк — `8b47216`.
- Защищённый манифест: 104 файла (всё, кроме 4 правленых).

---

## 1. Что было в live до правки (артефакт Workbench)

- AST: 5 фаз находились в группе **`AstraShell`**, группа `Reload` без них.
- Обе ASI: **все десять строк `*.Erc.<phase>` отсутствовали** (Workbench вычистил их повторно).
- AGF: `AstraShellErcG` = `Group "AstraShell"`, источники `Source "AstraShell.<phase>"`.

---

## 2. Что сделано (только в live `MP133_AstraShellGraph_test/`)

1. **AST**: пять фаз `StartReload, GrabShell, InsertShell, CheckContinue, EndReload` возвращены в группу **`Reload`** (перед `Finger_trigger_in`), колонки `Erc/Pne` сохранены; `Reload_InsertMag/RemoveMag` НЕ возвращались (0).
2. **P ASI**: добавлены строки `Reload.Erc.{StartReload,GrabShell,InsertShell,CheckContinue,EndReload}` с исходными P-клипами и GUID (`FCB314232D355753`, `1D4C14261EFC54DB`, `D3868FB32BF75DEE`, `36BCB6296CAE5334`, `D1B33891A663548D`).
3. **W ASI**: то же для W-клипов и GUID (`979C9964AD7956F5`, `E6534D7B659C59E5`, `090759CC560C55F2`, `5B6872625F3454A4`, `008B42BF7C535275`).
4. **AGF**: `AstraShellErcG` → `Group "Reload"` (`Column "Erc"` без изменения); пять источников `Source "AstraShell.<phase>"` → `Source "Reload.<phase>"`.
5. **Сохранены реальные исправления Astra** из `3e5c935`: `RackStanceSTM`/`RackErcG`/`RackPneG` (Erc/Pne для затвора), безопасные условия прерывания, удаление старой магазинной ветки, изоляция `CMD2–6`. Целый AGF к `8b47216` НЕ откатывался.
6. **Не изменялись**: `.aw`, `.agr`, все `.meta`, GUID, исходные 10 ANM, оригинальная папка `Assets/MP133_AstraShellGraph/`.

---

## 3. Проверки (PASS)

| Проверка | Результат |
|---|---|
| AST группа `Reload` содержит 5 фаз | True |
| P ASI `Reload.Erc.<phase>` | 5/5 |
| W ASI `Reload.Erc.<phase>` | 5/5 |
| `AstraShell.Erc.*` строк (не должно быть) | 0/0 |
| `AstraShellErcG` Group = `Reload` | True |
| 10 исходных ANM GUID | все сохранены |
| legacy `Reload_InsertMag`/`Reload_RemoveMag` | 0 / 0 |
| Astra-исправления: `RackStanceSTM`/`RackErcG`/`RackPneG` | 2 / 2 / 2 |
| Защищённый набор (104 файла) | `PROTECTED_FILES_UNCHANGED=1` |
| Оригинал `Assets/MP133_AstraShellGraph` | хэши не изменились |
| live == labs (4 файла) | True |

---

## 4. Тесты

`agent/tests/test_astra_rebuild_contracts.py` обновлён: контракт теперь утверждает восстановленные **`Reload.Erc`**-строки (10), отсутствие `AstraShell.Erc`, наличие 10 исходных ANM GUID, отсутствие legacy-слотов, поддержку `RackStanceSTM`/`RackErcG`/`RackPneG`, сохранность CMD1 rack и безопасного конечного цикла.
**Python в среде недоступен** (только WindowsApps-заглушка) — тест-сьют не запускался; выполнены эквивалентные ручные контрактные проверки (см. §3). Тест-файл — source-only, запуск за владельцем/CI.

---

## 5. Критично: персистентность в Workbench (pending)

Workbench уже дважды вычищал эти десять строк. Поэтому после проверки в Animation Editor необходимо:
1. Открыть **`MP133_AstraShellGraph_test.aw`**, убедиться: `Reload/Erc` показывает пять P и пять W назначений; ноль **новых** красных ошибок; пять узлов-источников разрешаются.
2. **Сохранить** Workspace, закрыть и **повторно открыть** `.aw`.
3. Проверить, что десять строк `Reload.Erc.<phase>` физически **остались** в обеих `.asi` на диске.
4. Если строки снова исчезли — **STOP**: проблема в синхронизации AST↔ASI или в обработке ресурсов Workbench; дальнейшие ручные восстановления бессмысленны до выяснения причины. Не переносить обратно в `AstraShell`, не перестраивать граф наугад.

Игровой R/CMD4/5/6 не запускать (физическая замена `Tube3` движком — UNRESOLVED).
