# MP-133 Astra — Stage 1B: перезапись ASI в Workbench и изолированный эксперимент «группа vs путь»

> **Addendum (Stage 1B execution, 2026-10-04):** одобренный путь — минимальная field-wise **in-place** правка ЕДИНСТВЕННОГО живого аддона (пять фаз в группе `Reload`), а не развёртывание подготовленного `variant-reload`. Артефакты `artifacts/astra-stage1b/` — только анализ, не второй аддон. Выполнение и проверка владельца:
> [`MP133_ASTRA_STAGE1B_INPLACE_RELOAD_PATCH.md`](MP133_ASTRA_STAGE1B_INPLACE_RELOAD_PATCH.md).

Статус: **STAGE1B_ASI_REWRITE_CONFIRMED / GROUP_EXPERIMENT_READY_FOR_OWNER / WORKBENCH_PENDING**
Дата: 2026-10-04
Тип задачи: read-only диагностика + подготовка изолированного эксперимента на защищённой копии.
Живой аддон и источники не изменялись. Десять ANM и их `.meta` не изменялись.
Предшественник: `reports/MP133_ASTRA_STAGE1A_DIAGNOSIS_AND_WORKBENCH_REVALIDATION.md` (частично устарел — см. §1).

---

## 0. Главное

1. **Зафиксировано новое наблюдаемое событие.** 2026-10-04 в **20:58:58** Workbench открыл и перезаписал `Assets/MP133_AstraShellGraph` живого аддона `ARMSTMP133T4B_InstalledMagProbe`. При этом:
   - группа `AstraShell` **осталась** в `MP133_Astra.ast`;
   - все **33** ссылки `AstraShell.*` **остались** в `MP133_Astra.agf` (включая узел `AstraStartReload`);
   - **все десять строк `AstraShell.Erc.*` из обеих `.asi` были удалены**, а пути ресурсов нормализованы (`Mp_133/...` → `Assets/Weapons_RUS/...`), а `AnimSetInstanceSource "{...}"` превращён в анонимный `AnimSetInstanceSource {`.
2. Это **исчерпывающе объясняет текущий `Invalid source` в живом аддоне**: граф ссылается на `AstraShell.*`, а инстанс анимаций больше не содержит этих строк. То есть редактор при сохранении **молча выбросил привязки новой группы**.
3. Опубликованный (git) источник `Weapon_ARMA_X/labs/...` **не тронут** — в нём десять строк на месте. Разошлись именно живая копия (перезаписана Workbench) и опубликованная.
4. Гипотеза «обычный устаревший кеш» теперь **заменена** более точной: проблема не в сохранении/перезапуске как таковых, а в том, что Workbench **не принимает строки новой группы `AstraShell`** в инстанс (пункт 1). Это указывает на причину **A** (разрешение новой группы), но **не доказывает** её: удаление строк могло быть следствием и сбоя пути `GroupSelect` (причина **B**).
5. Чтобы различить A и B, подготовлен **один изолированный эксперимент** — релокация пяти shell-анимаций из новой группы `AstraShell` в существующую `Reload` при неизменной механике пути. Артефакты и рантбук: `artifacts/astra-stage1b/` (см. §6).
6. Пока эксперимент не выполнен, причина **не считается установленной**.

---

## 1. Поправка к Stage 1A

Отчёт Stage 1A зафиксировал состояние на 18:58:13, когда обе `.asi` ещё содержали десять строк, а 22 общих файла совпадали с опубликованным источником. Это состояние **больше не соответствует живому аддону**: в 20:58:58 Workbench перезаписал `MP133_Astra.{aw,ast,agr,agf}` и обе `.asi`. Хэши из приложения A отчёта Stage 1A для этих файлов **устарели**. Импортированные ANM/meta (`Clips/*.anm*`) с 18:58 не менялись и остаются актуальными.

Живые хэши после перезаписи Workbench (20:58:58):

