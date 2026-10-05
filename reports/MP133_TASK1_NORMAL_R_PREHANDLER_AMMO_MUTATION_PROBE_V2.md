# MP-133 Task #1 — NORMAL-R pre-handler ammo mutation probe V2

Статус: **NORMAL_R_PREHANDLER_MUTATION_PROBE_PREPARED_WB_OPEN_STOP**
Дата: 2026-10-05
Задание: NORMAL R PRE-HANDLER AMMO MUTATION PROBE V2.
Режим: static-audit + staged V2. **Workbench открыт → live script НЕ изменён** (жёсткий gate).

---

## 0. Ключевой вопрос
Кто и в какой момент меняет фиксированную Tube3 `2/3 → 1/3` относительно первого нажатия R?

V1: baseline `2/3`, но уже на **первом входе** в `HandleWeaponReloading()` — `1/3`. Значит, мутация происходит **до** handler.

---

## 1. SDK call-path (read-only)

```
обычный R (input)
  ↓
CharacterInputContext reload state
     GetWeaponReloadType() / WeaponIsStartReloading()          [SOURCE]
  ↓  ⟪ENGINE_BLACK_BOX⟫  native input→command mapping + возможные native
     операции с ammo/muzzleSupply/magazine (script source не показывает)
CharacterCommandHandlerComponent.Update(float pDt, int pCurrentCommandID, bool pCurrentCommandFinished)  [script, per-tick, protected, overridable]
  ↓
HandleWeapons(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)   [script umbrella, has ctx]
  ↓
HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)  [script, overridable]
  HandleWeaponReloadingDefault(...)   [proto external — engine default]
```
Раньше handler доступны (script-level, read-only):
- `CharacterControllerComponent.OnApplyControls(IEntity owner, float timeSlice)` — применение ввода (**SOURCE**, overridable);
- `Update(...)` — тик команды (**SOURCE**);
- `HandleWeapons(...)` — umbrella с `CharacterInputContext` (**SOURCE**).
Пост-факт: `CharacterControllerComponent.OnReloaded(IEntity owner, BaseWeaponComponent weapon)` (**SOURCE**).

**ENGINE_BLACK_BOX:** маппинг input→`CharacterInputContext`→`pCurrentCommandID` и любые native изменения ammo/muzzle supply **до** `Update`. В script source не видны. V2 локализует границу, но саму native-операцию, если она там, не покажет.

---

## 2. V1 evidence (owner log)

```
baseline: mag=M1 ammo=2/3 muzzleSupply=2/3 chambered=0
first HandleWeaponReloading entry: cmd=21 reloadType=1 startReloading=true M1 1/3 chambered=0
далее повторные вызовы по fixed frames: cmd=21 reloadType=1 startReloading=true M1 1/3
```
→ мутация `2/3→1/3` **раньше** первого handler-entry. `muzzleSupply` в V1 не логировался.

---

## 3. V2 (staged, observe-only + существующий lab suppress)

Файл (staged): `Weapon_ARMA_X/artifacts/astra-rebuild/stageV2/ARMST_T4B_NormalRHandlerProbe.c`.
Будет установлен в `Scripts/Game/ARMST_T4B/ARMST_T4B_NormalRHandlerProbe.c` после закрытия Workbench.

Добавлено (без изменения поведения):
- **`override void Update(...)`** — per-tick, до dispatch: `phase=baseline` (один раз), `phase=idle-control` (по **изменению** состояния — без spam), `phase=post-handler-next-frame` (следующий тик после handler).
- **`override bool HandleWeapons(...)`** — до `HandleWeaponReloading`: `phase=pre-handler` (первое появление `startReloading=true`).
- **`override bool HandleWeaponReloading(...)`** — `phase=handler-enter` (один раз) + `phase=handler-consume`, затем `return true` (consume). Non-lab → `super`.
- Монотонный `seq=`; единый snapshot: `cmd/reloadType/startReloading/wep/mag/magEntity/magAmmo/max/muzzleSupply/max/barrel/chambered`.
- `magEntity=M<n>` — reference-change tag (сохранён).
- `muzzleSupply` — через проверенный lab-способ `BaseMuzzleComponent.GetAmmoCount()` (как в `ARMST_T4B_WeaponProbe.T4BState`).

