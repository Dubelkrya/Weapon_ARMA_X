# MP-133 Lab — V2.6: почему помпа списывает трубу, но не заполняет патронник

**Статус:** read-only разбор. Workbench/игра **не запускались**, лабораторный
аддон в этом разборе **не изменялся**, гейт `m_bLabInsertEnabled` — **OFF**.
Рантайм — `OWNER TEST REQUIRED`.

Задача из Issue #27 (comment 5958821529): установить проектно-доказуемо, кто
списывает трубу и кто заполняет патронник, не сломали ли это граф/префаб лабы,
и предложить минимальную lab-only коррекцию с откатом и тестом — до реализации.

---

## 1. Две независимые цепочки (не смешивать)

### 1.1 Выстрел → помпа → патронник → выстрел (Core + движок)

| Шаг | Кто | Файл:строки | Что делает |
|---|---|---|---|
| Выстрел | движок | — | патронник `1→0`, труба не меняется (лог) |
| Нажатие **LSHIFT+R** | клиент | `ARMST_PLAYER_CharacterController.c:28` → `ARMST_WEAPONS_HANDLER.c:354-388` (`OnRackBoltMDown`) | `RpcAsk_TAO_ManualRack` + `inputCtx.SetReloadWeapon(1)` |
| Запрос помпы на сервер | сервер | `ARMST_WEAPONS_HANDLER.c:232-253` | `m_ServerManualRackPending=true`, фолбэк-таймер |
| Анимация | граф | `MP133*.agf` `WeaponReloadSTM.ReloadActionBolt` (`GetCommandI==1`) → `RackBoltAnim` | клип `W_MP133_Reload_Bolt.anm` = `{45B1772B8AFEAE46}`, события `BlendIn(5)/Weapon_EnableFire(10)/Weapon_Rack_Bolt(14)` |
| Событие помпы | сервер | `ARMST_WEAPONS_HANDLER.c:169-227` | по `Weapon_Rack_Bolt`: `TAO_DecrementAmmoOnRack()` + `TAO_ClearChamberIfNoMagOrEmpty()` |
| Списание трубы | сервер | `ARMST_WEAPONS_HANDLER.c:295-314` | `mag.SetAmmoCount(count-1)` — **единственная** запись трубы на помпу |
| Патронник | — | **нет кода** | `TAO_ClearChamberIfNoMagOrEmpty` только **очищает** (`ClearChamber`) |
| Следующий выстрел | движок | — | невозможен: патронник пуст |

**Вывод 1.1:** проектный код помпы **никогда не заполняет патронник**. Он умеет
только `tube−1` и (при пустой трубе) `ClearChamber`.

### 1.2 Поштучная досылка в трубу (лаба, гейт ON — сейчас OFF)

| Шаг | Файл:строки | Примечание |
|---|---|---|
| Входной гейт R | `ARMST_MP133_Lab_Character.c:441-524` | один заход на удержание, deferred begin |
| Пуск | `:549-629` | `inputCtx.SetReloadWeapon(7)` (пульс) |
| Граф | `MP133_Lab.agf` `InsertSingleProjectile` (`GetCommandI==7`) → `InsertMagAnim` | источник `Reload.Reload_InsertMag` |
| Клип | `MP133_Lab_weapon.asi:16-21` | `{1F9884C8701DAE1B}…/LabClips/W_MP133_Lab_Inject.anm` — события только `ARMST_Lab_Shell_Spawn/Commit/Release`, `BlendIn/Out` |
| Коммит | `ARMST_MP133_Lab_Character.c:754-820` | по `ARMST_Lab_Shell_Commit`: `reserve--`, `tube.SetAmmoCount(+1)` |

Патронник здесь не участвует вообще — досылка только в **трубу**.

---

## 2. Кто пишет трубу и патронник (проектный код, grep)

**Труба (`BaseMagazineComponent.SetAmmoCount`) пишут:**
- движок (выстрел);
- Core `TAO_DecrementAmmoOnRack` (`ARMST_WEAPONS_HANDLER.c:312`);
- Core `WeaponHandler` — «обрезка» до `m_MaxMagazineAmmo` (`:485`) и спавн лишнего магазина (`:507`);
- лаба `LabServerCommitInsert` (`:815`).

