# MP-133 Task #1 — Native mag mutation boundary audit (READ-ONLY)

Статус: **T4B_NATIVE_MAG_MUTATION_BOUNDARY_AUDIT_COMPLETE**
Дата: 2026-10-06
Задание: Issue #34 — «T4B_NATIVE_MAG_MUTATION_BOUNDARY_AUDIT» ([6019845629](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **read-only / source-only**. Live/граф/prefab/observer/Tube3/Core/grid/inventory не менялись.

Цель: найти **самую раннюю конкретную границу мутации** после `CMD_Weapon_Reload = 5` (что первым физически меняет/отсоединяет/скрывает/деспавнит/заменяет установленную трубу-магазин MP-133) и определить, есть ли **pre-mutation** weapon-local хук, который может подавить/перенаправить это, не ломая native `cmd1` rack.

---

## 0. Входные подтверждённые факты

- `RACK_RECOVERED_WITH_T4B_HANDLER_REMOVED` — глобальный `modded HandleWeaponReloading` отвергнут; native `cmd1` rack обязан остаться нетронутым.
- weapon-local `OnCharacterCommand` — валидный receiver; видит `1 → 5 → 3`.
- **Pinned Bohemia reference:** `references/bohemia/Arma-Reforger-Samples/83f12390/` (commit `817da0ef…`), audit `reports/MP133_BOHEMIA_SAMPLEWEAPON01_WORKSPACE_AUDIT.md`.
- Official SampleWeapon `WeaponReloadSTM` (SOURCE, `sampleweapon_01.agf` L214–261): `1`=rack, `2`=insert, `3`=insert+rack, `4`=remove+insert, `5`=remove+insert+rack, `6`=remove; `7–9` исключены entry-условием (`!inRange(...,7,9)`).
- **Важно:** cmd5/3 в графе переходят в `ReloadActionBolt` **внутренне**, без нового cmd1 (audit §4). Значит наблюдённый отдельный `OnCharacterCommand(...,3)` — это **отдельное обновление команды выше графа**, не внутренний переход (UNRESOLVED причина).

---

## 1. События native reload: origin / receiver / before-after / cancel (SOURCE)

Источник: `reports/MP133_V3_INSERT_EVENT_AUDIT.md` (T3, `.txa`/ANM-события production MP-133) + `MP133_V3_RELOAD_GRAPH_AUDIT.md` §3.2 + SDK.

| Событие | Клип / кадр | Origin | Receiver/consumer | Относительно физической мутации | bool/cancel |
|---|---|---|---|---|---|
| `Weapon_MagRelease` | remove f6 / insert f64 | clip ANM/TXA (authored) | **engine** (native weapon/mag/animation); project callback `OnAnimationEvent` | remove-side f6 = release/latch (до detach); insert-side f64 = после attach | **нет** (callback void) |
| `Weapon_DetachMagazine` | remove f10 | clip | **engine** | **detach установленного магазина = первая физическая мутация remove-стороны** | **нет** |
| `Weapon_DespawnMagazine` | remove f15 | clip | **engine** | после detach | **нет** |
| `Weapon_SpawnMagazine` | insert f10 | clip | **engine** | спавн объекта нового магазина | **нет** |
| `Weapon_AttachMagazine` | insert f43 | clip | **engine** | **attach целого магазина = становится источником ammo (мутация insert-стороны)** | **нет** |
| `Weapon_Rack_Bolt` | bolt f14 | clip | **engine** (+ Core реагирует) | после mag-операции | **нет** |