| Файл | Размер | SHA-256 |
|---|---|---|
| `MP133_Astra_player.asi` | 14115 | `C43E07527CF2602F168E76F2B149F17A03D9FA740AD5D2F26310FE7FA9851865` |
| `MP133_Astra_weapon.asi` | 4549 | `D88A956493A98508B3D6EFBCC34FE3702E5C8D89C16CBF29C9193EC2C8B75F61` |
| `MP133_Astra.agf` | 33764 | `D85971CF7F1848C3E34F40D0F76C1E4E5A84B91708268C5E3D5B93847709700D` |
| `MP133_Astra.agr` | 2414 | `424632CFB784CCDEA1D3096D3EB6EA582D5602545EF1647699B554AD8E437BAD` |
| `MP133_Astra.aw` | 984 | `D1057448BD1B216038F01555D42B63EA053D4A10DB358DD52DB5E66091F4B8FF` |
| `MP133_Astra.ast` | 1101 | `FC4ABF0720F960409A69DF0578EE95997337AFCA881D54782326D23A9C4BED5E` |

Проверка: разница live↔`labs` в `.agr/.aw/.agf` — это нормализация редактора (добавлен `Axis X`, порядок полей IK, `Mp_133/...` → `Assets/Weapons_RUS/...`, `Enabled Auto`, удалён пустой блок `AttachmentTesting`). Содержательная потеря ровно одна: **десять строк `AstraShell.Erc.*` в двух `.asi`**.

---

## 2. Что именно удалил Workbench

Диф `labs` → live для `MP133_Astra_player.asi` (аналогично weapon):

```
-AnimSetInstanceSource "{12820BA58DCB5EFB}" {
+AnimSetInstanceSource {
  Template "{FD37F7091A235471}Assets/MP133_AstraShellGraph/MP133_Astra.ast"
  Lines {
-  AnimSetInstanceSource_Line "AstraShell.Erc.StartReload" { ... P_Astra_StartReload.anm }
-  AnimSetInstanceSource_Line "AstraShell.Erc.GrabShell"  { ... P_Astra_GrabShell.anm }
-  AnimSetInstanceSource_Line "AstraShell.Erc.InsertShell" { ... P_Astra_InsertShell.anm }
-  AnimSetInstanceSource_Line "AstraShell.Erc.CheckContinue" { ... P_Astra_CheckContinue.anm }
-  AnimSetInstanceSource_Line "AstraShell.Erc.EndReload"  { ... P_Astra_EndReload.anm }
   AnimSetInstanceSource_Line "Reload.Erc.Fire" { ... }
   ...
```

Пять строк исчезли и в `player`, и в `weapon` (итого десять). Ресурсы `Reload.*`/`Inspection.*` сохранены.

Сопоставление с рабочим прецедентом:
- Кастомная группа + `GroupSelect` **работают**: `Boar` (`Group "Boar"`, `Column "Default"`, строки `Boar.Default.Attack1`, источники `Source "Boar.Attack1"`) — ровно та же схема, что у Astra.
- Кастомный дробовик `bc_ithaca_m37` кладёт весь shell-цикл (`Reload_GrabShell`, `Reload_InsertShell`, `Reload_PumpAction`, `Reload_ReturnToIdle`) в **существующую** группу `Reload`.

Вывод: схема `AstraShell` формально валидна, но редактор её строки не удержал. Нужен контролируемый эксперимент, различающий «новая группа» и «форма пути».

---

## 3. Гипотеза: где мы находимся

- **Устаревший кеш (Stage 1A):** ослаблен/заменён. Перезапись в 20:58:58 — это не «не прочитал старое», а **активная регенерация инстанса**, выбросившая строки новой группы.
- **Причина A — новая группа `AstraShell` не разрешается (не регистрируется/не принимается):** согласуется с удалением строк при регенерации, но не доказана.
- **Причина B — путь через `GroupSelect`/форма источника:** не объясняет удаление строк инстанса напрямую (ASI и граф живут раздельно), но граф мог считать группу неиспользуемой и тем спровоцировать очистку. Не исключена.

