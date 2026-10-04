# MP-133 Astra — Stage 1A: итог диагностики и повторная проверка в Workbench

Статус: **STAGE1A_DIAGNOSIS_COMPLETE / WORKBENCH_REVALIDATION_PENDING**
Дата: 2026-10-04

> **Addendum (Stage 1B, 2026-10-04):** в 20:58:58 Workbench перезаписал `MP133_Astra.{aw,ast,agr,agf}` и обе `.asi` живого аддона и удалил все десять строк `AstraShell.Erc.*`. Хэши `.aw/.ast/.agr/.agf/.asi` в §Приложение A этого отчёта для живого аддона **устарели**. Актуальное состояние и различающий эксперимент:
> [`MP133_ASTRA_STAGE1B_WORKBENCH_ASI_REWRITE_AND_GROUP_EXPERIMENT.md`](MP133_ASTRA_STAGE1B_WORKBENCH_ASI_REWRITE_AND_GROUP_EXPERIMENT.md).
Тип задачи: read-only диагностика + безопасная инструкция владельцу. Исходники не изменялись.
Связанные документы: `reports/MP133_T4B_ASTRA_V2_MIGRATION_AND_OWNER_WORKBENCH.md`, `reports/astra-t4b/migration_v2.json`.

---

## 0. Краткий итог

1. На диске связка `AstraShell` собрана полностью и согласованно: 10 ANM, 10 текущих importer‑meta, обе ASI, `.ast`, `.agr`, `.agf`, `.aw`. Все ресурсные GUID, на которые ссылаются ASI/AGR/AW, **точно совпадают** с GUID в соответствующих `.meta`.
2. Файлы Workbench‑аддона `ARMSTMP133T4B_InstalledMagProbe` (кроме импортированных 20 ANM/meta) **побайтно совпадают** с git‑версией в `Weapon_ARMA_X/labs/...`, а та, в свою очередь, совпадает с HEAD `cec5c81`. То есть на диске нет «полусостояния»: то, что лежит в проекте Workbench, равно опубликованному исходнику.
3. Ошибка `AstraStartReload` — это ошибка разрешения источника узла графа `AnimSrcNodeSource AstraStartReload { Source "AstraShell.StartReload" }` в `MP133_Astra.agf`. Статическая проверка на диске **не находит** обрыва в цепочке `AGF → AST(группа AstraShell) → ASI(AstraShell.Erc.StartReload) → ANM(GUID)`.
4. Поэтому гипотеза «Workbench использует устаревшее (кешированное) состояние анимационных ресурсов» **вероятна, но НЕ доказана**. Ручное назначение одного ANM доказывает лишь, что этот ANM читается редактором; оно не доказывает ни причину, ни работоспособность остальных девяти.
5. Итоговая проверка — за владельцем: сохранить только намеренное изменение, полностью закрыть и заново открыть `MP133_Astra.aw`, выполнить штатную пересборку графа и сверить вкладку Errors. Только результат этой проверки переводит гипотезу в доказанную или опровергнутую.
6. Причина **не считается найденной**, пока пересборка не даст проверяемый результат (см. §11).

---

## 1. Границы работы и что намеренно НЕ делалось

Read-only. Агент **не** изменял исходники, не импортировал ANM, не пересоздавал `.meta`, не удалял кеш вручную, не менял GUID, не запускал игровую перезарядку и не собирал граф в Workbench. Все наблюдения получены из файлов на диске и Git.

Проверка выполнялась при `git`, отсутствующем в `PATH`; использован встроенный Git из GitHub Desktop:
`C:\Users\yshky\AppData\Local\GitHubDesktop\app-3.6.6\resources\app\git\cmd\git.exe`.

---

## 2. Состояние Git

| Репозиторий | Ветка | HEAD | Рабочее дерево |
|---|---|---|---|
| `Weapon_ARMA_X` (инструменты) | `t4b/installed-mag-probe` | `cec5c81ff7edbf6366ed301ae0a1c9af730c2a35` | Чисто, синхронно с `origin`. Один **untracked**: `reports/CORE_ARMST_READONLY_AUDIT.md` |
| `ARMST-PLATFORM---Weapons` (живой аддон) | `main` | `9ebf3234fa4dabdae1faafb1051977ecf818d18f` | Позади `origin/main` на 3 коммита. Изменены: `resourceDatabase.rdb`, `worlds/Weapon_test/weapon_test_Layers/default.layer` |
| `ARMSTMP133T4B_InstalledMagProbe` (Workbench‑аддон) | — | — | **Не git‑репозиторий** (`.git` отсутствует) |

