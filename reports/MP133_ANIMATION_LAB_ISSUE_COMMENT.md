# Issue #27 (V2.2) — status comment (ready to paste)

Publication of repo files is done via installed Git; exact SHA in the chat reply.
No game/Workbench launch (owner override).

---

**Статус V2.2: READY_FOR_OWNER_TEST.** Компиляция и игровые критерии —
**NOT RUN / OWNER TEST REQUIRED**.

## Что показал прогон владельца (issue #27) и что исправлено

- **Lookup-баг (корень «нет STATE»):** `GetCurrentWeaponLab()` использовал
  `wpn.FindComponent(...)` (на компоненте) → возвращал `null`, хотя
  `e.FindComponent(...)` (сущность) находил компонент (`labComp=1` в логе).
  **Исправлено:** централизованный `LabCompOf(wpn)` через
  `wpn.GetOwner().FindComponent(...)` (как в Core) во всех проверках/коммите.
  Это возвращает `STATE` и весь путь досылки.
- **Физическая труба была 10, не 3.** `m_iTubeCapacityOverride`/
  `m_MaxMagazineAmmo=3` ограничивали только лаб-логику, не физический магазин
  (`GetMaxAmmoCount()=10`).
  **Исправлено:** новый lab-only магазин
  `{CC71464F7CA58F57}Prefabs/Weapons/MP133_Lab/armst_12ga_Lab_3rnd.et`
  (наследует боевой 12ga, `MaxAmmo 3`, `AmmoMapping { 0 0 0 }`), и оба лаб-префаба
  переопределяют `MuzzleComponent.MagazineTemplate` на него → физическая
  ёмкость 3, клиентское 3/3.
- Префабы сохраняют `m_iTubeCapacityOverride 3` +
  `ARMST_SHOTGUN_COMPONENTS.m_MaxMagazineAmmo 3` (Core-трим согласован/ no-op).
- Локальный non-RIS префаб был перезаписан Workbench-сохранением
  (`ARMST_SHOTGUN_COMPONENTS { Enabled 0 }`); правка переприменена **без**
  `Enabled` (компонент Core должен быть активен), координаты владельца сохранены.

## Префабы (ResourceName / GUID) — владелец ставит в свой мир

- `{FC1935AF936F63E5}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`
- `{4B288C21B7125D50}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et`

Lab-магазин: `{CC71464F7CA58F57}Prefabs/Weapons/MP133_Lab/armst_12ga_Lab_3rnd.et`.

## Проверки

- `validate_mp133_lab.py` → **PASSED**.
- `test_mp133_lab_validation.py` → **10/10 OK** (добавлены проверки lab-магазина
  и ёмкости 3; отсутствие world/layer; GUID-резолв).
- Компиляция Workbench / игра → **NOT RUN** (запрет на запуск).
- `check_repository_integrity.py` → NOT RUN (в среде нет `jsonschema`).
- Оригиналы не тронуты (`MP133.agf` = `5E8476D0…B2468A`).

## Владельцу (точный тест)

1. Пересобрать скрипты; поставить lab-префаб в свой мир.
2. Взять `MP-133 [LAB]` (труба `12g 3rnd [LAB]`, 3 патрона).
3. В логе ожидать: `WEAPON … labComp=1`, `STATE labWeapon=1 cap=3 tube=x/3 …`.
4. R → досылка (3/3 максимум, четвёртый отклонён); LSHIFT+R → помпа;
   прислать `console.log` с маркерами `reload request detected` /
   `begin insert loop` / `SERVER Insert COMMIT`.

Нерешённые анимационные предупреждения SPAS-12 / Remington 870 / MP-153 —
вне задачи, отдельным findings-разделом.
