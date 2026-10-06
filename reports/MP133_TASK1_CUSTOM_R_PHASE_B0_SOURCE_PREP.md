# MP-133 Task #1 — Custom-R input routing Phase B0 (source prep)

Статус: **T4B_CUSTOM_R_PHASE_B0_SOURCE_PREPARED_OWNER_REVIEW**
Дата: 2026-10-06
Задание: Issue #34 — Phase B0 source prep ([#6021866345](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34)).
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
| `Scripts/Game/ARMST_T4B/ARMST_T4B_CustomRInputProbe.c` | `0D77CFDD045ED4EF2E2CD7E954F6AB50DC293B8D187DC3B172743B6AF038BE45` | 3944 | listener + event-driven context lifecycle + `[ARMST-T4B-RINPUT]` log |

**Целевые live-пути (при GO):** те же три пути в `ARMSTMP133T4B_InstalledMagProbe/`.

---

## 2. Static verification

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

## 3. Lifecycle

- `OnInit`: `AddActionListener("ARMST_MP133_Reload", DOWN, T4BRInputDown)` + подписка на `BaseWeaponManagerComponent.m_OnWeaponChangeCompleteInvoker`.
- `T4BRWeaponChanged` → `T4BRSyncContext`: `ActivateContext("ARMST_MP133_ReloadContext")` только если current weapon несёт `ARMST_T4B_WeaponProbe`; иначе `DeactivateContext`.
- `OnDelete`: `RemoveActionListener` + `DeactivateContext` (cleanup).
- **Без** `Update`/polling/таймеров.

**To confirm at compile:** точная сигнатура `m_OnWeaponChangeCompleteInvoker` callback (без параметров) — если не совпадёт, заменить на `OnWeaponActive`/`OnWeaponInactive`-подписку; это единственная непроверенная сигнатура.

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

Статус: **`T4B_CUSTOM_R_PHASE_B0_SOURCE_PREPARED_OWNER_REVIEW`**.
