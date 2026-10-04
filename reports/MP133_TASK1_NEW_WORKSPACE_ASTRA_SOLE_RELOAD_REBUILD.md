# MP-133 Task #1 — новый Workspace `MP133_AstraRebuild` (Astra — единственный путь перезарядки)

Статус: **TASK1_NEW_WORKSPACE_CLONED_ASTRA_SOLE_RELOAD_GRAPH_SOURCE_READY_OWNER_WB** (GUID-регистрация новых ресурсов — owner Workbench)
Дата: 2026-10-04
Задание: Issue #34 [#5983992087](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983992087) (supersedes Phase2A-2C диагностику).
База: `t4b/installed-mag-probe` @ `f42f35f`. Оригинальный Workspace не изменялся.

---

## 0. Preflight

- Workbench/игра/писатели: **нет**.
- Источник: LIVE `ARMSTMP133T4B_InstalledMagProbe\Assets\MP133_AstraShellGraph` (owner-saved, 22:36:38).
- Оригинальный Workspace прочитан и **не изменялся** (все проверки ниже — по staged-копии).

---

## 1. Что сделано (реальная переработка, не отчёт)

Создан **staged** независимый Workspace `Weapon_ARMA_X/labs/ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraRebuild/`:

| Файл | Содержимое |
|---|---|
| `MP133_Astra.agf` | **переработан** (см. §2) |
| `MP133_Astra.aw` | копия, внутренние ссылки перенацелены на `Assets/MP133_AstraRebuild/…` |
| `MP133_Astra.agr` | копия, ссылки на новый `.ast`/`.agf` |
| `MP133_Astra.ast` | копия (группы/анимации без изменений) |
| `MP133_Astra_player.asi` / `weapon.asi` | копии; `Template` → новый `.ast`; **клипы остаются по ссылке** на оригинальные `Assets/MP133_AstraShellGraph/Clips/*.anm` (без дублирования/переимпорта) |

Плюс изолированный тестовый префаб: `Weapon_ARMA_X/labs/.../Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` — thin child производственного MP-133, фиксированный `Tube3` mag, lab-probe, **без** ASTRA PROBE действия, **без** write-enabled G3B2, без input-хуков.

---

## 2. Переработка `.agf` (Astra — единственный путь; bolt сохранён)

Метод — **безопасный**: legacy-узлы не удалялись (остаются инертными orphan-ссылками, как разрешено заданием), но **старый mag-маршрут сделан недостижимым**, а реальная перезарядка перенаправлена.

- Добавлен `AnimSrcNodeStateMachine ReloadRouteSTM` (Child нового состояния `Reload`):
  - `Bolt` → `Child "RackBoltAnim"`, `StartCondition "GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(...) == 0.0"` (CMD1 — передёргивание, сохранено);
  - `Shell` → `Child "AstraShellErcG"`, `StartCondition "GetCommandI(CMD_Weapon_Reload) >= 2 && <= 6"` (CMD2-6 → `ShellReloadSTM` 5 фаз Astra).
- Состояние `Reload` (в `IdleReloadSTM`): `Child` переведён с `"Blend T 1"` (→ native `WeaponReloadStanceSTM → WeaponReloadSTM → MagReloadSTM`) на `"ReloadRouteSTM"`. Тем самым **маршрут `…→WeaponReloadStanceSTM→WeaponReloadSTM→MagReloadSTM` недостижим**.
- Удалён диагностический вход Astra по `ASTRA_ShellRequest` и состояния `AstraShell`/`AstraWaitRelease` (3 перехода + 2 состояния).
- Убрано `ASTRA_ShellRequest`-гейтирование из условия реального входа `Idle → Buffer3`.
- Сохранены: `ShellReloadSTM` (5 фаз, repeat `CheckContinue→GrabShell`, exit), `AstraShellErcG` (Reload/Erc), 5 Astra-источников; `Reload.ReloadActionBolt`/`RackBoltAnim`; fire/idle/inspection/safety/modes/IK.

