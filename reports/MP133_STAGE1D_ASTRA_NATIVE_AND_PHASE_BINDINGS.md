# MP-133 Astra — Stage 1D: восстановление нативных строк и привязка пяти P/W фаз

Статус: **T4B_STAGE1D_ASTRA_NATIVE_AND_PHASE_BINDINGS_SOURCE_READY_OWNER_WORKBENCH**
Дата: 2026-10-04
Задание: Issue #34 [#5983377482](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983377482) (owner authorization). Диагностическая база: [#5983349834](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983349834), `reports/MP133_STAGE1C_RENAME_CROSSWALK_AND_TWO_ERROR_FIX_PLAN.md`.
Исполнитель: ordinary T4b agent. Аддон: **один** существующий `ARMSTMP133T4B_InstalledMagProbe` (ID `ARMSTMP133T4BInstalledMag`).
`SOURCE/STATIC = PASS`; Workbench/GUI — **PENDING** (за владельцем).

---

## 0. Preflight

- Workbench/editor/game и все писатели: **закрыты** (процессов `Workbench/Reforger/Arma/Enfusion` нет) — проверено до правки.
- Git: `t4b/installed-mag-probe` @ `2cdc04c`; рабочее дерево `Weapon_ARMA_X` — только untracked служебный отчёт.
- Захвачен манифест SHA-256 по **90 защищённым файлам** (всё, кроме четырёх правленых): десять ANM + импортерские `.anm.meta`, `.agr/.aw`, все прочие meta, скрипты, G3B2, bridge prefab.
- Pre-Stage1D live-состояние (владельческое, после rename) сохранено в отчёте Stage 1C (полный crosswalk + хэши). Никаких reset/stash/restore/clean, никакого wholesale-восстановления из `03d8621`.

---

## 1. Внесённые правки (4 существующих текстовых файла, field-wise)

### `MP133_Astra.ast` (группа `Reload`)
Возвращены три независимые нативные строки: `Safety`, `Reload_RemoveMag`, `Reload_InsertMag`. Distinct-строки фаз Astra `StartReload`, `GrabShell`, `InsertShell`, `CheckContinue`, `EndReload` сохранены. `ReloadActionBolt`, fire/idle/inspection/finger/mode и GUID группы/колонок не тронуты. Итог: 22 анимации, дубликатов нет.

