# MP-133 Task #1 — Native reload producer-path audit (READ-ONLY / SOURCE-ONLY)

Статус: **T4B_NATIVE_RELOAD_PRODUCER_PATH_AUDIT_COMPLETE**
Дата: 2026-10-06
Задание: Issue #34 — producer/path audit после player-side runtime ([#6021425322](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **read-only / source-only**. Live/labs/Workbench/prefab/graph/gameplay не менялись.

Метки: **SOURCE** (SDK/файл), **RUNTIME** (owner-лог), **INFERENCE**, **UNRESOLVED**.

---

## 0. Принятая runtime-классификация (RUNTIME)

- `MAG_DISAPPEARS_BETWEEN_CMD5_AND_CMD3 = PROVEN`
- `WEAPON_SIDE_MAG_EVENTS_NOT_OBSERVED = PROVEN`
- `PLAYER_SIDE_MAG_EVENTS_NOT_OBSERVED = PROVEN`
- `CHARACTER_EVENT_OBSERVER_PATH_FUNCTIONAL = PROVEN`
- `MAG_MUTATION_WITHOUT_OBSERVED_WEAPON_OR_CHARACTER_MAG_EVENTS = PROVEN`
- `MAG_MUTATION_WITHOUT_ANY_ENGINE_ANIMATION_EVENT = NOT PROVEN`
- `NATIVE_MUTATION_PATH_BELOW_OR_OUTSIDE_OBSERVED_ANIMATION_EVENT_CALLBACKS = STRONGLY_SUPPORTED`

Глобальный `HandleWeaponReloading` **не** восстанавливаем (доказанно ломал rack).

---

## 1. Известная цепочка: input/reload request → cmd5

| Шаг | Что | Метка |
|---|---|---|
| 1 | обычный `R` → `CharacterInputContext` (reload type / `WeaponIsStartReloading`) | RUNTIME+SOURCE |
| 2 | `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading(...)` (script) → `HandleWeaponReloadingDefault(...)` (`proto external`, движок) | SOURCE |
| 3 | движок выбирает reload-тип и выставляет `CMD_Weapon_Reload` с `intValue` 1..6 | SOURCE (SampleWeapon/production graph) |
| 4 | weapon-side `OnCharacterCommand(commandID, intValue, ...)` наблюдает `1 → 5 → 3` | RUNTIME |
| 5 | движковый reload-STM ре-оценивает команду по кадрам | INFERENCE |

**Producer cmd5/3 (SOURCE/UNRESOLVED):** движковые reload-триггеры — `CharacterControllerComponent.ReloadWeapon()` и `ReloadWeaponWith(IEntity ammunitionEntity, bool bForceDetach=false)` (`proto external bool`); завершение — `OnReloaded(IEntity owner, BaseWeaponComponent weapon)` (script `void`). **Скриптового producer'а** значений `5`/`3` не найдено: значения приходят из внутреннего engine reload-решения; точная причина `5→3` (один удержанный R vs engine phase) — **UNRESOLVED** (совпадает с §5 прошлого аудита).

---

## 2. Граница: cmd5 → `GetCurrentMagazine()==null`

- cmd5: installed tube есть, ammo `0/3` (RUNTIME).
- до cmd3: первый последующий snapshot уже `magPresent=false`, `ammo=-1/-1` (RUNTIME).
- на **обеих** наблюдаемых сторонах (weapon `BaseItemAnimationComponent.OnAnimationEvent`, character `SCR_CharacterControllerComponent.GetOnAnimationEvent`) **нет** `Weapon_MagRelease`/`DetachMagazine`/`DespawnMagazine`/`SpawnMagazine`/`AttachMagazine` (RUNTIME).
- значит мутация выполняется **ниже/вне** обоих наблюдаемых animation-event callback'ов (INFERENCE, STRONGLY_SUPPORTED).

**Кандидаты-API самой мутации (SOURCE):**
- `CharacterControllerComponent.DetachCurrentMagazine()` — `proto external bool` (native detach);
- `CharacterControllerComponent.ReloadWeaponWith(IEntity, bool bForceDetach=false)` — `proto external bool` (reload с явным магазином; `bForceDetach` — прямой намёк на detach);
- `BaseWeaponComponent.GetCurrentMagazine()` — `proto external` (read).
- **Ни** `BaseWeaponComponent`, **ни** `BaseMagazineComponent` не имеют script-хука detach/attach (SOURCE).

---

## 3. Таблица hook'ов

