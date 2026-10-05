# ARMST — глобальный отказ pickup/equip: аудит цепочки + staged probe

Статус: **PICKUP_FAIL_INCONCLUSIVE** (статикой однозначный класс не доказан) — **probe подготовлен, live НЕ тронут**.
Дата: 2026-10-05
Задание: Issue #34 — проверить цепочку `interaction → действие поднятия → inventory admission → hand/weapon slot → WeaponManager` для обычного оружия (AK) и ASTRA2 MP-133; классифицировать сбой; при невозможности — подготовить минимальный read-only probe и остановиться перед записью в live.
Запрещено (соблюдено): ASTRA2, `default.layer`, spawn point, reload. Режим: **read-only**.

---

## 0. Классификация (ранжированная)

| # | Класс | Уверенность | Обоснование |
|---|---|---|---|
| 1 | `PICKUP_FAIL_STORAGE_ADMISSION_REJECTED` | средняя | ARMST Core **полностью заменяет** базовый `SCR_UniversalInventoryStorageComponent.CanStoreItem` на grid-проверку, которая **fail-closed** и может навсегда «отравить» хранилище (§2). |
| 2 | `PICKUP_FAIL_CONTROLLER_OR_INTERACTION_CONTEXT` | средняя | В логах нет ни одной строки взаимодействия; в прошлом аудите pawn спавнился не в каждом reload. Если possession/контроллер не поднялся — любое взаимодействие недоступно (§4). |
| 3 | `PICKUP_FAIL_HAND_OR_WEAPON_MANAGER_MISSING_OR_BROKEN` | низкая | `BaseWeaponManagerComponent` модом не трогается; проверяется probe'ом. |
| 4 | `PICKUP_FAIL_CHARACTER_INVENTORY_MISSING_OR_BROKEN` | низкая | `SCR_CharacterInventoryStorageComponent` модом не удаляется. |
| 5 | `PICKUP_FAIL_NO_INTERACTION_ACTION` / `ACTION_NOT_PERFORMABLE` | низкая | Мод не переопределяет pickup-user-action. |
| 6 | `PICKUP_FAIL_ENGINE_BLACK_BOX` | — | Не подтверждён. |

**Итог:** статикой — `PICKUP_FAIL_INCONCLUSIVE`; ведущий кандидат `PICKUP_FAIL_STORAGE_ADMISSION_REJECTED`. Для однозначного класса подготовлен **минимальный read-only probe** (§5), запись в live не выполнялась.

---

## 1. Карта цепочки и точки вмешательства мода

```
interaction (F на предмете)
  └─ pickup user action (vanilla)                         [мод НЕ переопределяет]
       └─ SCR_InventoryStorageManagerComponent.TryInsertItem   [мод: modded class, override только OnItemRemoved]
            └─ FindStorageForItem(...) → target storage
                 └─ target.CanStoreItem(item, slot)        [★ мод: override в SCR_UniversalInventoryStorageComponent]
                      └─ hand / weapon slot / WeaponManager (vanilla)
```

| Звено | Класс | Переопределено ARMST Core? | Файл |
|---|---|---|---|
| interaction / pickup action | vanilla user action | **нет** | — |
| storage manager | `SCR_InventoryStorageManagerComponent` | да, но только `OnItemRemoved` (orphan attachments) | `ARMST_AttachmentInventoryManager.c` |
| **admission** | `SCR_UniversalInventoryStorageComponent` | **да: `CanStoreItem` / `CanStoreResource` / `CanReplaceItem` заменены grid-логикой** | `ARMST_UniversalInventoryStorageComponent.c` |
| item attributes | `SCR_ItemAttributeCollection` | да: grid-атрибуты | `ARMST_ItemAttributeCollection.c`, `ARMST_SCR_ItemAttributeCollection.c` |
| inventory UI | `SCR_InventoryMenuUI` | да (drag/drop, repack) | `ARMST_InventoryMenuUI.c`, `ARMST_SCR_InventoryMenuUI.c` |
| hand/weapon slot, WeaponManager | `SCR_CharacterInventoryStorageComponent`, `BaseWeaponManagerComponent` | **нет** | — |

---

## 2. Ведущий кандидат: admission `CanStoreItem` fail-closed

`ARMST_UniversalInventoryStorageComponent.c`:
```cpp
override bool CanStoreItem(IEntity item, int slotID)
{
    if (owner has SCR_ArsenalInventoryStorageManagerComponent) return super.CanStoreItem(...);
    if (!item) return false;
    if (!ARMST_PassesItemFilter(item)) return false;          // false, если у item нет attributes
    InventoryItemComponent pItemComp = ...; if (!pItemComp) return false;
    if (!ARMST_CellMatrix.CanItemFitInStorage(this, item)) return false;   // ★ grid
    return true;
}
```

`ARMST_CellMatrix.BuildStorageGrid` (используется из `CanItemFitInStorage`) **fail-closed**:
```cpp
foreach (existing item in storage) {
    ... place existing item ...
    if (!placed)
        return false;        // ★ один непомещаемый предмет «травит» хранилище для ВСЕХ новых
}
```
Следствия:
- Если в хранилище есть предмет, который нельзя разместить (например, `armst_Tripod_6T5_PKM.et` с `m_iCustomGridWidth/Height = 100/100`, либо конфликт сохранённой позиции + размер больше сетки), `BuildStorageGrid` вернёт `false` → `CanStoreItem` вернёт `false` для **любого** нового предмета → глобальный отказ.
- `ARMST_PassesItemFilter` возвращает `false`, если у предмета нет attributes (`GetAttributes() == null`).

