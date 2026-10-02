# MP-133 Lab — V2.7: C2-диагностика патронника + read-only разбор изоляции Core

**Статус:** C2 реализована lab-only; первый прогон компиляции владельца дал
lab-owned `SCRIPT (E)` на строке 433 → **исправлено** (см. §1b); после правки
`COMPILE_BLOCKED` снят, статус `OWNER RETEST REQUIRED`. Гейт досылки **OFF** на
обоих префабах; прод/Core/миры/граф/ASI/ANM **не менялись**; Workbench/игру агент
не запускал.

Источник: Issue #27, comment 5959385576 (START AUTHORIZED: V2.7 C2 instrumentation
+ read-only Core-isolation feasibility).

---

## 1. Что реализовано (C2)

Файл (единственный изменённый): `ARMST_MP133_AnimationLab/Scripts/Game/ARMST_MP133_Lab/ARMST_MP133_Lab_Character.c`
(маркер строк лога `[ARMST_MP133_LAB-C2]`).

Пассивная хронологическая трасса, наблюдает **любое** текущее оружие (лаб или
нетронутый прод), не меняя прод. Триггеры и rate-limit:

- **смена состояния** — сэмплер в существующем `LabWatchTick` (100 мс): логирует
  только при изменении подписи (не по кадрам);
- **значимые анимационные события** — `Weapon_Rack_Bolt`, `Weapon_EnableFire`,
  `Weapon_SpawnMagazine`, `Weapon_AttachMagazine`, `Weapon_MagRelease`,
  `Weapon_DetachMagazine`, `Weapon_DespawnMagazine`, `ARMST_Lab_Shell_*`;
- **отложенный «устоявшийся» сэмпл** через 150 мс после события (`SETTLE:`);
- **действие помпы** — `OnLabPumpDown` (существующее `ARMST_LIGHT_RELOAD_ACTION`).

Формат строки:

```
[ARMST_MP133_LAB-C2] TRACE #<seq> t=<cs> <SV|CL> reason=<r> wep_id=<int> wep=<prefab> lab=<0|1>
  mag_id=<int> mag=<prefab> tube=<a>/<m> chambered=<0|1> barrel=<i>/<n> muzzleAmmo=<a>/<m>
  chNeed=<0|1> chPoss=<0|1> relPoss=<0|1> reloadType=<t> start=<0|1> raised=<0|1>
  isReloading=<0|1> pump=<0|1> cIns=<0|1> sIns=<0|1>
```

`reason` выводит дельту: `+MAGID(prev->new)`, `+TUBE(prev->new)`,
`+CHAMBER(prev->new)`, `+RTYPE(prev->new)`, `+PUMP(prev->new)`, а также
`EVT:<name>` / `SETTLE:<name>` / `PUMP_ACTION_LSHIFT_R` / `no-weapon`.

**Идентичность** — физические экземпляры: оружие и магазин логируются по
`IEntity.GetID()` **и** `GetPrefabData().GetPrefabName()`; отличить смену
магазина от простого изменения счётчика можно по `mag_id`.

**Различение операций** (по проектным признакам):
- помпа → `reason=…+PUMP(0->1)` / `PUMP_ACTION_LSHIFT_R` (`pump=1`);
- нативный R → `reason=…+RTYPE(…->x)` без `pump`;
- выстрел → `reason=watch+CHAMBER(1->0)` (патронник; при выстреле труба не меняется).

Использованы только проектно-доказанные API + официальный локальный справочник
(`BaseWeaponComponent.IsChamberingNecessary/IsChamberingPossible/IsReloadPossible`,
`BaseMuzzleComponent.GetCurrentBarrelIndex/GetAmmoCount/GetMaxAmmoCount`).
Недоступное честно помечено (`?`/`null`); фрейм-спам исключён подписью.

Отдельная lab-конфигурация не потребовалась.

---

## 1b. Compile-fix по ошибке владельца (line 433)

Первый прогон Workbench владельца (`comment 5959746653`) дал **lab-owned**:

```
SCRIPT (E): .../ARMST_MP133_Lab_Character.c,433: Formula too complex
SCRIPT (E): .../ARMST_MP133_Lab_Character.c,433: Incompatible parameter '|'
```

Строка 433 — сборка подписи одним длинным inline-выражением (~20 операторов `+`):

```
string sig = LabTraceIdI(we).ToString() + "|" + magId.ToString()
    + "|" + tubeA.ToString() + "/" + tubeM.ToString()
    + "|" + LabB(chambered) + "|" + barrel.ToString()
    + "|" + rtype.ToString() + LabB(start) + LabB(raised) + LabB(isRel)
    + "|" + LabB(m_bLabPumpLatch) + LabB(m_bLabClientInsertActive)
    + LabB(m_bLabServerInsertActive);
```

