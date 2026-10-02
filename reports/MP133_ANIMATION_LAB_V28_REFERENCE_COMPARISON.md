# MP-133 Lab — V2.8: read-only сравнение с рабочим дробовиком (BC/Ithaca)

**Статус:** только анализ. Код лабы/прод/Core/граф/ASI/ANM/префабы **не менялись**;
оба гейта `m_bLabInsertEnabled` — **OFF**; Workbench/игру агент не запускает.
Рантайм — `OWNER TEST REQUIRED`. Источник: Issue #27, comment 5960748663.

> Сырые вложения владельца (`BC_PumpShotgunComponent`, `SCR_IthacaAnimationComponent`,
> `bc_ithaca_m37_player.asi`, скриншоты графа) **недоступны локально как файлы** —
> анализ построен на цитатах задания + читаемых исходниках проекта/SDK
> (`ArmaReforgerScriptAPIPublic`). Ничего из reference не переносится.

---

## 0. Установленный факт из V2.7b

Владелец на скомпилированной V2.7b-сборке получил: после выстрела обычный R →
`CMDCHG id=21 reloadType=1`, **патронник не заполняется**; LSHIFT+R вручную
списывает трубу при пустом патроннике. То есть lab-owned compile-фикс сработал,
C2-трасса и лог команды работают.

Важно: `CMDCHG id=21` — это `pCurrentCommandID` обработчика персонажа, **не**
значение `GetCommandI(CMD_Weapon_Reload)` в графе оружия (там 1 = затвор, 5 =
магазин+затвор). `reloadType=1` — значение input-context. Граф по типу 1 идёт в
`ReloadActionBolt` — это подтверждает, что **обе** сборки (прод и лаба) для типа 1
играют одну и ту же ветку `RackBoltAnim`.

---

## 1. Четыре независимых механизма (по сторонам)

| # | Триггер | Кто вызывает | Куда приходит | Патронник |
|---|---|---|---|---|
| **a** native post-shot R | движок (ввод) | `SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` → input `reloadType=1` | **граф оружия** `WeaponReloadSTM.ReloadActionBolt` (cmd 1) → `RackBoltAnim` = `W_MP133_Reload_Bolt.anm` (`Weapon_EnableFire`, `Weapon_Rack_Bolt`) | `0→1` **не наблюдалось** (V2.7b) |
| **b** reference BC `TryRackBolt` | скрипт, **край нажатия курка** (`WeaponIsPullingTrigger`), не R | `BC_PumpShotgunComponent` | 3 вызова: `weaponAnim.CallCommand(<cmd>,1,0.0)` (**граф оружия**), `charAnim.CallCommand(<cmd>,1,0.0)` (**граф персонажа**), `controller.ReloadWeapon()` (**native**) | предполагается, но **не доказано** |
| **c** ARMST Core LSHIFT+R | Core-слушатель `ARMST_LIGHT_RELOAD_ACTION` | `OnRackBoltMDown` → RPC + `inputCtx.SetReloadWeapon(1)` | **граф** `ReloadActionBolt` + **сервер** `TAO_DecrementAmmoOnRack`/`TAO_ClearChamberIfNoMagOrEmpty` (+фолбэк) | нет (только `tube−1`) |
| **d** lab shell insert (гейт OFF) | lab-хук `HandleWeaponReloading` | `SetReloadWeapon(7)` (пульс) | **граф оружия** `InsertSingleProjectile` → `InsertMagAnim` (санитизированный `W_MP133_Lab_Inject.anm`) | нет; сервер `tube+1` по `ARMST_Lab_Shell_Commit` |

Различия принципиальны: reference **(b)** — скриптовый, по краю нажатия курка, и
единственный, кто зовёт **`controller.ReloadWeapon()`**; наша lab/core-схема
`ReloadWeapon()` не вызывает вообще.

---

## 2. Что из reference реально доступно в MP133

