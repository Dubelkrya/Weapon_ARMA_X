# MP-133 AnimationLab — импорт клипов и подключение (V2.3), R-план

**Статус проверки (2026-10-02):** в лаборатории **нет**
`LabClips/W_MP133_Lab_Inject.anm` / `P_MP133_Lab_Inject.anm` — есть только
два `.txa`. Значит, импорт (Часть 1) необходим.

**Реализация R (существующий механизм модов) уже подготовлена:**
- `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_CommandHandler.c` —
  `modded SCR_CharacterCommandHandlerComponent` с lab-gated
  `override bool HandleWeaponReloading(...)`: для лаб-оружия запускает
  лабораторную вставку и возвращает `true` (не даёт ванильной перезарядке
  заменить магазин), иначе `super`.
- Гейт `ARMST_MP133_Lab_Component.m_bLabInsertEnabled` (по умолчанию **off**) —
  хук инертен, пока клипы не подключены; авто-триггер также выключен.
- Включение гейта — только ПОСЛЕ подключения санитизированных ANM (Часть 2).

---

Порядок зафиксирован владельцем (#27):
1. Агент готовит импорт двух `LabClips/*.txa` и точную инструкцию для Animation
   Editor. Если импорт требует Workbench — это **единственная** операция владельца.
2. После импорта агент сам подключает полученные `.anm` к лабораторным `.asi` и
   графу, **не используя** события `Weapon_SpawnMagazine`, `Weapon_AttachMagazine`,
   `Weapon_MagRelease`.
3. Обработку R агент реализует только через существующие механизмы модов и
   лабораторные скрипты (без исследования/изменения движка).
4. Затем — проверка полноценной поштучной зарядки.

---

## Часть 1. Инструкция импорта (выполняет владелец, Workbench, БЕЗ Play)

**Файлы (уже лежат в лаборатории):**
- `Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.txa`
- `Assets/Weapons_RUS/Mp_133/Workspace/LabClips/P_MP133_Lab_Inject.txa`

Это копии оригинальных движений досылки, у которых события замены магазина
переименованы в нейтральные:
`BlendIn`(1), `ARMST_Lab_Shell_Spawn`(10), `ARMST_Lab_Shell_Commit`(43),
`ARMST_Lab_Shell_Release`(64), `BlendOut`(100) — **без** `Weapon_*Magazine`.

**Цель:** получить рядом с каждым `.txa` скомпилированный
`*.anm` (+ `*.anm.meta`) с этими же событиями — ровно так, как оригинальные
`Reload/*.anm` были получены из своих `Reload/*.txa`. Оригиналы не трогать.

**Шаги:**
1. Открыть Workbench с проектом `ARMST_MP133_AnimationLab` (игру/Play не
   запускать).
2. Проверить, не скомпилировались ли ANM автоматически при загрузке проекта:
   появились ли
   `.../LabClips/W_MP133_Lab_Inject.anm` и `.../LabClips/P_MP133_Lab_Inject.anm`
   (+ `.meta`).
   - **Если да** — импорт не нужен, переходите к «Что прислать».
   - **Если нет** — перейдите к шагу 3.
3. Открыть **Animation Editor** → рабочее пространство
   `Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.aw`.
   Использовать функцию импорта анимаций (та же, которой были импортированы
   оригинальные `Reload/W_MP133_Reload_Inject.txa` и
   `Reload/P_MP133_Reload_Inject.txa`); импортировать оба файла из `LabClips/`.
   Результат (`*.anm` + `*.meta`) должен появиться **рядом** с `.txa` в `LabClips/`.
   - Если в вашей сборке Workbench пункт называется иначе (например, через
     Resource Manager «Import»), цель та же: скомпилировать `.txa` → `.anm`
     в `LabClips/`, не изменяя оригиналы.
4. Убедиться (открыв ANM в Animation Editor), что события именно
   `ARMST_Lab_Shell_*` + `BlendIn/BlendOut`, и **нет** `Weapon_*Magazine`.

**Что прислать агенту (одно сообщение):**
- строку `Name "{GUID}Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.anm"`
  из `W_MP133_Lab_Inject.anm.meta`;
- строку `Name "{GUID}.../LabClips/P_MP133_Lab_Inject.anm"` из `P_...anm.meta`;
- подтверждение списка событий (скрин/текст).
После этого агент выполняет Часть 2 сам.

---

## Часть 2. Подключение после импорта (делает агент — одной командой)

После импорта достаточно сообщить два GUID; подключение выполняет
детерминированный коннектор (в `Weapon_ARMA_X`, без Workbench):

```
python agent/scripts/mp133_lab_connect_anims.py --w-guid <WGUID> --p-guid <PGUID> [--harden-graph] [--dry-run]
```

Поведение (учтены замечания ревью #27):
- **Preflight до записи:** для каждого `.anm` проверяется наличие самого файла и
  `.anm.meta` с **тем же GUID и тем же путём**; в каждом `.asi` должно быть ровно
  по одной строке `Reload.Erc.Reload_InsertMag` и `Reload.Pne.Reload_InsertMag`;
  проверяется структура `WeaponReloadSTM`. При любом несоответствии — отказ, **ничего не пишется**.
- **ASI:** перепривязываются ровно две строки на инстанс (Erc+Pne); частичная
  правка считается ошибкой; идемпотентно.
- **Граф — опционально** (`--harden-graph`, по умолчанию **выключено**):
  структурно, только внутри `WeaponReloadSTM`, состояния с `Child "MagReloadSTM"`/
  `Child "RemoveMagAnim"` (сейчас ровно `MagReload`, `MagNoBulletReload`, `RemoveMag`)
  переводятся на `InsertMagAnim`; вложенный `MagReloadSTM`, переходы, `RackBoltAnim`
  и прочие узлы не трогаются; неожиданная структура — отказ.
- **Атомарность:** все файлы валидируются до записи; запись через temp+replace с
  откатом уже записанных при сбое.
- `--dry-run` печатает точный diff (строки/состояния), ничего не пишет.

`--no-harden-graph` — рабочий явный выключатель (эквивалентен умолчанию).

Пример ручного diff (если нужно без скрипта):

`Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi` — заменить:
```
AnimSetInstanceSource_Line "Reload.Erc.Reload_InsertMag" {
 Resource "{45B1772B8AFEAE47}Assets/Weapons_RUS/Mp_133/Workspace/Reload/W_MP133_Reload_Inject.anm"
}
AnimSetInstanceSource_Line "Reload.Pne.Reload_InsertMag" {
 Resource "{45B1772B8AFEAE47}Assets/Weapons_RUS/Mp_133/Workspace/Reload/W_MP133_Reload_Inject.anm"
}
```
на (GUID из импортированного ANM):
```
AnimSetInstanceSource_Line "Reload.Erc.Reload_InsertMag" {
 Resource "{<WGUID>}Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.anm"
}
AnimSetInstanceSource_Line "Reload.Pne.Reload_InsertMag" {
 Resource "{<WGUID>}Assets/Weapons_RUS/Mp_133/Workspace/LabClips/W_MP133_Lab_Inject.anm"
}
```

`Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_player.asi` — аналогично для
`{<PGUID>}Assets/Weapons_RUS/Mp_133/Workspace/LabClips/P_MP133_Lab_Inject.anm`.

**Граф и контроллер менять не нужно:**
- `MP133_Lab.agf` уже циклит `InsertSingleProjectile` по `IsEvent("BlendOut")`
  (BlendOut сохранён в санитизированных клипах) при `CMD_Weapon_Reload == 7`.
- Контроллер уже слушает `ARMST_Lab_Shell_Commit` (единственный триггер коммита)
  и повторно «взводит» цикл по `BlendOut`; `Weapon_AttachMagazine` из триггеров
  исключён.
- Лабораторный магазин 3 патрона и оба префаба уже настроены (V2.2).

После этой правки события замены магазина в цикле досылки физически не firing →
движок не сможет заменить трубу во время вставки.

---

## Часть 3. Обработка R через существующие механизмы модов

Существующий механизм (как в Core): `modded`-класс + действие ввода и
`CharacterInputContext.SetReloadWeapon(type)`.

**Подготовленный кандидат (агент включит ПОСЛЕ импорта клипов):**
`modded class SCR_CharacterCommandHandlerComponent` —
`override bool HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)`;
для лабораторного оружия: запустить лабораторную вставку и вернуть `true`
(взять обработку на себя), иначе `super`. Плюс заново включить лабораторный
триггер (`LabReloadRequested`) — но **только** после того, как в `.asi` стоят
санитизированные клипы, иначе вернётся регрессия с ванильной заменой магазина
(как в логе владельца: `10/10`).

**ОТДЕЛЬНЫЙ R-БЛОКЕР (описывается как есть):**
- Точное ванильное action-имя перезарядки неизвестно (в `data.pak`), поэтому
  нельзя гарантированно различить R и LSHIFT+R по имени действия.
- Не подтверждено (без игры), что `HandleWeaponReloading`, возвращающий `true`,
  реально предотвращает нативный mag-swap (события `Weapon_Detach/Attach`),
  а не только пропускает анимационный обработчик.
- Пока это не подтверждено владельцем, авто-триггер лаборатории остаётся
  выключенным (безопасное состояние V2.3): без бесконечного цикла и без
  вызванной лабой замены магазина.
- Что нужно для снятия R-блокера: после импорта клипов владелец нажимает R и
  присылает `console.log`; критерий — в цикле вставки **нет**
  `anim event 'Weapon_MagRelease/DetachMagazine/DespawnMagazine'`, а труба
  растёт 2/3 → 3/3 с `SERVER COMMIT`. Если события замены всё же есть —
  `HandleWeaponReloading` не подавляет нативную перезарядку, и нужен другой
  существующий механизм (обсудить отдельно).

---

## Часть 4. Чек-лист после импорта

1. Пересобрать скрипты; в логе нет `SCRIPT (E)`.
2. Открыть ANM: события `ARMST_Lab_Shell_*` + `BlendIn/BlendOut`, без `Weapon_*Magazine`.
3. Взять `MP-133 [LAB]` (труба `12g 3rnd [LAB]`, 3).
4. R: труба 2/3→3/3, четвёртый insert отклонён; **нет** событий замены магазина;
   `SERVER COMMIT` присутствует.
5. LSHIFT+R: помпа (труба −1, Core), консистентно.
6. Прерывания: опускание/смена/помпа — без залипшего `clientInsert` и без
   бесконечного цикла.