Причина — предел сложности формулы EnforceScript на одно выражение; вторичная
ошибка `Incompatible parameter '|'` — следствие разбора того же выражения.

**Правка (lab-only, синтаксис):** сборка подписи — короткими инкрементальными
присваиваниями `sig = sig + ...;` (≤3 оператора на строку), имена префабов и
`.ToString()` — через типизированные локальные переменные (`int weId`,
`string weName/meName`, `int tubeA/tubeM/bi/bc/ma/mm`). Аналогично разбиты длинные
конкатенации в `LabTraceSnapshot` и блоки `reason` (с фигурными скобками).
Поведение не изменилось: те же поля, 100 мс сэмплинг, 150 мс settle, физические
`wep_id`/`mag_id`.

**Хэши файла:**
```
до V2.7 (baseline):      37D07A1EC676AD586587790A44D8D000B8B0FD93B228B60B813A75063DA52A34
V2.7 C2 (ошибка 433):    4A20782505D8FB53853923740C49692E2924057BCD0B8F7A31AF26FF8C275EA0
V2.7 C2 fix (текущий):   7737D8AB2525B15183D5013099FB9D6075BB8E190119E7707019965056218C6A
```

**Регрессионная проверка:** `check_v27_trace` теперь требует инкрементальную
сборку (`int weId = LabTraceIdI(we);`, `string sig = weId.ToString();`,
`sig = sig + "|" + magId.ToString();`) и отвергает строку с ≥12 операторами `+`
(эвристика «formula too complex»). Python-валидатор не доказывает компиляцию
EnforceScript; компиляцию проверяет владелец.

Разбор именно lab-owned ошибок. Прочие ошибки base-game UI/persistence из того же
лога **не** приписываются лабе и не правятся без отдельного разрешения.

---

## 2. Правки, бэкап, хэши, откат

Изменённый локальный файл:

```
...\addons\ARMST_MP133_AnimationLab\Scripts\Game\ARMST_MP133_Lab\ARMST_MP133_Lab_Character.c
SHA-256 was: 37D07A1EC676AD586587790A44D8D000B8B0FD93B228B60B813A75063DA52A34
SHA-256 now: 4A20782505D8FB53853923740C49692E2924057BCD0B8F7A31AF26FF8C275EA0
```

Бэкап (вне knowledge-репо, `artifacts/` git-ignored):
`Weapon_ARMA_X/artifacts/MP133_Lab/v27_backups/Scripts/` — все 3 lab-скрипта
до правки. Откат = скопировать `ARMST_MP133_Lab_Character.c` обратно (SHA должен
стать `37D0…2A34`), CommandHandler/Component не менялись.

Не менялись: graph/ASI/AST/ANM, оба lab-префаба, lab-магазин, прод/Core.

---

## 3. Статические проверки

| Проверка | Результат |
|---|---|
| `validate_mp133_lab.py` (структура/GUID/проводка/гейт OFF/trace) | **PASSED** |
| `test_mp133_lab_validation.py` | **14/14 OK** (добавлен `test_v27_trace`) |
| `test_mp133_lab_connect_anims.py` | **15/15 OK** |
| `test_mp133_lab_r_gate_model.py` | **17/17 OK** |
| ASCII + баланс скобок (lab resources) | **CLEAN** |
| `m_bLabInsertEnabled` на non-RIS и RIS | **0 (OFF)** |

Компиляция/рантайм — `OWNER TEST REQUIRED` (агент Workbench/игру не запускает).

---

## 4. Read-only: можно ли lab-only отключить списание/очистку Core

### Что установлено по исходникам (факты)

- Нажатие LSHIFT+R: Core регистрирует слушатель
  `inputMgr.AddActionListener("ARMST_LIGHT_RELOAD_ACTION", EActionTrigger.DOWN,
  OnRackBoltMDown)` (`ARMST_PLAYER_CharacterController.c:28`).
- `OnRackBoltMDown` (`ARMST_WEAPONS_HANDLER.c:354-388`): `Rpc(RpcAsk_TAO_ManualRack)`
  + `inputCtx.SetReloadWeapon(1)`.
- Сервер: `RpcAsk_TAO_ManualRack` (`:232-253`) ставит `m_ServerManualRackPending=true`
  и запускает фолбэк `TAO_ServerProcessManualRack_Fallback` (`:256-284`).
- По `Weapon_Rack_Bolt` (`OnAnimEvent_RackBoltCaseEject`, `:169-227`), если
  `m_ServerManualRackPending && !m_ServerRackCooldownActive`:
  `TAO_DecrementAmmoOnRack()` (`:295-314`, `tube−1`) +
  `TAO_ClearChamberIfNoMagOrEmpty()` (`:319-349`, очистка только при пустой трубе).
- Все эти методы/поля — `protected`, **не `virtual`**, в Core-блоке
  `modded class SCR_CharacterControllerComponent`.

