# ARMST Weapon_test — почему «нет pawn»: аудит world / GameMode / spawn

Статус: **WEAPON_TEST_PAWN_SPAWN_AUDIT_DONE**
Дата: 2026-10-05
Задание: Issue #34 — узкая проверка `worlds/Weapon_test/weapon_test.ent`, GameMode, spawn point / player spawning и последних изменений.
Режим: **read-only** (live не изменялся). Branch `t4b/installed-mag-probe`.

---

## 0. Главный вывод (premise correction)

**Персонаж в логе ЕСТЬ.** В последней сессии Workbench (`logs_2026-10-05_21-28-15`) за 4 цикла `Workbench Reload Game` созданы:

- `SCR_PlayerController` — 4×;
- `SCR_EditorManagerEntity` — 4×;
- **`Character_US_Rifleman.et` / `SCR_ChimeraCharacter` — 2×** (циклы A и B).

Последовательность «`SCR_PlayerController` → `SCR_EditorManagerEntity` → и всё, персонажа нет» соответствует **циклам C и D** этой же сессии. Т.е. pawn спавнится **не всегда**, а не «вообще не спавнится». `possess` в логе отдельной строкой не логируется, поэтому «нет possession» по логу не доказуемо.

Цикл, в котором персонаж **есть** (фрагмент, `logs_2026-10-05_21-28-15\console.log`):

```
L737  WORLD   : Initializing world systems @BaseGameModeSystems.conf
L853  ENTITY  : Init entity ... ('GameMode_Plain1', SCR_BaseGameMode) at <123.266 1.000 136.614>
L870  ENTITY  : SpawnEntityPrefab @DefaultPlayerControllerMP.et
L871  ENTITY  : Create entity ... ('SCR_PlayerController')
L888  ENTITY  : SpawnEntityPrefab @EditorManager.et
L889  ENTITY  : Create entity ... ('SCR_EditorManagerEntity')
L896  ENTITY  : SpawnEntityPrefab @Character_US_Rifleman.et
L897  ENTITY  : Create entity ... ('SCR_ChimeraCharacter') at <147.451 2.791 76.570>
L916  SCRIPT  : SCR_BaseGameMode::OnGameStateChanged = GAME
```

Цикл, в котором персонажа **нет** (C):

```
L1877 WORLD   : Game::LoadEntities
L1878 WORLD   : Initializing world systems @BaseGameModeSystems.conf
L1994 ENTITY  : Init entity ... ('GameMode_Plain1', SCR_BaseGameMode)
L2012 ENTITY  : SpawnEntityPrefab @DefaultPlayerControllerMP.et
L2013 ENTITY  : Create entity ... ('SCR_PlayerController')
L2030 ENTITY  : SpawnEntityPrefab @EditorManager.et
L2031 ENTITY  : Create entity ... ('SCR_EditorManagerEntity')
L2046 SCRIPT  : SCR_BaseGameMode::OnGameStateChanged = GAME      <-- Character_US_Rifleman отсутствует
```

GameMode-сущность инициализируется **одинаково** во всех 4 циклах (тот же `ENTITY:4611686018427387906`, те же координаты `<123.266 1.000 136.614>`), `OnGameStateChanged = GAME` — во всех 4. Ошибок скриптов, объясняющих отсутствие pawn, нет.

---

## 1. Корреляция: спавн pawn привязан к загрузке world/subscene

Единственные два места в логе, где грузится **миссия-мир** и её родительский subscene:

```
L313/L314 WORLD : Entities load '$ARMSTPLATFORMWeapons:worlds/Weapon_test/weapon_test.ent'
L315      WORLD : Subscene load @"{3048828FE14AE687}worlds/Tests/TestFramework/Autotest_GameMode_Plain.ent"
...
L1122/L1123 WORLD : Entities load '$ARMSTPLATFORMWeapons:worlds/Weapon_test/weapon_test.ent'
L1124      WORLD : Subscene load @".../Autotest_GameMode_Plain.ent"
```

| Цикл | `Workbench Reload Game` | `Entities load …weapon_test.ent` + `Subscene load` | `GameMode_Plain1` init | `SCR_ChimeraCharacter` |
|---|---|---|---|---|
| A | L291/L718 | **да** (L313-315) | L853 | **да** (L897) |
| B | L954/L1100/L1478 | **да** (L1122-1124) | L1622 | **да** (L1667) |
| C | L1706/L1857 | **нет** | L1994 | **нет** |
| D | L2058/L2209 | **нет** | L2346 | **нет** |

Во всех циклах грузятся world systems (`BaseGameModeSystems.conf`) и создаются мировые сущности, но **полная загрузка `.ent` + parent-subscene происходит только в A и B — и только там спавнится pawn**. Дальнейшие `Workbench Reload Game` (горячая перезагрузка скриптов/ресурсов) пересоздают GameMode, но не перезагружают mission-`.ent`, и vanilla-GameMode не выполняет повторный спавн игрока.

