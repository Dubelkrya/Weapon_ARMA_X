# ARMST MP-133 T4b — pickup regression: SCOPE CORRECTED to lab-addon-only A/B

Статус: **T4B_RPROBE_V1_PLUS_UPDATE_PREPARED_WB_OPEN_STOP**
Дата: 2026-10-05
Задание: Issue #34 — HARD STOP [#6001136884](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34) + V1-результат [#6001411080](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34): `HANDLE_WEAPON_RELOADING_PICKUP_REGRESSION = EXONERATED`.
Режим: V1 установлен в live; вариант **V1 + Update()** — **только подготовлен**, live не менялся.

---

## 0. Коррекция границ задачи (принята)

Предыдущий вывод про глобальный `SCR_UniversalInventoryStorageComponent.CanStoreItem` (ARMST Core grid) — **ошибочный выход за границы Task #1**. Grid-система, Core inventory и item-attributes — **OUT OF SCOPE**. Работа по ним остановлена.

Подтверждено владельцем: pickup-регрессия вызвана включением **`ARMSTMP133T4B_InstalledMagProbe`** (с ним подобрать нельзя **никакой** предмет; без него — работает).

---

## 1. Что сделано по HARD STOP

- **`ARMST_T4B_PickupChainProbe.c` НЕ установлен** ни в live, ни в labs, ни в Core, ни в Weapons (проверено рекурсивно: файл отсутствует везде). Удалять из live нечего.
- Staged-артефакт `artifacts/astra-rebuild/stagePickup/ARMST_T4B_PickupChainProbe.c` **удалён** (пустая папка тоже).
- `SCR_UniversalInventoryStorageComponent` / grid / admission / item attributes / ARMST Core / production Weapons — **не тронуты**.
- ASTRA2, canonical prefab, `default.layer`, spawn point, reload, Tube3 — не тронуты.

---

## 2. Инвентарь lab-addon скриптов и глобальные модификации

