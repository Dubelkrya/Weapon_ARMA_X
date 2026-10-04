# MP-133 Task #1 — Phase 2A: Chungus applicability + Phase 2B STOP (weapon-side variable setter absent)

Статус: **TASK1_PHASE2B_STOP_NEEDS_OWNER_DECISION**
Дата: 2026-10-04
Задание: Issue #34 [#5983713556](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983713556) (Phase 2A read-only proof + conditional Phase 2B) и Chungus addendum [#5983753037](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5983753037).
Режим: **READ-ONLY**. Живой аддон, `labs/`, скрипты, prefab — не изменялись.
База: `t4b/installed-mag-probe` @ `9ba67d3`; live graph mtime 22:36:38.

---

## 0. Preflight

- Workbench/редактор/игра: **закрыты** (процессов `Workbench|Reforger|Arma|Enfusion` нет).
- Addon `ARMSTMP133T4B_InstalledMagProbe`, ID `ARMSTMP133T4BInstalledMag`.
- Live: `MP133_Astra.agf` `C9639C5F…`, `player.asi` `DC9C5105…`, `weapon.asi` `6D966498…`.
- Скрипты T4b: `ARMST_T4B_InstalledMagProbe.c`, `ARMST_T4B_AstraV2_WeaponAnimationComponent.c`, `ARMST_T4B_G3B1_DonorConsume.c`, `ARMST_T4B_G3B2_Transfer.c`.

---

## 1. Phase 2A — доказательства по SDK 1.8.0.13

### 1.1 Иерархия компонентов
- `BaseAnimPhysComponent : GameComponent` — подклассы: `AnimalAnimationComponent`, `CharacterAnimationComponent`, `SCR_CharacterAnimationComponent`.
- `BaseItemAnimationComponent` (→ подклассы `WeaponAnimationComponent`, `MagazineAnimationComponent`, `UGLAnimationComponent`, …) — **НЕ** является `BaseAnimPhysComponent`.

### 1.2 Точные API (SDK 1.8.0.13)
- `BaseAnimPhysComponent`: `BindVariableBool(string) → TAnimGraphVariable`, `BindVariableFloat/Int`, `SetVariableBool(TAnimGraphVariable,bool)`, `SetVariableFloat/Int`, `BindCommand/BindEvent/BindTag/BindPrediction`, `CallCommand/CallCommand4I`.
- `CharacterAnimationComponent`: всё выше + `SetSharedVariableBool(TAnimGraphVariable,bool,bool varHasOtherUsers)` (+Float/Int), `SetAnimAimY`, `SetIKTarget(string bindingName,…)`, `SetAnimationLayerFPP/TPP`.
- `BaseItemAnimationComponent`/`WeaponAnimationComponent`: **только** `GetOwner`, `IsAnimationEvent/Tag`, `OnAnimationEvent`, `OnCharacterBoolVariable/FloatVariablet/IntVariable` (приёмные колбэки), `OnCharacterCommand`, `OnPrepareAnimInput`, `OnProcessAnimOutput`, `RemoveSyncReference`, `SyncWithCharacter` (+ weapon-specific `FoldWeapon/SetBipod/…`). **Ни одного bind/set переменной.**

### 1.3 Семантика
- `SyncWithCharacter(ChimeraCharacter, bool, string)` — «Syncs the item with the character and **subscribes to its animation variable changes and animation command calls**». Т.е. источник переменных — **персонаж**; оружейный компонент **наблюдает** их через `OnCharacterBoolVariable`.
- Доступ к компоненту персонажа (подтверждено): `ChimeraCharacter.GetAnimationComponent()` и `CharacterControllerComponent.GetAnimationComponent()` → `CharacterAnimationComponent`. Рабочий прецедент в Core: `modded SCR_CharacterControllerComponent { m_animComp = GetAnimationComponent(); }`.
- **Точные имена из Chungus addendum — `BindBoolVariable`, `SetBoolVariable`, `GetCharAnimComp`, `SetAnimBoolVars` — в SDK 1.8.0.13 отсутствуют.** Индекс функций показывает только `BindVariableBool/SetVariableBool` (BaseAnimPhysComponent) и `SetSharedVariableBool` (CharacterAnimationComponent).

### 1.4 Что это значит для P/W
- **P (player/character injection):** переменные можно связать/выставить на `CharacterAnimationComponent` (единый SDK-путь).
- **W (weapon graph):** прямого сеттера **нет**. Оружейный компонент может только получать изменения переменных персонажа (`OnCharacterBoolVariable`), а не задавать собственные.
- Инъекция оружия (`AnimInjection`, `BindingName "Weapon"`, `BindWithInjection 1`) и `SyncWithCharacter` дают **косвенное** основание предположить, что变量-владельцем является компонент персонажа и один набор переменных управляет и P, и W. Но статически это **не доказано**, а addendum прямо предупреждает «do not assume SyncWithCharacter alone synchronizes custom flags».

