# MP-133 Task #1 — Аудит: правильный engine-маршрут «обычный R → Astra five-phase shell reload»

Статус: **NORMAL_R_ROUTE_NOT_PROVEN**
Дата: 2026-10-05
Задание: Issue #34 [#5999519980](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5999519980).
Режим: **read-only** (никаких правок live). Workbench был открыт — правок не делалось.
Метки: **SOURCE** (файлы/SDK), **LOG** (прошлые owner-логи), **INFERENCE**, **UNRESOLVED**.

---

## A. Executive recommendation

**Однозначного маршрута, удовлетворяющего всем ограничениям задачи (без глобальных input-хуков, без CMD2-6, без ASTRA_ShellRequest, без debug-кнопок, без script-ammo-mutation), статически не существует.**

Engine-корректный слой — **C: character command handler** (`SCR_CharacterCommandHandlerComponent.HandleWeaponReloading()`), потому что именно там движок потребляет обычный R и запускает native reload. Однако это **глобальный `modded`-override** класса персонажа (историческая лаба гейтила его на lab-оружие). Задача прямо запрещает «глобальные input hooks». Значит, выбор между «допустить один узко-гейтнутый глобальный handler» и «маршрут не доказан» — за владельцем.

Confidence: **высокая** (нет native per-shell API; AGF не может потребить R; weapon-scoped reload handler отсутствует). Итог: `NORMAL_R_ROUTE_NOT_PROVEN` до решения по слою C или до runtime-probe.

---

## B. Candidate comparison

| candidate | evidence | pros | risks | fixed-tube safety | replication | verdict |
|---|---|---|---|---|---|---|
| **A. weapon AnimGraph condition only** | AGF читает `IsCommand/GetCommandI(CMD_Weapon_Reload)` (**SOURCE**); native handler обрабатывает R независимо от графа (**INFERENCE**) | без скрипта/нового API | граф **не может** потребить R; native mag-swap всё равно сработает; точное значение команды для R **UNRESOLVED** | плохая | n/a | **отклонено** |
| **B. weapon animation component** | `WeaponAnimationComponent.OnCharacterCommand` только наблюдает (**SOURCE**); `SetVariableBool` у него нет | можно логировать | не подавляет native reload | плохая | n/a | **отклонено** |
| **C. character command handler** | `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading()/HandleWeaponReloadingDefault()` (**SOURCE**); историческая лаба: `modded HandleWeaponReloading` pass-through для не-lab, consume для lab + `SetReloadWeapon(7)` (**LOG/SOURCE**) | единственная engine-точка, где R потребляется до native handling; серверная авторитетность возможна | **глобальный `modded`** (задача запрещает глобальные хуки); риск задеть другие стволы без гейта | при consume native swap не запускается (**INFERENCE**) | character-side; server-authoritative | **единственный engine-корректный, но нарушает no-global-hook** |
| **D. native per-shell support** | в SDK 1.8.0.13 только `BaseWeaponComponent.IsReloadPossible()`, `GetCurrentMagazine()`, `GetCurrentMuzzle()`; **нет** `EWeaponReloadType`/per-shell/tube API (**SOURCE**) | «правильный» слой, если бы существовал | **отсутствует** | n/a | n/a | **недоступно** |
| **E. lab-only script bridge (animation only)** | `SCR_CharacterAnimationComponent.BindCommand("CMD_Weapon_Reload")→TAnimGraphCommand`, `BindVariableBool/SetVariableBool` (**SOURCE**); историческая лаба использовала `BindCommand` + `inputCtx.SetReloadWeapon(7)` (**LOG**) | можно двигать анимацию без ammo-мутаций | всё равно нужно **подавить native reload** → зависит от C; P→W propagation ранее не подтверждён | частичная (зависит от C) | зависит от C | **частично; не самодостаточно** |

---

## C. Текущая карта команд/контролов