**Вывод:** поведение pawn привязано к загрузке мира/родительского subscene в vanilla-GameMode, а не к prefab'у оружия, ASTRA2 или cleanup. Точная внутренняя причина (почему повторный reload без world-load не спавнит) — в vanilla `SCR_BaseGameMode`/`Autotest_GameMode_Plain`, исходников которых в репозитории нет; помечено **UNRESOLVED (vanilla/Workbench)**.

---

## 2. World / GameMode

`ARMST-PLATFORM---Weapons\worlds\Weapon_test\weapon_test.ent` (весь файл):

```
SubScene {
 Parent "{3048828FE14AE687}worlds/Tests/TestFramework/Autotest_GameMode_Plain.ent"
}
```

- Родитель — **vanilla** TestFramework GameMode: строка `Autotest_GameMode_Plain` найдена в `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger\addons\data\resourceDatabase.rdb` (там же 11 вхождений `SCR_SpawnPoint`). В addons-репозитории этого ресурса нет.
- **История `weapon_test.ent`:** коммиты `2f3a2f9` («Тестовые изменения») и `1be4216` («тестовый мир»); на HEAD (`9ebf323`) содержимое идентично рабочему. **Родитель не менялся недавно.**
- `weapon_test_Layers/default.layer` (577 строк) — только оружие/магазины/столы/оптика. **Ни одного `SCR_SpawnPoint` / spawn-сущности.** Значит, позиция спавна задаётся vanilla-GameMode (в циклах A/B координаты разные: `<147.451 2.791 76.570>` и `<146.928 2.366 75.813>` → не фиксированный world-spawn-point, похоже на позицию Workbench-камеры на момент Play).

---

## 3. Последние изменения (что реально изменилось)

В `ARMST-PLATFORM---Weapons` **незакоммичены**:

| Файл | Изменение | Связь со спавном |
|---|---|---|
| `worlds/Weapon_test/weapon_test_Layers/default.layer` | заменён `ARMST_T4B_TestWeapon.et` → `ARMST_T4B_AstraRebuild_TestWeapon.et`; добавлены 4× `ARMST_T4B_G3B2_Tube3Mag.et` | **нет** (только оружие) |
| `resourceDatabase.rdb` | служебная БД Workbench | нет |

Других изменений в мире/GameMode нет. **Cleanup ASTRA2 на спавн не влиял.**

Побочно: в **закоммиченном** `default.layer` осталась ссылка на удалённый в прошлой задаче `{C2D3E4F506172839}Prefabs/Test/ARMST_T4B_TestWeapon.et`. В рабочей копии она уже заменена на канонический prefab — dangling только в HEAD-состоянии (см. §5).

---

## 4. Что проверено и исключено

- **Нет ошибок спавна в script.log:** единственные `(E)` — `WARNING: One or more override stats failed to set` (оружие/аттачменты), к pawn отношения не имеют.
- **ARMST-скрипты не управляют спавном в этом мире:** `weapon_test` использует vanilla `Autotest_GameMode_Plain`; ARMST-специфичный спавн/респавн (`ARMST_RESPAWN_SYSTEM.c`, `ARMST_SCR_PlayerInit.c`, `ARMST_SCR_PlayerCreateCharacter.c`) завязан на `SCR_RespawnSystemComponent`/ARMST-UI полного гейммода и в этом логе не активируется.
- `modded class SCR_ChimeraCharacter` (ARMST Core) не блокирует спавн (только `EOnInit` + звук/камера/логика смерти).
- Количество оружий/канонический prefab создаются нормально — это подтверждает, что дело не в prefab'ах.

---

## 5. Рекомендация

1. **Перед следующим тестом — полностью перезапустить Workbench** (закрыть и открыть заново, затем загрузить `weapon_test`), а не полагаться на `Workbench Reload Game`. «Предыдущий рабочий запуск» с `Character_US_Rifleman` — это свежая загрузка мира; последние два цикла — горячие reload'ы без world-load.
2. Проверять спавн pawn **до** любых манипуляций с оружием/`R`.
3. Если нужен **гарантированный** спавн (не зависящий от порядка reload'ов) — добавить в `default.layer` явный `SCR_SpawnPoint` (или использовать гейммод с собственным player-spawn). Это **изменение дизайна мира**, требует отдельного согласования; в этой задаче не делалось.
4. Закоммитить рабочую правку `default.layer` (она снимает dangling-ссылку на удалённый `ARMST_T4B_TestWeapon.et`) — иначе HEAD-состояние ссылается на несуществующий prefab.
5. ASTRA2 / канонический prefab **не трогать** (как и просил владелец).

---

## 6. Итог

- **Premise:** не подтверждена — pawn спавнится, но не в каждом `Workbench Reload Game`.
- **Причина (наблюдаемая):** спавн pawn совпадает с полной загрузкой mission-`.ent` + parent-subscene; повторные script-reload'ы без неё pawn не спавнят.
- **Не причина:** cleanup ASTRA2, канонический prefab, `default.layer` (оружие), ARMST-скрипты.
- **UNRESOLVED:** внутренняя причина в vanilla `SCR_BaseGameMode`/`Autotest_GameMode_Plain` (нет исходников в репо).

Статус: **`WEAPON_TEST_PAWN_SPAWN_AUDIT_DONE`**.
