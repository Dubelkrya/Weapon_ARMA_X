# MP-133 Task #1 — Native cmd1→cmd5→cmd3 sequence audit (READ-ONLY)

Статус: **T4B_NATIVE_CMD1_CMD5_SEQUENCE_AUDIT_COMPLETE**
Дата: 2026-10-06
Задание: Issue #34 — «read-only/source-only native command sequence audit» ([#6009350264](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **read-only**. Live/граф/prefab/observer/Tube3 не менялись; Workbench считается RUNNING.

---

## 0. Принятый runtime-результат

`RACK_RECOVERED_WITH_T4B_HANDLER_REMOVED` — native rack вернулся, когда глобальный T4B `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` **полностью отсутствует**. Глобальная handler-архитектура **отвергнута** для Task #1.

**Контрадикция (record):** вывод `WEAPON_ONCHARACTERCOMMAND_NOT_A_VALID_RECEIVER` **нигде в репозитории не зафиксирован** (проверено grep по `reports/**`). Чистый no-handler A/B его бы опроверг: weapon-local `BaseItemAnimationComponent.OnCharacterCommand` **является** валидным receiver'ом штатных reload-команд. Возвращать глобальный handler нельзя.

---

## 1. Наблюдённая последовательность (owner log, no-handler A/B)

```
один R → commandID=0 intValue=1        (rack)
       → Weapon_Rack_Bolt (anim event), snapshot chambered=1
       → commandID=0 intValue=5        (native reload)
       → intValue=3
       → magazine disappearance в диагностическом snapshot
```

---

## 2. Requirement 1 — cmd5/3: тот же удержанный R или отдельный follow-up?

**UNRESOLVED (статикой не доказуемо).** Для решения нужен per-command `WeaponIsStartReloading()`/`WeaponIsRaised()` (owner-лог `start=`/`raised=`), которого в текущем наборе нет.

Правдоподобный механизм (не факт): движковый reload-STM ре-оценивает `GetCommandI(CMD_Weapon_Reload)` каждый кадр, пока input-context запрашивает reload; значение меняется по мере прохождения фаз (rack → mag remove/insert → bolt). Т.е. `1→5→3` — вероятно **один** запрос, но это **INFERENCE**, не доказательство.

---

## 3. Requirement 2 — историческое значение cmd2–6 (наш собственный evidence)

Источник: `reports/MP133_V3_RELOAD_GRAPH_AUDIT.md` §2.3 (production `MP133.agf`, `WeaponReloadSTM`), **SOURCE**:

| cmd | состояние (production graph) | клип/смысл |
|---|---|---|
| 1 | `ReloadActionBolt` | rack bolt (native manual pump) |
| 2 | `NoMagReload` (`InsertMagAnim`) | вставка целого магазина |
| 3 | `NoMagNoBulletReload` (`InsertMagAnim`) → `ReloadActionBolt` | вставка + bolt |
| 4 | `MagReload` (`MagReloadSTM`: Remove→Insert) | смена магазина |
| 5 | `MagNoBulletReload` (`MagReloadSTM`) → `ReloadActionBolt` | смена магазина + bolt |
| 6 | `RemoveMag` (`RemoveMagAnim`) | извлечение магазина |

**Важно про текущий lab:** активный `MP133_Astra2.agf` ссылается на `CMD_Weapon_Reload` **только для значения 1** (rack); состояния cmd2–6 **удалены** (Stage D). Тем не менее owner-лог показал **реальную пропажу магазина** после cmd5 → значит native whole-mag swap в текущем lab выполняется **движком**, а не ASTRA2-графом (**INFERENCE** из runtime + graph source). Следствие: смену магазина **нельзя** остановить удалением graph-состояний — она ниже уровня графа.

---

## 4. Requirement 3 — earliest weapon-local point для диверсии cmd5 в ASTRA2

SDK 1.8.0.13, weapon-local (`BaseItemAnimationComponent`, **SOURCE**):

| хук | сигнатура | можно ли остановить reload? |
|---|---|---|
| `OnCharacterCommand` | `void OnCharacterCommand(int,int,float)` | **нет** (void) — receiver/detector |
| `OnAnimationEvent` | `void OnAnimationEvent(...)` | **нет** (void) |
| `OnPrepareAnimInput` | `bool OnPrepareAnimInput(IEntity, float)` | UNRESOLVED (anim input, не reload-решение) |
| `OnProcessAnimOutput` | `bool OnProcessAnimOutput(IEntity, float)` | UNRESOLVED (anim output) |
| `OnCharacter*Variable` | `void ...` | нет |
| `IsAnimationEvent` / `IsAnimationTag` | read-only | нет |