| Элемент reference | В MP133 | Доказательство |
|---|---|---|
| `CMD_BC_Weapon_Rack_Bolt` | **НЕТ** | lab/прод граф использует `CMD_Weapon_Reload`; в AGF/ASI/`CommandHandler` нет `BC_` |
| sources `Reload_PumpAction`, `Reload_GrabShell`, `Reload_InsertShell`, `Reload_OpenAction`, `Reload_CloseAction` | **НЕТ** | grep lab-AGF: 0 вхождений; в AST-строках только `Reload_InsertMag`/`Reload_RemoveMag`/`ReloadActionBolt` |
| `BC_PumpActionForward` (сброс busy) | **НЕТ** | кастомное событие reference |
| `CharacterControllerComponent.ReloadWeapon()` | **ЕСТЬ** (API), lab не вызывает | `ArmaReforgerScriptAPIPublic` `CharacterControllerComponent.ReloadWeapon()` → bool |
| `HandleWeaponFire` / `HandleWeaponFireDefault` | **ЕСТЬ** (API), lab не переопределяет | `CharacterCommandHandlerComponent.HandleWeaponFire(CharacterInputContext,float,int)` |
| `WeaponIsPullingTrigger()` | **ЕСТЬ** (API) | индекс функций |
| `CallCommand` / `BindCommand` | **ЕСТЬ** (`BaseAnimPhysComponent`; lab уже применяет `BindCommand` на `SCR_CharacterAnimationComponent`) | API |
| аналог ветки помпы в графе | **НЕТ**; ближайшее — `ReloadActionBolt`/`RackBoltAnim` | lab AGF |

Вывод: reference-подход нельзя «портировать» дословно — в MP133 нет ни его
команд, ни его graph-source'ов, ни `BC_PumpActionForward`. Единственный прямо
доступный недостающий вызов — **`ReloadWeapon()`**.

---

## 3. Где `chamber 0→1` наблюдаемо, а где гипотеза

- **Наблюдалось**: только **инициализация/экипировка** (V2.7b: `tube 3→2; chamber 0→1`).
- **Не наблюдалось**: после выстрела + обычного R (V2.7b); после LSHIFT+R.
- Проектный код патронник **не пишет** (V2.6: у `BaseMuzzleComponent` только
  геттеры + `ClearChamber`; сеттера нет).
- В reference `Weapon_Rack_Bolt` лишь планирует `UpdateHud()` — то есть это
  **не** доказательство досылки.

Итого: любая пост-выстрельная досылка — **нативная гипотеза**; конкретный
триггер (нативная перезагрузка / `ReloadWeapon()` / команда графа) не доказан.

---

## 4. Кандидатные причины (ranked, не доказательства)

1. **Нативный `ReloadWeapon()` / нативная перезагрузка.** Reference зовёт
   `ReloadWeapon()`, lab — нет. Средняя уверенность; самая дешёвая проверка.
2. **Разница префаба/магазина лабы**: `ARMST_SHOTGUN_COMPONENTS Enabled 0` (только
   non-RIS), `MuzzleComponent.MagazineTemplate` → 3-патронный lab-магазин. Может
   менять нативное поведение перезарядки. Средняя.
3. **Значение команды графа / hardened-состояния.** Для cmd 1 ветка идентична
   проду, поэтому маловероятна как причина — но тип 5 в лабе переведён на
   `InsertMagAnim` (санитизированный), в отличие от прода. Средняя.
4. **Отдельные pump/shell источники графа** (как в reference). В MP133
   отсутствуют; потребовали бы новых клипов/ANM (импорт владельца). Низкая
   уверенность, большой объём.

---

## 5. Ranked эксперименты (по одному изменению за раз)

Правило: baseline + откат для каждого; наблюдение только владельцем; гейт OFF;
менять **ровно одну** переменную.

- **E0 — baseline-сравнение (read-only, без правок).** Оригинальный прод-MP-133
  vs non-RIS lab MP-133, один и тот же сценарий: `Single.ManualAction`, один
  выстрел, один обычный R. Использовать уже скомпилированную C2-трассу (она
  пассивно наблюдает **любое** оружие) + `CMDCHG`. Сравнить: нативный `id`,
  `reloadType`, `Weapon_Rack_Bolt`, `Weapon_*Magazine`, устоявшиеся
  `tube`/`chamber`/`mag_tag`. **Это и есть «рабочий оригинал vs lab graph/command
  path» — первый шаг, без кода.**