**Патронник (`BaseMuzzleComponent`) пишет:**
- **никто.** Публичный API (`interfaceBaseMuzzleComponent.html`) даёт только
  `ClearChamber(int)` и геттеры `IsBarrelChambered / IsCurrentBarrelChambered /
  IsChamberingPossible / GetAmmoCount / GetMaxAmmoCount`. **Сеттера патронника
  нет.** `BaseWeaponComponent` даёт только `IsChamberingNecessary /
  IsChamberingPossible / IsReloadPossible` (запросы).
- Значит, `chambered:0→1` — **внутренняя логика движка**, недоступная из
  мод-скрипта документированным API.

**Вывод 2:** «помпа не заполняет патронник» нельзя исправить скриптом лабы
напрямую (нет API). Это не артефакт нашего кода — нашего кода на патронник нет.

---

## 3. Что именно изменила лаба (и что нет)

Изменения только lab-only, по сравнению с прод-`armst_Shotgun_mp_133.et`:

1. **Граф (`MP133_Lab.agf`), `WeaponReloadSTM`:**
   `Child "MagReloadSTM"` ×2 → `InsertMagAnim`; `Child "RemoveMagAnim"` →
   `InsertMagAnim` (offline-скрипт `mp133_lab_connect_anims.py --harden-graph`).
   Ветка **помпы `ReloadActionBolt`/`RackBoltAnim` не тронута**.
2. **ASI (`MP133_Lab_weapon.asi`/`_player.asi`):** перепривязаны только строки
   `Reload.Erc/Pne.Reload_InsertMag` → санитизированный клип без событий
   `Weapon_SpawnMagazine/AttachMagazine/MagRelease`.
3. **Префаб:** `MuzzleComponent.MagazineTemplate` → lab-магазин 3 патрона;
   `ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo 3`; у **non-RIS** варианта
   `ARMST_SHOTGUN_COMPONENTS { Enabled 0 }` (у RIS `Enabled 0` нет);
   lab-граф/ASI. `FireModes.ManualAction 1` наследуется (блок `MuzzleComponent`
   — тот же GUID, merge).
4. **Магазин:** `armst_12ga_Lab_3rnd.et` — `MaxAmmo 3`, `AmmoMapping {0 0 0}`,
   наследует `AmmoConfig`/`MagazineWell` от `12ga_Buckshot_base.et`
   (`MaxAmmo 10`, `AmmoMapping {0×10}`). Калибр/тип совпадает.

**Не изменено:** ветка помпы, `ReloadActionBolt`, события `Weapon_Rack_Bolt/
Weapon_EnableFire`, оригинальные клипы `W_MP133_Reload_Bolt.anm` и т.д.

---

## 4. Факты (лог владельца) vs гипотезы

**Факты (из лога, comment 5958821529):**
- после выстрела `chambered 1→0`, труба `2/3` не меняется;
- на LSHIFT+R (`type=1`, `pump action (LSHIFT+R) fired -> not an insert`):
  труба `2/3→1/3→0/3`, **патронник остаётся `0/1`**;
- резерв 30, ни одного лабораторного `ACTION_BEGIN/SERVER COMMIT` (гейт OFF).

**Проектно-доказано:**
- единственная запись трубы на помпу — Core `TAO_DecrementAmmoOnRack`;
- заполнения патронника в проектном коде нет и публичного API нет;
- ветка помпы графа/клипов идентична проду → лаба её не ломала.

**Гипотезы (нужен рантайм для подтверждения):**
- *(сильная)* движок заполняет патронник на **нативных событиях замены
  магазина** (`Weapon_AttachMagazine` и т.п.). В проде обычный **R** играл
  `InsertMagAnim` с этими событиями (`W_MP133_Reload_Inject.anm`) → движок
  прикреплял магазин и досылал патрон. Лаба заменила эти строки
  санитизированным клипом без событий → досылка в патронник исчезла. Тогда
  «помпа» владельца в проде — это фактически нативная перезагрузка по **R**,
  а не Core-помпа по LSHIFT+R (последняя и в проде только списывает).
- *(слабая)* `ARMST_SHOTGUN_COMPONENTS { Enabled 0 }` на non-RIS как-то влияет.
  Против: у RIS его нет; компонент не имеет колбэков.
- *(неизвестно)* точное событие/условие, по которому движок досылает патрон —
  из проектных файлов не доказуемо, движок не исследуем.

**Про «пустой `prefab=`»:** это чисто диагностическое поле
(`LabWeaponIdentity` → `GetPrefabData().GetPrefabName()`). Игровой роли не
играет; `labComp=1` подтверждает, что оружие то.

