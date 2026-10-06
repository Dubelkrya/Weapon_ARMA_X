# MP-133 Task #1 — Custom-R input routing Phase B0 (source prep)

Статус: **T4B_CUSTOM_R_PHASE_B0_CORRECTED_OWNER_REREVIEW**
Дата: 2026-10-06
Задание: Issue #34 — Phase B0 source prep ([#6021866345](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)) + owner review [#6022566622](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34) (BLOCKED: lifecycle/callback).
Режим: **source-only**. Live/labs/Core/gameplay **не менялись**. Staged: `artifacts/astra-rebuild/stageCustomRInput/`.

---

## 0. Lab-isolation — доказана как возможная (SOURCE)

**Ключевое доказательство:** `ARMST-PLATFORM---Core/Configs/System/chimeraInputCommon.conf` **переобъявляет** vanilla-контекст `CharacterGeneralContext` через **аддитивный** массив `ActionRefs +{ ... }`. Оператор `+{` имеет смысл только если базовый контекст уже существует → движок **сливает** (overlay) addon-овый `chimeraInputCommon.conf` с базовым (иначе Core-файл стёр бы vanilla-actions и сломал игру). → **lab-owned input config возможен без правки Core**.

Дополнительно (SOURCE): одна физическая клавиша `R` уже привязана к нескольким action'ам в разных контекстах — `RotateItem` (single `KC_R`, `InventoryContext`), `BuyItem` (single `KC_R`, `CharacterGeneralContext`), `ARMST_LIGHT_RELOAD_ACTION` (`R+LSHIFT`), `ARMST_CHECK_AMMO_ACTION` (`R+LCONTROL`) → контекст управляет тем, какой action сработает.

**Suppression (Priority/Flags) — UNRESOLVED:** базовый приоритет контекста и семантика `Flags` в SDK 1.8.0.13 не документированы. В staged-конфиге `Flags 0x6 0` скопирован из **существующего** контекста (`BookContext`/`TraderContext`), `Priority 20000` выбран выше максимального наблюдённого (10000). Это ровно то, что измеряет Phase B.

→ статус **PREPARED** (не BLOCKED).

---

## 1. Staged-файлы

| path | SHA-256 | bytes | назначение |
|---|---|---|---|
| `Configs/System/chimeraInputCommon.conf` | `71D4B2DD92B12BF93E76DEAF6B1B8CF763F2505D837981C7C469FF99D0DDCF4B` | 1661 | additive: `Action ARMST_MP133_Reload` (KC_R) + `ActionContext ARMST_MP133_ReloadContext` |
| `Configs/System/keyBindingMenu.conf` | `368B51F7862B245C730E40CA1C226B369F845C7E0DC9B604E822F2078BCDC01D` | 791 | key-binding entry для `ARMST_MP133_Reload` |
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `9DBF75C4C9721C23DB7663C6F0094C0678D9047711DACAA913145326E289BA69` | 5682 | listener + event-driven context lifecycle + `[ARMST-T4B-RINPUT]` log |

**Целевые live-пути (при GO):** те же три пути в `ARMSTMP133T4B_InstalledMagProbe/`.

---

## 2b. Corrections (owner review #6022566622)

| # | Проблема | Исправление |
|---|---|---|
| 1 | callback `T4BRWeaponChanged()` не совпадал с `ScriptInvoker<BaseWeaponComponent>` | сигнатура → `protected void T4BRWeaponChanged(BaseWeaponComponent newWeapon)`; аргумент **не** используется для мутаций |
| 2 | `Insert` без `Remove` | менеджер сохранён в `m_pT4BRWeaponManager`; в `OnDelete` — `m_pT4BRWeaponManager.m_OnWeaponChangeCompleteInvoker.Remove(T4BRWeaponChanged)` (Insert=1/Remove=1) |
| 3 | глобальный `AddActionListener`/context без local-gate | **proven pattern** (историческая ARMST lab + Core): `owner == SCR_PlayerController.GetLocalControlledEntity()` внутри `override protected void OnControlledByPlayer(IEntity owner, bool controlled)`; только local player делает `AddActionListener`/`ActivateContext`/`DeactivateContext`/лог |
| 4 | нет initial sync | после локальной регистрации — один `T4BRSyncContext()` (context активируется, если lab MP-133 уже current) |

**Cleanup path:** `OnControlledByPlayer` (loss of local control) → `T4BRTeardownLocal()` (Remove listener + DeactivateContext); `OnDelete` → `T4BRTeardownLocal()` + invoker `Remove`. Все снятия под флагами `m_bT4BRListenerActive`/`m_bT4BRContextActive`.

**Local-player proof:** `SCR_PlayerController.GetLocalControlledEntity()` — проверенный API (historical `ARMST_MP133_Lab_Character.c` L546/L609/L702; множество Core-файлов). Не изобретён.

