# MP-133 AnimationLab — HANDOFF / технический отчёт для следующей модели

Дата: 2026-10-02. Автор: предыдущая сессия. Задача: Issue #25
(`Weapon_ARMA_X`, репозиторий `Dubelkrya/Weapon_ARMA_X`).
Статус: **реализация собрана, статически проверена, в Workbench компилируется и
загружается; игровой поток досылки НИ РАЗУ не запускался — не подтверждён.**
Отчёт самодостаточен: цель, файлы, архитектура, история правок, фактические
логи, открытые вопросы и план для следующей модели.

---

## 0.000 Snapshot investigation (issue #27 follow-up) — нет готовых анимаций в снапшотах

> **Готовый план импорта + подключения + R:** см. отдельный документ
> `reports/MP133_ANIMATION_LAB_V23_IMPORT_AND_R.md` (инструкция Animation Editor,
> точный ASI-diff с placeholder-GUID, отдельный R-блокер).

Проверено фактически (read-only):
- `agent/scripts/base_game_snapshot.py` — **read-only** индексатор; явно обрабатывает
  только `ext in (".et", ".conf")` (строка 115). Анимации по дизайну не индексируются.
- `catalog/` и `indexes/`: **0** файлов `.anm/.asi/.ast/.agf/.agr/.aw/.txa`.
  Содержимое — `.et`/`.conf` (оружие, магазины, патроны, конфиги) и JSON-индексы
  (`weapons.json`, `magazines.json`, `ammunition.json`, `reference_graph.json`,
  authoring/script references).
- Сопоставление с лабораторией: снапшоты подтверждают MP-133
  (`Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et`), цепочку 12ga
  (`12ga_Buckshot_base` → `armst_12ga_Buckshot` → `armst_12ga_Shell`), патрон
  `armst_Ammo_12ga` — всё это лаб уже использует через живой аддон. **Готовых
  per-shell анимаций (клипов без mag-swap событий) в снапшотах нет.**

Вывод: BLOCKED из V2.3 остаётся и теперь **подтверждён фактами** — знаниевый
репозиторий не может предоставить анимацию поштучной досылки. Нужны либо
(a) lab-only санитизированные `.anm` (импорт TXA в Workbench Animation Editor —
действие владельца), либо (b) проверенный хук подавления ванильной перезарядки.

Внешняя находка: живой `armst_Ammo_12ga.et` **имеет** `.meta`; предупреждение
EntityPool «unregistered prefab armst_Ammo_12ga.et» — runtime-регистрация/загрузка
вне лаборатории и вне снапшотов (отдельная issue).

## 0.00000000 V2.7 — C2-диагностика патронника + read-only разбор изоляции Core

