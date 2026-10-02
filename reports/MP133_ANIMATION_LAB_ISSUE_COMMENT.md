# Issue #26 (V2) — status comment (ready to paste)

Copied here because this environment has no `gh`/token to post; publication of
the repo files is done via the installed Git (see commit SHA in the reply).

---

**Статус V2: READY_FOR_OWNER_TEST.** Реализация, конфиг префабов, граф/ASI и
static/unit-проверки закрыты; компиляция и игровые критерии — **NOT RUN /
OWNER TEST REQUIRED** (агенту запрещено запускать игру/Workbench Play).

Продолжение V1 без пересоздания аддона. Соблюдён OWNER OVERRIDE: только
префабы + изолированные скрипты/анимации; мир/`.ent`/`.layer`/сценарий/спавн
отсутствуют (проверяется валидатором `check_no_world`).

## Что изменено в V2

- **Ёмкость трубы = 3 (owner override).** Оба лаб-префаба задают
  `ARMST_MP133_Lab_Component.m_iTubeCapacityOverride 3` и **переопределяют
  унаследованный** `ARMST_SHOTGUN_COMPONENTS "{69E4C57F6C1EE3A6}" { m_MaxMagazineAmmo 3 }`.
  Это снимает конфликт с Core `WeaponHandler` (иначе он режет трубу обратно до 2
  и спавнит лишний магазин): Core согласован на 3 **строго для этих префабов**,
  без правок Core/Weapons/vanilla и без влияния на обычные дробовики.
  Рантайм-энфорсмент (загрузка 3, третий insert, отклонение четвёртого,
  отсутствие лишних магазинов/потерь, независимость ствола, отсутствие
  двойного списания) — **OWNER TEST REQUIRED**.
- **Gate A — идентичность экипированного оружия.** Добавлен безусловный
  rate-limited (1 Гц) лог текущего оружия, даже если lab-компонент не найден:
  `WEAPON wm=… wpn=… ent=… prefab=… labComp=… tube=… reloadType=… startReloading=… raised=… isReloading=…`.
  Это однозначно решает «lab-оружие не экипировано» vs «lookup не находит
  компонент». `FindComponent` на компоненте валиден (Core: `item.FindComponent(…)`),
  поэтому наиболее вероятная причина прошлых нулей — оружие не было в руках.
- **Gate C — идемпотентность вместо таймера.** Введено состояние цикла:
  окно `armed` при открытии и повторно после завершения клипа (`BlendOut`);
  успешный коммит снимает `armed`. Дубликат кадра 43 без завершения клипа не
  коммитит (`SERVER commit ignored: cycle not armed`). Cooldown 500 мс —
  вторичная защита.
- **Gate B — трассировка R.** Сохранены `watcher` (100 мс) и `OnApplyControls`;
  новые логи `WEAPON`/`reload request detected` покажут, отражают ли
  `WeaponIsStartReloading()/GetWeaponReloadType()` нажатие R на этой ревизии.
- **Метки:** `MP-133 [LAB]` / `MP-133 RIS [LAB]`.
- **Валидатор/тесты:** добавлена проверка отсутствия world/layer; **8/8 PASS**.

## Префабы (ResourceName / GUID) — владелец ставит в свой мир

- `{FC1935AF936F63E5}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`
- `{4B288C21B7125D50}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et`

## Acceptance (кратко)

| Проверка | Статус |
|---|---|
| Isolation | PASS (SHA-256; оригиналы не тронуты) |
| Dependencies | PASS (static) |
| Resource wiring | PASS (static) |
| Compile | требует перекомпиляции владельцем (не запускал Workbench по его запрету); ранее компилировалось |
| No world/layer | PASS (валидатор) |
| One-shell / Pump / Interrupt / Networking / Recovery | UNVERIFIED (нужен игровой прогон) |

## Точный следующий шаг владельца

1. Пересобрать скрипты; убедиться, что нет `SCRIPT (E)`.
2. Поставить один из префабов выше в **свой** мир, взять оружие
   (**имя `MP-133 [LAB]`**).
3. В логе проверить `WEAPON … labComp=1` (подтверждение экипировки).
4. Нажать R → прислать `console.log` (маркеры `reload request detected`,
   `begin insert loop`, `SERVER Insert COMMIT`).

Если `WEAPON … labComp=0` при видимом lab-оружии — это точная цель для
исправления lookup. Если `labComp=1`, но при R нет `reload request detected` —
цель для Gate B (перехват R).