**Статическая проверка переработанного `.agf`:**
- `ASTRA_ShellRequest = 0`; `ReloadRouteSTM` = 1; `Reload` Child = `ReloadRouteSTM`; `Bolt→RackBoltAnim`, `Shell→AstraShellErcG` — есть; 5 Astra источников — есть; `Reload.ReloadActionBolt` — есть.
- Все `Child "…"` ссылки разрешаются (unresolved = 0); все `FromState`/`ToState` разрешаются (unresolved = 0); скобки 306/306.
- Legacy-узлы (`WeaponReloadSTM`, `MagReloadSTM`, `InsertMagAnim`, `RemoveMagAnim`, `Blend T 1`, `ReloadErcCroG/PneG`, `WeaponReloadStanceSTM`) присутствуют как **недостижимые** (orphan), что исключает «две конкурирующие системы».

---

## 3. Критический GUID-блокер (owner Workbench GUI)

Новые copied-**ресурсы** обязаны иметь **уникальные** Workbench GUID. Задание прямо запрещает клонировать `.meta` с исходным GUID или изготавливать GUID вручную. Поэтому staged-пакет **намеренно без `.meta`**, а фактическая регистрация в живом аддоне — GUI-шаг владельца:

1. В Workbench (проект T4b) дублировать ресурсы `Assets/MP133_AstraShellGraph/MP133_Astra.{aw,agr,agf,ast,_player.asi,_weapon.asi}` в `Assets/MP133_AstraRebuild/` — Workbench выдаст **новые GUID** и перенастроит внутренние ссылки.
2. Заменить дублированный `MP133_AstraRebuild/MP133_Astra.agf` на staged `MP133_Astra.agf` (переработанный; внутренних ресурсных GUID не содержит).
3. Создать тестовый префаб `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` (staged шаблон дан) и выставить `AnimGraph/AnimInstance/AnimInjection` на **новые** AGR/ASI GUID (в шаблоне стоят исходные GUID — их нужно заменить после дублирования).
4. Оригинальная `Assets/MP133_AstraShellGraph/` остаётся байт-в-байт как baseline/rollback.

Пока GUID не назначены Workbench, жёсткое прописывание новых GUID «руками» не делалось (запрещено).

---

## 4. Физическая замена магазина (движок) — статус

Из нового графа **удалён достижимый mag-swap маршрут**, но это, как прямо указано в задании, **не доказывает**, что движок не выполнит автономную замену физического `Tube3` по реальному input/команде (CMD4/5). Это остаётся **engine-level UNRESOLVED** и требует отдельного, узко ограниченного lab-scoped решения (например, перехват/маппинг реального reload-входа на новый лаб-фикстур) — **без** global `modded` и без изменений других стволов. В `MP133_AstraRebuild_TestWeapon.et` фиксированный `Tube3` уже задан; реальный R/CMD4/5 тест **не проводился**.

---

## 5. Сохранность

- Оригинал `Assets/MP133_AstraShellGraph/` (в т.ч. рабочий `.agf`), 10 ANM + importer meta, native CMD1 `Reload_Bolt`, скрипты, G3B2, bridge-префаб, Core/production/worlds — **не изменялись**.
- Изменения — только новый staged пакет в `Weapon_ARMA_X/labs/` (+ отчёт). Живой аддон не тронут, т.к. регистрация новых ресурсов требует Workbench.

---

## 6. Проверка владельцем (закрыв Workbench перед правками)

1. Выполнить GUI-дублирование (§3) и заменить `.agf`.
2. Открыть **новый** `Assets/MP133_AstraRebuild/MP133_Astra.aw` независимо от оригинала: ноль новых красных ошибок графа/скриптов; 5 фаз `Reload/Erc` P/W ASI назначены.
3. Animation-only preview нового графа: `StartReload → GrabShell → InsertShell → CheckContinue → EndReload`, repeat `CheckContinue→GrabShell`, выход; CMD1 (bolt) не тронут.
4. **Не** запускать gameplay R/CMD4/5 до подтверждённой защиты физического `Tube3`. Rack — отдельный известный путь.

**Ожидаемый статус после GUI-шага:** `TASK1_NEW_WORKSPACE_CLONED_ASTRA_SOLE_RELOAD_GRAPH_SOURCE_READY_OWNER_WB`.
