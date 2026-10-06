# MP-133 Task #1 — Custom R input-routing audit (Phase A, READ-ONLY / SOURCE-ONLY)

Статус: **T4B_CUSTOM_R_INPUT_ROUTING_AUDIT_COMPLETE**
Дата: 2026-10-06
Задание: Issue #34 — архитектурный pivot, Phase A ([#6021866345](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **read-only / source-only**. Live/labs/gameplay/ASTRA2/prefab/Tube3/Core/grid/inventory не менялись.

**Финальная классификация:** `CUSTOM_R_ACTION_FEASIBLE_BUT_VANILLA_SUPPRESSION_UNRESOLVED`

Метки: **SOURCE** (SDK/файл), **RUNTIME** (owner-лог), **INFERENCE**, **UNRESOLVED**.

---

## 1. Точный input path (SOURCE/RUNTIME)

**Custom action (существующий ARMST-паттерн, SOURCE):**
- `ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf`:
  ```
  ActionManager {
   Actions { Action ARMST_LIGHT_RELOAD_ACTION { InputSource InputSourceCombo { KC_R + KC_LSHIFT } } ... }
   Contexts {
    ActionContext CharacterGeneralContext { ActionRefs +{ "ARMST_...", ... } }
    ActionContext InventoryContext { ActionRefs +{ "RotateItem" } }   // RotateItem = single KC_R
    ActionContext ARMST_Pda3DContext { Priority 10000 ... }
    ActionContext PdaContext { Priority 100 ... }
    ActionContext BookContext { Priority 100 Flags 0x6 0 ... }
   }
  }
  ```
- `keyBindingMenu.conf` — `SCR_KeyBindingEntry { m_sActionName "ARMST_..." }` для каждого action.

**Подписка в скрипте (SOURCE):**
- Core `ARMST_WEAPONS_HANDLER.c` / `ARMST_PLAYER_CharacterController.c`:
  `GetGame().GetInputManager().AddActionListener("ARMST_LIGHT_RELOAD_ACTION", EActionTrigger.DOWN, OnRackBoltMDown)` / `RemoveActionListener(...)`.

**Ключевой факт (SOURCE):** одна физическая клавиша `R` **уже** привязана к нескольким action'ам в **разных контекстах**:
`RotateItem` (single `KC_R`, `InventoryContext`), `BuyItem` (single `KC_R`, `CharacterGeneralContext`), vanilla reload (`Reload`, базовый контекст), `ARMST_LIGHT_RELOAD_ACTION` (`R+LSHIFT`), `ARMST_CHECK_AMMO_ACTION` (`R+LCONTROL`). → **контекст определяет, какой action сработает для одной и той же клавиши** (SOURCE).

**Vanilla reload action** — базовый `Reload`/`WeaponReload` в базовом character-контексте (не в Core-конфиге; движковый). Hmm — точное имя/контекст vanilla reload action в SDK-конфиге **UNRESOLVED** (vanilla `.conf` в paks).

---

## 2. Action/context API (SOURCE)

| Механизм | Где | Метка |
|---|---|---|
| `ActionManager { Actions { Action <NAME> { InputSource ... } } }` | config | SOURCE |
| `ActionContext { Priority <N>; Flags <0xN>; Actions {...}; ActionRefs +{...} }` | config | SOURCE |
| `ActionRefs +{ }` — добавить action в **существующий** контекст | config | SOURCE |
| `ActionContext <NAME> : "<guid>path.conf"` — наследование контекста | config | SOURCE |
| `GetGame().GetInputManager().AddActionListener(name, trigger, cb)` / `RemoveActionListener` | script | SOURCE (использование в Core) |
| `ActivateContext(name)` / `DeactivateContext(name)` | script | SOURCE (Core: `ActivateContext("TraderContext")`) |
| `SCR_MenuActionsComponent.ActivateActions()/DeactivateActions()`, `AddActionListeners()` | script | SOURCE (SDK) |
| `SCR_RadialMenu.AddActionListeners()`, `GetPreventSelectionContext()` | script | SOURCE (SDK) |

**Приоритет/consume/exclusive (UNRESOLVED):** конфиг предоставляет `ActionContext.Priority` и `ActionContext.Flags 0xN`, и одна клавиша реально используется разными контекстами (`RotateItem` vs `BuyItem` vs vanilla reload) → **контекстная селекция существует** (SOURCE). Но **семантика** `Priority`/`Flags` (блокирует ли контекст более низкий при той же клавише, или оба срабатывают) в установленном SDK/Doxygen **не документирована** (класс `InputManager`/`ActionContext` в публичном индексе отсутствует) → **UNRESOLVED**.

---

## 3. Может ли ARMST action получить `R`, а vanilla reload — нет? (цель double-fire)

- **Action** для ARMST MP-133 **технически создать можно** (SOURCE: config `Action` + `keyBindingMenu.conf` + `AddActionListener`).
- **Одна клавиша R в разных контекстах** — подтверждено (SOURCE).
- **Гарантированное подавление vanilla reload action** для MP-133 **без глобального `HandleWeaponReloading`** — **UNRESOLVED**: неизвестно, даёт ли `ActionContext.Priority`/`Flags` «block lower context» семантику. Если нет — возможен **double-fire** (`ARMST action` + vanilla reload) → FAIL по критерию владельца.
- Требуемый критерий владельца: `MP-133: R -> ARMST only` и `other weapon: R -> vanilla only`. Доказать его статикой **нельзя**; нужен runtime (Phase B).

---

## 4. Lifecycle MP-133 context (SOURCE/INFERENCE, без per-frame polling)