Существенные следствия:

- **`git status` не описывает аддон `ARMSTMP133T4B_InstalledMagProbe`** — именно там лежат `MP133_Astra.aw`, `.asi`, `.agf`, `.agr`, `.ast` и 10 ANM. Изменения в этом аддоне Git не видит по определению.
- Опубликованный источник Astra — это `Weapon_ARMA_X/labs/ARMSTMP133T4B_InstalledMagProbe` (ветка `t4b/installed-mag-probe`, коммиты `15fccb9` — интеграция графа, `cec5c81` — починка конструктора bridge‑компонента).
- Два грязных файла живого аддона (`resourceDatabase.rdb`, `worlds/.../default.layer`) — рабочие артефакты Workbench. Их **не трогать** (правило 8 AGENTS.md; `default.layer` помечен «never touch»).

---

## 3. Состояние локальных файлов

Все файлы `Assets/MP133_AstraShellGraph` в Workbench‑аддоне имеют один массовый штамп времени **2026-10-04 18:58:13** (ANM — 18:58:12). Это признак пакетного копирования/импорта, а **не** свидетельство последней ручной правки: mtime здесь неинформативен.

Состав поддерева `Assets/MP133_AstraShellGraph`:

| Группа | Файлов | Где есть |
|---|---|---|
| Основные ресурсы + meta (`.aw/.ast/.agr/.agf/.asi` ×2) | 12 | Workbench‑аддон **и** git/labs |
| Исходные `.txa` | 10 | Workbench‑аддон **и** git/labs |
| Импортированные `.anm` | 10 | **только** Workbench‑аддон |
| Текущие importer `.anm.meta` | 10 | **только** Workbench‑аддон |
| Итого | **42** | git/labs содержит 22 из 42 |

Сравнение по SHA‑256: у всех **22 общих** файлов хэши в Workbench‑аддоне и в git/labs **совпадают**. Различий нет. Git‑версия чистая относительно HEAD, следовательно набор, открываемый в Workbench, побайтно равен коммиту `cec5c81` во всём, кроме 20 локально импортированных ANM/meta.

Дополнительно: отдельного аддона `ARMSTMP133AstraShellGraph` (`CC35799EC8FA55E1`) в `addons/` **нет** — риска одновременного включения с коллизией GUID сейчас не обнаружено. Проверка ID всех `addon.gproj` подтвердила: `ARMSTMP133T4BInstalledMag` / GUID `B1C2D3E4F5061728`.

---

## 4. `MP133_Astra_player.asi` — детально

Файл: `ARMSTMP133T4B_InstalledMagProbe\Assets\MP133_AstraShellGraph\MP133_Astra_player.asi`
Размер 14680, mtime `2026-10-04 18:58:13`, SHA‑256 `A3DE8D923CE0FC6F1E9661A00354D31807045ECD916CBB4E953F6BD9EEE949D9`.

Содержимое — пять строк назначения группы `AstraShell`, колонка `Erc`:

| Строка ASI | Ресурс | GUID |
|---|---|---|
| `AstraShell.Erc.StartReload` | `Clips/P_Astra_StartReload.anm` | `FCB314232D355753` |
| `AstraShell.Erc.GrabShell` | `Clips/P_Astra_GrabShell.anm` | `1D4C14261EFC54DB` |
| `AstraShell.Erc.InsertShell` | `Clips/P_Astra_InsertShell.anm` | `D3868FB32BF75DEE` |
| `AstraShell.Erc.CheckContinue` | `Clips/P_Astra_CheckContinue.anm` | `36BCB6296CAE5334` |
| `AstraShell.Erc.EndReload` | `Clips/P_Astra_EndReload.anm` | `D1B33891A663548D` |