---

## 5. Почему «R» владельца работал в проде, а в лабе — нет

- В проде **обычный R** = нативная перезагрузка (`MagReload`/`InsertSingleProjectile`
  → `InsertMagAnim` = `W_MP133_Reload_Inject.anm` с `Weapon_SpawnMagazine/
  AttachMagazine/MagRelease`) → движок сам досылает патрон. Да, ценой
  «замены трубчатого магазина» (то, что прод-костыль и режет/спавнит).
- **LSHIFT+R** = Core-помпа (`TAO_DecrementAmmoOnRack`) → патронник не
  заполняет и в проде.
- Наша лаба (для V2.5-плана R=досылка, LSHIFT+R=помпа) отобрала у R нативные
  события и повесила досылку в трубу — патронник заполнять стало **нечем**.

---

## 6. Предлагаемая минимальная lab-only коррекция (нужно одобрение)

Порядок владельца: **сначала вернуть подачу патрона помпой**, затем
короткое/долгое R. Гейт до исправлений — OFF.

**Идея:** вернуть нативной ветке перезагрузки досылку патрона (её события), а
санитизированный клип оставить **только** лабораторной поштучной досылке.

- **C1 (основная правка, lab-only):**
  1. в lab-графе вернуть `MagReload`/`MagNoBulletReload` → `MagReloadSTM`,
     `RemoveMag` → `RemoveMagAnim` (снять hardening);
  2. строки ASI `Reload.Erc/Pne.Reload_InsertMag` вернуть на **оригинальный**
     `W_MP133_Reload_Inject.anm` (события `Weapon_AttachMagazine` и т.д. —
     нативная досылка патрона вернётся);
  3. добавить **отдельную** lab-строку/источник для санитизированного клипа
     (новая `AnimSetInstanceSource_Line`, напр. `Reload.Reload_InsertMag_Lab`,
     + строка в `MP133_Lab.ast` + `AnimSrcNodeSource`) и направить на неё
     **только** состояние `InsertSingleProjectile` (`CMD_Weapon_Reload==7`).
  - Итог: обычная перезагрузка (короткий R/помпа) снова досылает патрон, а
    долгий R-досылка остаётся без mag-swap.
- **C2 (диагностика, одновременно, если C1 не подтвердится):** lab-only лог
  `wpn.IsChamberingNecessary()/IsChamberingPossible()`, `muzzle.IsCurrentBarrelChambered()`,
  `muzzle.GetAmmoCount()` на каждом `Weapon_*`-событии (клиент+сервер) и в
  `STATE`, чтобы увидеть, считает ли движок досылку возможной вообще.

**Управление (после C1):** короткий R = **нативная** перезагрузка/помпа
(досылает патрон), удержание R > ≈250 мс = лабораторная поштучная досылка.
Порядок обработки: на key-down лабораторный хук **не** начинает досылку сразу,
а решения принимает на пороге/отпускании (короткое нажатие отдаётся нативной
ветке). Это укладывается в требование владельца и снимает конфликт «одно
нажатие → помпа и досылка».

**Откат:** lab-префабы/graph/ASI — из `artifacts/MP133_Lab/prefab_backups/` и
текущих бэкапов; прод/Core/миры/движок не трогаются.

**Проверка (owner test, гейт OFF для C1):**
1. выстрел → `chambered 1→0`;
2. R (нативно) → труба `−1`, **`chambered 0→1`**, возможен следующий выстрел;
3. `STATE … chambered=1/1`; отсутствие лишних mag-сущностей.

**Что не делаем:** не «досыпаем» патрон в патронник скриптом (нет API —
это был бы фейк), не трогаем прод/Core, не включаем гейт досылки до
подтверждения помпы.

---

## 7. Открытый вопрос к решению владельца

Нативная досылка патрона по короткому R в проде сопровождалась «заменой
трубчатого магазина» (её и обходит лаба). Поэтому нужно выбрать:
- **(A)** короткий R = нативная перезагрузка (досылает, но возможен визуальный
  mag-swap), долгий R = lab-досылка; либо
- **(B)** искать lab-only событие/клип, сохраняющий досылку патрона без
  mag-swap (C2-диагностика покажет, какое событие досылает).

Рекомендация: начать с **C2-диагностики (гейт OFF)** + **C1**, один прогон
проверяет обе гипотезы без включения лабораторной досылки.