**Initial sync:** 1 явный вызов `T4BRSyncContext()` в `OnControlledByPlayer` (local+controlled); +1 вызов из `T4BRWeaponChanged` (weapon change). Без `Update`/polling.

**Suppression остаётся UNRESOLVED:** `Priority 20000` / `Flags 0x6 0` не менялись (Phase B измеряет).

## 2c. Static verification (corrected)

```
callback sig T4BRWeaponChanged(BaseWeaponComponent) = 1
Insert = 1   Remove = 1
AddActionListener = 1   RemoveActionListener = 1
GetLocalControlledEntity (local gate) = 4
initial/weapon-change T4BRSyncContext call sites = 2 (+1 definition)
ActivateContext = 1   DeactivateContext = 2 (sync + teardown)
braces 21/21   parens 83/83
FORBIDDEN (writers/reload APIs/Update/timers) = 0
staged configs unchanged vs 50a1295 (diff empty)
```



| Проверка | Результат |
|---|---|
| action name (`ARMST_MP133_Reload`) | conf=5, kb=3, script=8 (вкл. комментарии) |
| `keyboard:KC_R` | conf=1 |
| context name | conf=2, script=4 |
| `ActivateContext` / `DeactivateContext` | 1 / 2 (вторая — delete-cleanup, под `m_bT4BRContextActive`) |
| `AddActionListener` / `RemoveActionListener` | 1 / 1 (сбалансировано) |
| `ARMST_T4B_WeaponProbe` gate | 3 (комментарий + 2 кода) |
| braces / parens | 15/15, 60/60 |
| FORBIDDEN (`SetAmmoCount`/`ReloadWeapon`/`ReloadWeaponWith`/`SetReloadWeapon`/`HandleWeaponReloading`/`HandleWeaponReloadingDefault`/`SetCurrentCommand`/`CallCommand`/`Update`/`HandleWeapons`/`CallLater`/mag spawn-attach-detach-despawn-release/`ClearChamber`) | **0** |

---

## 3. Lifecycle (corrected)

- `OnInit`: `m_pT4BRWeaponManager = GetWeaponManagerComponent()`; `Insert(T4BRWeaponChanged)` на `m_OnWeaponChangeCompleteInvoker`.
- `OnControlledByPlayer(owner, controlled)`: **local gate** `owner == SCR_PlayerController.GetLocalControlledEntity()`; если `controlled && local` → `AddActionListener("ARMST_MP133_Reload", DOWN, T4BRInputDown)` + **initial** `T4BRSyncContext()`; иначе → `T4BRTeardownLocal()`.
- `T4BRWeaponChanged(BaseWeaponComponent newWeapon)` (local-gated) → `T4BRSyncContext()`.
- `T4BRSyncContext()` (local-gated): `ActivateContext` если current weapon несёт `ARMST_T4B_WeaponProbe`, иначе `DeactivateContext`.
- `OnDelete`: `T4BRTeardownLocal()` + `Remove(T4BRWeaponChanged)` на сохранённом `m_pT4BRWeaponManager`.
- **Без** `Update`/polling/таймеров. Только local player регистрирует listener/context и пишет лог.

---

## 4. Phase B runtime test (описать, НЕ запускать)

**Test A — control weapon (не-MP-133):** нажать `R` → `[ARMST-T4B-RINPUT]` отсутствует; vanilla reload работает как раньше.
**Test B — canonical T4B MP-133:** нажать `R` один раз; смотреть одновременно `[ARMST-T4B-RINPUT]` и `[ARMST-T4B-CMDROUTE]`.
- SUCCESS: `ARMST_R_RECEIVED=YES` и vanilla `CMD_Weapon_Reload = NONE` → `CUSTOM_R_CONTEXT_FEASIBLE_WITH_VANILLA_SUPPRESSION`.
- DOUBLE-FIRE FAIL: `ARMST_R_RECEIVED=YES` и присутствует любой vanilla cmd1–6 → `CUSTOM_R_DOUBLE_FIRE_CONFIRMED`.
- ROUTING FAIL: `ARMST_R_RECEIVED=NO`.

**Не является fail:** если context забрал `R` и vanilla `cmd1` больше не появляется — ожидаемо; rack восстанавливать в Phase B **не** нужно.

---

## 5. Границы

Live/labs/Core/world/grid/inventory/prefab/ASTRA2/Tube3/handler/observer — не тронуты. Глобальный `HandleWeaponReloading` не добавляется; global storage override не добавляется; cmd7 не используется; Chungus не копируется. Ничего в live не устанавливалось.

Статус: **`T4B_CUSTOM_R_PHASE_B0_CORRECTED_OWNER_REREVIEW`**.
