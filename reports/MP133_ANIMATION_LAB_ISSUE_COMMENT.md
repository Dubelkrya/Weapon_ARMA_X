# Issue #27 (V2.3) — status comment (ready to paste)

Repo files are published via installed Git (SHA in the chat reply). No game/
Workbench launch (owner override).

---

**Статус V2.3: регрессия остановлена; per-shell insert — BLOCKED (точная
причина ниже).** Игровое поведение и компиляция — **OWNER TEST REQUIRED**.

## Что показал лог владельца (после V2.2) и что исправлено

Лог (comment #5956970464): Gate A и физическая труба 3 работают
(`STATE labWeapon=1 cap=3 tube=2/3`). Но:
- `reloadType=1` (помпа) открывал лаб-окно и сразу закрывал;
- `reloadType=5` (ванильная перезарядка) заставлял **оригинальные** клипы
  отыграть `Weapon_MagRelease/DetachMagazine/DespawnMagazine/SpawnMagazine/
  AttachMagazine` и заменить трубу 3 на стоковый магазин `10/10`;
- после закрытия серверного окна клиент продолжал пульсировать команду 7 →
  **бесконечная перезарядка**; `SERVER Insert COMMIT` отсутствовал.

**V2.3 (code-only):**
- **Авто-триггер отключён** — ванильные типы (1..6) больше не открывают лаб-окно
  (только лог `auto-trigger disabled`). Прекращает и цикл, и замену магазина.
- **Commit только по lab-событию** `ARMST_Lab_Shell_Commit`; `Weapon_AttachMagazine`
  больше не триггер коммита (это событие ванильного swap).
- **Идемпотентное закрытие окна** `LabServerEndInsert(notifyOwner)` — терминальные
  ветки уведомляют владельца через `RpcDo_LabCeaseInsert` (нет `clientInsert=1`).
- **Watchdog** ~18 с — страховка от бесконечного цикла.
- Lookup-фикс V2.2 (через сущность) сохранён. Тесты: **11/11 PASS** (добавлена
  `check_v23_safety`).

## BLOCKED — точная причина (по #27 §2/§6)

- Настоящий per-shell insert **невозможен с оригинальными inject-клипами**: они
  содержат `Weapon_SpawnMagazine/AttachMagazine/MagRelease`, и движок выполняет
  реальную замену всего магазина. Lab-only санитизированные источники есть
  (`LabClips/W_MP133_Lab_Inject.txa`, `P_MP133_Lab_Inject.txa`), но **не
  скомпилированы в .anm** — нужен импорт в Animation Editor Workbench, который
  агенту запускать запрещено.
- Подавление нативной перезарядки для лаб-оружия требует проверенного
  engine-хука/точного action-имени — без Workbench/игры недоказуемо.
- **Нужные данные:** (a) GUID-ы lab-only ANM после импорта TXA владельцем;
  (b) подтверждение хука, надёжно подавляющего ванильную перезарядку для лабы.

До этого лаборатория в **безопасном** состоянии: без авто-триггера, без
вызванной лабой замены магазина, без фантомных патронов.

## Проверки

- `validate_mp133_lab.py` → **PASSED**; `test_mp133_lab_validation.py` → **11/11 OK**.
- Компиляция/игра → **NOT RUN** (запрет). `check_repository_integrity.py` → NOT RUN (нет `jsonschema`).
- Оригиналы не тронуты (`MP133.agf` = `5E8476D0…B2468A`); мир/слой отсутствуют.

## Префабы (ResourceName / GUID) и лабораторный магазин

- `{FC1935AF936F63E5}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Lab.et`
- `{4B288C21B7125D50}Prefabs/Weapons/MP133_Lab/armst_Shotgun_mp_133_Ris_Lab.et`
- `{CC71464F7CA58F57}Prefabs/Weapons/MP133_Lab/armst_12ga_Lab_3rnd.et`

## Владельцу (что проверить сейчас)

1. Пересобрать скрипты; поставить lab-префаб; взять `MP-133 [LAB]`.
2. Убедиться, что **бесконечной перезарядки больше нет** и труба остаётся 3/3
   (ванильная замена 10/10, вызванная лабой, не повторяется).
3. R/перезарядка сейчас **не выполняет** per-shell (BLOCKED) — это ожидаемо до
   решения по клипам/хуку; прислать `console.log` с маркерами
   `STATE … tube=…/3`, `auto-trigger disabled`, `anim event '…'`.