То есть назначение `StartReload → P_Astra_StartReload.anm` **присутствует на диске**. Однако:

- Файл не под Git (аддон не репозиторий) — состояние на диске нельзя сравнить с базой.
- Массовый mtime 18:58:13 **не позволяет** отличить «ручное назначение владельца» от «назначения, перенесённого вместе с миграцией».
- Ни Git, ни mtime не могут показать, разошлась ли **память Workbench** с этим файлом (несохранённая правка). Это принципиальное ограничение, а не пробел проверки.

`MP133_Astra_weapon.asi` зеркально назначает те же пять позиций на `W_Astra_*.anm`; все пять GUID также совпадают с meta.

---

## 5. Согласованность GUID (статическая)

Проверены все десять пар `ASI → ANM.meta` и ссылки каркаса:

- `MP133_Astra.aw` → AST `FD37F7091A235471`, W ASI `AE8E3367177C57BD`, P ASI `2629533DCE9A5811`, AGR `9A5A46E2D8F8586F` — совпадают с meta.
- `MP133_Astra.agr` → AST `FD37F7091A235471`, AGF `9ABFB44D704F57A9` — совпадают.
- Все 10 ASI‑строк → GUID ANM — совпадают (см. §4 и `migration_v2.json`).

**Вывод:** обрыва адресации на диске нет. Статически источник `AstraShell.StartReload` разрешается полностью.

---

## 6. Что именно означает ошибка `AstraStartReload` / `Invalid source`

В `MP133_Astra.agf` (линии 110–134) пять узлов-источников:

```
AnimSrcNodeSource AstraStartReload { Source "AstraShell.StartReload" ... }
AnimSrcNodeSource AstraGrabShell  { Source "AstraShell.GrabShell"  ... }
AnimSrcNodeSource AstraInsertShell{ Source "AstraShell.InsertShell"... }
AnimSrcNodeSource AstraCheckContinue { Source "AstraShell.CheckContinue" ... }
AnimSrcNodeSource AstraEndReload  { Source "AstraShell.EndReload"  ... }
```

Узел `StartReload` стейт-машины `ShellReloadSTM` ссылается на `Child "AstraStartReload"`, а узел `AstraShellErcG` — `Group "AstraShell"`, `Column "Erc"`.

Значит `AstraStartReload` в Errors — это **не** отдельный ресурс, а имя узла графа, чей `Source "AstraShell.StartReload"` не разрешился в момент сборки/загрузки графа. Цепочка разрешения: `AGF node → AST (группа AstraShell) → ASI (AstraShell.Erc.StartReload) → ANM (GUID)`. Поскольку все звенья на диске корректны, отказ имеет смысл искать в двух местах:

1. **Состояние ресурсов в работающем Workbench** (сессия/кеш/индекс не знает новых ANM или старой группы) — тогда помогает повторное открытие + пересборка.
2. **Логика разрешения новой группы `AstraShell`** (регистрация группы, колонка `Erc`, сопоставление имён строк ASI) — тогда пересборка не поможет, и это предмет Stage 1B.

Статически эти два варианта **неразличимы**. Именно поэтому нужен контролируемый прогон.

---

## 7. Гипотеза устаревшего состояния Workbench

Формулировка: *Workbench в текущей сессии разрешает источники графа по устаревшему/закешированному набору анимационных ресурсов; ручное назначение `P_Astra_StartReload.anm` открыло сам ANM, но граф компилируется против старого состояния и потому держит `Invalid source`.*

Статус: **ВЕРОЯТНАЯ, НЕ ДОКАЗАННАЯ.**

Что её поддерживает:
- На диске всё согласовано, значит ошибка, скорее всего, не файловая.
- Ручное открытие ANM доказало, что ресурс читается редактором.

Что её **не** доказывает:
- Успешное назначение **одного** ANM не говорит о причине и о судьбе остальных девяти.
- `Invalid source` может быть следствием того, как граф разрешает **новую группу `AstraShell`**, а не кеша.
- Нет ни одного проверяемого «после пересборки» результата.

---

## 8. Ограничения доказательств