| Hook | Тип | Локальность | Класс |
|---|---|---|---|
| `BaseItemAnimationComponent.OnCharacterCommand` | `void` | weapon-local | **PRE_MUTATION_CANDIDATE** (видит cmd5 до мутации), но observer-only |
| `BaseItemAnimationComponent.OnAnimationEvent` | `void` | weapon-local | **POST_MUTATION** / не срабатывает для mag-событий |
| `SCR_CharacterControllerComponent.GetOnAnimationEvent` | `ScriptInvoker` | character | **POST_MUTATION** (те же события; mag-события не приходят) |
| `CharacterControllerComponent.OnReloaded(IEntity, BaseWeaponComponent)` | `void` | character | **POST_MUTATION** (completion callback) |
| `BaseWeaponComponent.IsReloadPossible()` | `proto external bool` | weapon (класс), но **global `modded`** | **PRE_MUTATION_CANDIDATE**, UNRESOLVED (читает ли его handler; глобальный) |
| `SCR_WeaponAttachmentsStorageComponent.CanRemoveItem(IEntity)` | `bool` | weapon-storage (класс), **global `modded`** | **UNRESOLVED** (магазин ли в этой storage; в SDK у storage есть `OnRemovedFromSlot`/`m_OnItemRemovedFromSlotInvoker`) |
| `CharacterControllerComponent.DetachCurrentMagazine()` | `proto external bool` | character | **NOT_APPLICABLE** (это сама мутация) |
| `CharacterControllerComponent.ReloadWeapon` / `ReloadWeaponWith` | `proto external bool` | character | **NOT_APPLICABLE** (producer, не pre-mutation hook) |
| `BaseMagazineComponent.SetAmmoCount` / `BaseMuzzleComponent.ClearChamber` | `proto external` | local | **NOT_APPLICABLE** (единственные writer'ы; не detach) |
| `BaseWeaponManagerComponent.SelectWeapon`/`SetSlotWeapon` | `proto external` | character | **NOT_APPLICABLE** (weapon switch) |
| `CharacterInputContext.SetReloadWeapon(int)` | `proto external void` | character (input) | **PRE_MUTATION** технически, но исторически ломал rack (V1/V2 evidence) → rejected |
| `SCR_CharacterAnimationComponent.CallCommand`/`SetCurrentCommand`/`BindCommand` | script | character | **UNRESOLVED** (можно менять команду, но character-side + propagation не доказана) |

---

## 4. Самый ранний безопасный кандидат

**`NO_SAFE_PRE_MUTATION_INTERCEPTION_FOUND`.**

- Самая ранняя **точка наблюдения** до мутации — weapon-local `OnCharacterCommand(cmd5)`, но она `void` (observer-only).
- Кандидаты, которые могли бы **отменить** мутацию, — все вне «безопасного weapon-local»:
  - `IsReloadPossible`-override и `SCR_WeaponAttachmentsStorageComponent.CanRemoveItem`-override — **global `modded`** + **UNRESOLVED** (не доказано, что движок их читает для reload/detach);
  - `SetReloadWeapon` / `CallCommand`/`SetCurrentCommand` — character-side; `SetReloadWeapon` уже доказанно ломал rack;
  - `DetachCurrentMagazine`/`ReloadWeaponWith` — это сама мутация/producer, не hook.
- **Не угадываю.** Доказанного безопасного pre-mutation перехвата, не затрагивающего `cmd1` rack, **нет**.

---

## 5. Один следующий минимальный diagnostic experiment (НЕ реализован)

**Цель:** определить, проходит ли detach установленного магазина через **weapon-storage** (`SCR_WeaponAttachmentsStorageComponent`/`EquipedWeaponStorageComponent`) — то есть существует ли weapon-local `bool`-гейт (`CanRemoveItem`) **до** мутации.

**Минимальный пассивный probe (отдельная задача/GO):**
- на существующем weapon-side observer добавить подписку/логирование invoker'ов weapon-storage: `m_OnItemRemovedFromSlotInvoker` / `m_OnItemAddedToSlotInvoker` (+ `OnRemovedFromSlot`/`OnAddedToSlot`) для магазина (identity = `BaseMagazineComponent.GetOwner()`);
- логировать **вызовы** `CanRemoveItem`/`CanReplaceItem` на weapon-storage с результатом (если доступны как override-хук — только логирование, `super` сохраняется);
- snapshot (mag ref-tag/ammo/muzzle/chambered) на каждом;
- никаких writers/`Update`/таймеров/input listeners.

**Read-out:** если mag detach проходит через weapon-storage и `CanRemoveItem` вызывается **до** `GetCurrentMagazine()==null` → появляется weapon-local `bool` pre-mutation кандидат. Если storage-хуки не срабатывают → detach идёт напрямую через `DetachCurrentMagazine`/`ReloadWeaponWith` (engine), и weapon-local перехвата нет.

---

## 6. Границы

Live/labs/Workbench/prefab/graph/gameplay не менялись; `GAMEPLAY_FILES_CHANGED=0`. cmd7 не предлагается; глобальный `HandleWeaponReloading` не восстанавливается; Chungus не копируется; gameplay probe не писался.

Статус: **`T4B_NATIVE_RELOAD_PRODUCER_PATH_AUDIT_COMPLETE`**.
