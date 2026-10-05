# MP-133 Task #1 — Layer-C NORMAL-R handler runtime probe (phase 1: observe + suppress)

Статус: **NORMAL_R_HANDLER_PROBE_READY_OWNER_RUNTIME_TEST**
Дата: 2026-10-05
Задание: Issue #34 [#5999608920](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5999608920).
Новый файл: `Scripts/Game/ARMST_T4B/ARMST_T4B_NormalRHandlerProbe.c` (lab-only диагностика).
Live-граф/ASI/AGR/AST/AW/metas/ANM/ORIGINAL/old_pa/G3B2/production/Core — **не изменялись**.

---

## 1. Что сделано

Единственный `modded`-override, узко-гейтнутый на lab-оружие:

```c
modded class SCR_CharacterCommandHandlerComponent {
    override bool HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID) { ... }
}
```

- **Точная сигнатура (SDK 1.8.0.13, SOURCE):** `bool HandleWeaponReloading(CharacterInputContext pInputCtx, float pDt, int pCurrentCommandID)` на `CharacterCommandHandlerComponent` (скриптовый, переопределяемый). `HandleWeaponReloadingDefault(...)` — `proto external` (движковый).
- **Точный lab-gate (сильный, компонентный):** текущее оружие через `GetControllerComponent() → BaseWeaponManagerComponent.GetCurrentWeapon() → BaseWeaponComponent.GetOwner()`; lab-идентификация — наличие компонента `ARMST_T4B_WeaponProbe` (проверенный lab-паттерн). Никаких substring/class-name гейтов.
- **Non-lab:** немедленно `return super.HandleWeaponReloading(pInputCtx, pDt, pCurrentCommandID)` — оригинальное поведение не тронуто.
- **Lab (phase 1):** только чтение + лог + `return true` (потребление запроса). Логируются: `cmd` (`pCurrentCommandID`), `reloadType` (`pInputCtx.GetWeaponReloadType()`), `startReloading` (`pInputCtx.WeaponIsStartReloading()`), префаб оружия, entity/префаб магазина, **`magEntity=M<n>`**, `magAmmo/magMax`, `barrel`, `chambered`.

**Instance identity (`magEntity`).** В SDK 1.8.0.13 нет документированного raw entity-ID для `IEntity`, поэтому применён проверенный lab-паттерн: сравнение ссылки на entity + счётчик-тег. `m_rprobeMagEnt/m_rprobeMagTag/m_rprobeMagNextTag` хранят последний наблюдённый `magEnt`; при смене ссылки тег инкрементируется. **Разный тег ⇒ движок уничтожил/заменил экземпляр магазина, даже если prefab-имя совпадает.** Read-only, поведение probe не изменено.

## 2. Запрещённые в phase 1 API — НЕ вызываются (проверено по коду)

`SetReloadWeapon`, `ReloadWeapon(`, `ReloadWeaponWith`, `SetAmmoCount`, `SpawnMagazine`, `AttachMagazine`, `DetachMagazine`, `DespawnMagazine`, `MagRelease`, `SetVariableBool`, `CallCommand` — **0 вхождений в коде** (встречаются только в комментарии-запрете). Кастомные anim-переменные не эмитятся.

Статические проверки кода: скобки `{}` 8/8, `()` 44/44; `super.HandleWeaponReloading` — 1 (delegation); `return true` — 1 (consume).

## 3. Один тест владельца (после компиляции)

1. Скомпилировать Game-модуль; убедиться, что нет ошибок компиляции.
2. Экипировать **lab MP-133** (любой T4b lab-префаб с `ARMST_T4B_WeaponProbe`, напр. `ARMST_T4B_AstraRebuild_TestWeapon.et` / bridge).
3. Зафиксировать ДО: физический магазин (entity/префаб), ammo count, chamber.
4. Нажать **обычную R один раз**.
5. Вернуть:
   - строку `[ARMST-T4B-RPROBE] phase=handler-enter cmd=… reloadType=… startReloading=… wep=… mag=… magAmmo=… barrel=… chambered=… consumed=1`;
   - магазин entity/префаб/ammo/chamber ДО и ПОСЛЕ (должны совпасть);
   - отсутствие native `Weapon_SpawnMagazine/Attach/Detach/DespawnMagazine` в логе;
   - подтверждение, что на не-lab оружии поведение прежнее (по желанию — короткий контроль).

**STOP**, если наблюдение запроса требует пропустить native swap — не запускать такой вариант.

## 4. Что это доказывает / не решает

- **Доказывает (после теста):** (1) R реально доходит до `HandleWeaponReloading`; (2) lab-запрос можно потребить до native mag-swap; (3) труба/ammo/chamber не меняются.
- **Не решает:** reserve ammo, repeat/full/empty, физическая one-shell транзакция, shell count mutation, репликация per-shell. Это отдельные задачи.
- **Phase 2 не выполняется автоматически** — кандидат на lab animation-only сигнал (безопасное значение `CMD_Weapon_Reload` без native state/event path либо другой engine-контрол) будет предложен отдельно, с доказательством и отдельной авторизацией. `SetReloadWeapon(<value>)` пока не используется.

## 5. Git

Один узкий commit: новый lab-скрипт + этот отчёт; синхронизация нового скрипта в `labs/`. Остальное не тронуто.