- Git не отслеживает аддон `ARMSTMP133T4B_InstalledMagProbe` — `git status` там неприменим.
- Одинаковый mtime 18:58:13 не различает миграцию и ручную правку.
- Ни Git, ни mtime не видят несохранённые изменения в памяти Workbench.
- Статический разбор **не является** runtime/Workbench‑подтверждением (правило 13 AGENTS.md).

---

## 9. Безопасная процедура для владельца

Цель — одна контролируемая проверка. **Не** переимпортировать ANM, **не** пересоздавать `.meta`, **не** чистить кеш вручную, **не** менять GUID, **не** запускать игровую перезарядку.

0. **Резервная копия (до сохранения).** Скопировать (не перемещать) поддерево и ключевые файлы в scratch‑папку инструментального репозитория:
   ```powershell
   $src = "C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\ARMSTMP133T4B_InstalledMagProbe\Assets\MP133_AstraShellGraph"
   $dst = "C:\Users\yshky\Documents\My Games\ArmaReforgerWorkbench\addons\Weapon_ARMA_X\artifacts\astra-stage1a-backup"
   New-Item -ItemType Directory -Force -Path $dst | Out-Null
   Copy-Item $src -Destination $dst -Recurse -Force
   ```
   Это копия **наружу**, в git‑ignored `artifacts/`; в аддон ничего не пишется. Сверить, что копия создана, до шага 1.

1. **Сохранить только намеренное изменение** в открытом `MP133_Astra.aw` (Animation Editor → Save). Не использовать «Save All», если он запишет посторонние ассеты; если иначе нельзя — сначала зафиксировать, какие именно файлы он пишет.

2. **Полностью закрыть Workbench** (не только окно workspace), чтобы освободить память и кеш сессии.

3. **Повторно открыть проект** `...\ARMSTMP133T4B_InstalledMagProbe\addon.gproj`. Убедиться, что standalone‑аддон `ARMSTMP133AstraShellGraph` отсутствует/выключен (сейчас его нет на диске). Core/T2A/V2/P2 не подключать.

4. **Открыть** `Assets/MP133_AstraShellGraph/MP133_Astra.aw`.

5. **Штатная пересборка графа** командой редактора анимаций (Compile/Rebuild в Anim Graph/Workspace). Вручную `.agf` не редактировать.

6. **Открыть вкладку Errors** и зафиксировать:
   - исчезла ли ошибка `AstraStartReload`;
   - сколько ошибок осталось и их полный текст/пути;
   - сохранились ли десять назначений ASI (в частности `AstraShell.Erc.StartReload` → `P_Astra_StartReload.anm`);
   - по возможности — скриншот таблицы ASI и вкладки Errors.

7. **После сохранения** (по желанию) прислать новые mtime/SHA‑256 `MP133_Astra_player.asi` и `.agf`, чтобы поймать, менялись ли файлы на самом деле.

Время: одна сессия. Никаких промежуточных правок между шагами.

---

## 10. Что ожидается на выходе

- Ответ по `AstraStartReload`: исчезла / осталась.
- Число и текст оставшихся ошибок.
- Статус десяти ASI‑назначений (сохранены / пропали / изменились).
- (если есть) новые хэши `.asi` и `.agf` после сохранения.

---

## 11. Решающий порог (decision gate)

- **Ошибка `AstraStartReload` исчезла после переоткрытия и штатной пересборки, назначения сохранены** → гипотеза устаревшего состояния получает **проверяемое подтверждение** для этого узла. Всё равно открыть каждый из десяти ANM: исчезновение одной ошибки не доказывает корректность остальных девяти.
- **Ошибки остались без изменений** → гипотеза кеша **ослаблена**. Переходим к Stage 1B: как граф разрешает новую группу `AstraShell` (регистрация группы и колонки `Erc`, `AnimSrcNodeGroupSelect`, сопоставление имён строк ASI, порядок групп в `.ast`).
- **Назначение `StartReload` пропало после переоткрытия** → отдельный сигнал: сохранение не персистировалось либо Workbench перезаписал ASI.

Пока ни один из исходов не получен, причина **не считается установленной**.

---

## 12. Несанкционированные действия