Weapon-local **сеттеров** команды/переменной нет (`BaseItemAnimationComponent` — только callbacks). Сеттеры/`CallCommand`/`SetCurrentCommand`/`SetVariableBool` находятся на **character-side** `SCR_CharacterAnimationComponent` (`BindCommand`, `CallCommand`, `SetCurrentCommand`, `SetVariableBool/Float/Int`, `SetSharedVariable*`) — это **не** weapon-local, и историческая Phase 2A показала, что P→W propagation не доказана, а weapon-side variable setter **отсутствует** в 1.8.0.13.

**Earliest weapon-local point:** `OnCharacterCommand` (receiver). **Weapon-local cancel/consume reload-команды НЕ найден.** Остальные кандидаты — вне weapon-local:
- `BaseWeaponComponent.IsReloadPossible()` (`proto external bool`) — требует **глобального** `modded class`; доказательств, что нативный handler его читает, нет → UNRESOLVED;
- character-side `SetVariableBool`/`CallCommand` → отвергается (не weapon-local; Phase 2A: propagation не доказана).

→ **Weapon-local diversion point для cmd5 = NOT FOUND** в SDK 1.8.0.13.

---

## 5. Requirement 7 — может ли `OnCharacterCommand` различить cmd1 vs cmd5?

**Да, различает.** `OnCharacterCommand(int commandID, int intValue, float floatValue)` на текущем weapon-компоненте получает:
- `commandID` = тип команды (`CMD_Weapon_Reload`; T2c runtime наблюдал `0`);
- `intValue` = параметр reload-типа (`1`=rack, `5`=native mag reload, `3`=следующий этап).

Т.е. он **безопасно различает** `cmd1` (rack, оставить нетронутым) и `cmd5` (whole-mag, цель для диверсии).

**Но:** `OnCharacterCommand` — **observer-only** (`void`). Он **не** может отменить/consume'нуть native reload. Максимум — **drive a separate weapon-local request path** (например, выставить weapon-local флаг/запрос, который читает ASTRA2-граф) **без мутации native reload state**; при этом native whole-mag swap **всё равно продолжится** (см. §3: swap движковый). Т.е. «увидеть cmd5» ≠ «остановить cmd5».

---

## 6. Итог

| Вопрос | Ответ |
|---|---|
| cmd5/3 — тот же R или follow-up? | **UNRESOLVED** (нужен per-command `start=`/`raised=`) |
| cmd2–6 meanings | восстановлены (production graph, §3); в ASTRA2 — только cmd1; swap движковый |
| earliest weapon-local diversion point | **NOT FOUND**; `OnCharacterCommand` — receiver-only |
| различает ли cmd1 vs cmd5 | **да** (commandID + intValue) |
| observer-only или drive path | **observer-only**; отдельный weapon-local request path возможен, но native swap не отменяет |
| глобальный `HandleWeaponReloading` | **отвергнут** (сломал rack) |
| Chungus | reference-only; решение выводить из ARMST runtime + SDK + ASTRA2 |

**Главный вывод:** путь для **детекции** есть (`OnCharacterCommand`), но безопасного **weapon-local способа остановить/заменить cmd5** в SDK 1.8.0.13 **не найдено**; native whole-mag swap выполняется движком ниже уровня графа. Следующий шаг — отдельная узкая задача (не в этом аудите): искать weapon-local механизм отмены (кандидаты `IsReloadPossible`-override / `OnPrepareAnimInput`-bool — оба UNRESOLVED), либо принять, что отмена требует не-weapon-local слоя.

---

## 7. Границы

`GAMEPLAY_FILES_CHANGED=0`; live handler = no-handler A/B `D5BA3052…`; observer `B3D71CF5…`; ASTRA2/graph/prefab/Tube3/Core/grid/inventory — не тронуты. Чистый read-only.

Статус: **`T4B_NATIVE_CMD1_CMD5_SEQUENCE_AUDIT_COMPLETE`**.