---

## 2. `TASK1_CHUNGUS_PATTERN_APPLICABILITY`

| (i) proven P/W binding APIs | **P:** `CharacterAnimationComponent.BindVariableBool/SetVariableBool/SetSharedVariableBool` — PROVEN. **W:** сеттера нет; Chungus-имена отсутствуют → **weapon-side паттерн NOT PORTABLE** в 1.8.0.13. |
| (ii) T4b ownership / action path | Lab-действие: существующий паттерн `ScriptedUserAction` (`ARMST_T4B_AddRoundWeaponAction`) в prefab'ах. Доступ к персонажу: `pUserEntity → ChimeraCharacter.GetAnimationComponent()`. Astra-bridge — `WeaponAnimationComponent` (сеттера нет). |
| (iii) safe stop/repeat/release | Проектируемо на character-side (request true/false, repeat flag, release → `AstraWaitRelease → Idle`), **но** зависит от того, доходит ли переменная до нужного инстанса графа (см. (iv)). |
| (iv) unresolved | (a) доходит ли character-scope переменная до **injected W graph** `IdleReloadSTM`; (b) наличие у weapon-инстанса собственного независимого набора переменных; (c) routing/authority generic-событий P→W (приходит ли P-маркер ровно один раз на W-receiver и на authority). |
| (v) expressly excluded (Chungus) | `TryRackBolt()`→`controller.ReloadWeapon()` (нативный), `PumpShotgunSetAmmoCount→InsertShell` (+1 патрон), `FixAmmoCount()` (временный dummy +1), fallback spawn/attach стандартного магазина, любые Chungus resource GUID. В T4b **не переносятся**. |

---

## 3. Вопрос о CMD2-6 (Phase 2A п.3) — классификация

- **LOG-PROVEN:** нативные `Reload_InsertMag/Reload_RemoveMag` несут `Weapon_Spawn/Attach/Detach/DespawnMagazine`; owner-runtime CMD5 → whole-mag (`3/3→10/10`).
- **UNRESOLVED:** выполняет ли движок физическую замену/извлечение Tube3 по CMD2-6 **независимо** от проигрывания этих клипов.
- Для данной задачи это **не блокер**: новый lab-action не эмитит CMD2-6 и не пишет патроны; CMD2-6 остаётся вне Phase 2B.

---

## 4. Точный блокер

`STOP`: **в SDK 1.8.0.13 нет подтверждённого сеттера граф-переменной для weapon-инстанса.** `WeaponAnimationComponent`/`BaseItemAnimationComponent` его не имеют; Chungus-методы (`BindBoolVariable`/`SetBoolVariable`/`GetCharAnimComp`/`SetAnimBoolVars`) в установленном SDK отсутствуют. Значит, требование задания «выставлять `ASTRA_ShellRequest/Repeat/Stop` одновременно на **P injection И W weapon graph**» нельзя подтвердить штатными API. Предусловие Phase 2B (a) «correct graph owner(s)/instance(s)» для **W** не выполнено → по правилам задачи **правки не вносились**.

---

## 5. Минимальное предложение (для отдельного решения владельца)

1. **Разрешить W-ownership (предпочтительно, без правок):** по Bohemia/официальной документации или подтверждённому Chungus-источнику установить, является ли `CharacterAnimationComponent` единственным владельцем переменных для **injected weapon graph**, или у weapon-инстанса отдельный набор (тогда нужен иной путь). При подтверждении «одна переменная управляет и P, и W» Phase 2B реализуется только на character-side.
2. **Либо bounded probe (отдельное одобрение, default OFF, без CMD2-6/ammo):** крошечный lab-action, который связывает и выставляет `ASTRA_ShellRequest` на `CharacterAnimationComponent`, с логированием; владелец в Workbench (animation-only) проверяет, реагирует ли **weapon** `IdleReloadSTM`. Это фальсифицируемо решает (iv)(a) перед полной реализацией.
3. Только после (1)/(2) — Phase 2B: lab-action + bind/set `ASTRA_ShellRequest/Repeat/Stop` с fail-closed (missing component → no-op), release/reset после цикла, без `CMD_Weapon_Reload`, без ammo/mag-операций.

---

## 6. Сохранность

Только чтения. Живой аддон, `labs/`, `.agf/.agr/.ast/.asi`, скрипты, prefab, ANM/meta, 90 protected, G3B2 — без изменений. Публикуется только этот отчёт.

Возврат: **`TASK1_PHASE2B_STOP_NEEDS_OWNER_DECISION`** — первое недоказанное предусловие: отсутствие weapon-side сеттера граф-переменной и, как следствие, неподтверждённый маппинг P/W инстансов.