**Ключевое (SOURCE, T3):** все `Weapon_*Magazine` события потребляются **движком** (native weapon/magazine/animation system). Проектный callback `OnAnimationEvent` — это **нотификация**, а не гейт; bool-хука на mag attach/detach в SDK нет (`BaseMagazineComponent`/`BaseMuzzleComponent` не имеют attach/detach admission API; единственные writer'ы — `BaseMagazineComponent.SetAmmoCount`, `BaseMuzzleComponent.ClearChamber`).

---

## 2. Хронологическая таблица: cmd5 → физическая мутация

```
cmd5 (MagNoBulletReload: remove -> insert + rack)   [graph/engine]
  │  (в текущем ASTRA2-графе НЕТ состояния cmd5 — состояния cmd2..6 удалены)
  ▼
native remove-фаза:
  Weapon_MagRelease (release/latch)         ← клип, если проигрывается
  Weapon_DetachMagazine                     ← ПЕРВАЯ физическая мутация установленной трубы
  Weapon_DespawnMagazine
  ▼
native insert-фаза:
  Weapon_SpawnMagazine (новый объект)
  Weapon_AttachMagazine                     ← новый магазин становится источником ammo
  Weapon_MagRelease (latch)
  ▼
  Weapon_Rack_Bolt                          ← bolt
  ▼
позже отдельный cmd3 (обновление команды выше графа, UNRESOLVED)
```

**Наблюдение (owner runtime):** после cmd5 зафиксирована **реальная пропажа магазина** — при том, что активный `MP133_Astra2.agf` **не** содержит состояний cmd2–6. Следствие (**INFERENCE**): в текущем lab физическая мутация выполняется **движком ниже уровня графа**; удаление graph-состояний/ASI-маппингов **не** блокирует мутацию (согласуется с требованием 7).

---

## 3. Классификация кандидатов

| Кандидат | Локальность | Класс |
|---|---|---|
| `BaseItemAnimationComponent.OnCharacterCommand(cmd5)` | weapon-local | **PRE_MUTATION_CANDIDATE** (срабатывает до мутации), но **observer-only** (`void`) |
| `BaseItemAnimationComponent.OnAnimationEvent("Weapon_*")` | weapon-local | **POST_MUTATION_OBSERVER** (нотификация потребляемого движком события; не гейт) |
| `BaseItemAnimationComponent.OnPrepareAnimInput` (`bool`) | weapon-local | **UNRESOLVED** (anim input, не reload/mag-решение) |
| `BaseItemAnimationComponent.OnProcessAnimOutput` (`bool`) | weapon-local | **UNRESOLVED** (anim output) |
| `BaseWeaponComponent.IsReloadPossible()` (`proto external bool`) | weapon (класс), но **global `modded`** | **UNRESOLVED** (не доказано, что нативный handler его читает; глобальный — против правила 5/9) |
| `BaseWeaponComponent.OnWeaponActive/Inactive` (`void`) | weapon-local | **NOT_APPLICABLE** (equip/unequip) |
| mag attach/detach admission hook (weapon/mag-local) | — | **NOT_APPLICABLE** (в SDK отсутствует) |
| inventory `CanStoreItem` admission | inventory (не weapon) | **NOT_APPLICABLE** (вне scope Task #1) |
| `Weapon_*` events as gate | — | **NOT_APPLICABLE** (движок потребляет; callback void) |

---

## 4. Earliest proven pre-mutation interception candidate

**`NO_PRE_MUTATION_WEAPON_LOCAL_HOOK_FOUND`.**

- Самая ранняя weapon-local **точка наблюдения** до мутации — `OnCharacterCommand(cmd5)` (до remove/insert). Но она **observer-only** (`void`) → не interception.
- Первая физическая мутация remove-стороны — **`Weapon_DetachMagazine`** (remove f10; `Weapon_MagRelease` f6 — release/latch до него); insert-сторона — **`Weapon_AttachMagazine`** (f43). Оба события **потребляет движок**; weapon-local `bool`/cancel-хука нет.
- Weapon-local `bool`-хуки (`OnPrepareAnimInput`/`OnProcessAnimOutput`) — anim input/output, не reload/mag-решение (**UNRESOLVED**, не доказано).
- `IsReloadPossible`-override — **global**, UNRESOLVED, против правил.

→ До мутации **нет доказанного** weapon-local способа подавить/перенаправить cmd5. Не угадывать.

---

## 5. Рекомендуемый минимальный диагностический probe (НЕ реализован)

Цель: измерить точный runtime-порядок `cmd5 → первое событие → первая мутация → cmd3` и убедиться, проигрываются ли `Weapon_*` события в текущем ASTRA2-графе (или мутация чисто движковая).

Минимальный **read-only** probe (только логирование; отдельная задача/GO):
- на **существующем** weapon-local observer (`ARMST_T4B_AstraV2_WeaponAnimationComponent`) — расширить `OnAnimationEvent`, чтобы логировать **любое** событие с именем `Weapon_*` (MagRelease/Detach/Despawn/Spawn/Attach/Rack_Bolt) + мгновенный snapshot (mag entity ref-tag, `GetAmmoCount/GetMaxAmmoCount`, muzzle `GetAmmoCount`, `IsCurrentBarrelChambered`, barrel);
- в `OnCharacterCommand` — логировать `commandID/intValue/floatValue` (уже есть);
- ничего не менять в поведении, никаких writers/таймеров/`Update`.

Ожидаемый read-out: есть ли `Weapon_DetachMagazine`/`Weapon_AttachMagazine` в логе (клип-драйв) или только смена mag-ref (чисто движковая мутация), и какой `cmd`-интервал им соответствует. Это решит, где именно ставить следующий (уже отдельно авторизуемый) шаг.

---

## 6. Границы соблюдены

- `OnAnimationEvent` **не** считается «достаточно ранним» — доказано, что движок потребляет события (POST_MUTATION_OBSERVER).
- Удаление graph-состояний/ASI **не** считается доказательством блокировки (owner-лог: мутация произошла).
- cmd7 не предлагается как решение (не доказан для tube-магазинов).
- Глобальный `HandleWeaponReloading` не восстанавливается.
- Chungus — reference-only.
- Live/ASTRA2/prefab/observer/Tube3/Core/grid/inventory — не тронуты; `GAMEPLAY_FILES_CHANGED=0`.

Статус: **`T4B_NATIVE_MAG_MUTATION_BOUNDARY_AUDIT_COMPLETE`**.
