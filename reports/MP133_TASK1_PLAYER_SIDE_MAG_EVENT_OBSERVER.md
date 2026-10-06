# MP-133 Task #1 — Player/character-side mag-event observer (source prep)

Статус: **T4B_PLAYER_SIDE_MAG_EVENT_OBSERVER_SOURCE_PREPARED_OWNER_REVIEW**
Дата: 2026-10-06
Режим: **source prep only**. Live **НЕ изменялся**.

---

## 0. Уточнённая классификация (принята от владельца)

| Утверждение | Статус |
|---|---|
| `MAG_DISAPPEARS_BETWEEN_CMD5_AND_CMD3` | **PROVEN** (mag=M1 0/3 на cmd5 → mag=- на cmd3) |
| `WEAPON_SIDE_MAG_EVENTS_NOT_OBSERVED` | **PROVEN** (weapon observer видит `Weapon_EnableFire`/`Weapon_Rack_Bolt`, но **не** видит `Weapon_MagRelease`/`Detach`/`Despawn`/`Spawn`/`Attach`) |
| `MAG_MUTATION_WITHOUT_ANY_ANIMATION_EVENTS` | **NOT PROVEN** (прежний вывод был слишком сильным) |
| `PLAYER/CHARACTER_SIDE_EVENT_PATH` | **UNRESOLVED** |

Причина: probe стоит на **weapon-side** `BaseItemAnimationComponent.OnAnimationEvent`; отсутствие mag-событий там **не** доказывает, что engine/player-анимация их не исполнила. T3-аудит прямо оставлял открытым вопрос о character/player receiver.

---

## 1. Что делает новый observer

Второй пассивный observer на **character/player animation стороне**, логирующий те же события + snapshot, без writers и без вмешательства в reload.

Механизм (проверенный паттерн, historical lab `ARMST_MP133_Lab_Character.c`): `modded class SCR_CharacterControllerComponent` → в `OnInit` подписка `GetOnAnimationEvent().Insert(callback)`; callback получает **все** animation events, включая `Weapon_*`.

Staged: `artifacts/astra-rebuild/stageCharObserver/ARMST_T4B_CharacterMagEventObserver.c`
- SHA-256: `7D3B97F8D06B8D03367294623B9123EE4E325C058B5F9654AE74393E0CEB9533` (3702 bytes).
- Логирует `[ARMST-T4B-CHAREVT] seq=… side=SV/CL event=<Weapon_…> intParam=… from/to=… magPresent=… magTag=… ammo=…/… muzzleSupply=… barrel=… chambered=…`.
- **Lab-gated**: только когда текущее оружие несёт `ARMST_T4B_WeaponProbe` (без глобального спама).
- Только `OnInit` + пассивный callback. **Нет** writers, `Update`, `HandleWeapons`, `HandleWeaponReloading`, `SetReloadWeapon`, таймеров, input-listener'ов, graph/prefab изменений.

---

## 2. Static proofs

| Проверка | результат |
|---|---|
| braces / parens | 6/6, 43/43 |
| `modded class SCR_CharacterControllerComponent` | 1 |
| `GetOnAnimationEvent` | 1 (подписка) |
| `StartsWith("Weapon_")` | 1 (фильтр) |
| `SetAmmoCount` / `ReloadWeapon` / `ReloadWeaponWith` / mag spawn-attach-detach-despawn-release / `CallCommand` / `SetVariableBool` / `ClearChamber` | **0** |
| `override void Update` / `override bool HandleWeapons` / `HandleWeaponReloading` / `SetReloadWeapon` | **0** |
| `CallLater` (таймеры) / `AddActionListener` (input) / `SetCurrentCommand` / `BindCommand` | **0** |

---

## 3. Риск и mitigation (важно)

Это **единственный character-global** файл в T4B lab (`modded SCR_CharacterControllerComponent`). Историческая лаба с character-global mod'ом была в списке подозреваемых (I1 H2, MEDIUM), но P2 локализовал поломку R в **handler'е**, а не в character-компоненте. Здесь файл:
- **observe-only** (не трогает reload command flow, не подписывается на input, не переопределяет `OnApplyControls`);
- **lab-gated** (лог только для lab-оружия).

**Проверка при прогоне:** native `cmd1` rack обязан по-прежнему работать. Если rack регрессирует с этим файлом — удалить его первым (он единственный character-global).

---

## 4. Install plan (только по отдельному GO + закрытый Workbench)

1. Добавить новый live-файл `Scripts/Game/ARMST_T4B/ARMST_T4B_CharacterMagEventObserver.c` (staged `7D3B97F8…`).
2. Handler (`D5BA3052…`) и observer (`7BE1D375…`) — **не трогать**.
3. Sync labs; узкий commit.
Rollback: удалить новый файл (ничего существующего не меняется).

---

## 5. Что разделит результат

- **player-side видит `Weapon_DetachMagazine`/`AttachMagazine` ровно между cmd5 и cmd3** → native reload всё ещё клип/event-driven, просто мы смотрели не на ту сторону → следующий сильный A/B: player-клип **без magazine events** (не ломая `cmd1`).
- **и player-side ничего не видит, а магазин всё равно исчезает** → мутация выполняется **ниже/вне** animation-event path → тогда (и только тогда) идём к producer audit (уровень выше `OnCharacterCommand`).

---

## 6. Границы

Live/граф/prefab/observer/Tube3/Core/grid/inventory не менялись; `GAMEPLAY_FILES_CHANGED=0`. cmd7 не предлагается; глобальный `HandleWeaponReloading` не восстанавливается; Chungus — reference-only.

Статус: **`T4B_PLAYER_SIDE_MAG_EVENT_OBSERVER_SOURCE_PREPARED_OWNER_REVIEW`**. STOP.
