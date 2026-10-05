# MP-133 Task #1 — V1 inert reload-command bridge probe (SOURCE PREP ONLY)

Статус: **T4B_V1_INERT_COMMAND_BRIDGE_ONESHOT_SOURCE_PREPARED_OWNER_REVIEW**
Дата: 2026-10-05
Задание: Issue #34 — «V1 inert reload-command bridge probe (SOURCE PREP ONLY)» ([#6001717566](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **source preparation only**. Live **НЕ изменялся** (даже при закрытом Workbench). ASTRA2/AGR/AGF/ASI/AW/ANM/prefab/world/Core/grid/inventory — не тронуты.

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

### B1. `ARMST_T4B_NormalRHandlerProbe.c` (base = текущий V1) — **ONE-SHOT**
- SHA-256 staged: `5CBB22C18B29D64E16E36DCABE85642BDB08951D0B4F3F46CFE3B7E4A5E7BE20`.
- Base = pickup-safe V1 (`57c7124`), SHA-256 `D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32`.
- Добавлено **только**:
  - файловые глобалы `const int ARMST_T4B_INERT_RELOAD_CMD = 10;` и `const int ARMST_T4B_RELOAD_COMMAND_ID = 0;` (см. ниже);
  - латч-поля `m_bInertCmdSet` / `m_bInertCmdSkipLogged`;
  - в lab-ветке `HandleWeaponReloading`, при `startReloading && pInputCtx && !m_bInertCmdSet`: `m_bInertCmdSet = true;` (латч **до** сеттера) → `pInputCtx.SetReloadWeapon(ARMST_T4B_INERT_RELOAD_CMD);` + лог `phase=inert-command-set once=1`;
  - `else if (startReloading && pInputCtx && !m_bInertCmdSkipLogged)` → один раз лог `phase=inert-command-skip alreadySet=1` (подтверждение латча без спама).
- **One-shot rationale:** V1 уже показал, что `HandleWeaponReloading()` вызывается много кадров подряд при `startReloading=true`; без латча это дало бы многократный `SetReloadWeapon(10)`, а engine-level поведение cmd10 не доказано. Латч гарантирует **ровно один** `SetReloadWeapon` на один cold-start тест; повторные вызовы только логируются (один раз).
- Non-lab путь **не изменён**: `if (!probe) return super.HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID);`.
- Consume сохранён: `return true`.

### B2. `ARMST_T4B_AstraV2_WeaponAnimationComponent.c` (base = текущий live AstraV2)
- SHA-256 staged: `B3D71CF57ACBF95C55D4B0098FDDACF86F00CF9B93AA88C287856D9914228D28` (base live `DBBD9B49C376123A702BDF16C5F7EA16CCC147F1A67947E6C5AB07E0F1FDD00B`).
- Добавлен **только** weapon-local observer:
  `override void OnCharacterCommand(int commandID, int intValue, float floatValue)` → `super` + лог `[ARMST-T4B-CMDROUTE] receiver=weapon commandID=… intValue=… floatValue=… isReloadCommand=… inert=…`.
- **Маршрут считается доказанным ТОЛЬКО при совпадении обоих:** `inert = (commandID == ARMST_T4B_RELOAD_COMMAND_ID) && (intValue == ARMST_T4B_INERT_RELOAD_CMD)` — **не** по `intValue` alone. `isReloadCommand` логируется отдельно.
- Observation only; no graph transition.

### B3. Reload command-id constant (evidence)
`const int ARMST_T4B_RELOAD_COMMAND_ID = 0;` — evidence: T2c owner runtime наблюдал `commandID=0` и для native rack (`intValue=1`), и для stock remove+insert (`intValue=5`). SDK **не** публикует именованной константы `CMD_Weapon_Reload` (анимационные команды биндятся строкой через `SCR_CharacterAnimationComponent.BindCommand`, см. `ARMST_Consumable.c`: `BindCommand("CMD_HealSelf")`). Поэтому тип reload-команды зафиксирован по наблюдаемому значению; **raw `commandID`/`intValue` логируются всегда**, чтобы владелец мог скорректировать константу по рантайм-факту.

### Диффы (exact)
- `stageInertBridge/diff_handler_V1_to_inert.diff` — added 49 / removed 15 (удаления только в шапке-комментарии; логика — только `const`×2 + one-shot блок `SetReloadWeapon`).
- `stageInertBridge/diff_astraV2_to_observer.diff` — added 20 / removed 0.

### Static proofs
| Проверка | handler | observer |
|---|---|---|
| braces | 12/12 | 15/15 |
| parens | 57/57 | 73/73 |
| `override void Update` | 0 | 0 |
| `override bool HandleWeapons` | 0 | 0 |
| forbidden writers (`SetAmmoCount`/`ReloadWeapon`/`ReloadWeaponWith`/mag spawn-attach-detach-despawn-release/`CallCommand`/`SetVariableBool`/`ASTRA_ShellRequest`/`ClearChamber`) | **0** | **0** |
| `SetReloadWeapon` (разрешённый API) | 1 (one-shot, латч) | 0 |
| `m_bInertCmdSet` (латч) | 3 (decl/check/set) | 0 |
| `isReloadCommand && intValue==10` (доказательство) | — | 1 (`inert=`) |
| non-lab `super` path | сохранён | n/a |

### Rollback
- Точный V1: SHA-256 `D16D3D436A030C86A61DDE3C98A88D3B9EB62BE761B83812DD82CC302E1FAF32` (файл `stageV1/…`, git `57c7124`).
- AstraV2 base: SHA-256 `DBBD9B49C376123A702BDF16C5F7EA16CCC147F1A67947E6C5AB07E0F1FDD00B`.

---

## Future owner runtime acceptance test (НЕ авторизован)

После отдельного GO: cold Workbench → equip canonical ASTRA2 lab MP-133 → снять tube identity/ammo/chamber → один обычный `R` → требуется:
- handler видит запрос и логирует `phase=inert-command-set inertCmd=10`;
- weapon-local `[ARMST-T4B-CMDROUTE] receiver=weapon … inert=1` (та же инертная команда);
- нет native CMD1/2–6 route;
- magazine identity не заменена (`magEntity` tag стабилен);
- ammo/chamber неизменны;
- pickup работает.

Исходы:
- `R_TO_INERT_COMMAND_TO_WEAPON_RECEIVER_PROVEN`
- `HANDLER_SET_BUT_WEAPON_RECEIVER_NOT_REACHED`
- `INERT_COMMAND_CAUSED_NATIVE_SIDE_EFFECT_STOP`

---

## Итог
- cmd10 re-verified как graph-level инертный; engine-level инертность измеряется probe'ом.
- Исходники подготовлены (2 файла), НЕ записаны в live.
- Ничего из forbidden не использовано; `Update=0`, `HandleWeapons=0`; non-lab путь не изменён.

Статус: **`T4B_V1_INERT_COMMAND_BRIDGE_ONESHOT_SOURCE_PREPARED_OWNER_REVIEW`**. STOP.
