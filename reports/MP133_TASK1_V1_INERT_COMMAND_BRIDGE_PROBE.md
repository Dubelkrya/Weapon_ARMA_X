# MP-133 Task #1 — V1 inert reload-command bridge probe (SOURCE PREP ONLY)

Статус: **T4B_V1_INERT_BRIDGE_RACK_BYPASS_REVIEW_PASS_WAITING_WB_CLOSED**
Дата: 2026-10-05
Задание: Issue #34 — «V1 inert reload-command bridge probe (SOURCE PREP ONLY)» ([#6001717566](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)) + one-shot ревизия + review-pass + owner GO.
Режим: **source prep only**. Live = предыдущий one-shot вариант (`5CBB22C1…`, установлен ранее); rack-bypass ревизия **НЕ в live**. ASTRA2/prefab/world/Core/grid/inventory — не тронуты.

Вопрос probe: **может ли pickup-safe V1 handler потребить обычный `R` и выставить уже-доказанную инертную reload-команду, которая дойдёт до weapon-local animation receiver, не запустив native whole-mag reload и не изменив tube/ammo/chamber?**

---

## Phase A — выбор команды (re-verified по ТЕКУЩЕМУ lab-графу)

Источник: `ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraShellGraph_test/MP133_Astra2.agf` (**SOURCE**, активный lab-граф).

Все вхождения `CMD_Weapon_Reload` в текущем ASTRA2:
| Строка | Условие |
|---|---|
| L221 | `ShellReloadSTM` entry: `… && !IsCommand(CMD_Weapon_Reload)` |
| L259, L301 | `IdleReloadSTM`/`ReloadRouteSTM` entry: `IsCommand(CMD_Weapon_Reload) && GetCommandI(CMD_Weapon_Reload) == 1 && GetCommandF(CMD_Weapon_Reload) == 0.0` |
| L266, L313 | exit: `(RemainingTimeLess(…) || GetCommandI(CMD_Weapon_Reload) == -2) …` |
| L336 | `RackStanceSTM` state `StartCondition "GetCommandI(CMD_Weapon_Reload) == 1 && …"` |

Выводы (**SOURCE**):
- В активном ASTRA2 **единственная командная ветка reload — `1` (bolt/rack)**; старые whole-mag состояния (`WeaponReloadSTM`/`MagReloadSTM`/`InsertMagAnim`/`RemoveMagAnim`) **удалены** (Stage D). Нет `inRange(7,9)`-veto, нет cmd2–6, нет cmd10.
- Клипы `Reload_Inject`/`Reload_RemoveMag` с событиями `Weapon_Spawn/Attach/Detach/DespawnMagazine` больше **не referenced** активным графом.
- `CharacterInputContext.SetReloadWeapon(int ReloadType)` — **`proto external void`** (SDK **SOURCE**), документированный input-context API. Отдельного enum reload-типов в SDK нет.

**Выбранная инертная команда: `10`.**
Проверка по критериям задачи:
| Критерий | cmd10 |
|---|---|
| нет native magazine spawn/attach/detach/despawn **в графе** | ✓ (нет состояния, клипы не referenced) |
| нет bolt/rack path | ✓ (bolt = cmd1) |
| нет production meaning в lab-графе | ✓ (нет состояния) |
| нет ammo/chamber writer | ✓ (в графе writers отсутствуют) |

**Оговорка (честно):** инертность на уровне **native engine** для cmd10 — **UNRESOLVED** (тело `HandleWeaponReloadingDefault` в SDK-референсе недоступно). Именно это probe и измеряет: если появятся side effects — `INERT_COMMAND_CAUSED_NATIVE_SIDE_EFFECT_STOP`. Fallback `NO_SAFE_INERT_RELOAD_COMMAND_FOUND` не сработал: cmd10 — единственная команда, удовлетворяющая graph-level критериям.

---

## Phase B — подготовленные исходники (staged, НЕ в live)

Каталог: `Weapon_ARMA_X/artifacts/astra-rebuild/stageInertBridge/`