| Файл | Размер | Глобальная модификация |
|---|---|---|
| `ARMST_T4B_NormalRHandlerProbe.c` | 7727 | **`modded class SCR_CharacterCommandHandlerComponent`** ← единственная |
| `ARMST_T4B_InstalledMagProbe.c` | 20525 | нет |
| `ARMST_T4B_AstraRequestProbe.c` | 3186 | нет |
| `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | 5386 | нет |
| `ARMST_T4B_G3B1_DonorConsume.c` | 16624 | нет |
| `ARMST_T4B_G3B2_Transfer.c` | 52659 | нет |

Скан `modded class` / `modded enum` / `[RplRpc]` по всему `Scripts/` lab-addon: **единственная** глобальная модификация — `ARMST_T4B_NormalRHandlerProbe.c`. Все остальные файлы — локальные компоненты/экшены.

---

## 3. Suspect: `ARMST_T4B_NormalRHandlerProbe.c` (hash `C9D49A1B…EA6`)

`modded class SCR_CharacterCommandHandlerComponent` с тремя override:

| Override | Поведение |
|---|---|
| `Update(float, int, bool)` | каждый тик: `RProbeResolve` (→ `GetControllerComponent` → `GetWeaponManagerComponent` → `GetCurrentWeapon` → `FindComponent(ARMST_T4B_WeaponProbe)`); non-lab → `super.Update`; lab → лог + `super.Update` |
| `HandleWeapons(CharacterInputContext, float, int)` | non-lab → сразу `super`; lab → лог при `WeaponIsStartReloading()` + `super` |
| `HandleWeaponReloading(CharacterInputContext, float, int)` | non-lab → `super`; **lab → `return true`** (consume reload request) |

Все override вызывают `super` для non-lab, поэтому статически «почему ломается pickup любого предмета» **не доказано**. Единственная глобальная точка вмешательства lab-addon — этот файл; A/B тест это и проверит.

---

## 4. A/B изоляции — ПРИМЕНЕНО

Workbench полностью закрыт (`Workbench/Reforger/Arma/Enfusion` = NONE). Выполнен **ровно один rename**:

| | |
|---|---|
| live | `ARMST_T4B_NormalRHandlerProbe.c` → `ARMST_T4B_NormalRHandlerProbe.c.disabled` |
| labs | `ARMST_T4B_NormalRHandlerProbe.c` → `ARMST_T4B_NormalRHandlerProbe.c.disabled` |
| содержимое | **не изменялось** — hash `.disabled` = `C9D49A1B029E7A4CF39D5F31214666BE8B44F4D9881B170BDF839ED954B92EA6` (совпадает с исходным) |
| прочие файлы | **не тронуты** |

Backup: `artifacts/astra-rebuild/stageBisect/ARMST_T4B_NormalRHandlerProbe.c.bak` (тот же hash).

Тест владельца: cold-start Workbench → свежий `weapon_test` → pickup (1) обычного предмета, (2) обычного оружия.

Результат:
- pickup работает → регрессия локализована в `NormalRHandlerProbe.c`;
- pickup по-прежнему сломан → восстановить файл байт-в-байт из backup и бисектить остальные lab-скрипты (G3B2 → G3B1 → InstalledMagProbe → AstraV2 → AstraRequest).

Откат: `Rename-Item .../ARMST_T4B_NormalRHandlerProbe.c.disabled → .../ARMST_T4B_NormalRHandlerProbe.c` (hash совпадает → restore безопасен).

---

## 5. Статус

Workbench закрыт, rename применён и синхронизирован в labs, узкий commit сделан (`717d66a`).

Статус A/B: **`T4B_LAB_ONLY_PICKUP_BISECT_READY_OWNER_TEST`**.

**Не тронуто:** grid / `SCR_UniversalInventoryStorageComponent` / admission / item attributes / ARMST Core / production Weapons / ASTRA2 / world / spawn / reload / Tube3 / canonical prefab.

---

## 6. Контроль V1 (`57c7124`) — ПРИМЕНЕНО

Владелец подтвердил: причина локализована до `ARMST_T4B_NormalRHandlerProbe.c`; остальная lab работает (ASTRA2, pawn, T4B-события). Контроль — **старый V1 из `57c7124`**: только `HandleWeaponReloading(...)`, без V2-override'ов `Update(...)` и `HandleWeapons(...)`.

Workbench закрыт. Применено:
- live `ARMST_T4B_NormalRHandlerProbe.c` = V1, SHA-256 `D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32` (4434 bytes);
- labs синхронизирован тем же файлом;
- `.disabled` (A/B) удалён;
- override'ов ровно один: `HandleWeaponReloading`; `Update` = 0, `HandleWeapons` = 0; braces 10/10, parens 47/47, 0 запрещённых writers.

Тест владельца: cold start → свежий `weapon_test` → pickup (1) обычного предмета, (2) обычного оружия.

Результат:
- V1 pickup работает → поломку внесли именно **V2-override'ы** `Update(...)` / `HandleWeapons(...)`;
- V1 тоже ломает → причина в самом `modded class SCR_CharacterCommandHandlerComponent` / `HandleWeaponReloading`.

Откат к V2: `artifacts/astra-rebuild/stageBisect/ARMST_T4B_NormalRHandlerProbe.c.bak` (`C9D49A1B…EA6`).

Статус: **`T4B_LAB_ONLY_PICKUP_BISECT_V1_READY_OWNER_TEST`**.

---

## 7. Контроль «V1 + Update() only» — ПОДГОТОВЛЕН (live не тронут)

Владелец подтвердил (Issue #34 [#6001411080](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)):
- с V1 предметы/оружие подбираются снова; `R` намеренно не перезаряжает (V1 `HandleWeaponReloading` возвращает `true`);
- **`HANDLE_WEAPON_RELOADING_PICKUP_REGRESSION = EXONERATED`**;
- fault domain: `V2 Update(...)` и/или `HandleWeapons(...)`.

Staged (в live **не записан**): `artifacts/astra-rebuild/stageV1Update/ARMST_T4B_NormalRHandlerProbe.c`
- SHA-256 `33CDFFCE0F28081AAFEC0DC29C12F4F4C0263D26B8ADD7CE8A73D2DD92D4CE3E` (8389 bytes).
- Состав: base = **V1 handler-only (`57c7124`)**; добавлены **только** V2 `Update(...)` + строго необходимые helper/state (`RProbeResolve`, `RProbeTag`, `RProbeLog`, поля seq/last-state).
- `override void Update` = **1**; `override bool HandleWeapons` = **0**; `override bool HandleWeaponReloading` = **1** (V1, без изменений).
- braces 28/28, parens 123/123; **0** запрещённых writers.

Точный diff vs текущий V1: `artifacts/astra-rebuild/stageV1Update/V1_to_V1PlusUpdate.diff`
(added 177 / removed 19 — удаления только в шапке-комментарии; добавленные методы: `RProbeResolve`, `RProbeTag`, `RProbeLog`, `Update`; `HandleWeapons` отсутствует).

Решение:
- pickup ломается с V1+Update → источник регрессии `Update`;
- pickup работает → остаётся `HandleWeapons`.

Правила соблюдены: no Core/grid/inventory/world/ASTRA2/prefab changes; live не изменялся; применение — только после подтверждения владельцем, что Workbench закрыт.

Статус: **`T4B_RPROBE_V1_PLUS_UPDATE_PREPARED_WB_OPEN_STOP`**.