`ARMST_ItemSizeConfig.DetermineStorageGrid` для `SCR_UniversalInventoryStorageComponent` берёт сетку из class-data: `m_iGridColumns` (default **5**), `m_iGridRows` (default **4**) → **5×4**.

---

## 3. Наблюдаемая аномалия: grid-атрибуты «Unknown keyword/data»

Во **всех** последних прогонах (`21-28-15`, `21-43-48`, `21-46-48`, `20-45-33`, `21-06-31`) при загрузке prefab'ов:

```
WORLD (E): Unknown keyword/data 'm_bAutoDetectGridSize' at offset ...
WORLD (E): Unknown keyword/data 'm_iCustomGridWidth'  at offset ...
WORLD (E): Unknown keyword/data 'm_iCustomGridHeight' at offset ...
```

Суммарно по прогонам: `m_iCustomGridHeight=185`, `m_bAutoDetectGridSize=118`, `m_iCustomGridWidth=95`, `m_Rail=16`, `m_mStackableCustom=7` — это ровно атрибуты ARMST `SCR_ItemAttributeCollection`. Значит, при парсинге prefab'ов класса `ARMST-PLATFORM---Weapons` модовый `SCR_ItemAttributeCollection` **не регистрирует** эти атрибуты (вероятно, порядок загрузки addon'ов: `ARMST-PLATFORM---Weapons` не зависит от `ARMST-PLATFORM---Core`). Эффект: grid-размеры у оружия отбрасываются (остаются defaults 1×1) — само по себе это **не** блокирует admission, но подтверждает, что grid-подсистема неконсистентна. Требует подтверждения probe'ом (`hasAttrs`/`dim`).

---

## 4. Что проверено и исключено

- **Нет** ошибок interaction/action/admission в `script.log` — только оружейные `WARNING: One or more override stats failed to set` (к pawn/pickup отношения не имеют). Значит, «молчаливый» отказ.
- Мод **не** переопределяет pickup-user-action → `NO_INTERACTION_ACTION` маловероятно.
- `BaseWeaponManagerComponent` и `SCR_CharacterInventoryStorageComponent` модом не модифицируются.
- Предыдущий аудит (`ARMST_WEAPON_TEST_PAWN_SPAWN_INVESTIGATION.md`): pawn спавнился не в каждом `Workbench Reload Game` — если тест pickup делался в цикле без possess'а, это даёт `CONTROLLER_OR_INTERACTION_CONTEXT`.

---

## 5. Подготовленный минимальный read-only probe

Staged (в live **не записан**): `Weapon_ARMA_X/artifacts/astra-rebuild/stagePickup/ARMST_T4B_PickupChainProbe.c`
- `modded class SCR_UniversalInventoryStorageComponent` → override `CanStoreItem`, вызывает `super`, затем **только логирует**:
  `storage, item, hasAttrs, dim=WxH, grid=cols x rows, fit, CanStoreItem, slotID`.
- Гейт: только предметы с `WeaponComponent` (AK, MP-133 и др.), жёсткий бюджет 200 строк.
- **Никаких** мутаций/запрещённых API: проверено — 0 writers, braces 6/6, parens 21/21.

Как читать результат:

| Наблюдение при нажатии F на оружии | Класс |
|---|---|
| **нет** строк `[ARMST-T4B-PICKUP]` | сбой до admission → `NO_INTERACTION_ACTION` / `ACTION_NOT_PERFORMABLE` / `CONTROLLER_OR_INTERACTION_CONTEXT` |
| есть строки, `fit=0` / `CanStoreItem=0` | `PICKUP_FAIL_STORAGE_ADMISSION_REJECTED` |
| есть строки, `CanStoreItem=1`, но оружие не экипируется | `PICKUP_FAIL_HAND_OR_WEAPON_MANAGER_MISSING_OR_BROKEN` |

Отдельно probe покажет `hasAttrs=0` для оружия → подтверждение §3.

**Не записываю probe в live.** Для установки нужно: (1) закрытый Workbench, (2) явное разрешение владельца, (3) узкая установка только этого файла в `ARMSTMP133T4B_InstalledMagProbe/Scripts/Game/ARMST_T4B/`.

---

## 6. Итог

- Цепочка картирована; единственная существенная точка вмешательства мода на пути pickup — **grid admission** (`SCR_UniversalInventoryStorageComponent.CanStoreItem`), которая **fail-closed**.
- Статикой класс не доказан → **`PICKUP_FAIL_INCONCLUSIVE`**, ведущий кандидат `PICKUP_FAIL_STORAGE_ADMISSION_REJECTED`.
- Подготовлен минимальный read-only probe; live не изменялся; ASTRA2/`default.layer`/spawn/reload не тронуты.

Статус: **`PICKUP_FAIL_INCONCLUSIVE` — probe staged, live write pending owner go-ahead.**
