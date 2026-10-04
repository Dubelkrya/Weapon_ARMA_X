# MP-133 Task #1 — Phase 2C: P→W variable-propagation probe (source-ready)

Статус: **TASK1_PW_PROPAGATION_PROBE_SOURCE_READY_OWNER_TEST**
Дата: 2026-10-04
Задание: Issue #34 [#5983798795](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983798795). База: `t4b/installed-mag-probe` @ `b381242`.

Ровно одна диагностическая проверка: доходит ли `ASTRA_ShellRequest`, выставленный на `CharacterAnimationComponent`, до **инжектированного weapon-графа** этого T4b (`IdleReloadSTM → ShellReloadSTM`). Полная интеграция Request/Repeat/Stop и нативный R — не входят.

---

## 0. Preflight

- Workbench/игра/писатели: **нет**.
- Addon `ARMSTMP133T4B_InstalledMagProbe` (ID `ARMSTMP133T4BInstalledMag`); HEAD `b381242`.
- Полный манифест аддона (94 файла) снят до правок.

---

## 1. Read-only трассировка (до изменений)

- Astra-граф: `MP133_Astra.agr` ControlTemplate объявляет `ASTRA_ShellRequest/Repeat/Stop/Eligible/FireStop` (`AnimSrcGCTVarBool`). `IdleReloadSTM → AstraShell` gate: `ASTRA_ShellRequest && ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing && WeaponInspectionState == 0 && Stance == 0 && !IsCommand(CMD_Weapon_Reload)`.
- Инъекция/синхронизация (bridge prefab): `ARMST_T4B_AstraV2_WeaponAnimationComponent` → `AnimGraph MP133_Astra.agr` + `AnimInstance MP133_Astra_weapon.asi`; `AnimInjection AnimationAttachmentInfo { AnimGraph MP133_Astra.agr; AnimInstance MP133_Astra_player.asi; BindingName "Weapon" }`; `BindWithInjection 1`. Prefab не содержит `Auto Variables Bind`/`AnimVariablesToBind` — переменные на оружейную сторону по имени не привязаны.
- API (installed SDK docs): `BaseAnimPhysComponent.BindVariableBool(string) → TAnimGraphVariable`, `SetVariableBool(var,bool)`; `CharacterAnimationComponent.SetSharedVariableBool(var,bool,bool varHasOtherUsers)`. `WeaponAnimationComponent`/`BaseItemAnimationComponent` сеттера не имеют. `SyncWithCharacter` лишь «subscribes to its animation variable changes» (`OnCharacterBoolVariable`). `ChimeraCharacter.GetAnimationComponent() → CharacterAnimationComponent` — подтверждён.
- Выбор метода: переменная потребляется инжектированным weapon-графом (другой анимационный пользователь) → документированный shared-метод `SetSharedVariableBool(var, value, true)`.
- `TAnimGraphVariable` — built-in handle (объявлен без typedef-страницы), как и `AnimationEventID`, который в этом проекте используется как `= -1` / `< 0` → проверка валидности `v < 0` compile-safe (документированное допущение).

---

## 2. Что реализовано (2 файла, аддитивно)

### Новый скрипт `Scripts/Game/ARMST_T4B/ARMST_T4B_AstraRequestProbe.c`
`class ARMST_T4B_AstraRequestProbeAction : ScriptedUserAction` — изолированный диагностический триггер:
- `PerformAction(pOwnerEntity, pUserEntity)`: `ChimeraCharacter.Cast(pUserEntity)` → `GetAnimationComponent()`; fail-closed при отсутствии; `TAnimGraphVariable v = anim.BindVariableBool("ASTRA_ShellRequest")`; при `v < 0` — reject `bind-unavailable` (outcome C); иначе **toggle** `m_bRequested` и `anim.SetSharedVariableBool(v, m_bRequested, true)`; лог `[ARMST-T4B-ASTRA-PROBE] phase=write name=ASTRA_ShellRequest value=… idx=…`.
- Ни одной операции с патронами/магазином/патронником/дон-atom/инвентарём; нет `CMD_Weapon_Reload`, R/CMD5, `ReloadWeapon()`, native mag events.
- Default OFF: без вызова владельцем ничего не делает; toggle даёт явный `false→true` запрос и явный `true→false` возврат (без таймеров/латчей).

### Additive правка `Prefabs/Test/ARMST_T4B_AstraV2_Bridge_TestWeapon.et`
В существующий `ActionsManagerComponent.additionalActions +{ … }` добавлена одна запись:
```
ARMST_T4B_AstraRequestProbeAction "7A1B2C3D4E5F6071" { ParentContextList { "default" } UIInfo UIInfo "7A1B2C3D4E5F6072" { Name "ASTRA PROBE: ShellRequest ON/OFF" } }
```
Существующая запись `ARMST_T4B_G3B2_TransferAction` и все её поля, а также `AnimGraph/AnimInstance/AnimInjection/BindWithInjection` не изменялись. Добавлены только новые **локальные** instance-ID (не resource GUID).

