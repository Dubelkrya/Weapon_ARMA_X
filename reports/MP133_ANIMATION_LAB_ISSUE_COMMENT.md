# Issue #25 — status comment (ready to paste)

Copied here because this environment has no `gh`/`git`/token to post it.

---

**Статус: реализация в изолированном аддоне выполнена; компиляция/ресурсы —
подтверждены; игровой поток досылки — НЕ подтверждён (требует прогона).**

Соблюдён **OWNER OVERRIDE**: поставка содержит только полностью настроенные
префабы + их изолированные скрипты/анимации. Мир, `.ent`, `.layer`, сценарий,
спавн или размещённые сущности **отсутствуют** (ранее созданный в сессии
lab-мир `Worlds/MP133_Lab` удалён, не является поставкой).

## Префабы для размещения владельцем в своём мире (ResourceName / GUID)

- `{FC1935AF936F63E5}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`
- `{4B288C21B7125D50}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et`

Аддон: `ARMST_MP133_AnimationLab` (ID `ARMSTMP133AnimationLab`, GUID
`{1187677F04E33069}`; зависимости `58D0FB3206B6F859` vanilla,
`69E4C3542B6CDC19` Core, `6A70E400C54051DC` Weapons).

## Acceptance checks

| Проверка | Статус | Доказательство |
|---|---|---|
| Isolation | **PASS** | SHA-256 16 исходных файлов; оригиналы не изменены (`artifacts/MP133_Lab/original_consumed_hashes.txt`) |
| Dependencies | **PASS (static)** | ID сверены с живыми `addon.gproj`; Workbench загрузил модуль лаборатории |
| Resource wiring | **PASS (static) / частично** | GUID/строки `.asi`↔`.ast`/проводка префабов — валидатор PASS; компонент виден в редакторе; preview графа не выполнен |
| Compile | **PASS** | `logs\<ts>\script.log`: чистая компиляция после фикса |
| Preview | **N/A** | Animation Editor preview не выполнялся |
| One-shell transaction | **UNVERIFIED** | поток досылки не запускался (см. ниже) |
| Negative tests | **UNVERIFIED** | — |
| Pump | **UNVERIFIED** | Core-путь не менялся |
| Dual instances | **UNVERIFIED** | — |
| Networking | **UNVERIFIED** | — |
| Recovery | **UNVERIFIED** | — |
| Production | **PASS** | оригиналы и пользовательские правки не тронуты |

## Факт из Workbench-логов

Код компилируется и выполняется:
```
[ARMST_MP133_LAB] component attached; capacity=2 reserve=30
[ARMST_MP133_LAB-DIAG] character component init: anim=1 cmdBound=1 isServer=1
[ARMST_MP133_LAB-DIAG] OnControlledByPlayer controlled=1 local=1
[ARMST_MP133_LAB-DIAG] watcher started
```
Но во **всех** логах за день: `STATE labWeapon` = 0, `reload request detected`
= 0, `Insert COMMIT` = 0. Строка `STATE` пишется раз в секунду только когда
`GetCurrentWeaponLab()` != null, т.е. когда в руках лабораторное оружие. ⇒
цепочка досылки ни разу не запускалась; во время тестов лабораторное оружие
текущим не было (вероятно, тестировалось обычное оружие: симптом «магазин на
30 / 30 выстрелов» = обычный автомат; у лаб-MP-133 ёмкость трубы = 2).

## Главные неопределённости (для следующего шага)

1. Почему не запускается: не экипировано лаб-оружие **или**
   `GetCurrentWeaponLab()` не находит компонент — различается безусловным логом
   текущего оружия.
2. Корректный перехват ванильной перезарядки по **R** (флаги
   `WeaponIsStartReloading()`/`GetWeaponReloadType()` не подтверждены).
3. Доставка анимационных событий на сервер и семантика `CMD_Weapon_Reload==7`.
4. Санитизация `LabClips/*.txa` (реимпорт в Animation Editor) — опционально.

## Артефакты

`Weapon_ARMA_X/reports/`:
- `MP133_ANIMATION_LAB_HANDOFF.md` — полный хендовер с исходниками в приложениях;
- `MP133_ANIMATION_LAB_V1.md` — дизайн, GUID-карта, риски, критика прод-костыля;
- `MP133_ANIMATION_LAB_V1_TEST_CHECKLIST_RU.md` — RU-чек-лист + диагностика;
- `agent/scripts/validate_mp133_lab.py` + `agent/tests/test_mp133_lab_validation.py` — 7 тестов, PASS.

Git: `git`/`gh` в среде отсутствуют — **ничего не закоммичено и не запушено**;
файлы переданы локально. Ветки/римоуты не менялись.
