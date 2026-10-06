# MP-133 Task #1 — No-handler A/B (source prep)

Статус: **T4B_NO_HANDLER_AB_REVIEW_PASS_WAITING_WB_CLOSED**
Дата: 2026-10-06
Задание: Issue #34 — «prepare clean A/B with NO T4B HandleWeaponReloading override» ([#6009194998](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
Режим: **source prep only**. Live **НЕ изменялся**.

Предыдущий результат: `RACK_STILL_BROKEN_WITH_ONLY_T4B_HANDLER` — конкурирующий исторический `ARMST_MP133_AnimationLab` **не** был единственной причиной.

---

## 1. Goal

Определить, ломает ли **само присутствие** `modded SCR_CharacterCommandHandlerComponent.HandleWeaponReloading` (наш T4B override) native rack, даже когда его rack-ветка возвращает `super`.

A/B = T4B lab, в котором **весь** кастомный `HandleWeaponReloading` override **отсутствует**.

---

## 2. Staged A/B source

`Weapon_ARMA_X/artifacts/astra-rebuild/stageNoHandler/ARMST_T4B_NormalRHandlerProbe.c`
- SHA-256: `D5BA3052C07CD9B470F638AFF10DFB6C97ED835F08CF95D57E228A332F2658DE`.
- Содержит **только** два общих `const int` (`ARMST_T4B_INERT_RELOAD_CMD`, `ARMST_T4B_RELOAD_COMMAND_ID`) + комментарии.
- **Нет** `modded class`, **нет** `HandleWeaponReloading`, **нет** `HandleWeaponReloadingDefault`, **нет** `Update`/`HandleWeapons`, **нет** writers, **нет** таймеров/поллинга.
- Два глобала оставлены, потому что на них ссылается weapon-local observer (`ARMST_T4B_AstraV2_WeaponAnimationComponent`): `isReloadCommand`/`isInert`. Они инертны и не влияют на input/reload flow (requirement 7).

Дифф vs текущий live handler: `stageNoHandler/diff_live_handler_to_nohandler.diff` — added 18 / removed 169 (весь override удалён).

Observer (`ARMST_T4B_AstraV2_WeaponAnimationComponent.c`) — **без изменений** (`B3D71CF57ACBF95C55D4B0098FDDACF86F00CF9B93AA88C287856D9914228D28`); продолжает компилироваться (ссылается на оставшиеся глобалы).

---

## 3. Static proofs

| Проверка | A/B файл |
|---|---|
| `modded class` | **0** |
| `HandleWeaponReloading` / `HandleWeaponReloadingDefault` | **0 / 0** |
| `override` (любой) | **0** |
| `override void Update` / `override bool HandleWeapons` | **0 / 0** |
| writers (`SetAmmoCount`/`ReloadWeapon`/`ReloadWeaponWith`/mag spawn-attach-detach-despawn-release/`CallCommand`/`SetVariableBool`/`ClearChamber`) | **0** |
| `SetReloadWeapon` | **0** |
| глобалы `ARMST_T4B_INERT_RELOAD_CMD` / `ARMST_T4B_RELOAD_COMMAND_ID` | 1 / 1 (только объявления) |
| braces / parens | 0/0, 0/0 |
| ASTRA2 graph/prefab/observer/Tube3 | **не тронуты** |

---

## 4. Install plan (только по отдельному GO)

1. Заменить live `Scripts/Game/ARMST_T4B/ARMST_T4B_NormalRHandlerProbe.c` на staged A/B (`D5BA3052…`).
2. Observer **не трогать**.
3. Синхронизировать labs; узкий commit.
Rollback: live handler `83DA1EC584B13D251359B776D2C05AEE41E07A42ACB3334389814C0501BA8B39`; observer `B3D71CF5…`.

---

## 5. Owner test (после GO)

Cold start → canonical MP-133 → выстрел → один `R` → наблюдать, вернулся ли native rack.

Outcomes:
- `RACK_RECOVERED_WITH_T4B_HANDLER_REMOVED` → глобальный handler-архитектура отвергается для Task #1; переходим к **independently derived ARMST/MP-133 weapon-local candidate, informed only by general lessons from Chungus and validated against our own runtime/SDK evidence**.
- `RACK_STILL_BROKEN_WITH_T4B_HANDLER_REMOVED` → следующий аудит ниже уровня handler: текущий ASTRA2 / native CMD1 wiring/runtime.

---

## 6. Итог

- A/B source подготовлен (override полностью отсутствует; только два инертных глобала для observer).
- Live не менялся; ASTRA2/graph/prefab/observer/Tube3/Core/grid/inventory — не тронуты.

Статус: **`T4B_NO_HANDLER_AB_REVIEW_PASS_WAITING_WB_CLOSED`**. STOP.