### B1. `ARMST_T4B_NormalRHandlerProbe.c` — **RACK BYPASS ревизия**
- SHA-256 staged: `83DA1EC584B13D251359B776D2C05AEE41E07A42ACB3334389814C0501BA8B39`.
- Base = текущий live one-shot handler (`5CBB22C18B29D64E16E36DCABE85642BDB08951D0B4F3F46CFE3B7E4A5E7BE20`).
- Изменение **только** rack-bypass + один лог-латч `m_bRackBypassLogged`:
  - **LAB + `reloadType == 1`:** НЕ вызывать `SetReloadWeapon(10)`, НЕ ставить one-shot латч, НЕ consume'ить → `return super.HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID);` (штатный native bolt/rack не трогаем); один раз лог `phase=rack-bypass reloadType=1 consumed=0 setCmd10=0 -> super`.
  - **LAB + `startReloading == true` + `reloadType != 1`:** one-shot латч (`m_bInertCmdSet`, латч **до** setter) → ровно один `pInputCtx.SetReloadWeapon(ARMST_T4B_INERT_RELOAD_CMD);` + лог `phase=inert-command-set once=1`; затем consume (`return true`).
  - `else if (startReloading && reloadType != 1 && !m_bInertCmdSkipLogged)` → один раз лог `phase=inert-command-skip`.
- **Порядок (code):** rack-bypass блок L87–95 (`return super` L94) **до** `SetReloadWeapon` L101 → rack path физически не достигает setter'а.
- Non-lab путь **не изменён**: `if (!probe) return super.HandleWeaponReloading(...)`.
- Consume сохранён **только** для non-rack lab-запроса.

### B2. `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` (base = текущий live AstraV2)
- SHA-256 staged: `B3D71CF57ACBF95C55D4B0098FDDACF86F00CF9B93AA88C287856D9914228D28` (base live `DBBD9B49C376123A702BDF16C5F7EA16CCC147F1A67947E6C5AB07E0F1FDD00B`).
- Добавлен **только** weapon-local observer:
  `override void OnCharacterCommand(int commandID, int intValue, float floatValue)` → `super` + лог `[ARMST-T4B-CMDROUTE] receiver=weapon commandID=… intValue=… floatValue=… isReloadCommand=… inert=…`.
- **Маршрут считается доказанным ТОЛЬКО при совпадении обоих:** `inert = (commandID == ARMST_T4B_RELOAD_COMMAND_ID) && (intValue == ARMST_T4B_INERT_RELOAD_CMD)` — **не** по `intValue` alone. `isReloadCommand` логируется отдельно.
- Observation only; no graph transition.

### B3. Reload command-id constant (evidence)
`const int ARMST_T4B_RELOAD_COMMAND_ID = 0;` — evidence: T2c owner runtime наблюдал `commandID=0` и для native rack (`intValue=1`), и для stock remove+insert (`intValue=5`). SDK **не** публикует именованной константы `CMD_Weapon_Reload` (анимационные команды биндятся строкой через `SCR_CharacterAnimationComponent.BindCommand`, см. `ARMST_Consumable.c`: `BindCommand("CMD_HealSelf")`). Поэтому тип reload-команды зафиксирован по наблюдаемому значению; **raw `commandID`/`intValue` логируются всегда**, чтобы владелец мог скорректировать константу по рантайм-факту.

### Диффы (exact)
- `stageInertBridge/diff_handler_live_to_rackbypass.diff` — added 28 / removed 12 (vs текущий live one-shot handler; логика — только rack-bypass блок + лог-латч `m_bRackBypassLogged`).
- `stageInertBridge/diff_astraV2_to_observer.diff` — added 20 / removed 0 (observer без изменений).

### Static proofs
| Проверка | handler | observer |
|---|---|---|
| braces | 14/14 | 15/15 |
| parens | 61/61 | 73/73 |
| `override void Update` | 0 | 0 |
| `override bool HandleWeapons` | 0 | 0 |
| forbidden writers (`SetAmmoCount`/`ReloadWeapon`/`ReloadWeaponWith`/mag spawn-attach-detach-despawn-release/`CallCommand`/`SetVariableBool`/`ASTRA_ShellRequest`/`ClearChamber`) | **0** | **0** |
| `reloadType == 1` → `super` (rack bypass) | **1** | — |
| `SetReloadWeapon` (разрешённый API) | 1 callsite, **только** после rack-bypass (non-rack) | 0 |
| one-shot латч на rack path | **не ставится** (rack `return super` L94 < setter L101) | — |
| `m_bInertCmdSet` (латч) | 3 (decl/check/set) | 0 |
| `isReloadCommand && intValue==10` (доказательство) | — | 1 (`inert=`) |
| non-lab `super` path | сохранён | n/a |