Событийные кандидаты (SOURCE, SDK):
- `BaseWeaponManagerComponent.m_OnWeaponChangeCompleteInvoker` / `m_OnWeaponChangeStartedInvoker` (+ `OnWeaponChangeComplete/Started`) — weapon switch/equip;
- `BaseWeaponComponent.OnWeaponActive()` / `OnWeaponInactive()` (`void`, script-overridable) — weapon activated/deactivated;
- `SCR_CharacterControllerComponent` invokers `m_OnWeaponRaising*/m_OnWeaponLowering*`.

**Предлагаемый lifecycle (INFERENCE):**
- активировать MP-133 context (`ActivateContext("ARMST_MP133_ReloadContext")`) при экипировке canonical/lab MP-133 (проверка `ARMST_T4B_WeaponProbe` на текущем оружии);
- деактивировать при switch/unequip;
- триггеры — `OnWeaponChangeComplete`/`OnWeaponActive`/`OnWeaponInactive` (событийно), **без** `Update`/polling.

Точная привязка «context только для MP-133» — **UNRESOLVED** (нужен runtime).

---

## 5. Можно ли получить R без vanilla reload API?

Требование: для MP-133 custom path **не** вызывать `HandleWeaponReloading`/`HandleWeaponReloadingDefault`/`ReloadWeapon`/`ReloadWeaponWith`/`SetReloadWeapon`.
- ARMST action через `AddActionListener` **не** вызывает ни одну из этих функций (SOURCE) — можно получать `R` в ARMST-коде независимо.
- Но **сам vanilla reload action** (движковый) всё равно сработает на ту же `R`, если контекст его не подавит → см. §3 (UNRESOLVED).

---

## 6. Native rack — анализ (RUNTIME/SOURCE)

- RUNTIME: `R` → `cmd1` (rack) при пустом патроннике; затем `Weapon_Rack_Bolt`; патрон в патроннике.
- Т.е. **`cmd1` сейчас приходит от той же физической `R`** через vanilla reload decision (SOURCE: `HandleWeaponReloadingDefault` + graph cmd1).
- Следствие (INFERENCE): если MP-133 context **подавит** vanilla reload action целиком, то **`cmd1` rack тоже исчезнет**. Значит custom route обязан **сам** обслуживать rack (например, через ASTRA rack-ветку), либо context должен подавлять **только** tube-reload (cmd2–6), а не rack (cmd1) — а это одна и та же action, поэтому **разделить статикой нельзя**.
- **Вывод:** сохранение native rack — отдельный обязательный пункт Phase B/C; «подавить R для vanilla» и «сохранить rack» **конфликтуют**, если подавляется весь reload action. Не угадывать.

---

## 7. Double-fire: механизм предотвращения

Требуемый результат:
```
MP-133     : R -> ARMST only
other weapon: R -> vanilla only
```
Механизм-кандидат (INFERENCE): MP-133-only `ActionContext` с `Priority` выше базового и флагом «block lower», активируемый на equip/switch. **Гарантия отсутствия double-fire статикой не доказана** → **UNRESOLVED**.

---

## 8. Один минимальный Phase-B probe (НЕ реализован)

**Цель:** доказать routing одной `R` без единого writer'а.
- добавить (отдельно авторизуемо) MP-133-only action `ARMST_MP133_Reload` (`chimeraInputCommon.conf` + `keyBindingMenu.conf`) и context, активируемый на equip canonical MP-133;
- `AddActionListener("ARMST_MP133_Reload", DOWN, cb)` → лог `ARMST_R_RECEIVED=1`;
- **одновременно** пассивно логировать отсутствие/наличие vanilla `CMD_Weapon_Reload` (`OnCharacterCommand` уже есть) в том же окне;
- **никаких** `SetAmmoCount`, mag attach/detach, chamber writers, ASTRA-запуска, G3B2, таймеров, `Update`;
- контроль: обычное (не-MP-133) оружие должно по-прежнему получать vanilla reload.

**Read-out:**
- `ARMST_R_RECEIVED=1` и vanilla `cmd5` отсутствует → `CUSTOM_R_CONTEXT_FEASIBLE_WITH_VANILLA_SUPPRESSION` подтверждён;
- `ARMST_R_RECEIVED=1` **и** vanilla `cmd5` присутствует → double-fire → suppression не работает;
- `ARMST_R_RECEIVED=0` → routing не сработал.

---

## 9. Итог

| Вопрос | Ответ | Метка |
|---|---|---|
| можно ли отдельный ARMST R action | да (config + listener) | SOURCE |
| одна клавиша R в разных контекстах | да (RotateItem/BuyItem/reload) | SOURCE |
| подавление vanilla reload контекстом | семантика `Priority`/`Flags` не документирована | UNRESOLVED |
| MP-133-only context lifecycle | событийно (weapon-change/active) | INFERENCE |
| R без vanilla reload API | да (listener), но vanilla action всё равно на ту же R | SOURCE/UNRESOLVED |
| native rack | сейчас от той же R → конфликт с полным подавлением | RUNTIME/INFERENCE |
| double-fire prevention | кандидат есть, гарантия не доказана | UNRESOLVED |

**Классификация: `CUSTOM_R_ACTION_FEASIBLE_BUT_VANILLA_SUPPRESSION_UNRESOLVED`.**
Custom R action выполним; **гарантированное подавление vanilla reload** (без глобального `HandleWeaponReloading` и без double-fire) статикой не доказано — нужен Phase-B runtime.

---

## 10. Границы

Live/labs/Workbench/prefab/graph/gameplay не менялись; `GAMEPLAY_FILES_CHANGED=0`. Global `HandleWeaponReloading` не восстанавливается; global storage override не реализуется; cmd7 не предлагается; Chungus не копируется; input не реализован.

Статус: **`T4B_CUSTOM_R_INPUT_ROUTING_AUDIT_COMPLETE`**.
