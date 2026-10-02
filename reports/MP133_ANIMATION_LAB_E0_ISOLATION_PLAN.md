# MP-133 — E0 результат и план изоляции (read-only)

**Статус:** `SHARED_ENVIRONMENT_MANUAL_R_REGRESSION; root cause UNKNOWN`.
Только анализ. Код лабы/прод/Core/граф/ASI/ANM/префабы **не менялись**; оба гейта
`m_bLabInsertEnabled` — **OFF**; Workbench/игру агент не запускает.
Источник: Issue #27, comment 5961221260.

---

## 1. Результат E0 (факты владельца)

| | Оригинальный MP-133 (`lab=0`) | MP-133 [LAB] (`lab=1`) |
|---|---|---|
| Экипировка | `tube 10→2→1/10`, `chamber 0→1` | `tube →2/3`, `chamber 0→1` |
| После выстрела | `tube 1/10`, `chamber 0/1` | `tube 2/3`, `chamber 0/1` |
| Запрос R | `CMDCHG id=21 reloadType=1 start=1` | `reloadType=1`, повторяется |
| После R | `tube 1/10`, `chamber 0/1` | `tube 2/3`, `chamber 0/1` |
| `Weapon_Rack_Bolt` | **не зафиксирован** | **не зафиксирован** |

Выводы, которые можно сделать:
- **Оба** оружия ведут себя одинаково (обычный R после выстрела не наполняет
  патронник), при этом на **экипировке** патронник заполняется у обоих
  (`tube −1`, `chamber 0→1`) — то есть один нативный механизм подачи работает.
- После обычного R **не наблюдается** ни `Weapon_Rack_Bolt`, ни mag-событий.
  Это **ключевой сигнал**: похоже, клип передёргивания не проигрывается/не
  эмитит событие. Это наблюдение, не доказательство.
- E0 на «оригинале» шёл **при загруженной лабе** (`lab=0` = лишь отсутствие
  lab-компонента на оружии, не отсутствие глобальных lab-скриптов) — поэтому
  виновника по этому логу установить нельзя.

---

## 2. Read-only проверка общего кода (задание п.1)

### 2.1 Переопределения `HandleWeaponReloading`

Во **всех** загруженных аддонах (`Core`, `Weapons`, `MP133_AnimationLab`,
`Equipments`, `MO-Furnitures`, `MO-Vehicles`, `RangeScanner`, `Armst_Work`,
`Arm_Structura`, `ReforgerToolkit`) переопределяет `HandleWeaponReloading`
**только** lab:

- `ARMST_MP133_Lab_CommandHandler.c:30` — `override bool HandleWeaponReloading(...)`.
- Core/прочие — **не** переопределяют. `HandleWeaponReloadingDefault` **нигде**
  не переопределяется.

**Pass-through для не-lab и для lab при гейте OFF — подтверждён по коду:**

```
override bool HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID)
{
    ...только логирование C2 (без мутаций)...
    ctrl = Cast(GetControllerComponent());
    if (ctrl && ctrl.LabInsertEnabledOnCurrentWeapon())   // для не-lab = false
    { ctrl.LabRequestInsertFromHandler(pInputCtx); return true; }
    return super.HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID); // ← как vanilla
}
```

`LabInsertEnabledOnCurrentWeapon()` → `GetCurrentWeaponLab()` → `LabCompOf()`
— только чтение; для оружия без lab-компонента возвращает `false`. Мутации
псевдо-команды нет.

### 2.2 Кто ещё мутирует команду перезарядки

`SetReloadWeapon` во всём проекте встречается **только**:
- Core `ARMST_WEAPONS_HANDLER.c:387` — внутри `OnRackBoltMDown` (**LSHIFT+R**,
  `ARMST_LIGHT_RELOAD_ACTION`), не обычный R;
- lab `Character.c:934/950` — пульс type 7 / сброс, только при гейте ON.

`inputCtx.SetReloadWeapon(1)` для обычного R не вызывает **никакой** скрипт —
команду задаёт движок.

### 2.3 Общие (merged) переопределения, затрагивающие персонажа/оружие

- Core: `modded SCR_CharacterControllerComponent` ×2 (мышь/раскладка + rack
  AnimEvent), `modded SCR_WeaponInfo`, `modded SCR_MuzzleEffectComponent` (пусто),
  `modded SCR_ChimeraCharacter`, камера/урон.
- Lab: `modded SCR_CharacterControllerComponent`, `modded SCR_CharacterCommandHandlerComponent`.

`OnReloaded` в Core пуст (зовёт super); `OnInit`/`OnControlledByPlayer`/
`OnApplyControls` лабы зовут super и только читают/логируют + вешают слушатель
`ARMST_LIGHT_RELOAD_ACTION`. На reload-команду не влияют. Но **полностью
исключить глобальный эффект merged-переопределений статически нельзя** — нужен
изоляционный тест.

### 2.4 Привязка перезагрузки `ReloadActionBolt` (read-only)

- Оригинал: ASI `MP133_weapon.asi` `Reload.Erc/Pne.ReloadActionBolt` →
  `{45B1772B8AFEAE46}…/Reload/W_MP133_Reload_Bolt.anm`.