До результата проверки владельца запрещено: изменять исходники, массово импортировать ANM, пересоздавать `.meta`, удалять кеш вручную, менять GUID, запускать игровую перезарядку, коммитить/пушить что‑либо из этого. Настоящий отчёт — артефакт инструментального репозитория; игровой аддон не тронут.

---

## Приложение A. Зафиксированные SHA-256 (состояние до проверки)

Основные файлы (`ARMSTMP133T4B_InstalledMagProbe\Assets\MP133_AstraShellGraph`):

| Файл | Размер | SHA-256 |
|---|---|---|
| `MP133_Astra_player.asi` | 14680 | `A3DE8D923CE0FC6F1E9661A00354D31807045ECD916CBB4E953F6BD9EEE949D9` |
| `MP133_Astra_player.asi.meta` | 405 | `640CB9E6093162313121B6A467F0F4307014ECDC17F891D6F2785A4299BD8443` |
| `MP133_Astra_weapon.asi` | 5228 | `C93D31B3A30099B068EDA0D2330005ED458CBB83621A7D503B352975905F0737` |
| `MP133_Astra_weapon.asi.meta` | 405 | `6D629DB4A0B096BA6D8B6F29AAB499EBCD69CB832F16DBD69B4162761BCCFB56` |
| `MP133_Astra.aw` | 1022 | `4A4BF5A5E93CA5E1D08767A2D66104C5AB845DAEADB8CD6177381CDDD71B917E` |
| `MP133_Astra.ast` | 1101 | `FC4ABF0720F960409A69DF0578EE95997337AFCA881D54782326D23A9C4BED5E` |
| `MP133_Astra.agr` | 2472 | `6C08181FF2E5E846C68EAF0CD75BC34E12DDE68B4BBAF469E1A014FC20F772AC` |
| `MP133_Astra.agf` | 33684 | `9867D553DD5CC4B55F6DE84EEE4EC6CA2C4EED06772D038A46E00666601E19EF` |
| `Scripts/.../ARMST_T4B_AstraV2_WeaponAnimationComponent.c` | 5386 | `DBBD9B49C376123A702BDF16C5F7EA16CCC147F1A67947E6C5AB07E0F1FDD00B` |

Импортированные ANM (`...\Clips`):

| Файл | Размер | SHA-256 |
|---|---|---|
| `P_Astra_StartReload.anm` | 4439 | `4B8B87D8F3AA80A2574D2F22D48ECA2BB5134A6FECE033FE8EE7B4D5BB675FA5` |
| `P_Astra_GrabShell.anm` | 7195 | `6BF1429CEA8CC62C219C83A647D4758425029DFFCC1D1318861BAC638687E625` |
| `P_Astra_InsertShell.anm` | 8514 | `875958267DCADE9645F69DFDA633C01A2A4BDED1ABEE4745F86778F047012EA0` |
| `P_Astra_CheckContinue.anm` | 4441 | `3C3C3FBD0F877BE17966FF1C182B67D60A7909855DD2E02792B399BC370603C7` |
| `P_Astra_EndReload.anm` | 4584 | `3D8B3BB14EAF54D3839E9D295F9871EBE8F362AA42C1AEF73B62132D2474A42C` |
| `W_Astra_StartReload.anm` | 771 | `BE1A6B3D1612570CD39E13D9B3A3D947C6F867330353FA493C868F0B9C7B420B` |
| `W_Astra_GrabShell.anm` | 1031 | `695D07748768AA2B759A994BA25024584C40BC360050CE966D5F0C7328BB92D9` |
| `W_Astra_InsertShell.anm` | 1556 | `96D1BE725952251CEC4401B21255153870987B872D49F573894D6FAF7438CFA8` |
| `W_Astra_CheckContinue.anm` | 773 | `0D3E6C73C40C3CEE795313C628BA8A682B96618864F4BFB58633DEA5E9F2EAFE` |
| `W_Astra_EndReload.anm` | 916 | `D2A48EA5784F584C637C22F9B86D219465A94A28D3D26DA6A5DB93B79D25D885` |

Все 22 файла, общие для Workbench‑аддона и `Weapon_ARMA_X/labs/...`, совпали по SHA‑256; 20 ANM/meta присутствуют только в Workbench‑аддоне.
