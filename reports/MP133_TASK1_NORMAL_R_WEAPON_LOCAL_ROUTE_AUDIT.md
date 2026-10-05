# MP-133 Task #1 — Normal-R weapon-local route audit (READ-ONLY)

Статус: **T4B_NORMAL_R_WEAPON_LOCAL_ROUTE_AUDIT_COMPLETE**
Дата: 2026-10-05
Задание: Issue #34 — «find weapon-local/native Normal-R route (READ-ONLY)» ([#6001582300](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **read-only**. Live/prefab/world/ASTRA2 не изменялись; probe'ы не добавлялись.

**Источник доказательств:** установленный SDK API-референс
`C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\docs\ArmaReforgerScriptAPIPublic\html\`
(Doxygen-страницы `interface<Class>.html` / `interface<Class>-members.html`). Реализации (тела) методов движка в этот референс не входят — где вывод зависит от тела, это помечено **UNRESOLVED**.

Текущее безопасное состояние: V1 handler-only `57c7124`, SHA-256 `D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32`.

---

## 1. Вопрос

Можно ли перехватить/направить обычный `R` для lab MP-133 **weapon-local**, без глобального `modded SCR_CharacterCommandHandlerComponent`?

---

## 2. Кандидаты (точные сигнатуры + классификация)

| # | Класс + метод/событие | Сигнатура | Локальность | До нативной мутации? | Consume/cancel? | Требует `modded class`? | Класс |
|---|---|---|---|---|---|---|---|
| 1 | `BaseItemAnimationComponent.OnCharacterCommand` | `void OnCharacterCommand(int commandID, int intValue, float floatValue)` | **weapon-local** (per-instance; lab уже несёт `ARMST_T4B_AstraV2_WeaponAnimationComponent : WeaponAnimationComponent`) | UNRESOLVED (T2c видел команды; pre/post мутации не установлено) | **нет** (void) | нет (подкласс уже есть) | **OBSERVE_ONLY** |
| 2 | `BaseItemAnimationComponent.OnAnimationEvent` | `void OnAnimationEvent(AnimationEventID, AnimationEventID, int, float, float)` | weapon-local | нет — событие анимации идёт во время/после reload | нет (void) | нет | **OBSERVE_ONLY / TOO_LATE_AFTER_NATIVE_MUTATION** |
| 3 | `BaseItemAnimationComponent.OnPrepareAnimInput` / `OnProcessAnimOutput` | `bool OnPrepareAnimInput(IEntity owner, float ts)` / `bool OnProcessAnimOutput(IEntity owner, float ts)` | weapon-local | UNRESOLVED | bool, но это anim input/output, **не** reload-решение | нет | **OBSERVE_ONLY / NOT_APPLICABLE** |
| 4 | `BaseWeaponComponent.IsReloadPossible` | `proto external bool IsReloadPossible()` | weapon (класс), но **глобальный** `modded` | возможно (getter до reload) — UNRESOLVED | возможно `false` (gated) — **если** handler его читает | **да** (`modded class WeaponComponent`) | **VIABLE_BUT_GLOBAL** (UNRESOLVED) |
| 5 | `SCR_WeaponComponent.m_OnWeaponStateChanged` (+ `SCR_WeaponState.m_bReloading`) | `ref ScriptInvokerWeaponState m_OnWeaponStateChanged` | weapon-local invoker, **но** только на `SCR_WeaponComponent` | observer | нет | — | **NOT_APPLICABLE** (prefabs используют `WeaponComponent`, не `SCR_WeaponComponent`) |
| 6 | `BaseWeaponComponent.OnWeaponActive` / `OnWeaponInactive` | `void OnWeaponActive()` / `void OnWeaponInactive()` | weapon-local (script-overridable) | — | — | да | **NOT_APPLICABLE** (equip/unequip, не reload) |
| 7 | `BaseWeaponManagerComponent` / `CharacterWeaponManagerComponent` | `SelectWeapon(BaseWeaponComponent)`, `m_OnWeaponChange*Invoker`, `GetCurrentWeapon()` | character | — | нет | — | **NOT_APPLICABLE** (нет reload-хука) |
| 8 | `BaseMuzzleComponent` | `ClearChamber(int)` (единственный writer), `IsCurrentBarrelChambered()` | weapon-local | — | нет | — | **NOT_APPLICABLE** |
| 9 | `BaseMagazineComponent` | `SetAmmoCount(int)` (единственный writer) | mag-local | — | нет | — | **NOT_APPLICABLE** |
| 10 | weapon-local `ScriptComponent` + `InputManager.AddActionListener("Reload", …)` | — | **global input hook** (не weapon-scoped сам по себе) | до нативного пути | consume — да, но дублирует нативный путь | нет | **VIABLE_BUT_GLOBAL** |
| 11 | per-weapon context action (как существующий `ARMST_T4B_AddRoundWeaponAction`) | — | weapon-local | — | — | нет | **NOT_APPLICABLE** (это отдельная клавиша/action, не native `R`) |
| 12 | `CharacterCommandHandlerComponent.HandleWeaponReloading` | `bool HandleWeaponReloading(CharacterInputContext, float, int)` | **character-global** | да (в пути решения reload) | **да** (`return true` = consume) | да (это и есть V1) | **VIABLE_BUT_GLOBAL** |
| 13 | `SCR_CharacterAnimationComponent.BindCommand` / `BindEvent` | подписка на команду/событие анимации | character | UNRESOLVED | observer | нет | **OBSERVE_ONLY** |

Дополнительно подтверждено по SDK:
- `CharacterCommandHandlerComponent.HandleWeaponReloading` = **`bool`** (script-overridable), `HandleWeaponReloadingDefault` = `proto external bool` (движковый дефолт). V1-сигнатура совпадает.
- У `BaseWeaponComponent` **нет** ни `OnReload`/`Reload`/`SetReload`, ни reload-invoker'а; `GetCurrentMagazine/GetCurrentMuzzle/IsReloadPossible/IsChambering*` — `proto external` геттеры.
- У `WeaponAnimationComponent`/`BaseItemAnimationComponent`/`MagazineAnimationComponent` — один и тот же набор колбэков (таблица выше), все `void` кроме `OnPrepareAnimInput`/`OnProcessAnimOutput`.

---

## 3. Решение

**`NORMAL_R_WEAPON_LOCAL_ROUTE_NOT_FOUND`.**

В SDK 1.8.0.13 **нет weapon-local hook, который одновременно (а) срабатывает на обычный `R`, (б) выполняется до нативной whole-mag мутации и (в) может её отменить/consume'нуть**:
- все weapon-local колбэки — observer'ы (`void`) либо anim-input/output (`bool`, но не reload-решение);
- единственный reload-getter `IsReloadPossible()` требует **глобального** `modded class`, и даже тогда не доказано, что нативный handler его читает (тело `HandleWeaponReloading` в SDK-референсе недоступно → **UNRESOLVED**);
- `m_OnWeaponStateChanged` недоступен на lab MP-133 (prefabs используют `WeaponComponent`, а invoker объявлен на `SCR_WeaponComponent`).

### Почему текущий V1 — узкая доказанно-безопасная точка

V1 `HandleWeaponReloading` остаётся **наиболее узким доказанным** местом перехвата:
- это **единственный** script-overridable хук в пути решения reload, который может **consume** запрос (`return true`) до нативной whole-mag перезарядки;
- он gated к lab-оружию через `ARMST_T4B_WeaponProbe`; все не-lab оружия делегируют без изменений в `super` (проверено A/B: pickup PASS);
- weapon-local эквивалента в SDK нет (§2).

Ограничение V1 (зафиксировано): он **character-global** по классу (единственный `modded class SCR_CharacterCommandHandlerComponent` в lab) и потому остаётся **временным** до появления weapon-local/native маршрута.

---

## 4. Архитектурное правило Task #1 (без изменений)

- **никакого** глобального `SCR_CharacterCommandHandlerComponent.Update(...)` override в финальном решении (доказанная причина pickup-регрессии);
- V1 handler-only — временная R-интерцепция/probe;
- weapon-local маршрут в SDK 1.8.0.13 **не найден**; следующий шаг (если он нужен) — только по отдельному указанию владельца (например, аудит `IsReloadPossible`-override или input-listener, оба `VIABLE_BUT_GLOBAL`).

---

## 5. Ограничения аудита

- Источник — установленный SDK **API-референс**, а не тела скриптов движка; выводы, зависящие от реализации (`IsReloadPossible` консультируется ли handler'ом; timing `OnCharacterCommand` относительно мутации), помечены **UNRESOLVED** и требуют runtime-проверки, если владелец решит идти по `VIABLE_BUT_GLOBAL` ветке.
- Ничего не изменялось: `GAMEPLAY_FILES_CHANGED=0`; live = V1 (`D16D3D43…`); Core/grid/inventory/world/ASTRA2/prefab/Tube3 не тронуты.

Статус: **`T4B_NORMAL_R_WEAPON_LOCAL_ROUTE_AUDIT_COMPLETE`**.
