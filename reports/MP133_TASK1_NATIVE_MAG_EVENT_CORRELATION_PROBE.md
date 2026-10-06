# MP-133 Task #1 — Native mag-event correlation probe (source prep)

Статус: **T4B_NATIVE_MAG_EVENT_CORRELATION_PROBE_SOURCE_PREPARED_OWNER_REVIEW**
Дата: 2026-10-06
Цель-лейбл: `T4B_NATIVE_MAG_EVENT_CORRELATION_PROBE`
Режим: **source prep only**. Live **НЕ изменялся**.

Основание: аудит `reports/MP133_TASK1_NATIVE_MAG_MUTATION_BOUNDARY_AUDIT.md` (`NO_PRE_MUTATION_WEAPON_LOCAL_HOOK_FOUND`) + owner-решение: следующий шаг — **не новый перехватчик**, а минимальный пассивный runtime-probe на существующем observer, чтобы измерить порядок событий.

---

## 1. Что должен дать probe

Ровно такую трассу (interleave `OnCharacterCommand` + `OnAnimationEvent`):
```
CMD 5 received
├─ snapshot: mag=A, ammo=...
├─ Weapon_MagRelease ?
├─ Weapon_DetachMagazine ?   └─ snapshot: mag=?
├─ Weapon_DespawnMagazine ?
├─ Weapon_SpawnMagazine ?
├─ Weapon_AttachMagazine ?   └─ snapshot: mag=B, ammo=...
├─ Weapon_Rack_Bolt ?
└─ CMD 3 received
```

Два принципиально разных исхода:
- **`Weapon_DetachMagazine`/`AttachMagazine` реально приходят** → физическая замена всё ещё связана с animation-event pipeline → следующий сильный A/B: lab-копия соответствующего player-клипа **без magazine events** (проверка: перестанет ли заменяться магазин), не ломая `cmd1`.
- **Магазин исчезает, а `Weapon_*Magazine` не приходят** → замена выполняется reload-системой независимо от клипов/графа → AGF/ASI/custom CMD не решают; искать уровень **выше** `OnCharacterCommand`, где движок принимает решение о whole-mag reload.

---

## 2. Staged probe (source-only)

`Weapon_ARMA_X/artifacts/astra-rebuild/stageMagEvent/ARMST_T4B_AstraV2_WeaponAnimationComponent.c`
- SHA-256: `7BE1D37513AF31E0C5BC3629BC3301DAFABEC966129AF83D04B688DD4D19BF8A`.
- Base = текущий live observer `B3D71CF57ACBF95C55D4B0098FDDACF86F00CF9B93AA88C287856D9914228D28`.
- Изменено **только** `OnAnimationEvent` (+ новый пассивный helper + счётчик):
  - добавлена ветка `if (name.StartsWith("Weapon_")) { T4BMagEventSnapshot(...); return; }` **до** существующего `if (!name.StartsWith("ASTRA_Shell")) return;`;
  - helper `T4BMagEventSnapshot(eventName, intParam, from, to)` — read-only snapshot: `magPresent`, `magTag` (ref-tag), `ammo/max`, `muzzleSupply`, `barrel`, `chambered`;
  - счётчик `m_iMagEvtSeq`.
- `OnCharacterCommand` **не менялся** (CMD-строки `[ARMST-T4B-CMDROUTE]` уже дают `commandID/intValue`).
- **Никаких** writers, `Update`, `HandleWeapons`, handler, таймеров/`CallLater`, graph/prefab изменений.

Дифф vs live observer: `stageMagEvent/diff_live_observer_to_magevt.diff` — added 81 / removed 3.

---

## 3. Static proofs

| Проверка | результат |
|---|---|
| braces / parens | 23/23, 110/110 |
| `SetAmmoCount` / `ReloadWeapon` / `ReloadWeaponWith` / mag spawn-attach-detach-despawn-release / `CallCommand` / `SetVariableBool` / `ClearChamber` | **0** |
| `override void Update` / `override bool HandleWeapons` / `HandleWeaponReloading` / `SetReloadWeapon` | **0** |
| `CallLater` (таймеры) | **0** |
| `StartsWith("Weapon_")` | 1 (новая ветка) |
| `m_iMagEvtSeq` | 3 (decl/inc/use) |
| `OnCharacterCommand` | не изменён |

---

## 4. Install plan (только по отдельному подтверждению)

1. Подтверждение, что Workbench / Game Mode / Animation Editor закрыты.
2. Заменить **только** live `Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c` на staged (`7BE1D375…`).
3. Handler (`ARMST_T4B_NormalRHandlerProbe.c`, no-handler A/B `D5BA3052…`) — **не трогать**.
4. Sync labs; узкий commit → статус готовности к прогону.
Rollback: observer `B3D71CF57ACBF95C55D4B0098FDDACF86F00CF9B93AA88C287856D9914228D28`.

---

## 5. Owner runtime (после GO)

Cold start → canonical MP-133 → выстрел → один `R` → снять все строки `[ARMST-T4B-CMDROUTE]` + `[ARMST-T4B-MAGEVT]` (и, если появятся, `[ARMST-T4B-ASTRA]`). Сопоставить по времени: приходят ли `Weapon_*Magazine` события и где именно меняется `magTag`.

---

## 6. Границы

Live/граф/prefab/observer/Tube3/Core/grid/inventory не менялись; `GAMEPLAY_FILES_CHANGED=0`. cmd7 не предлагается; глобальный `HandleWeaponReloading` не восстанавливается; Chungus — reference-only.

Статус: **`T4B_NATIVE_MAG_EVENT_CORRELATION_PROBE_SOURCE_PREPARED_OWNER_REVIEW`** (цель `T4B_NATIVE_MAG_EVENT_CORRELATION_PROBE` — после установки по GO). STOP.