**Native reload (SOURCE, audit §3.1):**
- cmd1 → bolt/rack (`ReloadActionBolt`/`RackBoltAnim`, `Weapon_Rack_Bolt`); **сохраняем как bolt-only**.
- cmd2/3 → insert (whole-mag); cmd4/5 → remove+insert; cmd6 → remove.
- cmd7–9 veto на входе; cmd10 проходит вход, но состояния нет.
- Клипы inject/remove несут `Weapon_Spawn/Attach/Detach/DespawnMagazine` → native whole-mag swap (M1→M3→M5, **LOG**).

**Engine API (SOURCE, SDK 1.8.0.13):**
- `CharacterInputContext`: `GetWeaponReloadType()`, `SetReloadWeapon(int)`, `WeaponIsStartReloading()`.
- `CharacterCommandHandlerComponent`: `HandleWeaponReloading()`, `HandleWeaponReloadingDefault()`.
- `CharacterControllerComponent`: `IsReloading()`, `ReloadWeapon()`, `ReloadWeaponWith(IEntity, bool)`, `OnReloaded()`.
- `BaseWeaponComponent`: `GetCurrentMagazine()`, `GetCurrentMuzzle()`, `IsReloadPossible()`.
- `BaseMagazineComponent.SetAmmoCount(int)` — единственный writer ammo; **нет** атомарной one-shell/loose-round API (SOURCE, T4 report).
- `SCR_CharacterAnimationComponent` (BaseAnimPhysComponent): `BindCommand(string)→TAnimGraphCommand`, `CallCommand`, `BindVariableBool/SetVariableBool`.
- **Нет** native per-shell/tube reload type.

**Текущий ASTRA2 граф (SOURCE):**
- `Idle → AstraShell` on `ASTRA_ShellRequest && ASTRA_ShellEligible && !ASTRA_ShellStop && !ASTRA_FireStop && !Firing && WeaponInspectionState==0 && Stance==0 && !IsCommand(CMD_Weapon_Reload)`.
- `AstraShell → AstraWaitRelease`; `AstraWaitRelease → Idle` on `!ASTRA_ShellRequest`.
- `Idle → Buffer3` (cmd1-only) → `Reload` (Child `ReloadRouteSTM`) → `Bolt → RackStanceSTM → RackErcG/RackPneG → RackBoltAnim`.
- `ShellReloadSTM` (5 фаз) достижим **только** через `AstraShell` (т.е. через `ASTRA_ShellRequest`, сеттера у которого нет).

**Failed bind path (SOURCE/LOG):** `CharacterAnimationComponent.BindVariableBool(...)` на `player_main.agr` не дал рабочей P→W передачи; Workbench неоднократно вычищал ASI-строки; `ASTRA_ShellRequest` не имеет ни одного сеттера. → `ASTRA_ShellRequest` **provisional/dead**.

---

## D. Предлагаемое минимальное будущее изменение графа (не выполнять)

**Если владелец принимает слой C (гейтнутый handler):**
1. Скрипт: `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading(...)` — **pass-through `super` для любого не-lab оружия**; для lab-оружия — consume (`return true`) и `inputCtx.SetReloadWeapon(<LAB_SHELL_CMD>)`; **никаких ammo-мутаций**.
2. Граф: перевести `Idle → AstraShell` с `ASTRA_ShellRequest` на условие по новой команде: `IsCommand(CMD_Weapon_Reload) && GetCommandI(CMD_Weapon_Reload) == <LAB_SHELL_CMD>` (либо через `BindCommand/CallCommand`-контрол). Удалить `AstraWaitRelease`/`ASTRA_ShellRequest`-гейт (после подтверждения).
3. `ShellReloadSTM` self-loop `CheckContinue → GrabShell` уже структурно пригоден; repeat/stop — см. §E.
4. CMD1 остаётся `ReloadRouteSTM → RackStanceSTM → RackBoltAnim` без изменений.

Это **минимально** и не трогает fire/safety/inspection/IK/modes и native mag-клипы.

---

## E. Источник данных repeat/stop