---

## 3. Статические проверки (PASS)

| Проверка | Результат |
|---|---|
| Новый скрипт braces/parens | 11/11, 30/30 |
| Нативный код (без комментариев) содержит `ReloadWeapon`/`CMD_Weapon_Reload`/`SetAmmoCount`/mag-events | **нет** |
| Изменённые/новые файлы аддона | ровно 2: новый `.c` + bridge `.et` |
| Прочие 93 файла | без изменений (`PROTECTED` set) |
| `.agf/.agr/.ast/.aw/.asi`, 10 ANM + meta, `ARMST_T4B_InstalledMagProbe.c`, AstraV2 bridge `.c`, G3B2 `.c`, `ARMST_T4B_TestWeapon.et` | **unchanged=True** |
| live == labs для 2 файлов | True |

Компиляция Workbench — **за владельцем** (агент компилятор не запускает).

---

## 4. Один тест владельца (game-mode/lab, safety)

1. Скомпилировать; открыть/убедиться в нуле красных ошибок; назначения ASI целы.
2. Экипировать именно **bridge lab weapon** (`ARMST_T4B_AstraV2_Bridge_TestWeapon.et`), стойка Erc, idle.
3. Вызвать действие **«ASTRA PROBE: ShellRequest ON/OFF»** один раз (request=true).
   - Ожидаемо в логе: `phase=write name=ASTRA_ShellRequest value=1 idx=…`.
   - Наблюдать: активировался ли **weapon**-граф Astra (маркеры `ASTRA_Shell_StartReload_W` … или активные фазы `ShellReloadSTM`).
4. Вызвать действие снова (request=false) — вернуть Idle/`AstraWaitRelease → Idle`.
5. Сравнить физический Tube3 (entity/slot/ammo) и chamber до/после — **должны быть неизменны**.

**Outcomes:**
- **(A) `P_SET_AND_W_ASTRA_ACTIVATED`** — P и W реагируют → ownership/sync общий для этой связки; далее — отдельное ревью полной обвязки Request/Repeat/Stop и release (без R-redirect).
- **(B) `P_SET_W_NO_REACTION`** — P пишется, W молчит → изучать `SyncWithCharacter`/binding/инжекцию с точным evidence.
- **(C) `P_BIND_UNAVAILABLE`** — `BindVariableBool` вернул невалидный хэндл → неверный AGR/инстанс/настройка; STOP и разбор.

`OnCharacterBoolVariable` сам по себе — диагностика, **не** доказательство активации графа.

---

## 7. Compile-fix (2026-10-04, owner log)

`Game` module failed to compile with:
`Scripts/Game/ARMST_T4B/ARMST_T4B_AstraRequestProbe.c(87): Undefined function 'TAnimGraphVariable.ToString'`.
Причина — только диагностический вывод: `" idx=" + v.ToString()`. `TAnimGraphVariable` не имеет `.ToString()` в installed SDK.

Исправление (одна строка, L87): удалён `+ " idx=" + v.ToString()`; остаётся `phase=write name=ASTRA_ShellRequest value=<true/false>`. `BindVariableBool`, `SetSharedVariableBool`, toggle, ветка `v < 0`, флаги действия, граф и prefab — без изменений. Прочие ошибки компиляции (`SCR_PlayerArsenalLoadout`, ScenarioFramework getters, `SCR_SpinningWidgetComponent`, `SCR_ScenarioUICommon`) **не** трогались — они переоцениваются следующим полным compile-логом. Compile PASS агентом не заявлен; повторный лог — за владельцем.

## 5. Допущения/ограничения

- `TAnimGraphVariable` трактуется как int-like handle (по аналогии с `AnimationEventID` в этом же аддоне) — для `v < 0`. Если компилятор это отвергнет — исправить минимально по его логу.
- Выбран `SetSharedVariableBool(var,value,true)` (shared с инжектированным пользователем). Если W не реагирует, следующий тест — `SetVariableBool` (см. outcome B).
- Пока propagation не подтверждён, полная интеграция **не продолжается**.

---

## 6. Сохранность и Git

Изменены только: новый lab-скрипт, существующий lab-prefab (additive), отчёт. Основной граф Astra, `.agr/.ast/.asi/.aw`, 10 ANM/meta, CMD1 `Reload_Bolt`, стрельба/idle/inspection, G3B2, Core/production/worlds — не тронуты. Принятые lab-исходники синхронизированы в `Weapon_ARMA_X/labs/`; коммит на `t4b/installed-mag-probe`. Workbench-косметика в репозиторий не вносилась.