### Оценка (что возможно без правки Core)

`modded class SCR_CharacterControllerComponent` — это частичный (merged) класс:
Core-блок и lab-блок сливаются в один класс. Значит lab **видит** поля
`m_ServerManualRackPending`, `m_ServerFallbackRunning`, `m_ServerRackCooldownActive`
и метод `TAO_ServerProcessManualRack_Fallback`.

- **Прямой override `TAO_DecrementAmmoOnRack`/`OnAnimEvent_RackBoltCaseEject`
  невозможен:** методы не `virtual`, а повторное определение в другом modded-блоке
  не является допустимым override. Значит «отключить» метод можно только правкой
  Core — запрещено.
- **Косвенно, без правки Core, теоретически возможно** обнулить разделяемое
  `m_ServerManualRackPending` из lab-метода на сервере (lab-RPC, отправленный при
  LSHIFT+R только для lab-оружия) и снять фолбэк-таймер. Тогда Core-блок
  (`if (m_ServerManualRackPending && …)`) не выполнит ни `TAO_DecrementAmmoOnRack`,
  ни `TAO_ClearChamberIfNoMagOrEmpty`, **сохранив ту же команду и анимацию**
  `SetReloadWeapon(1)`.
- **Но это timing-зависимо и само по себе не решает задачу:** порядок lab-RPC и
  Core-RPC не гарантирован; фолбэк Core срабатывает примерно через 6×30 мс, а
  AnimEvent `Weapon_Rack_Bolt` — позже (≈кадр 14), поэтому подавление обязано
  успеть до фолбэка. И главное: подавление лишь убирает `tube−1` Core — **патронник
  оно не заполняет**. Полезно только если движок нативно досылает патрон на помпу
  (чего текущие данные не подтверждают).

### Что обязательно учесть

- **`tube=0, chamber=1`**: при подавлении `TAO_ClearChamberIfNoMagOrEmpty`
  пропадает и «страховка» очистки патронника при пустой трубе. Это допустимое
  состояние (последний патрон в патроннике), но при lab-досылке в пустую трубу
  возможен рассинхрон/фантомный патрон. Требует явного правила.
- **Фолбэк-таймер Core** (`TAO_ServerCooldown…`, `m_ServerFallbackRunning`) обязан
  быть снят вместе с `m_ServerManualRackPending`, иначе помпа всё равно спишет
  патрон спустя ~180 мс, даже если AnimEvent не придёт.
- `TAO_ClearChamberIfNoMagOrEmpty` вызывается из двух мест (AnimEvent и фолбэк) —
  подавление `m_ServerManualRackPending` снимает оба.

**Вывод 4:** lab-only подавление Core возможно лишь косвенно и timing-fragile;
оно **не заменяет** досылку патрона и не должно реализовываться до C2-результата.
Если C2 покажет, что движок на помпу патрон **не** досылает, единственный
проектный путь досылки — нативная ветка перезагрузки (C1 из V2.6), а не
подавление Core.

---

## 5. Один контролируемый игровой тест (gate OFF) — инструкция владельцу

Цель: получить достоверный ответ, что происходит с патроном при передёргивании,
и возможен ли `труба 2→1, патронник 0→1` без смены магазина.

Подготовка: поставить `MP-133 [LAB]` (non-RIS) в свой мир, запустить, открыть
`console.log`/`script.log`, фильтр `ARMST_MP133_LAB-C2`.

Шаги (ровно один раз, без повторов при подозрении на сбой):

1. Убедиться: `tube=2/3`, `chambered=1`, `mag_id=<X>` (запомнить `X`), `lab=1`.
2. **Выстрел** (ЛКМ) — ожидаем лог `reason=watch+CHAMBER(1->0)`, труба `2/3`,
   `mag_id` тот же.
3. **Одно короткое нажатие R** и дождаться `SETTLE:`. Смотреть:
   - труба: `2/3 → 1/3`?
   - патронник: `0 → 1`?
   - `mag_id` — **тот же** `X`? (`MAG_SWAP`/смена `mag_id` = плохо)
   - `chNeed/chPoss/relPoss` и события `Weapon_Rack_Bolt/Weapon_EnableFire`.
4. Проверить, стреляет ли второй раз.

**STOP (не продолжать)**, если: труба стала `10/10` или `mag_id` сменился
(замена магазина), патрон потерян (`2→0` одним действием), `tube=0, chamber=1`
без объяснимого выстрела, или в логе `SCRIPT (E)`.
Затем прислать выдержку `[ARMST_MP133_LAB-C2]` вокруг шагов 1–3.

**Если нативный короткий R нельзя безопасно проиграть в текущем графе** —
скажи, и я предложу изолированный A/B-тест (без его выполнения агентом).

---

## 6. Факты / гипотезы / неизвестное