### Rollback
- Точный V1: SHA-256 `D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32` (файл `stageV1/…`, git `57c7124`).
- AstraV2 base: SHA-256 `DBBD9B49C376123A702BDF16C5F7EA16CCC147F1A67947E6C5AB07E0F1FDD00B`.

---

## Future owner runtime acceptance test (НЕ авторизован)

После отдельного GO — правильная последовательность:
```
выстрел            → chambered=0
первый R           → reloadType=1
                   → native rack через super
                   → chambered=1   (патронник снова заряжен)
второй R           → смотрим raw reloadType
```
1. Cold-start Workbench → свежий `weapon_test`.
2. Equip canonical ASTRA2 lab MP-133.
3. **Выстрел** → `chambered=0`.
4. **Первый R** (патронник пуст):
   - `reloadType=1`;
   - native rack через `super`;
   - после успешного передёргивания **`chambered=1`** (патронник снова заряжен, НЕ пуст);
   - `phase=inert-command-set` **НЕ** появляется (cmd10 не выставлен).
   → `NATIVE_RACK_BYPASS_PASS`.
5. **Второй R** — уже при **заряженном** патроннике (`chambered=1`); именно он должен показать, что движок считает «обычной перезарядкой трубки». Смотреть raw `reloadType`:
   - `reloadType != 1` → ожидается one-shot cmd10 probe + weapon-local `[ARMST-T4B-CMDROUTE] … isReloadCommand=1 inert=1` → `R_TO_INERT_COMMAND_TO_WEAPON_RECEIVER_PROVEN`;
   - `reloadType` снова `1` → `POST_RACK_RELOADTYPE_STILL_1_STOP`, больше не экспериментировать.

Outcome labels:
- `NATIVE_RACK_BYPASS_PASS`
- `R_TO_INERT_COMMAND_TO_WEAPON_RECEIVER_PROVEN`
- `POST_RACK_RELOADTYPE_STILL_1_STOP`

---

## Итог
- cmd10 re-verified как graph-level инертный; engine-level инертность измеряется probe'ом.
- Исходники подготовлены (2 файла), НЕ записаны в live.
- Ничего из forbidden не использовано; `Update=0`, `HandleWeapons=0`; non-lab путь не изменён.

Статус: **`T4B_V1_INERT_BRIDGE_RACK_BYPASS_REVIEW_PASS_WAITING_WB_CLOSED`**. STOP.

---

## LIVE INSTALL (owner GO, Workbench закрыт)

Ровно два файла установлены в live + labs:

| файл | SHA-256 | live overrides |
|---|---|---|
| `Scripts/Game/ARMST_T4B/ARMST_T4B_NormalRHandlerProbe.c` | `5CBB22C18B29D64E16E36DCABE85642BDB08951D0B4F3F46CFE3B7E4A5E7BE20` | `HandleWeaponReloading=1`, `SetReloadWeapon=1` (one-shot, `m_bInertCmdSet`), `Update=0`, `HandleWeapons=0` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | `B3D71CF57ACBF95C55D4B0098FDDACF86F00CF9B93AA88C287856D9914228D28` | `OnCharacterCommand=1` (`isReloadCommand && intValue==10` → `inert`) |

Rollback: V1 `D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32` + AstraV2 base `DBBD9B49C376123A702BDF16C5F7EA16CCC147F1A67947E6C5AB07E0F1FDD00B`.

**Cold-start тест (owner):** cold Workbench → equip canonical ASTRA2 lab MP-133 → snapshot tube/ammo/chamber → один обычный `R` → ожидание: `[ARMST-T4B-RPROBE] phase=inert-command-set inertCmd=10 once=1` **и** `[ARMST-T4B-CMDROUTE] receiver=weapon … isReloadCommand=1 inert=1`; без native CMD1/2–6, без замены magazine identity, ammo/chamber неизменны, pickup работает.
