# MP-133 Task #1 — Rack-bypass reconciliation audit (READ-ONLY)

Статус: **RACK_BYPASS_AUDIT_COMPLETE / HANDLER_SUPER_PATH_INSUFFICIENT**
Дата: 2026-10-06
Задание: Issue #34 — owner correction «rack bypass delegated to super, but native rack DID NOT execute» ([#6003677961](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **read-only**. Live не изменялся; Workbench считается RUNNING.

---

## 0. Исправленная классификация

Предыдущий `NATIVE_RACK_BYPASS_PASS` **недействителен**.

Лог доказал только:
```
reloadType=1 → наш handler НЕ ставит cmd10 → уходит в super
```
Факт игры: **затвор не передёрнулся**. Верный результат:
**`RACK_BYPASS_DELEGATED_TO_SUPER_BUT_NATIVE_RACK_NOT_EXECUTED`**.

Следствие: последующий `reloadType=6` **нельзя** считать нормальной «перезарядкой трубки после rack» — rack не завершился, chamber не восстановлен.

---

## 1. Audit outcome

**Ведущий: `HANDLER_SUPER_PATH_INSUFFICIENT`.**

Присутствие `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` не даёт native rack выполниться, **даже когда override делегирует в `super`**. Это подтверждено двумя независимыми фактами:
- текущий runtime: `reloadType=1` → `return super.HandleWeaponReloading(...)` → rack не выполнился;
- исторический **P2** (`reports/MP133_V3_1_I1_LAB_INTERFERENCE_INVENTORY.md`): pass-through `modded HandleWeaponReloading` ломал обычный R на всех pump-shotguns; исключение handler'а возвращало R (`P2_R_RESTORED / LEGACY_HANDLER_IMPLICATED`).

**Механизм — UNRESOLVED.** Доказать статикой, что `super.HandleWeaponReloading(...)` цепочкой доходит до движкового `HandleWeaponReloadingDefault`, нельзя; исторический I1 уже запрещал спекулятивный вызов `...Default` (риск double-run). SDK: `HandleWeaponReloading` = `bool` (script), `HandleWeaponReloadingDefault` = `proto external bool` (движок).

---

## 2. Критический confound: несколько handler'ов включены одновременно

`C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\profile\.projectList_app1874910_*.conf` (**SOURCE**) включает **одновременно**:
- `ARMSTMP133T4B_InstalledMagProbe` — наш handler;
- `ARMST_MP133_AnimationLab` — исторический handler (`ARMST_MP133_Lab_CommandHandler.c`);
- `.../MP133_Lab_Backups/P2_no_handler/ARMST_MP133_AnimationLab` — P2-копия.

`modded class SCR_CharacterCommandHandlerComponent` присутствует в **≥2** включённых аддонах (наш + исторический). Значит наш `super.HandleWeaponReloading(...)` **проходит через исторический override**, а тот при `ctrl.LabInsertEnabledOnCurrentWeapon()` делает `LabRequestInsertFromHandler(...); return true;` (consume). Даже при gate OFF исторический handler добавляет `modded SCR_CharacterControllerComponent` (`OnInit`/`OnControlledByPlayer`/`OnApplyControls` + trace) — дополнительный confound.

→ Точный виновник (наш override vs исторический) **не изолирован**.

---

## 3. Что проверено и исключено

| Проверка | Результат |
|---|---|
| `CMD1_GRAPH_ROUTE_NOT_REACHED` | **НЕ поддержано.** ASTRA2-граф всё ещё содержит ветку cmd1: `IdleReloadSTM → ReloadRouteSTM` entry `IsCommand(CMD_Weapon_Reload) && GetCommandI(...)==1 && GetCommandF(...)==0.0` (L259/L301) → `RackStanceSTM` (StartCondition `cmd==1`, L336) → `RackBoltAnim` (`Source "Reload.ReloadActionBolt"`). |
| `CURRENT_LAB_WIRING_BLOCKS_RACK` | **Сам по себе не подтверждён.** Canonical prefab wiring корректен: `WeaponComponent → ARMST_T4B_AstraV2_WeaponAnimationComponent {60B4EA76EB15F6E0}` → `MP133_Astra2.agr` + `_weapon.asi` + injection `_player.asi`, `BindWithInjection 1`. Но исторический `modded SCR_CharacterControllerComponent` — confound. |
| Core не трогает reload | Подтверждено ранее: Core **не** переопределяет `HandleWeaponReloading`/`...Default`. |
| `reloadType=1` = requested type at handler entry | Да; требует базового flow **после** return, который наш override (и/или исторический) ломает. |

---

## 4. Почему `return super` недостаточно (гипотезы)

| # | Гипотеза | Статус |
|---|---|---|
| H1 | Присутствие `modded HandleWeaponReloading` мешает native reload для всех оружий | **ведущая** (runtime + P2), механизм UNRESOLVED |
| H2 | `super.HandleWeaponReloading` не чейнится в `HandleWeaponReloadingDefault` | UNRESOLVED (нельзя доказать статикой; `...Default` спекулятивно вызывать запрещено) |
| H3 | Наш `super` уходит в **исторический** handler, который consume'ит | **сильный confound** (§2) |
| H4 | Исторический `modded SCR_CharacterControllerComponent` ломает reload-flow | confound, не проверено |

---

## 5. Рекомендации (read-only; выполнять владельцу)

1. **Изолировать handler'ы:** отключить в Workbench project list `ARMST_MP133_AnimationLab` и `P2_no_handler` (оставить только `ARMST-PLATFORM---Weapons` + `ARMSTMP133T4B_InstalledMagProbe`), затем повторить rack-тест. Если rack вернётся → виновник — исторический handler (H3).
2. Если rack всё ещё не работает при **единственном** T4B handler — выполнить чистый A/B: T4B lab **без** `modded HandleWeaponReloading` вообще. Если rack вернётся → `HANDLER_SUPER_PATH_INSUFFICIENT` доказан для нашего override (H1/H2).
3. **Не** вызывать `HandleWeaponReloadingDefault` спекулятивно (double-run risk).
4. **Не** классифицировать `reloadType=6` как normal tube-reload, пока не наблюдён успешный native rack + `chambered=1`.
5. Live не трогать до отдельного GO.

---

## 6. Итог

- Исправленная классификация: `RACK_BYPASS_DELEGATED_TO_SUPER_BUT_NATIVE_RACK_NOT_EXECUTED`.
- Audit outcome: **`HANDLER_SUPER_PATH_INSUFFICIENT`** (механизм UNRESOLVED) + **критический confound**: несколько `modded SCR_CharacterCommandHandlerComponent` включены одновременно.
- `CMD1_GRAPH_ROUTE_NOT_REACHED` — исключено; `CURRENT_LAB_WIRING_BLOCKS_RACK` — не подтверждён.
- Следующая цель: сначала **вернуть штатный rack**, потом снова исследовать обычный `R`.

Статус: **`RACK_BYPASS_AUDIT_COMPLETE / HANDLER_SUPER_PATH_INSUFFICIENT`**.