Статическая проверка staged-кода: скобки `{}` 24/24, `()` 94/94; **0** запрещённых API (`SetReloadWeapon/ReloadWeapon/ReloadWeaponWith/SetAmmoCount/CallCommand/SetVariableBool/Spawn|Attach|Detach|Despawn|MagRelease`); `super.Update`×2, `super.HandleWeapons`, `super.HandleWeaponReloading`, `return true`; все 6 фаз и `muzzleSupply` присутствуют.

---

## 4. Owner runtime test (минимальный, один R)

A. Запустить игру, экипировать lab MP-133.
B. **НЕ нажимать R** некоторое время → получить `phase=idle-control` (и убедиться, меняется ли `2/3` без R).
C. Зафиксировать `M1 / magAmmo / muzzleSupply / chambered`.
D. Нажать **R один короткий раз**.
E. Больше ничего не нажимать.
F. Снять лог до и после R; прислать строки `[ARMST-T4B-RPROBE]`.

**STOP**, если для наблюдения пришлось бы пропустить native swap.

---

## 5. Ожидаемые фазы

| seq | phase | что показывает |
|---|---|---|
| 1 | `baseline` | исходное `2/3`, `M1`, `muzzleSupply=2/3` |
| 2..n | `idle-control` | меняется ли состояние **без R** (2/3 остаётся или уходит) |
| n+1 | `pre-handler` | R-запрос виден до handler (`reloadType`, `startReloading`) |
| n+2 | `handler-enter` | первый вход в handler: ammo/muzzleSupply **на этот момент** |
| n+3 | `handler-consume` | `consumed=1` |
| n+4 | `post-handler-next-frame` | состояние после handler |

---

## 6. Классификация A–F (по runtime evidence, не выбирать заранее)

- **A. `AMMO_MUTATES_BEFORE_R`** — `idle-control` показывает `2/3→1/3` **до** R.
- **B. `AMMO_MUTATES_AFTER_R_BEFORE_SCRIPT_HANDLER`** — после R, но `pre-handler`/`handler-enter` уже `1/3`; `Update` до R был `2/3`.
- **C. `AMMO_MUTATES_INSIDE_SCRIPT_VISIBLE_PRE_HANDLER_STAGE`** — между `Update`/`pre-handler` и `handler-enter` (более ранняя script-точка).
- **D. `AMMO_MUTATES_ONLY_AFTER_HANDLER`** — `handler-enter` `2/3`, мутация после (интерпретация V1 ошибочна).
- **E. `MUTATION_POINT_ENGINE_BLACK_BOX`** — границы установлены, операция внутри native engine.
- **F. `INCONCLUSIVE`** — данных мало.

Дополнительно: если `muzzleSupply` меняется вместе с `magAmmo` (`2→1` и `2→1`) — это реальное изменение supply; если `magAmmo 2→1`, а `muzzleSupply` остаётся `2` — иное представление состояния.

---

## 7. Границы

V2 не подключает Astra, не решает физическую вставку, не трогает `MP133_Astra2.agf`/AST/ASI/AGR/AW/ANM/meta/G3B2, не восстанавливает CMD2-6, не компенсирует потерю патрона. Non-lab поведение — прежнее.

**Статус: `NORMAL_R_PREHANDLER_MUTATION_PROBE_PREPARED_WB_OPEN_STOP`.** Нужно полностью закрыть Workbench; после этого применю staged V2 в live, синхронизирую labs, сделаю узкий commit и дам статус `NORMAL_R_PREHANDLER_MUTATION_PROBE_READY_OWNER_TEST`.