| Факт | Источник | Статус |
|---|---|---|
| start | engine reload request → lab command (слой C) | **UNRESOLVED** (нужен probe) |
| repeat (ещё патрон в резерве) | нужен сигнал «резерв/труба»; `ASTRA_ShellRepeat` — provisional, сеттера нет | **UNRESOLVED** |
| stop (труба полна) | `BaseWeaponComponent.GetCurrentMagazine().GetAmmoCount()/GetMaxAmmoCount()` (**SOURCE**) — но это НЕ graph-control; нужен bridge или engine variable | **UNRESOLVED** |
| stop (нет резерва) | нет документированной «reserve ammo» graph-control; инвентарь item-level | **UNRESOLVED** |
| interrupt/fire | `Firing`/`TriggerPulled` — есть в AGR (**SOURCE**); `ASTRA_FireStop` provisional | частично |

**Не изобретать ammo-переменные.** `ASTRA_ShellEligible/Stop/Repeat` сейчас — provisional (нет сеттера), не считать их валидными только потому, что они объявлены в AGR.

---

## F. Зависимость физической транзакции одного патрона

**Анимационную маршрутизацию можно решить ОТДЕЛЬНО от физической вставки одного патрона** — при условии, что native whole-mag swap подавлен (слой C). Но сама физическая транзакция («взять 1 патрон из резерва → вставить в ту же фиксированную трубу, сохранив identity») **остаётся UNRESOLVED**: в SDK есть только `SetAmmoCount(int)`, нет атомарной/consume API (T4 report). Т.е. после решения анимации **потребуется отдельная engine-safe one-shell транзакция** (или принятие lab-only setter-based PoC с оговорками).

---

## G. Отклонённые подходы (blacklist)

- Native CMD2-6 entry (whole-mag swap, M1→M3→M5) — **запрещено**.
- Глобальные input hooks / `modded` без гейта — **запрещено** (слой C допустим только как узко-гейтнутый и по решению владельца).
- Debug-кнопки / `ASTRA PROBE` actions / toggle-переключатели — **запрещено**.
- Script ammo mutation (`SetAmmoCount` как proxy вставки) — **запрещено**.
- `ASTRA_ShellRequest` как дефолтное решение — **provisional/dead**.
- Новые workspace/параллельные системы — **запрещено**.

---

## H. Следующая узкая задача (не выполнять)

**Runtime probe (owner-only, read-only по ammo):** подтвердить, (i) какое именно значение `GetCommandI(CMD_Weapon_Reload)` даёт обычный R на фиксированной трубе MP-133; (ii) запускает ли `SetReloadWeapon(<value>)` из гейтнутого handler native swap или нет; (iii) можно ли графу ключеваться на этом значении. Это отдельная узкая диагностика; реализация маршрута — после неё.

---

## Ответы на acceptance criteria

1. **Чем заменить `ASTRA_ShellRequest`?** Engine-корректно — командой, выставленной из гейтнутого `HandleWeaponReloading` (слой C); AGF-only замены нет.
2. **AGF напрямую?** Нет — нужен bridge (command handler + `SetReloadWeapon`/`BindCommand`).
3. **Повтор цикла?** `ShellReloadSTM` self-loop `CheckContinue→GrabShell` структурно пригоден; источник «есть резерв» — **UNRESOLVED**.
4. **Stop/full/no-ammo/interrupt?** interrupt/fire — частично (`Firing`); full/no-ammo — **UNRESOLVED** (нет graph-control).
5. **Фиксированная труба?** Сохраняется только если native reload потреблён (слой C); граф сам по себе её не защищает.
6. **Что остаётся unresolved?** И **анимационная маршрутизация** (нужен слой C или отказ от no-global-hook), и **физическая one-shell транзакция** (нет API).

**Итог: `NORMAL_R_ROUTE_NOT_PROVEN`.** Live не изменялся; следующий шаг — решение владельца по слою C и/или узкий runtime-probe.
