# MP-133 [LAB] — контролируемый тест R (V2.3, только non-RIS) — RU

Разрешение: Issue #27 (owner authorization). Включён гейт **только** у
`Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`
(`m_bLabInsertEnabled 1`). RIS-префаб — gate OFF. Никаких глобальных
включений. Статус: **OWNER TEST REQUIRED** (агент Workbench/игру не запускает).

## Откат (немедленный)

Вернуть гейт OFF в `armst_Shotgun_mp_133_Lab.et`:
удалить строку `m_bLabInsertEnabled 1` (или поставить `0`).
Бэкап и хэши:
- `Weapon_ARMA_X/artifacts/MP133_Lab/prefab_backups/armst_Shotgun_mp_133_Lab.et.off-backup`
- sha256 до правки: `3A0749E59800986765517C34F342F7E7730CF45236F56448488126D721F8766D`
- sha256 с гейтом ON: `67E3D0FCAAA118E16ACF4E1689D32C9D70AD804E775E36CCF80C0117C5691099`

## Шаги теста

1. **Компиляция.** Пересобрать скрипты в Workbench.
   **STOP при любом `SCRIPT (E)`** → прислать `script.log`, гейт OFF.
   (Особенно важен новый файл `ARMST_MP133_Lab_CommandHandler.c` — он
   компилируется впервые.)
2. **Экипировка.** Взять **non-RIS `MP-133 [LAB]`**. В логе убедиться:
   `STATE labWeapon=1 cap=3 tube=x/3 …` (труба — `12g 3rnd [LAB]`, максимум 3).
3. **Один патрон по R.** При необходимости выстрелить, чтобы получить трубу
   `2/3`. Нажать **R один раз**. Ожидается:
   - ровно **один** `SERVER COMMIT: tube 2 -> 3`, резерв `30 -> 29`;
   - труба `2/3 → 3/3`;
   - **НЕТ** событий `Weapon_MagRelease/DetachMagazine/DespawnMagazine/SpawnMagazine/AttachMagazine`;
   - эталон — 4 успешных признака из Issue #27.
4. **Завершение действия.** После досылки: `clientInsert=0 serverInsert=0 armed=0`,
   `isReloading=0`; в покое **нет** повторяющихся циклов; труба остаётся `3/3`.
5. **Помпа и прерывание.** `LSHIFT+R` — помпа (труба −1 через Core, НЕ досылка).
   Смена/опускание оружия — цикл чисто прекращается (`ACTION_END`/cease).

## STOP-условия (немедленно вернуть гейт OFF и прислать лог)

- `SCRIPT (E)` при компиляции.
- труба стала `10/10` или произошла **штатная замена магазина**
  (`Weapon_MagRelease/Detach/Despawn/Spawn/Attach`).
- **бесконечный цикл** досылки.
- **двойной** `SERVER COMMIT` за одно нажатие.
- R выполнил не досылку (или LSHIFT+R выполнил досылку).
- отсутствует cease/`ACTION_END` (залип `clientInsert=1`).

## Что прислать (строки из `console.log`)

Grep по маркерам `[ARMST_MP133_LAB` и `anim event`:
- `[ARMST_MP133_LAB-DIAG] STATE labWeapon=1 cap=3 tube=…/3 …` (несколько);
- `reload request observed type=…`, `ACTION_BEGIN`, `SERVER CYCLE_BEGIN`, `SERVER COMMIT`;
- `anim event '…'` (важно: отсутствие `Weapon_MagRelease/Detach/Despawn/Spawn/Attach`);
- `ACTION_END` / `cease received` / `ACTION_ABORT (…)`;
- любые `SCRIPT (E)`.

Путь: `C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\logs\<свежая>\console.log`.

Результат этого теста определяет, работает ли перехват R, или требуется
доработка лабораторной реализации (без исследования движка).