Статус обеих: **вероятные, не доказанные**. Различающий эксперимент — §6.

---

## 4. Git и локальные файлы (на момент отчёта)

| Репозиторий | Ветка | HEAD | Состояние |
|---|---|---|---|
| `Weapon_ARMA_X` (инструменты) | `t4b/installed-mag-probe` | `cec5c81ff7edbf6366ed301ae0a1c9af730c2a35` | чисто, синхронно с origin; untracked `reports/CORE_ARMST_READONLY_AUDIT.md` (+ новые артефакты/отчёты этого шага) |
| `ARMST-PLATFORM---Weapons` (живой) | `main` | `9ebf3234fa4dabdae1faafb1051977ecf818d18f` | позади origin на 3; грязные `resourceDatabase.rdb`, `worlds/.../default.layer` |
| `ARMSTMP133T4B_InstalledMagProbe` | — | — | **не git-репозиторий**; перезаписан Workbench в 20:58:58 |

`git status` не видит аддон `ARMSTMP133T4B_InstalledMagProbe`, поэтому единственный способ поймать перезапись — прямое сравнение с опубликованным (`labs`) источником, что здесь и сделано.

---

## 5. Ограничения

- Ошибка `Invalid source` в живом аддоне **объясняется** отсутствием строк в ASI, но **не объясняет**, почему Workbench их выбросил.
- Статический анализ не заменяет прогон в Workbench.
- Причина не установлена до выполнения §6.

---

## 6. Изолированный эксперимент (готов)

Каталог: `Weapon_ARMA_X/artifacts/astra-stage1b/`
- `EXPERIMENT.md` — краткий рантбук и таблица истинности.
- `prepare_experiment.ps1` — сборка защищённых копий (уже выполнена, `ANM_META_UNCHANGED=1`).
- `baseline/ARMSTMP133T4B_InstalledMagProbe/` — опубликованное состояние графа + локальные ANM (десять строк ASI на месте).
- `variant-reload/ARMSTMP133T4B_InstalledMagProbe/` — те же ANM и та же механика пути, но пять shell-анимаций перенесены в существующую группу `Reload`.

Проверено: сравнение baseline↔variant даёт различие ровно в четырёх файлах (`MP133_Astra.ast`, `MP133_Astra.agf`, `MP133_Astra_player.asi`, `MP133_Astra_weapon.asi`); baseline ASI побайтно равны опубликованным; десять ANM и десять `.meta` идентичны исходным в обеих копиях.

**Единственная переменная:** группа, в которой объявлены shell-анимации (новая `AstraShell` → существующая `Reload`). `GroupSelect`, колонка `Erc`, бесколоночный `Source "<Group>.<Animation>"` и форма строк ASI `<Group>.Erc.<Animation>` не меняются.

**Различающая проверка в Workbench:** открыть `variant-reload`, сохранить workspace, пересобрать граф, посмотреть Errors и — главное — остались ли строки `Reload.Erc.StartReload … EndReload` в `.asi` **после** сохранения. Затем то же для baseline.

| Исход variant | Вывод | Следствие |
|---|---|---|
| строки сохранены, `AstraStartReload` исчез | **A**: новая группа не принимается | исправление = shell-анимации в существующей `Reload` (как `bc_ithaca_m37`) либо перерегистрация группы до сохранения ASI |
| строки снова удалены и/или ошибка осталась | **B**: дело не в имени группы, а в пути/форме привязки | изолировать `Source` с колонкой/без, заголовок instance, порядок строк |

**Условия:** одновременно загружен только эксперимент-проект; оригинальный T4b и standalone Astra выключены; ANM вручную не назначать; `.meta` не трогать; кеш не чистить; GUID не менять; перезарядку не запускать.

---

## 7. Несанкционированные действия

До результата эксперимента запрещено: править живой аддон, массово импортировать ANM, пересоздавать `.meta`, чистить кеш, менять GUID, запускать игровую перезарядку, коммитить эксперимент-копии (они в git-ignored `artifacts/`).