- **E1 (одна переменная, префаб, lab-only, нужно одобрение).** Если оригинал
  досылает, а lab — нет: в lab-префабе вернуть `ARMST_SHOTGUN_COMPONENTS`
  `Enabled 1` (или дефолтный `m_MaxMagazineAmmo`) — **только одно свойство**.
  Гейт OFF. Наблюдать `chamber` после обычного R.
- **E2 (одна переменная, код, lab-only, нужно одобрение).** В callable lab-пути
  обычного R добавить **один** вызов `controller.ReloadWeapon()` (после расчёта,
  только для lab-оружия), без графовых `CallCommand`. Наблюдать `chamber`.
- **E3 (одна переменная, граф/ASI, lab-only, нужно одобрение).** Для диагностики
  временно вернуть **оригинальный** клип/состояния перезагрузки (снять hardening
  + откатить ASI-строки) — вернёт mag-события; только если E1/E2 не объясняют.
- **E4 (крайний случай, большой объём).** Новые lab-only pump/shell graph
  sources + клипы (импорт ANM владельцем) — только если движок требует именно их.

Запрещено смешивать `ReloadWeapon()`, dual `CallCommand` и возврат оригинальных
mag-событий в одном эксперименте.

---

## 6. Минимальный следующий запрос

**Только E0 (read-only baseline).** Одна контролируемая сессия, гейт OFF:
1. Оригинальный прод-MP-133: `Single.ManualAction`, baseline `tube`/`chamber`,
   **один выстрел**, **один обычный R**, приложить выдержку `[ARMST_MP133_LAB-C2]`
   (`TRACE`, `CMDCHG`, `EVT:Weapon_Rack_Bolt`, `Weapon_*Magazine`).
2. То же на non-RIS lab MP-133.
Цель — увидеть, досылает ли **оригинал** патрон на обычном R, и чем его трасса
отличается. Никаких правок до ревью этого отчёта.

Если оригинал тоже не досылает на обычном R — значит «рабочий цикл» владельца
шёл не через обычный R/этот граф, и это меняет постановку (нужен отдельный
разбор).

---

## 7. Что из reference **нельзя** переносить без проверки

- `HandleWeaponFire` + `HandleWeaponFireDefault` в одном обработчике — риск
  двойного эффекта; сначала анализ дублей.
- «Пустой магазин»: временный dummy-патрон и последующее
  `PumpShotgunAdjustAmmoCount`; `SCR_IthacaAnimationComponent` может
  **спавнить/прикреплять** дефолтный магазин при отсутствии — риск вернуть
  замену магазина/дубли/`10/10`.
- `TryRackBolt` завязан на **край нажатия курка**, а не на R; менять намеренное
  поведение R владельца запрещено.
- Мультиплеерная авторитетность/op-id safeguards в reference не разобраны.

---

## 8. Факты / гипотезы / неизвестное

| Утверждение | Статус |
|---|---|
| lab/прод для `reloadType=1` идут в `ReloadActionBolt`/`RackBoltAnim` | **ФАКТ** (граф + V2.7b) |
| В MP133 нет `CMD_BC_Weapon_Rack_Bolt`/pump-shell sources/`BC_PumpActionForward` | **ФАКТ** (grep AGF/AST/ASI) |
| `ReloadWeapon()`, `HandleWeaponFire`, `WeaponIsPullingTrigger`, `CallCommand` доступны | **ФАКТ** (SDK) |
| Патронник заполняется только нативным путём; lab его не пишет | **ФАКТ** (V2.6) |
| Пост-выстрельный `chamber 0→1` возможен на обычном R | **НЕ ПОДТВЕРЖДЕНО** (E0) |
| Причина досылки = `ReloadWeapon()` / команда графа / состояние | **НЕИЗВЕСТНО** |