Владелец разрешил C2 (Issue #27, comment 5959385576). Отчёт:
`reports/MP133_ANIMATION_LAB_V27_C2_TRACE_AND_CORE_ISOLATION.md`.

- **C2 реализована lab-only** в `ARMST_MP133_Lab_Character.c` (маркер
  `[ARMST_MP133_LAB-C2]`): сэмплер каждые 100 мс на смену подписи, значимые
  `Weapon_*`-события, `SETTLE:` через 150 мс, действие LSHIFT+R. Пишет
  физические `wep_id`/`mag_id` (Entity.GetID), tube, chambered, barrel,
  `IsChamberingNecessary/Possible/IsReloadPossible`, reloadType/start/raised.
  Наблюдает и нетронутый прод-MP-133 пассивно.
- **Гейты OFF**, graph/ASI/ANM/префабы/прод/Core не менялись. Валидатор +
  `check_v27_trace` PASSED; тесты 14/14, 15/15, 17/17. Бэкап скриптов:
  `artifacts/MP133_Lab/v27_backups/` (baseline `37D0…2A34`).
- **Compile-fix (comment 5959746653):** первый прогон дал lab-owned
  `SCRIPT (E) ...433: Formula too complex / Incompatible parameter '|'` —
  длинная inline-подпись. Исправлено инкрементальной сборкой (`sig = sig + ...`)
  и типизированными локалами; хэши `4A20…5EA0` → `7737…8C6A`. Статус
  `COMPILE_BLOCKED` снят → `OWNER RETEST REQUIRED`. Регрессия в
  `check_v27_trace`: инкрементальные needles + запрет строк с ≥12 `+`.
- **V2.7b (comment 5960042056):** `Single.ManualAction` — штатный цикл; **обычный
  R = ручной цикл** (сохраняем, настройку не трогаем), **LSHIFT+R = отдельная
  Core-помпа**, **J — под будущую загрузку**. C1/Core-подавление заморожены до
  измерения обычного R. `IEntity.GetID` в справочнике нет и в логе дал 0 →
  идентичность на **тегах по ссылке** (`wep_tag`/`mag_tag`, смена = смена
  физического объекта). Добавлен лог команды `[ARMST_MP133_LAB-C2] CMDCHG id=…`
  в lab-хуке. Хэши: Character `524E…14E3`, CommandHandler `CD77…2268A`.
  Эксперимент: один выстрел + один обычный R (см. отчёт §7.4).
- **Read-only Core-изоляция:** lab-only отключение `TAO_DecrementAmmoOnRack`/
  `TAO_ClearChamberIfNoMagOrEmpty` прямой правкой Core запрещено; косвенно —
  возможно через разделяемое `m_ServerManualRackPending` (merged `modded`-класс)
  + снятие фолбэка, но timing-fragile и **патронник не заполняет**. Флаги:
  риск `tube=0, chamber=1`, фолбэк-таймер Core. Не реализовано.
- Следующая точка: один контролируемый тест gate-OFF (см. отчёт §5).

## 0.0000000 V2.6 — разбор «помпа списывает трубу, но не заполняет патронник» (read-only)

Приоритет сменён (Issue #27, comment 5958821529/5958846527): сначала вернуть
подачу патрона помпой, затем короткое/долгое R. Гейт досылки — OFF.

Подробный разбор: `reports/MP133_ANIMATION_LAB_V26_PUMP_CHAMBER_TRACE.md`.

Ключевое (проектно-доказанное):
- **Патронник скриптами не пишет никто.** Публичный API `BaseMuzzleComponent` —
  только `ClearChamber` + геттеры, сеттера нет. `chambered:0→1` — движок.
- Core-помпа (`ARMST_WEAPONS_HANDLER.c:295-314`) только `tube−1`;
  `TAO_ClearChamberIfNoMagOrEmpty` (`:319-349`) только очищает.
- Ветка помпы графа/клипов (`ReloadActionBolt`→`RackBoltAnim`→
  `W_MP133_Reload_Bolt.anm`) **идентична проду** — лаба её не ломала.
- Лаба сняла с перезагрузки нативные события (`Weapon_AttachMagazine` и др.),
  перенаправив `Reload_InsertMag` на санитизированный клип; в проде именно эти
  события, вероятно, и досылали патрон (обычный R владельца). LSHIFT+R
  (Core-помпа) не досылал и в проде.
- `ARMST_SHOTGUN_COMPONENTS { Enabled 0 }` есть только у **non-RIS** лаб-префаба
  (у RIS нет) — зафиксировано как переменная.
- `prefab=` в логе — чисто диагностическое поле.

Предложение (требует одобрения, ничего ещё не менялось): **C1** — отделить
нативную ветку перезагрузки (вернуть оригинальные события/клип → досылка
патрона) от лабораторной поштучной досылки (новая lab-строка на санитизированный
клип); **C2** — lab-only диагностика `IsChamberingNecessary/Possible` и
`chambered` по событиям. Откат — `artifacts/MP133_Lab/prefab_backups/` + бэкапы
graph/ASI. Рантайм — `OWNER TEST REQUIRED`.

## 0.000000 V2.5b — помпа через Core-действие; отпускание без таймера; отложенный старт

По review #27 (hold перед повторным тестом):
- **Помпа больше не определяется по `type==1`.** Входной гейт отклоняет помпу по
  срабатыванию **существующего Core-действия** `ARMST_LIGHT_RELOAD_ACTION`
  (listener на то же действие, что использует Core для rack). Обычный R с любым
  типом (включая транзитный 1) — попытка вставки.
- **Отложенный старт** `LAB_BEGIN_DEFER_MS=30` + `LabDeferredBegin`: pump-latch,
  установленный после вызова обработчика, всё равно отменяет старт — результат не
  зависит от порядка обработчиков (оба порядка покрыты тестами).
- **`LabInputReleased`** — только положительный idle:
  `!insertActive && !IsReloading && !pumpLatch && inputCtx && !start && type==0`.
  **Таймер-ре-арм удалён** (никакой имитации отпускания); `!inputCtx` не считается
  отпусканием; сброс — ещё и при потере управления персонажем.
- **Модель состояния** `agent/scripts/mp133_lab_r_gate_model.py` +
  `agent/tests/test_mp133_lab_r_gate_model.py` — **17/17** (в т.ч. удержание R > 2 с
  не ре-армит; оба порядка pump/handler; release). Явно **model-only**.
- Preflight-отчёт: `reports/MP133_ANIMATION_LAB_V25_INPUT_PREFLIGHT.md`.
- Гейт `m_bLabInsertEnabled` — **OFF** на обоих префабах.

## 0.000001 V2.5 — различение помпы через Core-действие; предикат отпускания; модель

По review #27 (hold перед повторным тестом):
- **Помпа больше не определяется по `type==1`.** Входной гейт отклоняет помпу по
  срабатыванию **существующего Core-действия** `ARMST_LIGHT_RELOAD_ACTION`
  (listener на то же действие, что использует Core для rack). Обычный R с любым
  типом (включая транзитный 1) — попытка вставки. Это устраняет риск, что
  отклонение `type==1` заблокирует штатный R.
- **`LabInputReleased`**: `!insertActive && !IsReloading && !pumpLatch &&
  !WeaponIsStartReloading && GetWeaponReloadType()==0`, плюс страховочный
  re-arm через 2 с. Abort/cease/lowered/full/held не ре-армят latch.
- **Модель состояния** `agent/scripts/mp133_lab_r_gate_model.py` +
  `agent/tests/test_mp133_lab_r_gate_model.py` — 15/15 (последовательности
  press→begin→hold→abort→release→press, lowered, pump vs R, full, release,
  safety-timeout). Явно **model-only**, не рантайм.
- Preflight-отчёт: `reports/MP133_ANIMATION_LAB_V25_INPUT_PREFLIGHT.md`
  (вердикт: кандидат тестируем; остаточные неизвестности перечислены).
- Гейт `m_bLabInsertEnabled` — **OFF** на обоих префабах.

## 0.00000 V2.4 — controlled R test failed; входной гейт реализован, гейт возвращён OFF

**Итог контролируемого теста (owner log, comment):** 61 `ACTION_BEGIN` /
`SERVER CYCLE_BEGIN`, но **0 `SERVER COMMIT`** и 0 `ARMST_Lab_Shell_Commit`;
немедленные `ACTION_ABORT (pump/rack type 1)` / `(weapon lowered)`; повторные
повторы. Причины: обработчик `HandleWeaponReloading` вызывается каждый кадр и
запускал новое действие (нет гейта входа), а пульс отменял валидную вставку по
остаточному значению type 1.

**V2.4 (lab-only):**
- **Входной гейт** `LabCanBeginFromHandler`: начать можно только для
  поднятого лабораторного оружия с валидным магазином (<cap) и резервом>0,
  и **не** для rack/pump (type 1). Проверки — до открытия серверного окна.
- **Защёлка ввода** `m_bLabInputLatched`: ровно одна попытка на удержание;
  повторный вход блокируется; сброс — только по отпусканию ввода
  (`input re-armed (released)`, watcher). Abort становится терминальным для
  этого нажатия — нового `ACTION_BEGIN` без нового валидного ввода нет
  (устраняет цикл).
- Убран abort по type 1 из пульса (валидная вставка не отменяется остаточным
  значением); genuine LSHIFT+R остаётся помпой.
- Хук передаёт `pInputCtx` в гейт.
- **Гейт `m_bLabInsertEnabled` возвращён OFF** (восстановлено из пре-тест
  бэкапа; хэш совпал с `3A0749E5…F8766D`).

**Проверки:** валидатор PASSED; лаб-тесты **13/13** (добавлен
`check_v24_entry_gate`), коннектор **15/15**. Клипы/граф/префабы не
перегенерировались.

**Остаётся (OWNER TEST REQUIRED):** после отдельного разрешения — снова включить
гейт на non-RIS и проверить 4 признака. Не подтверждено (явно): действительно ли
`HandleWeaponReloading` подавляет нативный reload — нулевой mag-swap в прошлом
прогоне не доказателен, т.к. коммита не было.

## 0.0000 Контролируемый тест R (owner authorization, issue #27)

- Гейт `ARMST_MP133_Lab_Component.m_bLabInsertEnabled = 1` включён **только** у
  `Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`; RIS — OFF.
- Клипы подключены (`W {1F9884C8701DAE1B}`, `P {FE510A1EC49563F1}`), граф
  «закалён» (`MagReload`/`MagNoBulletReload`/`RemoveMag` → `InsertMagAnim`).
- Бэкап префаба и хэши: `Weapon_ARMA_X/artifacts/MP133_Lab/prefab_backups/`
  (OFF-хэш `3A0749E5…F8766D`, ON-хэш `67E3D0FC…1099`). Откат: убрать/поставить 0
  строку `m_bLabInsertEnabled 1`.
- Порядок игрового теста и STOP-условия: `reports/MP133_ANIMATION_LAB_V23_R_TEST_RU.md`.
- Runtime — **OWNER TEST REQUIRED**, не PASS.

## 0.00 V2.3 (issue #27 owner regression) — регрессия остановлена; per-shell insert BLOCKED

**Игровой лог владельца после V2.2 (comment #5956970464):**
- Gate A и физический 3-зарядный лаб-магазин работают: `STATE labWeapon=1 cap=3 tube=2/3`.
- Регрессия: `reloadType=1` (помпа) открывал окно и сразу закрывал; `reloadType=5`
  (ванильная перезарядка магазина) заставлял **оригинальные** клипы отыграть
  `Weapon_MagRelease/DetachMagazine/DespawnMagazine/SpawnMagazine/AttachMagazine`
  и заменить реальную трубу 3 на стоковый магазин `10/10`; после закрытия
  серверного окна клиент продолжал пульсировать команду 7 → **бесконечная
  перезарядка**. `SERVER Insert COMMIT` не наблюдался.

**V2.3 (только код):**
- **Авто-триггер отключён:** ванильные типы перезарядки (1..6) больше не
  открывают лаб-окно (пишется `auto-trigger disabled`). Это останавливает и
  бесконечный цикл, и ванильную замену магазина.
- **Commit только по lab-событию** `ARMST_Lab_Shell_Commit`; `Weapon_AttachMagazine`
  исключён из триггеров коммита (это событие ванильной замены магазина).
- **Идемпотентное закрытие окна** `LabServerEndInsert(notifyOwner)`; терминальные
  ветки уведомляют владельца через `RpcDo_LabCeaseInsert` → нет «залипшего»
  `clientInsert=1`.
- **Watchdog** `LAB_CLIENT_MAX_TICKS` (~18 с) → нет бесконечного цикла.
- Lookup-фикс V2.2 (через сущность) сохранён. Тесты: **12/12 PASS**
  (добавлены `check_v23_safety`, `check_r_hook`).
- **Подготовлен R-хук** (существующий механизм модов):
  `Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_CommandHandler.c` —
  lab-gated `modded HandleWeaponReloading`, `return true` для лаб-оружия, иначе
  `super`; включается гейтом `ARMST_MP133_Lab_Component.m_bLabInsertEnabled`
  (off до подключения санитизированных ANM).

**BLOCKED (точно, по #27 §2/§6):**
- Настоящая per-shell досылка **невозможна с оригинальными inject-клипами**: они
  несут `Weapon_SpawnMagazine/AttachMagazine/MagRelease`, и движок выполняет
  реальную замену всего магазина. Lab-only санитизированные источники есть
  (`LabClips/W_MP133_Lab_Inject.txa`, `P_MP133_Lab_Inject.txa`), но они **не
  скомпилированы в .anm** — это требует импорта в Animation Editor Workbench,
  который агенту запускать запрещено.
- Подавление нативной перезарядки для лаб-оружия требует проверенного
  engine-хука/точного action-имени; без Workbench/игры это недоказуемо.
- Точные следующие данные: (a) GUID-ы скомпилированных lab-only ANM после импорта
  TXA владельцем; (b) подтверждение хука, надёжно подавляющего ванильную
  перезарядку/замену магазина для лаб-оружия.
- До этого лаборатория в **безопасном** состоянии: без авто-триггера, без
  вызванной лабой замены магазина, без фантомных патронов.

## 0.0 V2.2 (issue #27) — реальная труба на 3, фикс lookup, STATE

**Данные из игрового прогона владельца (issue #27):**
- оружие = lab MP-133, `labComp=1`, `capacity=3`, но `STATE` отсутствует и поток
  досылки не запускался: `GetCurrentWeaponLab()` использовал
  `wpn.FindComponent(...)`, который возвращает **null**, тогда как
  `e.FindComponent(...)` (сущность) находит компонент.
- физический магазин = `MaxAmmo 10` (9/10…0/10): `m_iTubeCapacityOverride`/
  `m_MaxMagazineAmmo=3` ограничивали только лаб-логику, не физическую трубу.

**Исправления V2.2:**
- `LabCompOf(wpn)` — поиск маркера через **сущность**
  (`wpn.GetOwner().FindComponent(...)`), как везде в Core; применён во всех
  проверках/коммите. Это возвращает `STATE` и весь путь досылки.
- **Новый lab-only магазин**
  `{CC71464F7CA58F57}Prefabs/Weapons/MP133_Lab/armst_12ga_Lab_3rnd.et`
  (наследует боевой 12ga-магазин, `MaxAmmo 3`, `AmmoMapping { 0 0 0 }`,
  имя `12g 3rnd [LAB]`). Оба лаб-префаба переопределяют
  `MuzzleComponent.MagazineTemplate` на него → физическая ёмкость трубы 3.
- префабы сохраняют `m_iTubeCapacityOverride 3` и
  `ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo 3`; при физическом магазине на 3
  Core-трим становится no-op.
- ПРИМЕЧАНИЕ: локальный non-RIS префаб был перезаписан Workbench-сохранением
  (`ARMST_SHOTGUN_COMPONENTS { Enabled 0 }`); правка заново применена **без**
  `Enabled` (компонент Core должен оставаться активным), координаты размещения
  владельца сохранены.

**Статически:** валидатор PASSED; **10/10** unit-тестов (добавлены проверки
lab-магазина и ёмкости). Компиляция/игра: **NOT RUN / OWNER TEST REQUIRED**.

**Неизвестно:** прикрепляет ли движок/лоадаут `MagazineTemplate`-магазин при
спавне (чтобы труба читалась 3/3) и детектируется ли R.

## 0. TL;DR для следующей модели

- Экспериментальный аддон `ARMST_MP133_AnimationLab` собран и **успешно
  компилируется** в текущем Workbench (engine 192142). Лабораторный
  `ScriptComponent` и модифицированный `SCR_CharacterControllerComponent`
  загружаются и выполняются (есть логи `component attached` и
  `character component init`, см. §6).
- **Но ни разу** не сработала цепочка «нажатие R → досылка»: во всех логах за
  день 0 строк `STATE labWeapon=1`, 0 `reload request detected`, 0
  `Insert COMMIT`. Вывод: во время тестов **в руках не было лабораторного
  оружия** (либо `GetCurrentWeaponLab()` не находит компонент — это надо
  различить, см. §8.1).
- Самая вероятная причина «не работает» в том виде, как это видел владелец
  («один магазин на 30 патронов, 30 выстрелов») — **тестировалось обычное
  оружие** (автомат с магазином на 30), а не лабораторный MP-133 (у него
  ёмкость трубы = 2). Логи это подтверждают косвенно.
- Главные технические неопределённости для следующей модели: (1) корректный
  перехват ванильной перезарядки по R; (2) доходят ли анимационные события
  `Weapon_AttachMagazine`/кастомные до сервера; (3) семантика удержания
  `CMD_Weapon_Reload==7`. См. §8–§9.

---

## 0.1 V2 (issue #26) — изменения этой сессии

- **Gate A (идентичность оружия):** добавлен безусловный rate-limited (1 Гц) лог
  ТЕКУЩЕГО оружия, даже если lab-компонент не найден:
  `WEAPON wm=… wpn=… ent=… prefab=… labComp=… tube=…/… reloadType=… startReloading=… raised=… isReloading=…`.
  Плюс `STATE …` когда lab-оружие в руках. Это однозначно решает
  «лаб-оружие экипировано?» vs «lookup не находит компонент».
- **Gate C (идемпотентность):** вместо таймера-500-мс как единственной гарантии
  введено состояние цикла: окно `armed` при открытии и повторно после
  завершения клипа (`BlendOut`); успешный коммит снимает `armed`. Дубликат
  кадра 43 без завершения клипа не коммитит; cooldown оставлен как вторичная
  защита. Лог `armed=…` в `STATE` и `SERVER commit ignored: cycle not armed`.
- **Gate B (R):** трассировка усилена (`watcher`/`OnApplyControls` +
  `WEAPON`-лог). Сам перехват R остаётся runtime-проверяемым: по новым логам
  видно, отражают ли `WeaponIsStartReloading()/GetWeaponReloadType()` нажатие.
- **Метки:** `MP-133 [LAB]` / `MP-133 RIS [LAB]` (отличимо в инвентаре/редакторе).
- **Валидатор/тесты:** добавлена проверка отсутствия world/layer/`.ent`
  (`check_no_world`), теперь **8/8 PASS**.
- **Вывод:** `FindComponent` на компоненте валиден (Core: `item.FindComponent(…)`,
  `Print(… + GetPrefabName())`). Вероятная причина отсутствия `STATE` — lab-оружие
  **не было экипировано**; это подтвердится первым же логом `WEAPON`.
- **Статус:** `READY_FOR_OWNER_GAME_TEST` при чистой компиляции; игровые
  критерии — `UNVERIFIED`.
- Мир/`Weapons`/`Core` не менялись; lab-аддон — локальный, без remote.

## 0.2 V2.1 — лаб-ёмкость трубы = 3 (owner override #26)

- Оба лаб-префаба теперь задают `ARMST_MP133_Lab_Component.m_iTubeCapacityOverride 3`.
- **Конфликт с Core:** `ARMST-PLATFORM---Core` `WeaponHandler` (через
  `SCR_WeaponInfo.OnAmmoCountChanged`) режет текущий магазин до
  `ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo` (по умолчанию 2) и спавнит
  «излишек». Чтобы это не обрезало трубу обратно до 2, **в обоих лаб-префабах
  переопределён унаследованный компонент**
  `ARMST_SHOTGUN_COMPONENTS "{69E4C57F6C1EE3A6}" { m_MaxMagazineAmmo 3 }`.
  Это строго lab-scoped правка (только эти префабы), Core/Weapons/vanilla не
  меняются, обычные дробовики (2) не затрагиваются.
- Лабораторная логика читает `GetEffectiveTubeCapacity()` → `m_iTubeCapacityOverride`
  (3), Core-трим согласован (3). При ровно 3 патронах Core-трим не создаёт
  сохраняющийся лишний магазин (excess=0 → новый магазин с 0 аммо удаляется).
- Валидатор/тесты: добавлена `check_capacity3` (оба префаба: override 3 +
  `m_MaxMagazineAmmo 3`), теперь **9/9 PASS**.
- Рантайм-энфорсмент ёмкости (загрузка 3, третий insert, отклонение четвёртого,
  отсутствие лишних магазинов/потерь, независимость ствола, отсутствие
  двойного списания) — **OWNER TEST REQUIRED**, без запуска игры агентом.

## 1. Цель и жёсткие ограничения (Issue #25)

Цель: изолированный экспериментальный аддон, полностью подключённый, с
per-shell досылкой в трубчатый магазин MP-133, помпой и тестовыми префабами;
владелец должен только запустить и проверить. Нельзя: менять боевой мод
`ARMST-PLATFORM---Weapons`, Core, ванильные ассеты, оригинальные `.agf`/клипы/
`.meta`/GUID, незакоммиченные правки пользователя; глобальные оверрайды,
влияющие на все дробовики. Всё новое — в одном новом аддоне. Не выдумывать API
Enfusion. Не объявлять игровой PASS без фактического подтверждения.

---

## 2. Расположение и границы

| Что | Путь |
|---|---|
| Новый экспериментальный аддон | `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMST_MP133_AnimationLab\` |
| Боевой аддон (только чтение) | `...\addons\ARMST-PLATFORM---Weapons\` |
| Core (только чтение) | `...\addons\ARMST-PLATFORM---Core\` |
| Репозиторий инструментов/отчётов | `...\addons\Weapon_ARMA_X\` |
| Workbench | `C:\Program Files (x86)\Steam\steamapps\common\Arma Reforger Tools\Workbench\ArmaReforgerWorkbenchSteamDiag.exe` |
| Логи Workbench | `...\ArmaReforgerWorkbench\logs\logs_<ts>\{console,script,error}.log` |
| Логи игры | `C:\Users\yshky\Documents\My Games\ArmaReforger\logs\logs_<ts>\` |

Важно: в этой среде **нет git и нет standalone Python**. Python-скрипты
репозитория запускались встроенным Python из Rizom/Blender. Workbench запускать
нельзя без явного разрешения владельца (он просил не запускать; в текущей сессии
не запускался).

---

## 3. Состав аддона (все новые файлы)

```
ARMST_MP133_AnimationLab/
  addon.gproj                              ID ARMSTMP133AnimationLab, GUID {1187677F04E33069}
  README.md
  Scripts/Game/ARMST_MP133_Lab/
    ARMST_MP133_Lab_Component.c            компонент на оружии (маркер/конфиг/резерв)
    ARMST_MP133_Lab_Character.c            modded SCR_CharacterControllerComponent: триггер R, коммит, диагностика
  Assets/Weapons_RUS/Mp_133/Workspace/
    MP133_Lab.ast / .agr / .agf / .aw      копии графового стека (новые GUID)
    MP133_Lab_weapon.asi / MP133_Lab_player.asi
    LabClips/W_MP133_Lab_Inject.txa
    LabClips/P_MP133_Lab_Inject.txa        санитизированные источники клипов (опционально)
  Prefabs/Weapons/MP133_Lab/
    armst_Shotgun_mp_133_Lab.et
    armst_Shotgun_mp_133_Ris_Lab.et
```

> OWNER OVERRIDE issue #25: аддон **не содержит мира/`.ent`/`.layer`/сценария/
> спавна**. Ранее созданный в этой сессии `Worlds/MP133_Lab` **удалён** как
> недопустимый; владелец сам ставит префаб в свой мир.

Зависимости `addon.gproj`: `58D0FB3206B6F859` (vanilla), `69E4C3542B6CDC19`
(Core), `6A70E400C54051DC` (Weapons).

### GUID-карта новых ресурсов

| Ресурс | GUID |
|---|---|
| MP133_Lab.agr | `{F23E6BC494967D16}` |
| MP133_Lab.agf | `{1EB8E2249801B1E3}` |
| MP133_Lab.ast | `{138604905EC95210}` |
| MP133_Lab.aw | `{EA8670F3600F156D}` |
| MP133_Lab_weapon.asi | `{DE3BB4522642DDE0}` |
| MP133_Lab_player.asi | `{B51A94B5A27E09B4}` |
| armst_Shotgun_mp_133_Lab.et | `{FC1935AF936F63E5}` |
| armst_Shotgun_mp_133_Ris_Lab.et | `{4B288C21B7125D50}` |
| instance id компонента | `{21B3393B3149815A}` |
| entity id lab / ris | `{77AB6DD3F7C4DF4D}` / `{4293C409C16270F8}` |

Родители префабов (боевые): `{63FF6FDCA4E7E735}` armst_Shotgun_mp_133.et и
`{9F8CA2FE5A3540DC}` armst_Shotgun_mp_133_Ris.et. Оригинальные клипы/модели
переиспользуются по своим GUID (см. `MP133_ANIMATION_LAB_V1.md` §2).

### Граф: что изменено

`MP133_Lab.agf` = побайтовая копия оригинального `MP133.agf` (включая
незакоммиченный прототип владельца `InsertSingleProjectile` для
`CMD_Weapon_Reload == 7`) **плюс один переход** внутри `WeaponReloadSTM`:

```
InsertSingleProjectile -> InsertSingleProjectile
Condition "IsEvent(\"BlendOut\") && GetCommandI(CMD_Weapon_Reload) == 7"
PostEval 1, BlendFn S, Duration 0.25
```

Смысл: пока геймплей держит тип 7, клип вставки циклится (один цикл = один
патрон); при сбросе типа штатный выход `Reload -> Buffer4 -> Idle` завершает
перезарядку. Строки `Fire/Idle/Trigger/Safety/Sight/Bolt/...` не тронуты.

---

## 4. Архитектура gameplay-логики

Источник истины:
| Состояние | Владелец | Пишет |
|---|---|---|
| Труба | `BaseMagazineComponent` (движок) | коммит лабы (`SetAmmoCount`, только master) + выстрел движка |
| Резерв | `ARMST_MP133_Lab_Component.m_iLabReserveShells` | коммит лабы (только сервер) |
| Ствол | `BaseMuzzleComponent` (движок, чтение) | движок |
| Помпа | существующий Core-обработчик `Weapon_Rack_Bolt` | 1 списание трубы на событие (не дублируется лабой) |

Поток досылки (текущая реализация v2):
1. Клиент-владелец: сторож (`LabWatchTick`, 100 мс) и/или `OnApplyControls`
   читают `CharacterInputContext` и считают запрос перезарядки
   (`WeaponIsStartReloading()` / изменение `GetWeaponReloadType()`).
   При лабораторном оружии → `LabBeginInsert()`.
2. `LabBeginInsert`: локальная предпроверка (`LabClientCanInsert`: труба есть и
   не полна), затем `Rpc(RpcAsk_LabBeginInsert)` и пульс 60 мс, который держит
   `inputCtx.SetReloadWeapon(7)` (тот же механизм, что Core использует для
   помпы: `SetReloadWeapon(1)`).
3. Сервер: `RpcAsk_LabBeginInsert` → `LabServerCanInsert` (труба есть, не полна,
   резерв>0) → открывает окно или отвечает `RpcDo_LabCeaseInsert`.
4. Сервер по событию `ARMST_Lab_Shell_Commit` ИЛИ `Weapon_AttachMagazine`:
   `LabServerCommitInsert` — ровно один раз за цикл (валидации + cooldown
   500 мс): `reserve--`, `tube.SetAmmoCount(current+1)`.
5. Стоп: труба полна / резерв пуст / опустил оружие / смена оружия / помпа →
   клиент сбрасывает `SetReloadWeapon(0)`.

RPC: `RpcAsk_LabBeginInsert/RpcAsk_LabEndInsert` (`RplRcver.Server`),
`RpcDo_LabCeaseInsert` (`RplRcver.Owner`). Паттерны — как в Core.

---

## 5. История правок и ошибок компиляции (хронология)

1. **v1**: триггер досылки — отдельное входное действие `ARMST_MP133_LAB_INSERT`
   (клавиша H) через `Configs/System/chimeraInputCommon.conf` (слияние с
   Core-конфигом). Результат владельца: «скрипт не отрабатывает совсем» →
   гипотеза: действие не попало в активный input-контекст, `AddActionListener`
   молча не срабатывал. Конфиг ввода **удалён**.
2. **v2**: триггер переведён на **R** — перехват запроса перезарядки в
   `OnApplyControls` + независимый сторож-таймер 100 мс; досылка через
   `inputCtx.SetReloadWeapon(7)`. Добавлена диагностика.
3. Ошибки компиляции, найденные Workbench и исправленные:
   - `UIWidgets.Toggle` не существует → `UIWidgets.CheckBox` (булев виджет;
     прецедент — Core).
   - `(lab ? a : b)` — **тернарный оператор с условием-ссылкой на класс не
     парсится**: `Broken expression (missing ';'?)`, `Invalid statement ':'` +
     каскад на строках 20/21. Заменено на явные `if/else`.
   - Убраны конструкции без прецедента в проекте: `static const` на
     `ScriptComponent`, `array<AnimationEventID>`, `(int)`-каст
     `TAnimGraphCommand`, `override void OnDelete`, ссылка-класс в `||` без
     явного `!= null`. Все значения команд — instance-`protected const`
     (как `protected const float TAO_*` в Core).
4. Диагностика сделана **безусловной** (аддон экспериментальный): маркеры
   `[ARMST_MP133_LAB]` и `[ARMST_MP133_LAB-DIAG]`, баннер, 1 Гц `STATE`,
   логирование всех известных анимационных событий, всех шагов досылки.

Неудачные/откатанные изменения: временно добавлялось/удалялось входное действие
H; мир сначала был под-сценой `weapon_test` (подмешивался боевой арсенал) —
переделан на ванильный `Autotest_GameMode_Plain`.

---

## 6. Фактические данные из Workbench-логов (доказательства)

Файл: `...\logs\logs_2026-10-02_17-54-32\console.log` (и `script.log`).

Сначала (до фикса тернарника) в этом же логе:
```
17:54:43.438 SCRIPT (E): @"scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c,144": Broken expression (missing ';'?)
17:54:43.438 SCRIPT (E): ... ,144: Invalid statement ':'
17:54:43.440 SCRIPT (E): Can't compile "Game" script module!
```

После пересборки (код скомпилировался и выполнился):
```
17:57:03.088 SCRIPT : [ARMST_MP133_LAB] ==================== ARMST MP133 LAB component active ====================
17:57:03.088 SCRIPT : [ARMST_MP133_LAB] component attached; capacity=2 reserve=30
17:57:10.440 SCRIPT : [ARMST_MP133_LAB-DIAG] character component init: anim=1 cmdBound=1 isServer=1
17:57:10.945 SCRIPT : [ARMST_MP133_LAB-DIAG] OnControlledByPlayer controlled=1 local=1
17:57:10.945 SCRIPT : [ARMST_MP133_LAB-DIAG] watcher started
```

Сводка по ВСЕМ логам за 2026-10-02 (все сессии):
```
STATE labWeapon           = 0
reload request detected   = 0
begin insert loop         = 0
Insert COMMIT             = 0
begin skipped             = 0
component attached        > 0 (десятки; оружие спавнится)
```
Интерпретация: скрипт жив (`capacity=2`, `anim=1`, `cmdBound=1`, `isServer=1`,
`watcher started`), но **ни один цикл досылки не выполнялся**. `STATE` пишется
раз в секунду только когда `GetCurrentWeaponLab()` != null, т.е. в руках
лабораторное оружие. Ноль `STATE` ⇒ в контролируемых прогонах лабораторное
оружие текущим не было.

Также ранее владелец сообщал: «считается как один магазин на 30 патронов, и
выстрелов 30» — это поведение обычного магазинного оружия (не лаб-дробовика с
трубой на 2), что согласуется с гипотезой «тестировалось не то оружие».

---

## 7. Что проверено и что нет

**Проверено (факты):**
- Компиляция модуля Game в Workbench (после фикса тернарника) — PASS (лог §6).
- Класс `ARMST_MP133_Lab_Component` виден в World Editor на префабе (владелец
  прислал скриншот: компонент + `ARMST_SHOTGUN_COMPONENTS` на сущности).
- Компонент и modded-класс инициализируются и логируют; `capacity=2 reserve=30`.
- Статический валидатор и 7 unit-тестов (`agent/scripts/validate_mp133_lab.py`,
  `agent/tests/test_mp133_lab_validation.py`) — PASS (структура/GUID/строки
  `.asi`↔`.ast`/проводка префабов/наличие insert-loop перехода).

**НЕ проверено (требует игру/Workbench Play):**
- Факт срабатывания перехвата R и вообще попадание лабораторного оружия в руки.
- Работа графа (`CMD_Weapon_Reload==7`, self-loop, выход).
- Доставка анимационных событий на сервер и коммит «ровно одного» патрона.
- Поведение помпы/выстрела/прерываний/сети.
- Инертность `Weapon_SpawnMagazine/_MagRelease` при досылке.
- Ёмкость 2 в бою, отсутствие ванильного mag-swap при R.

---

## 8. Главные открытые вопросы/блокеры

### 8.1 Почему не запустилась досылка (первоочередное)
Логи не различают два случая:
(а) владелец не экипировал лабораторное оружие (вероятнее всего);
(б) `GetCurrentWeaponLab()` не находит компонент даже с оружием в руках.
**Что сделать первым делом:** добавить безусловный лог текущего оружия (любого)
в `LabHeartbeatTick` — напр. имя класса/префаба текущего weapon-manager
(`GetWeaponManagerComponent().GetCurrentWeapon()` + owner prefab name) — чтобы
увидеть, ЧТО в руках, даже если это не лаб-оружие. Это снимет неоднозначность
за один прогон.

### 8.2 Корректный перехват ванильного R
Механизм `WeaponIsStartReloading()/GetWeaponReloadType()` (через
`CharacterInputContext`) **не подтверждён** — возможно, эти флаги не отражают
нажатие R на этой ревизии движка, либо ванильный mag-swap уже стартует в
той же кадре. Варианты для следующей модели (по возрастанию риска):
1. Определить точное имя ванильного action перезарядки и либо
   `AddActionListener` на него, либо отключать его для лаб-оружия через
   `ActionManager`; имя можно извлечь из ванильной input-конфигурации
   (`data.pak`) / Resource Browser / настроек клавиш владельца.
2. Оверрайд `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading(...)`:
   для лаб-оружия вернуть `true` (взять обработку на себя), оставив ванили
   только анимацию через `SetReloadWeapon(7)`.
3. Оверрайд `OnApplyControls` «до super» для подавления ванильного запроса
   (нужно проверить порядок заполнения input-контекста).
4. Если ванильный mag-swap неизбежен — сделать досылку через отдельную команду
   и валидировать аммо только на сервере (текущая архитектура это уже умеет),
   но убрать визуальный ущерб.

### 8.3 Анимационные события и семантика команд
- Доходят ли `Weapon_AttachMagazine` / `ARMST_Lab_Shell_Commit` до **сервера**
  (Core доказывает это только для `Weapon_Rack_Bolt`).
- Латчится ли `GetCommandI(CMD_Weapon_Reload)` при `SetReloadWeapon(7)` и
  приводит ли к self-loop. Диагностика выведет все `anim event '...'` — по ним
  это будет видно.
- Оригинальные Inject-клипы несут `Weapon_SpawnMagazine(10)`,
  `Weapon_AttachMagazine(43)`, `Weapon_MagRelease(64)`, `BlendOut(100)`.
  Для санитизации есть `LabClips/*_Lab_Inject.txa` (события переименованы в
  `ARMST_Lab_Shell_*`, движение идентично); их нужно один раз импортировать в
  Animation Editor, затем переключить строки `Reload_InsertMag` в `.asi`.

### 8.4 Ёмкость и резерв
- Действующее правило ARMST: `ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo`
  по умолчанию **2** (объявленный `MaxAmmo 10` трубы перекрывается
  существующим `WeaponHandler`-костылём Core, который режет магазин и спавнит
  лишнее). Лаба читает это правило (`GetEffectiveTubeCapacity`), подтверждено
  логом `capacity=2`.
- Резерв — виртуальный счётчик (30), не инвентарные патроны. Замена на
  инвентарный источник — отдельная задача.

---

## 9. Рекомендованный план для следующей модели (пошагово)

1. **Детерминированный тест.** Сделать так, чтобы лаб-оружие гарантированно
   было в руках: владелец ставит лабораторный префаб в **свой** мир
   (loadout/размещение) — аддон мира не содержит. Плюс
   безусловный лог текущего оружия (см. §8.1).
2. Снять 3 лога: (a) сразу после Play, (b) с лаб-оружием в руках (ожидаем
   `STATE labWeapon=1`), (c) после нажатия R. По (c) понять, срабатывает ли
   `reload request detected`.
3. Если флаги R не отражают нажатие — реализовать перехват через имя
   ванильного action или `HandleWeaponReloading` (§8.2).
4. Убедиться, что граф уходит в `InsertSingleProjectile` и что `anim event
   'Weapon_AttachMagazine'` приходит на сервер; проверить `Insert COMMIT`.
5. Проверить негативные кейсы: полная труба, резерв 0, прерывание, помпа
   (LSHIFT+R), отсутствие ванильного mag-swap при R.
6. Только после этого — санитизация клипов (§8.3) и перенос модели в прод
   (отдельная задача).

Полезно: перед экспериментами перечитать `reports/MP133_ANIMATION_LAB_V1.md`
(дизайн, риски, критика прод-костыля) и `docs/sync/CURRENT_AI_SYNC.md`.

---

## 10. Критика прод-«костыля» (контекст, зачем вообще лаба)

Текущий прод-код (`ARMST-PLATFORM---Core/Scripts/Game/Items/ARMST_WEAPONS_HANDLER.c`):
- в счётчик трубы пишут 5 разных мест: движок (выстрел), Core-помпа
  (`TAO_DecrementAmmoOnRack`), ванильный mag-swap, и `WeaponHandler` (вызывается
  на КАЖДОЕ изменение патронов), который режет трубу до `m_MaxMagazineAmmo` (2)
  и **спавнит лишний магазин** в мир/инвентарь → гонки, дубли, мусор;
- ёмкость enforced «резанием», а не логикой вставки;
- per-shell перезарядки нет (только ванильная замена трубчатого магазина);
- помпа требует клиентского флага «pending», иначе списание пропускается.

Целевая модель (реализована в лабе): один владелец на каждое состояние,
ёмкость ограничивается в точке вставки (валидация + debounce), граф — только
движение.

---

## 11. Как запускать/собирать (для контекста)

- Открыть проект: Workbench → Game Project Manager → Add Existing →
  `...\addons\ARMST_MP133_AnimationLab\addon.gproj`.
- Пересобрать скрипты; смотреть `logs\<свежий>\script.log` на `SCRIPT (E)`.
- Разместить лабораторный префаб в своём мире (аддон мира не содержит):
  `{FC1935AF936F63E5}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`
  или `{4B288C21B7125D50}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et`
  → запустить сцену. Примечание: аддон не создаёт/не меняет мир/слой.
- Фильтр лога:
  `Select-String -Path "...\logs\<ts>\console.log" -Pattern "ARMST_MP133_LAB"`.
- Ожидаемые маркеры: см. §6 и `reports/MP133_ANIMATION_LAB_V1_TEST_CHECKLIST_RU.md` §6.

---

## 12. Ассеты репозитория (что уже лежит)

- `reports/MP133_ANIMATION_LAB_V1.md` — полный отчёт реализации (дизайн, GUID,
  риски, критика прод-костыля).
- `reports/MP133_ANIMATION_LAB_V1_TEST_CHECKLIST_RU.md` — RU-чек-лист + раздел
  диагностики.
- `agent/scripts/validate_mp133_lab.py` + `agent/tests/test_mp133_lab_validation.py`
  — детерминированная статическая проверка (7 тестов).
- `artifacts/MP133_Lab/original_consumed_hashes.txt` — SHA-256 16 исходных
  файлов (доказательство неизменности оригинала).
- `artifacts/MP133_Lab/session_validation_notes.txt` — заметки сессии.
- Хэш оригинального незакоммиченного `MP133.agf`:
  `5E8476D0977FFABE17BC9D848B249F81608FC08E6C3DA1E7A381D9A0B4B2468A`.

---

## 13. Чёткое разделение: факт / гипотеза / неизвестно

| Утверждение | Статус |
|---|---|
| Аддон компилируется в Workbench (после фикса тернарника) | **ФАКТ** (лог §6) |
| Компонент и modded-класс инициализируются, `capacity=2` | **ФАКТ** (лог §6) |
| Оригинальные MP-133/Core файлы не изменены | **ФАКТ** (SHA-256) |
| Досылка по R когда-либо выполнялась | **ОПРОВЕРГНУТО логами** (0 STATE/COMMIT) |
| «Не работает» = не то оружие в руках | **ГИПОТЕЗА** (сильная; нужен прогон с лаб-оружием) |
| `WeaponIsStartReloading/GetWeaponReloadType` отражают R | **НЕИЗВЕСТНО** |
| События доходят до сервера, команда 7 латчится | **НЕИЗВЕСТНО** |
| Санитизированные клипы компилируются | **НЕИЗВЕСТНО** (TXA не импортировались) |

---

## 14. Самый короткий путь к результату (если у следующей модели мало времени)

1. В `LabHeartbeatTick` убрать ранний выход и логировать **текущее оружие** и
   его компоненты безусловно — один прогон покажет, что в руках.
2. Обеспечить, чтобы в руки попадал именно `armst_Shotgun_mp_133_Lab.et`
   (loadout/spawner).
3. Прогнать R и посмотреть `STATE` → `reload request detected` → `begin …`.
4. Если R не детектится — сделать перехват через точное ванильное action-имя
   или `HandleWeaponReloading`.

Этого достаточно, чтобы либо получить рабочий лабораторный цикл, либо точно
локализовать блокер (перехват R / доставка событий / семантика команд).

---

# ПРИЛОЖЕНИЕ — исходники (на момент отчёта)


## A. Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Component.c

```
// ============================================================================
// ARMST_MP133_AnimationLab - weapon-side lab component
// ----------------------------------------------------------------------------
// This component is attached ONLY to the lab test prefabs
// (armst_Shotgun_mp_133_Lab.et / armst_Shotgun_mp_133_Ris_Lab.et).
// Production MP-133 prefabs do not carry it, therefore no production weapon
// or character behavior is changed by this addon.
//
// Responsibilities:
//   - Marker that identifies "opt-in experimental" lab weapons for the
//     lab-guarded character controller (ARMST_MP133_Lab_Character.c).
//   - Lab-only configuration: tube capacity policy and the virtual shell
//     reserve counter used as the "reserve ammo" source for deterministic
//     tests (a future inventory loose-shell source can replace it).
//   - Diagnostics flag for lab-only logging.
//
// The tube itself (BaseMagazineComponent) and the chamber (BaseMuzzleComponent)
// belong to the vanilla engine. All ammo TRANSACTIONS of the lab reload flow
// are committed by the lab character controller (server only). The graph only
// decides motion; it never grants ammunition.
// ============================================================================

class ARMST_MP133_Lab_ComponentClass : ScriptComponentClass
{
};

[BaseContainerProps()]
class ARMST_MP133_Lab_Component : ScriptComponent
{
	// Tube capacity policy:
	//  0 = follow the existing ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo rule
	//      (effective default on the MP-133 chain is 2)
	//  >0 = lab-only override for experiments (visible in prefab properties).
	[Attribute("0", UIWidgets.Slider, "Tube capacity override (0 = ARMST rule)", "0 20 1")]
	int m_iTubeCapacityOverride;

	// Virtual shell reserve used by the lab reload loop (server-authoritative).
	[Attribute("30", UIWidgets.Slider, "Lab virtual reserve shells", "0 200 1")]
	int m_iLabReserveShells;

	// Lab-only diagnostic logging (off by default; never leaks to production).
	[Attribute("false", UIWidgets.CheckBox, "Lab debug logging")]
	bool m_bLabDebugLog;

	// Cached owner (entity carrying this component).
	protected IEntity m_owner;

	// ------------------------------------------------------------------
	override void OnPostInit(IEntity owner)
	{
		super.OnPostInit(owner);
		m_owner = owner;
		// Unconditional lab marker (proves the lab script + component are live
		// on this weapon). Grep marker: [ARMST_MP133_LAB]
		LabLog("==================== ARMST MP133 LAB component active ====================");
		LabLog("component attached; capacity=" + GetEffectiveTubeCapacity().ToString()
			+ " reserve=" + m_iLabReserveShells.ToString());
	}

	// ------------------------------------------------------------------
	// Effective tube capacity for the insertion loop.
	// Returns the capacity the reload loop may fill the tube to.
	// 0 = unresolvable (caller treats as "cannot insert").
	// ------------------------------------------------------------------
	int GetEffectiveTubeCapacity()
	{
		if (m_iTubeCapacityOverride > 0)
			return m_iTubeCapacityOverride;

		if (!m_owner)
			return 0;

		ARMST_SHOTGUN_COMPONENTS shotgun = ARMST_SHOTGUN_COMPONENTS.Cast(m_owner.FindComponent(ARMST_SHOTGUN_COMPONENTS));
		if (shotgun && shotgun.m_MaxMagazineAmmo > 0)
			return shotgun.m_MaxMagazineAmmo;

		return 0;
	}

	int GetReserve()
	{
		return m_iLabReserveShells;
	}

	// Server-owned transaction: consume exactly one reserve shell.
	// Returns the new reserve count (>= 0).
	int ConsumeReserveShell()
	{
		if (m_iLabReserveShells > 0)
			m_iLabReserveShells--;

		return m_iLabReserveShells;
	}

	void LabLog(string msg)
	{
		// Lab-only component, so logging is safe to keep unconditional. The
		// m_bLabDebugLog attribute is retained for verbose extras if needed.
		Print("[ARMST_MP133_LAB] " + msg, LogLevel.NORMAL);
	}
}
```

## B. Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c

```
// ============================================================================
// ARMST_MP133_AnimationLab - character-side lab flow + diagnostics
// ----------------------------------------------------------------------------
// Lab-guarded modded class. Every code path first checks that the controlled
// weapon carries ARMST_MP133_Lab_Component. Without it nothing runs and both
// vanilla behavior and the existing Core ARMST rack handler are untouched.
//
// DIAGNOSTICS (this build logs unconditionally; the lab addon is experimental
// and only ever acts on lab weapons):
//   * startup banner + character component init state;
//   * a 1 Hz STATE snapshot while a lab weapon is equipped (capacity, tube,
//     chamber, reserve, reload flags, insert flags, vanilla reload type);
//   * EVERY known weapon animation event with intParam and time, so the exact
//     event that fires (or does not) during a test is visible;
//   * every step of the insert flow: watcher detection, begin/skip reasons,
//     server window open/close, commit/reject, stop reasons.
// Grep markers: [ARMST_MP133_LAB]  and  [ARMST_MP133_LAB-DIAG]
// ============================================================================

modded class SCR_CharacterControllerComponent
{
	// CMD_Weapon_Reload values shared with the lab graph.
	protected const int LAB_NO_RELOAD  = 0;   // clear / idle
	protected const int LAB_RACK_CMD   = 1;   // pump (Core ARMST sends this)
	protected const int LAB_INSERT_CMD = 7;   // single-shell insert cycle

	protected const int LAB_CLIENT_PULSE_MS = 60;
	protected const int LAB_COMMIT_COOLDOWN_MS = 500;
	protected const int LAB_CLIENT_WATCH_MS = 100;
	protected const int LAB_HEARTBEAT_MS = 1000;

	// ---- local (owner client) state ----
	protected bool m_bLabClientInsertActive;
	protected bool m_bLabClientPulseActive;
	protected bool m_bLabWatchActive;
	protected bool m_bLabHeartbeatActive;
	protected int m_iLabLastReloadType = 0;
	protected IEntity m_labOwner;
	protected SCR_CharacterAnimationComponent m_labCharacterAnim;
	protected TAnimGraphCommand m_labCmdReload = -1;

	// ---- server-authoritative state ----
	protected bool m_bLabServerInsertActive;
	protected bool m_bLabServerCommitCooldown;

	// ---- animation events (logic) ----
	protected AnimationEventID m_evtLabShellCommit;
	protected AnimationEventID m_evtWeaponAttachMag;
	protected AnimationEventID m_evtWeaponRackBolt;

	// ---- diagnostics: registered known event ids ----
	protected AnimationEventID m_evtBlendIn;
	protected AnimationEventID m_evtBlendOut;
	protected AnimationEventID m_evtEnableFire;
	protected AnimationEventID m_evtSpawnMagazine;
	protected AnimationEventID m_evtMagRelease;
	protected AnimationEventID m_evtDetachMagazine;
	protected AnimationEventID m_evtDespawnMagazine;
	protected AnimationEventID m_evtLabShellSpawn;
	protected AnimationEventID m_evtLabShellRelease;

	// ========================================================================
	override void OnInit(IEntity owner)
	{
		super.OnInit(owner);
		m_labOwner = owner;

		m_labCharacterAnim = SCR_CharacterAnimationComponent.Cast(GetAnimationComponent());
		if (m_labCharacterAnim)
			m_labCmdReload = m_labCharacterAnim.BindCommand("CMD_Weapon_Reload");

		LabRegisterKnownEvents();

		ScriptInvoker onAnim = GetOnAnimationEvent();
		if (onAnim)
			onAnim.Insert(OnLabAnimationEvent);

		LabDiag("character component init: anim=" + LabB(m_labCharacterAnim != null)
			+ " cmdBound=" + LabB(m_labCmdReload >= 0)
			+ " isServer=" + LabB(Replication.IsServer()));
	}

	// ========================================================================
	// DIAGNOSTICS
	// ========================================================================
	void LabDiag(string msg)
	{
		Print("[ARMST_MP133_LAB-DIAG] " + msg, LogLevel.NORMAL);
	}

	string LabB(bool v)
	{
		if (v)
			return "1";
		return "0";
	}

	void LabRegisterKnownEvents()
	{
		m_evtBlendIn          = GameAnimationUtils.RegisterAnimationEvent("BlendIn");
		m_evtBlendOut         = GameAnimationUtils.RegisterAnimationEvent("BlendOut");
		m_evtWeaponRackBolt   = GameAnimationUtils.RegisterAnimationEvent("Weapon_Rack_Bolt");
		m_evtEnableFire       = GameAnimationUtils.RegisterAnimationEvent("Weapon_EnableFire");
		m_evtSpawnMagazine    = GameAnimationUtils.RegisterAnimationEvent("Weapon_SpawnMagazine");
		m_evtWeaponAttachMag  = GameAnimationUtils.RegisterAnimationEvent("Weapon_AttachMagazine");
		m_evtMagRelease       = GameAnimationUtils.RegisterAnimationEvent("Weapon_MagRelease");
		m_evtDetachMagazine   = GameAnimationUtils.RegisterAnimationEvent("Weapon_DetachMagazine");
		m_evtDespawnMagazine  = GameAnimationUtils.RegisterAnimationEvent("Weapon_DespawnMagazine");
		m_evtLabShellCommit   = GameAnimationUtils.RegisterAnimationEvent("ARMST_Lab_Shell_Commit");
		m_evtLabShellSpawn    = GameAnimationUtils.RegisterAnimationEvent("ARMST_Lab_Shell_Spawn");
		m_evtLabShellRelease  = GameAnimationUtils.RegisterAnimationEvent("ARMST_Lab_Shell_Release");
	}

	string LabEventName(AnimationEventID id)
	{
		if (id == m_evtBlendIn)         return "BlendIn";
		if (id == m_evtBlendOut)        return "BlendOut";
		if (id == m_evtWeaponRackBolt)  return "Weapon_Rack_Bolt";
		if (id == m_evtEnableFire)      return "Weapon_EnableFire";
		if (id == m_evtSpawnMagazine)   return "Weapon_SpawnMagazine";
		if (id == m_evtWeaponAttachMag) return "Weapon_AttachMagazine";
		if (id == m_evtMagRelease)      return "Weapon_MagRelease";
		if (id == m_evtDetachMagazine)  return "Weapon_DetachMagazine";
		if (id == m_evtDespawnMagazine) return "Weapon_DespawnMagazine";
		if (id == m_evtLabShellCommit)  return "ARMST_Lab_Shell_Commit";
		if (id == m_evtLabShellSpawn)   return "ARMST_Lab_Shell_Spawn";
		if (id == m_evtLabShellRelease) return "ARMST_Lab_Shell_Release";
		return "";
	}

	// One-line snapshot of everything needed to diagnose the lab weapon.
	string LabStateSnapshot()
	{
		BaseWeaponComponent wpn = GetCurrentWeaponLab();
		if (!wpn)
			return "labWeapon=0";

		ARMST_MP133_Lab_Component lab = ARMST_MP133_Lab_Component.Cast(wpn.FindComponent(ARMST_MP133_Lab_Component));
		BaseMagazineComponent tube = wpn.GetCurrentMagazine();
		BaseMuzzleComponent muzzle = wpn.GetCurrentMuzzle();
		CharacterInputContext ic = GetInputContext();

		string s = "labWeapon=1";
		if (lab)
			s = s + " cap=" + lab.GetEffectiveTubeCapacity().ToString();
		else
			s = s + " cap=?";
		if (tube)
			s = s + " tube=" + tube.GetAmmoCount().ToString() + "/" + tube.GetMaxAmmoCount().ToString();
		else
			s = s + " tube=null";
		if (muzzle)
			s = s + " chambered=" + LabB(muzzle.IsCurrentBarrelChambered()) + "/" + muzzle.GetBarrelsCount().ToString();
		else
			s = s + " muzzle=null";
		if (lab)
			s = s + " reserve=" + lab.GetReserve().ToString();
		else
			s = s + " reserve=?";
		s = s + " clientInsert=" + LabB(m_bLabClientInsertActive);
		s = s + " serverInsert=" + LabB(m_bLabServerInsertActive);
		s = s + " isReloading=" + LabB(IsReloading());
		if (ic)
			s = s + " reloadType=" + ic.GetWeaponReloadType().ToString()
				+ " startReloading=" + LabB(ic.WeaponIsStartReloading())
				+ " raised=" + LabB(ic.WeaponIsRaised());
		else
			s = s + " inputCtx=null";
		return s;
	}

	// ========================================================================
	override protected void OnControlledByPlayer(IEntity owner, bool controlled)
	{
		super.OnControlledByPlayer(owner, controlled);

		bool local = (owner == SCR_PlayerController.GetLocalControlledEntity());
		LabDiag("OnControlledByPlayer controlled=" + LabB(controlled) + " local=" + LabB(local));

		if (controlled && local)
		{
			LabStartWatcher();
			LabStartHeartbeat();
		}
		else
		{
			LabStopWatcher();
			LabStopHeartbeat();
			LabClientStopInsert();
		}
	}

	// ------------------------------------------------------------------
	// Owner-client watcher: catches the vanilla reload request. Runs on the
	// local owner only and is independent of OnApplyControls.
	// ------------------------------------------------------------------
	void LabStartWatcher()
	{
		if (m_bLabWatchActive)
			return;
		m_bLabWatchActive = true;
		GetGame().GetCallqueue().CallLater(LabWatchTick, LAB_CLIENT_WATCH_MS, true);
		LabDiag("watcher started");
	}

	void LabStopWatcher()
	{
		if (!m_bLabWatchActive)
			return;
		m_bLabWatchActive = false;
		GetGame().GetCallqueue().Remove(LabWatchTick);
	}

	void LabWatchTick()
	{
		if (!m_bLabWatchActive)
			return;
		if (SCR_PlayerController.GetLocalControlledEntity() != m_labOwner)
			return;
		if (m_bLabClientInsertActive)
			return;

		if (!GetCurrentWeaponLab())
			return;

		CharacterInputContext inputCtx = GetInputContext();
		if (!inputCtx)
			return;

		if (LabReloadRequested(inputCtx))
		{
			LabDiag("watcher: reload request detected -> " + LabStateSnapshot());
			LabBeginInsert();
		}
	}

	void LabStartHeartbeat()
	{
		if (m_bLabHeartbeatActive)
			return;
		m_bLabHeartbeatActive = true;
		GetGame().GetCallqueue().CallLater(LabHeartbeatTick, LAB_HEARTBEAT_MS, true);
	}

	void LabStopHeartbeat()
	{
		if (!m_bLabHeartbeatActive)
			return;
		m_bLabHeartbeatActive = false;
		GetGame().GetCallqueue().Remove(LabHeartbeatTick);
	}

	void LabHeartbeatTick()
	{
		if (!m_bLabHeartbeatActive)
			return;
		// Only report while a lab weapon is actually held (keeps the log clean).
		if (!GetCurrentWeaponLab())
			return;
		LabDiag("STATE " + LabStateSnapshot());
	}

	// A reload request = transient "start" flag OR a NEW reload type value.
	bool LabReloadRequested(CharacterInputContext inputCtx)
	{
		int t = inputCtx.GetWeaponReloadType();
		bool start = inputCtx.WeaponIsStartReloading();
		bool changed = (t != LAB_NO_RELOAD && t != m_iLabLastReloadType);
		m_iLabLastReloadType = t;
		return start || changed;
	}

	// ------------------------------------------------------------------
	// Secondary trigger: OnApplyControls (if reached on this build).
	// ------------------------------------------------------------------
	override protected void OnApplyControls(IEntity owner, float timeSlice)
	{
		super.OnApplyControls(owner, timeSlice);

		if (SCR_PlayerController.GetLocalControlledEntity() != owner)
			return;
		if (m_bLabClientInsertActive)
			return;
		if (!GetCurrentWeaponLab())
			return;

		CharacterInputContext inputCtx = GetInputContext();
		if (!inputCtx)
			return;

		if (LabReloadRequested(inputCtx))
		{
			LabDiag("OnApplyControls: reload request detected -> " + LabStateSnapshot());
			LabBeginInsert();
		}
	}

	// ========================================================================
	// Local helpers
	// ========================================================================
	BaseWeaponComponent GetCurrentWeaponLab()
	{
		BaseWeaponManagerComponent wm = GetWeaponManagerComponent();
		if (!wm)
			return null;

		BaseWeaponComponent wpn = wm.GetCurrentWeapon();
		if (!wpn)
			return null;

		ARMST_MP133_Lab_Component lab = ARMST_MP133_Lab_Component.Cast(wpn.FindComponent(ARMST_MP133_Lab_Component));
		if (!lab)
			return null;

		return wpn;
	}

	bool LabClientCanInsert(BaseWeaponComponent wpn)
	{
		if (!wpn)
			return false;

		ARMST_MP133_Lab_Component lab = ARMST_MP133_Lab_Component.Cast(wpn.FindComponent(ARMST_MP133_Lab_Component));
		if (!lab)
			return false;

		BaseMagazineComponent tube = wpn.GetCurrentMagazine();
		if (!tube)
			return false;

		int cap = lab.GetEffectiveTubeCapacity();
		if (cap <= 0)
			return false;

		return tube.GetAmmoCount() < cap;
	}

	void LabLogClient(string msg)
	{
		LabDiag("CLIENT " + msg);
	}

	void LabLogServer(string msg)
	{
		LabDiag("SERVER " + msg);
	}

	// ========================================================================
	// Client: insert loop
	// ========================================================================
	void LabBeginInsert()
	{
		if (m_bLabClientInsertActive)
			return;
		if (!m_labCharacterAnim || m_labCmdReload < 0)
		{
			LabDiag("begin skipped: no animation component / command (anim="
				+ LabB(m_labCharacterAnim != null) + " cmdBound=" + LabB(m_labCmdReload >= 0) + ")");
			return;
		}

		BaseWeaponComponent wpn = GetCurrentWeaponLab();
		if (!wpn)
			return;

		if (!LabClientCanInsert(wpn))
		{
			LabDiag("begin skipped: cannot insert -> " + LabStateSnapshot());
			return;
		}

		LabDiag("begin insert loop -> " + LabStateSnapshot());
		m_bLabClientInsertActive = true;
		Rpc(RpcAsk_LabBeginInsert);
		LabClientStartPulse();
		if (!m_bLabClientPulseActive)
		{
			LabDiag("begin aborted: pulse failed to start");
			m_bLabClientInsertActive = false;
			Rpc(RpcAsk_LabEndInsert);
		}
	}

	void LabClientStartPulse()
	{
		if (m_bLabClientPulseActive)
			return;
		if (!m_labCharacterAnim || m_labCmdReload < 0)
			return;

		m_bLabClientPulseActive = true;
		GetGame().GetCallqueue().CallLater(LabClientPulseTick, LAB_CLIENT_PULSE_MS, true);
	}

	void LabClientPulseTick()
	{
		if (!m_bLabClientInsertActive || !m_bLabClientPulseActive)
			return;

		if (!GetCurrentWeaponLab())
		{
			LabDiag("stop: weapon no longer lab");
			LabClientStopInsert();
			Rpc(RpcAsk_LabEndInsert);
			return;
		}
		CharacterInputContext inputCtx = GetInputContext();
		if (inputCtx && !inputCtx.WeaponIsRaised())
		{
			LabDiag("stop: weapon lowered");
			LabClientStopInsert();
			Rpc(RpcAsk_LabEndInsert);
			return;
		}
		if (inputCtx && inputCtx.GetWeaponReloadType() == LAB_RACK_CMD)
		{
			LabDiag("stop: pump (rack type 1) started");
			LabClientStopInsert();
			Rpc(RpcAsk_LabEndInsert);
			return;
		}

		if (inputCtx)
			inputCtx.SetReloadWeapon(LAB_INSERT_CMD);
	}

	void LabClientStopInsert()
	{
		if (m_bLabClientPulseActive)
		{
			m_bLabClientPulseActive = false;
			GetGame().GetCallqueue().Remove(LabClientPulseTick);
		}

		if (m_bLabClientInsertActive)
		{
			m_bLabClientInsertActive = false;
			CharacterInputContext inputCtx = GetInputContext();
			if (inputCtx)
				inputCtx.SetReloadWeapon(LAB_NO_RELOAD);
			LabDiag("stop: insert loop cleared");
		}
	}

	// ========================================================================
	// RPCs
	// ========================================================================
	[RplRpc(RplChannel.Reliable, RplRcver.Server)]
	protected void RpcAsk_LabBeginInsert()
	{
		if (!Replication.IsServer())
			return;
		BaseWeaponComponent wpn = GetCurrentWeaponLab();
		if (!wpn)
		{
			LabDiag("SERVER begin: no lab weapon");
			return;
		}

		if (!LabServerCanInsert(wpn))
		{
			LabDiag("SERVER begin rejected -> " + LabStateSnapshot());
			RpcDo_LabCeaseInsert();
			return;
		}

		m_bLabServerInsertActive = true;
		LabDiag("SERVER begin insert window -> " + LabStateSnapshot());
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Server)]
	protected void RpcAsk_LabEndInsert()
	{
		if (!Replication.IsServer())
			return;
		if (m_bLabServerInsertActive)
			LabDiag("SERVER end insert window (client request)");
		LabServerEndInsert();
	}

	[RplRpc(RplChannel.Reliable, RplRcver.Owner)]
	protected void RpcDo_LabCeaseInsert()
	{
		LabDiag("cease received by owner client");
		LabClientStopInsert();
	}

	bool LabServerCanInsert(BaseWeaponComponent wpn)
	{
		if (!wpn)
			return false;

		ARMST_MP133_Lab_Component lab = ARMST_MP133_Lab_Component.Cast(wpn.FindComponent(ARMST_MP133_Lab_Component));
		if (!lab)
			return false;

		BaseMagazineComponent tube = wpn.GetCurrentMagazine();
		if (!tube)
			return false;

		int cap = lab.GetEffectiveTubeCapacity();
		if (cap <= 0)
			return false;

		if (tube.GetAmmoCount() >= cap)
			return false;

		if (lab.GetReserve() <= 0)
			return false;

		return true;
	}

	// ========================================================================
	// Server: animation event -> exactly-one commit
	// ========================================================================
	protected void OnLabAnimationEvent(AnimationEventID animEventType, AnimationEventID animUserString, int intParam, float timeFromStart, float timeToEnd, SCR_CharacterControllerComponent controller)
	{
		// Diagnostic: report every known weapon animation event, but only while
		// this character is relevant to a lab weapon (avoids log flooding from
		// unrelated characters / animations).
		string evName = LabEventName(animEventType);
		bool relevant = (GetCurrentWeaponLab() != null) || m_bLabServerInsertActive;
		if (evName != "" && relevant)
			LabDiag("anim event '" + evName + "' int=" + intParam.ToString()
				+ " t=" + timeFromStart.ToString() + " isServer=" + LabB(Replication.IsServer()));

		if (animEventType == m_evtWeaponRackBolt)
		{
			if (m_bLabServerInsertActive)
				LabLogServer("rack interrupted insert window");
			if (m_bLabServerInsertActive)
				LabServerEndInsert();
			return;
		}

		if (animEventType == m_evtLabShellCommit || animEventType == m_evtWeaponAttachMag)
			LabServerCommitInsert();
	}

	protected void LabServerCommitInsert()
	{
		if (!Replication.IsServer())
			return;
		if (!m_bLabServerInsertActive || m_bLabServerCommitCooldown)
			return;

		BaseWeaponComponent wpn = GetCurrentWeaponLab();
		if (!wpn)
		{
			LabServerEndInsert();
			return;
		}

		ARMST_MP133_Lab_Component lab = ARMST_MP133_Lab_Component.Cast(wpn.FindComponent(ARMST_MP133_Lab_Component));
		if (!lab)
		{
			LabServerEndInsert();
			return;
		}

		BaseMagazineComponent tube = wpn.GetCurrentMagazine();
		if (!tube)
		{
			LabServerEndInsert();
			return;
		}

		int cap = lab.GetEffectiveTubeCapacity();
		if (cap <= 0)
		{
			LabServerEndInsert();
			return;
		}

		int currentAmmo = tube.GetAmmoCount();
		if (currentAmmo >= cap)
		{
			LabLogServer("Insert REJECTED (tube full) -> stop loop");
			RpcDo_LabCeaseInsert();
			LabServerEndInsert();
			return;
		}

		if (lab.GetReserve() <= 0)
		{
			LabLogServer("Insert REJECTED (reserve empty) -> stop loop");
			RpcDo_LabCeaseInsert();
			LabServerEndInsert();
			return;
		}

		// ---- exactly-one commit point ----
		lab.ConsumeReserveShell();
		tube.SetAmmoCount(currentAmmo + 1);
		m_bLabServerCommitCooldown = true;
		GetGame().GetCallqueue().CallLater(LabServerCommitCooldownOff, LAB_COMMIT_COOLDOWN_MS, false);
		LabLogServer("Insert COMMIT: tube " + currentAmmo.ToString() + " -> " + (currentAmmo + 1).ToString()
			+ ", reserve " + lab.GetReserve().ToString() + " | " + LabStateSnapshot());
	}

	protected void LabServerCommitCooldownOff()
	{
		m_bLabServerCommitCooldown = false;
	}

	protected void LabServerEndInsert()
	{
		m_bLabServerInsertActive = false;
		LabLogServer("insert window closed");
	}
}
```

## C. addon.gproj

```
GameProject {
	ID "ARMSTMP133AnimationLab"
	GUID "1187677F04E33069"
	TITLE "ARMST MP133 Animation Lab"
	Dependencies {
		"58D0FB3206B6F859" "69E4C3542B6CDC19" "6A70E400C54051DC"
	}
	Configurations {
		GameProjectConfig PC {
		}
		GameProjectConfig XBOX_ONE {
		}
		GameProjectConfig XBOX_SERIES {
		}
		GameProjectConfig PS4 {
		}
		GameProjectConfig PS5 {
		}
		GameProjectConfig HEADLESS {
		}
	}
}
```

## D1. Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et

```
GenericEntity : "{63FF6FDCA4E7E735}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133.et" {
	ID "77AB6DD3F7C4DF4D"
	components {
		ARMST_MP133_Lab_Component "{21B3393B3149815A}" {
			m_iTubeCapacityOverride 0
			m_iLabReserveShells 30
			m_bLabDebugLog 1
		}
		SCR_WeaponAttachmentsStorageComponent "{51F080D5CE45A1A2}" {
			Attributes SCR_ItemAttributeCollection "{51F080D5C64F12C5}" {
				ItemDisplayName WeaponUIInfo "{5222CB07CFF6712A}" {
					Name "MP 133 (LAB)"
				}
			}
		}
		WeaponComponent "{CFBAA4B706BA66E8}" {
			components {
				WeaponAnimationComponent "{60B4EA76EB15F6E0}" {
					AnimGraph "{F23E6BC494967D16}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr"
					AnimInstance "{DE3BB4522642DDE0}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi"
					AnimInjection AnimationAttachmentInfo "{532F3A9CB912F2BA}" {
						AnimGraph "{F23E6BC494967D16}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr"
						AnimInstance "{B51A94B5A27E09B4}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_player.asi"
					}
				}
			}
		}
	}
	coords 146.99 1.9 77.878
}
```

## D2. Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et

```
GenericEntity : "{9F8CA2FE5A3540DC}Prefabs/Weapons/Russian/Shotgun/armst_Shotgun_mp_133_Ris.et" {
	ID "4293C409C16270F8"
	components {
		ARMST_MP133_Lab_Component "{21B3393B3149815A}" {
			m_iTubeCapacityOverride 0
			m_iLabReserveShells 30
			m_bLabDebugLog 1
		}
		SCR_WeaponAttachmentsStorageComponent "{51F080D5CE45A1A2}" {
			Attributes SCR_ItemAttributeCollection "{51F080D5C64F12C5}" {
				ItemDisplayName WeaponUIInfo "{5222CB07CFF6712A}" {
					Name "MP 133 RIS (LAB)"
				}
			}
		}
		WeaponComponent "{CFBAA4B706BA66E8}" {
			components {
				WeaponAnimationComponent "{60B4EA76EB15F6E0}" {
					AnimGraph "{F23E6BC494967D16}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr"
					AnimInstance "{DE3BB4522642DDE0}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_weapon.asi"
					AnimInjection AnimationAttachmentInfo "{532F3A9CB912F2BA}" {
						AnimGraph "{F23E6BC494967D16}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab.agr"
						AnimInstance "{B51A94B5A27E09B4}Assets/Weapons_RUS/Mp_133/Workspace/MP133_Lab_player.asi"
					}
				}
			}
		}
	}
	coords 133.114 1.054 77.575
}
```

## E. MP133_Lab.agf — добавленный insert-loop переход (фрагмент WeaponReloadSTM)

```
     states {
      // ARMST PROTOTYPE: CMD_Weapon_Reload == 7 is one shell-insert animation cycle.
      // Reuses the existing MP133 Reload_InsertMag animation only as a temporary visual.
      AnimSrcNodeState InsertSingleProjectile {
       EditorPos 5.9 18.3
       Child "InsertMagAnim"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 7"
       TimeStorage "Real Time"
       IsExit 1
      }
      AnimSrcNodeState NoMagReload {
       EditorPos 4.4 16.2
       Child "InsertMagAnim"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 2"
       TimeStorage "Real Time"
       IsExit 1
      }
      AnimSrcNodeState NoMagNoBulletReload {
       EditorPos 8.4 16.2
       Child "InsertMagAnim"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 3 && GetCommandF(CMD_Weapon_Reload) == 0.0"
       TimeStorage "Real Time"
       IsExit 0
      }
      AnimSrcNodeState MagReload {
       EditorPos 11.2 17
       Child "MagReloadSTM"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 4"
       TimeStorage Inherit
       IsExit 1
      }
      AnimSrcNodeState MagNoBulletReload {
       EditorPos 14.4 17.1
       Child "MagReloadSTM"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 5 && GetCommandF(CMD_Weapon_Reload) == 0.0"
       TimeStorage Inherit
       IsExit 0
      }
      AnimSrcNodeState ReloadActionBolt {
       Tags {
        "TagRackBolt"
       }
       EditorPos 18.1 16.2
       Child "RackBoltAnim"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(CMD_Weapon_Reload) == 0.0"
       TimeStorage "Real Time"
       IsExit 1
      }
      AnimSrcNodeState RemoveMag {
       EditorPos 16.7 17.1
       Child "RemoveMagAnim"
       StartCondition "GetCommandI(CMD_Weapon_Reload) == 6"
       IsExit 1
      }
     }
     transitions {
      AnimSrcNodeTransition "{6906E74261458BB0}" {
       FromState "NoMagNoBulletReload"
       ToState "ReloadActionBolt"
       Duration "0.3"
       StartTime ""
       Condition "RemainingTimeLess(0.1)"
       BlendFn "S"
       PostEval 1
       MotionVecBlend 0x33 0
      }
      AnimSrcNodeTransition "{6906E74261458BB6}" {
       FromState "MagNoBulletReload"
       ToState "ReloadActionBolt"
       Duration "0.3"
       StartTime ""
       Condition "RemainingTimeLess(0.1)"
       BlendFn "S"
       PostEval 1
       MotionVecBlend 0x33 0
      }
      // ARMST MP-133 LAB: repeat the single-shell insert cycle while the lab
      // gameplay controller keeps CMD_Weapon_Reload == 7 alive; exit when it
      // clears (the client sends -2 = vanilla "reload finished" on release).
      AnimSrcNodeTransition "{801C018EA3A11FA1}" {
       FromState "InsertSingleProjectile"
       ToState "InsertSingleProjectile"
       Duration "0.25"
       StartTime ""
       Condition "IsEvent(\"BlendOut\") && GetCommandI(CMD_Weapon_Reload) == 7"
       BlendFn "S"
       PostEval 1
      }
     }
    }
```


## F. Мир/слой — УДАЛЕНЫ

Согласно OWNER OVERRIDE issue #25, мир, .ent, .layer, сценарий и спавн в аддоне
запрещены. Ранее созданные Worlds/MP133_Lab/MP133_Lab.ent и
Worlds/MP133_Lab/MP133_Lab_Layers/default.layer удалены из аддона и не являются
частью поставки. Владелец ставит префаб в свой мир лично:

- {FC1935AF936F63E5}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et
- {4B288C21B7125D50}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et