### `MP133_Astra.agf`
- `SafetyPose`, `SemiPose`, `AutoPose` → `Source "Reload.Safety"` (нативные consumer'ы восстановлены).
- `InsertMagAnim` → `Source "Reload.Reload_InsertMag"`; `RemoveMagAnim` → `Source "Reload.Reload_RemoveMag"`.
- Astra-узел InsertShell: ошибочный `Source "Reload.InsertShell1"` → `Source "Reload.InsertShell"`; узел переименован в `AstraInsertShell` (устранена коллизия имён), `Child` у состояния `InsertShell` обновлён на `AstraInsertShell`. Состояние по-прежнему называется `InsertShell`.
- `RackBoltAnim → Source "Reload.ReloadActionBolt"` — **не изменялся**. `GetEventTime(anim.Reload.Erc.Reload_InsertMag, "BlendIn")` снова валиден (строка восстановлена). `AstraShellErcG` = `Group "Reload"` / `Column "Erc"`.

### `MP133_Astra_player.asi` и `MP133_Astra_weapon.asi`
Пять фаз Astra привязаны **только Erc** к импортированным клипам:
| Фаза | P GUID | W GUID |
|---|---|---|
| StartReload | `FCB314232D355753` | `979C9964AD7956F5` |
| GrabShell | `1D4C14261EFC54DB` | `E6534D7B659C59E5` |
| InsertShell | `D3868FB32BF75DEE` | `090759CC560C55F2` |
| CheckContinue | `36BCB6296CAE5334` | `5B6872625F3454A4` (**исправлен W**) |
| EndReload | `D1B33891A663548D` | `008B42BF7C535275` |

Astra `Pne` — **не назначен** (валидных prone-клипов нет; ничего не клонировано из Erc и не оставлено нативными safety/remove/inject под именем фазы).

Восстановлены нативные строки `Safety` / `Reload_InsertMag` / `Reload_RemoveMag` для **Erc и Pne** с исходными нативными клипами (safety AK74; `P/W_MP133_Reload_Inject`; `P/W_MP133_Reload_Rem`). Все прочие прежние назначения сохранены; `ReloadActionBolt` Erc+Pne → `P/W_MP133_Reload_Bolt` без изменений.

---

## 2. Статические проверки (все PASS)

| Проверка | Результат |
|---|---|
| Защищённый набор 90 файлов | `PROTECTED_FILES_UNCHANGED=1` |
| AST: уникальность строк, наличие 8 ключевых | 22 анимации, дубликатов нет, все 8 присутствуют |
| AGF: разрешение всех `Source "Group.…"` по AST | `unresolved = []` |
| AGF: `Reload.InsertShell1` / `AstraShell.` | 0 / 0 |
| AGF: SafetyPose/SemiPose/AutoPose → `Reload.Safety` | 1 / 2 |
| AGF: InsertMagAnim → `Reload.Reload_InsertMag`; RemoveMagAnim → `Reload.Reload_RemoveMag` | 1 / 1 |
| AGF: RackBoltAnim → `Reload.ReloadActionBolt` | 1 (intact) |
| AGF: `Child "AstraInsertShell"`; `GetEventTime(…Reload_InsertMag…)` | 1 / 1 |
| ASI: 5 фаз P/W — точные GUID, только Erc, Pne отсутствует | PASS |
| ASI: нативные Safety/InsertMag/RemoveMag — Erc+Pne, точные GUID | PASS |
| ASI: ReloadActionBolt Erc+Pne → `Reload_Bolt` | PASS (intact) |
| ASI: дубликаты ключей / cross-assignment P↔W | 0 / 0 |
| Кодировка | LF, UTF-8 без BOM |

---

## 3. Разрешение двух ошибок Stage 1C

1. `Graph InsertShell: Invalid source …` → узел исправлен на `Reload.InsertShell`, коллизия имён снята переименованием **узла** в `AstraInsertShell` (состояние не тронуто).
2. `Graph MagReloadSTM Expr 'Start Time': Unknown anim 'Reload.Erc.Reload_InsertMag'` → строка `Reload_InsertMag` восстановлена в AST, выражение `GetEventTime(anim.Reload.Erc.Reload_InsertMag,…)` снова ссылается на существующую анимацию.

---

## 4. Хэши (live)

| Файл | До Stage1D (21:53:50) | После (22:08:07) |
|---|---|---|
| `MP133_Astra.ast` | `4268AE56…` (1130) | `C95CF76E…` (1189) |
| `MP133_Astra.agf` | `CD7FF61D…` (33734) | `163C2EB3…` (33750) |
| `MP133_Astra_player.asi` | `F87EFFDF…` (14403) | `DC9C5105…` (14866) |
| `MP133_Astra_weapon.asi` | `47FBA70B…` (4835) | `6D966498…` (5300) |
| `MP133_Astra.agr` / `.aw` | — | **не изменялись** |

Принятый live-текст синхронизирован в `Weapon_ARMA_X/labs/…` (live == labs по SHA-256 для всех четырёх). Один коммит на `t4b/installed-mag-probe`.

---

## 5. Ворота приёмки владельца (Workbench)

1. Открыть **существующий** T4b `Assets/MP133_AstraShellGraph/MP133_Astra.aw`, штатно пересобрать граф.
2. Обязательно: **ноль** Astra `Invalid source` и ноль stale `StartTime`; `Reload.StartReload/GrabShell/InsertShell/CheckContinue/EndReload` в **обеих** ASI указывают на импортированные Astra P/W клипы (Erc) и переживают **один** Save + Reopen; `AstraInsertShell`/state `InsertShell` согласованы.
3. Нативные `Safety` / `Reload_InsertMag` / `Reload_RemoveMag` (Erc+Pne) восстановлены; `ReloadActionBolt` и цепочка `RackBoltAnim → Reload.ReloadActionBolt → P/W_MP133_Reload_Bolt` + событие `Weapon_Rack_Bolt` без регресса (cmd1).
4. Один ручной animation-only цикл `ASTRA_ShellRequest`. **Никаких** native R/CMD5, G3B2, ammo-записей.

**STOP** (без повторных правок наугад): если редактор снова вычистит/переназначит любую из десяти P/W строк — вернуть post-save AST/P/W-ASI diff и первую точную ошибку. Не переимпортировать ANM/meta, не подменять фазы нативными клипами, не запускать destructive R/CMD5.

---

## 6. Границы

Только исправление animation-source ссылок и ASI-маппингов. Не изменялись: `.anm`/`.anm.meta`, `.agr`, `.aw`, скрипты, bridge prefab, G3B2, production/Core/worlds, native command routing, физмагазин. Второй аддон/workspace не создавался. Pre-Stage1D владельческое live-состояние зафиксировано в отчёте Stage 1C.
