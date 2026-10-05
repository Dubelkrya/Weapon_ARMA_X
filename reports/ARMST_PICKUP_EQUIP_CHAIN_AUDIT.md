# ARMST MP-133 T4b — pickup regression: SCOPE CORRECTED to lab-addon-only A/B

Статус: **T4B_LAB_ONLY_PICKUP_BISECT_PREPARED_WB_OPEN_STOP**
Дата: 2026-10-05
Задание: Issue #34 — корректирующий **HARD STOP** [#6001136884](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34).
Режим: **read-only**; live не изменялся (Workbench открыт).

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

## 4. План A/B изоляции (подготовлен, не применён)

1. Убедиться, что Workbench полностью закрыт.
2. Backup уже снят: `artifacts/astra-rebuild/stageBisect/ARMST_T4B_NormalRHandlerProbe.c.bak`
   (SHA-256 `C9D49A1B029E7A4CF39D5F31214666BE8B44F4D9881B170BDF839ED954B92EA6`).
3. Временно **отключить только** `ARMST_T4B_NormalRHandlerProbe.c` в live lab-addon
   (переименовать `→ ARMST_T4B_NormalRHandlerProbe.c.disabled`; Workbench не компилирует `.disabled`).
   Ничего другого не менять.
4. Cold-start Workbench → свежий `weapon_test` → проверить pickup обычного предмета и обычного оружия.
5. Результат:
   - pickup работает → регрессия локализована в `NormalRHandlerProbe.c`;
   - pickup по-прежнему сломан → **восстановить файл байт-в-байт** (из backup) и бисектить остальные lab-скрипты (G3B2 → G3B1 → InstalledMagProbe → AstraV2 → AstraRequest).

Откат: `Copy-Item artifacts/.../ARMST_T4B_NormalRHandlerProbe.c.bak <live>/.../ARMST_T4B_NormalRHandlerProbe.c` (hash совпадает → restore безопасен).

---

## 5. Блокер и статус

```
Workbench / Animation Editor / Game Mode: RUNNING (ArmaReforgerWorkbenchSteamDiag)
→ live write запрещён; A/B (отключение файла) НЕ применён
```

Статус: **`T4B_LAB_ONLY_PICKUP_BISECT_PREPARED_WB_OPEN_STOP`**.
После полного закрытия Workbench: отключу только `ARMST_T4B_NormalRHandlerProbe.c`, синхронизирую labs, узкий commit → **`T4B_LAB_ONLY_PICKUP_BISECT_READY_OWNER_TEST`**.

**Не трогаю:** grid / `SCR_UniversalInventoryStorageComponent` / admission / item attributes / ARMST Core / production Weapons / ASTRA2 / world / spawn / reload.