- Лаба: `MP133_Lab_weapon.asi` — **та же** строка/GUID (не менялась).
- Клип `W_MP133_Reload_Bolt.anm` существует; события: `BlendIn`(5),
  `Weapon_EnableFire`(10), `Weapon_Rack_Bolt`(14).
- Граф: `ReloadActionBolt` (`Child "RackBoltAnim"`, `Source "Reload.Reload_ActionBolt"`)
  StartCondition `GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(...) == 0.0`.
- Для cmd 1 lab-граф и прод-граф **идентичны** (hardening затрагивает только
  `MagReload`/`MagNoBulletReload`/`RemoveMag`).

Замечание по путям: строки ASI используют **относительный** путь
(`Mp_133/Workspace/…`), как и другие ARMST-дробовики (`Shootgun/…`), тогда как
`.meta Name` — полный (`Assets/Weapons_RUS/…`). У части соседних дробовиков эти
ссылки уже помечены как unresolved. Форма пути — **кандидат**, но «совпадение
пути ≠ рантайм-событие»: выводов не делаю, проверяется изоляцией.

---

## 3. Версия и хронология (только факты)

- Установленная игра: **1.8.0.13** (`ArmaReforgerSteam.exe` FileVersion), Tools
  buildid 24870687. Это ровно та версия, что указана владельцем.
- Core `ARMST_WEAPONS_HANDLER.c` не менялся с **2026-06-30**; последний коммит
  `ARMST_PLAYER_CharacterController.c` — **2026-09-23** (добавлены surrender-
  контролы, к reload не относится).
- Weapons: **2026-09-22** `fix(refs): sync resource references … after asset
  relocation` затронул у MP-133 только `.meta` (Name paths); содержимое
  `.asi`/`.agf`/`.agr` не менялось. Затем `9ee6248 revert(meta): restore .meta
  Name paths`.
- Нет найденных доказательств, что апдейт движка сломал reload; нет и
  доказательств обратного.

---

## 4. План изоляции (owner-only, обратимый; менять ровно одну переменную)

Правило: мир/слои/прод не редактировать ради сравнения. Если отключить лабу в
текущем мире нельзя безопасно — зафиксировать блокер.

- **I0 (сделано):** оригинал + **лаба загружена** → падает (E0).
- **I1 (ключевой):** оригинальный MP-133 + **lab-аддон ВЫКЛЮЧЕН** (прод + Core
  включены), отдельная безопасная сцена **без** ссылок на lab-префабы/скрипты.
  Тот же сценарий: `Single.ManualAction`, baseline `tube`/`chamber`, один
  выстрел, один обычный R.
  - Если заработало → виноват **глобальный merged-код лабы** (её
    `SCR_CharacterControllerComponent`/`CommandHandler`), не оружие.
  - Если не заработало → причина в **Core/прод/версии/ресурсах**, лаба ни при чём.
- **I2 (опционально, при выключенной лабе):** любое **ванильное** manual-action
  оружие (болт/помпа) в base game, тот же цикл. Отличает «сломан движок/версия»
  от «сломан конкретный MP-133/проект».
- **I3 (опционально, только владелец, обратимо):** оригинал с **закоммиченной**
  (не dirty) версией `MP133.agf` — проверить незакоммиченный WIP владельца.
  Замечу: diff dirty-графа (условие `inRange(7,9)→(8,9)` + `InsertSingleProjectile`)
  **не затрагивает** путь cmd 1, поэтому это скорее контрольный, чем основной тест.

При выключенной лабе C2-маркеры исчезнут: тогда собирать **визуальное**
передёргивание + UI патронов + нативные логи; отсутствие C2-строк не считать
доказательством отсутствия действия.

---

## 5. Чего не делаем

- Не правим граф/ASI/ANM/префабы, не добавляем `ReloadWeapon()`, не подавляем
  Core, не активируем J, не трогаем прод/Core/мир/слои.
- Не приписываем регрессию «движку» или «лабе» без I1/I2.
- E1–E4 остаются приостановленными; оба гейта OFF.

---

## 6. Факты / гипотезы / неизвестное

| Утверждение | Статус |
|---|---|
| Только lab переопределяет `HandleWeaponReloading`; pass-through для не-lab | **ФАКТ (код)** |
| Core не переопределяет reload-хендлер/`…Default`; мутирует команду только LSHIFT+R | **ФАКТ (код)** |
| `ReloadActionBolt` wiring/GUID/события присутствуют и идентичны оригинал/lab | **ФАКТ (файлы)** |
| После обычного R нет `Weapon_Rack_Bolt`/mag-событий; патронник не наполняется | **НАБЛЮДЕНИЕ владельца** |
| На экипировке патронник наполняется | **НАБЛЮДЕНИЕ владельца** |
| Причина регрессии — lab / Core / версия / ресурсы | **НЕИЗВЕСТНО** (I1/I2) |
| Относительная форма путей ASI — причина | **НЕ ПРОВЕРЕНО** (кандидат) |

**Следующий шаг:** одобрить и выполнить **I1** (оригинал при выключенной лабе,
прод/Core включены) — один изолированный прогон; затем, при необходимости, I2.