| Утверждение | Статус |
|---|---|
| C2 lab-only трасса собирает tube/chamber/mag_id/события | **РЕАЛИЗОВАНО + статически проверено** |
| Гейты OFF, прод/Core/граф не тронуты | **ФАКТ (валидатор + хэши)** |
| Патронник пишется только движком (нет API-сеттера) | **ФАКТ** (V2.6) |
| Core lab-only подавляем косвенно через shared `m_ServerManualRackPending` | **ВОЗМОЖНО, timing-зависимо, не реализовано** |
| Движок нативно досылает патрон на `Weapon_Rack_Bolt` | **НЕИЗВЕСТНО** (ответит C2) |
| `tube=0, chamber=1` как риск рассинхрона | **отмечено, требует правила** |

---

## 7. V2.7b — уточнение владельца: Manual Action, R vs J, идентичность, команда

Источник: Issue #27, comment 5960042056.

### 7.1 Смена понимания (не менять `Manual Action`)

Скриншот Workbench владельца: `BaseFireMode Single → Manual Action CHECKED`,
`Safe → UNCHECKED`. Исторический цикл MP-133: **выстрел → обычный R (ручной
цикл) → выстрел**. Значит:

- **обычный R = штатный ручной цикл оружия** (`Manual Action`) — сохраняем,
  не подменяем его досылкой и не трогаем настройку;
- **LSHIFT+R = отдельная ARMST Core-помпа** — другой механизм, её результат
  нельзя переносить на обычный R;
- **J свободна** — на неё в будущем вешается удержание «загрузка патронов в
  трубу»; правый/удерживаемый R и инспекция сохраняются.
- C1 и подавление Core **заморожены** до измерения обычного R.

Документированные значения (`CMD_Weapon_Reload`): 1 = передёргивание затвора,
5 = замена магазина + передёргивание. Какая команда у обычного R в оригинале и
в лабе — должен показать рантайм-лог.

### 7.2 Исправление идентичности (было `wep_id=0, mag_id=0`)

`IEntity.GetID()` в локальном справочнике `ArmaReforgerScriptAPIPublic` **нет**
(есть `GetId`/`GetRplComponent`), и в логе владельца оно вернуло 0. Заменено на
**теги физической идентичности по ссылке на компонент**:

- `LabTraceWpnTag(BaseWeaponComponent)` / `LabTraceMagTag(BaseMagazineComponent)`:
  тег увеличивается **только при смене самого объекта** (сравнение ссылок
  `!=`), не по prefab/GUID. В логе — `wep_tag=N`, `mag_tag=M`; смена тега =
  смена физического оружия/магазина. Это устойчиво к `GetID()=0`.

### 7.3 Лог команды перезарядки

В lab-хуке `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading`
(`ARMST_MP133_Lab_CommandHandler.c`) добавлен C2-лог **фактического id команды**:

```
[ARMST_MP133_LAB-C2] CMDCHG id=<N> reloadType=<t> start=<0|1> raised=<0|1> isServer=<0|1>
```

Пишется при смене id или раз в ≥1 с (без покадрового спама, ловит и повторный
тот же id), для любого оружия — включая обычный R. Это прямой ответ на вопрос
«какую команду даёт обычный R».

### 7.4 Точный эксперимент (заменяет §5 выше)

1. Гейт OFF; `Single.ManualAction` **CHECKED**; в руках non-RIS lab MP-133;
   зафиксировать устоявшееся `tube=2/3`, `chamber=1/1`, `wep_tag`, `mag_tag`.
2. **Выстрел ровно один** — устоявшееся `chamber 1→0`, `tube=2/3` (тег магазина тот же).
3. **Обычный R один раз, БЕЗ Shift**; подождать ≥150 мс после событий. Смотреть:
   - `CMDCHG id=<N>` (ожидаемо 1 = затвор; 5 = магазин+затвор);
   - события `Weapon_Rack_Bolt`, любые `Weapon_*Magazine`;
   - устоявшиеся `tube`/`chamber`, `mag_tag`/`wep_tag` (смена тега = смена магазина).
   Если `tube=1/3; chamber=1/1` и тег магазина тот же — допустим один
   подтверждающий выстрел.
4. **STOP** на `10/10`, смене `mag_tag`, потере патрона, `SCRIPT (E)`.
5. Если обычный R не наполняет патронник в лабе — отдельно согласованное
   **read-only наблюдательное** сравнение с оригинальным MP-133 тем же
   сценарием (без смены состояния/графа лабы).

Хэши lab-скриптов (V2.7b):
```
Character.c:        524E70B00B0E0D136AB1D2A027373B04C3BAE53EC55758F5BB85230A695E14E3
CommandHandler.c:   CD7759D5B1E681BEB2175ACA3799588A35053C86828D06AFDEBFA5BC7232268A
```
