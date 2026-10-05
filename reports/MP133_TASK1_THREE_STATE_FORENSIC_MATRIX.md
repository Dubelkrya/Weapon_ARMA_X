# MP-133 Task #1 — Трёхсостояниевое форензик-сопоставление (ORIGINAL / old_pa / ASTRA2)

Статус: **ASTRA2_KNOWN_GOOD_REFERENCE_CONFIRMED** + **CORRELATION_ONLY_MORE_GUI_EVIDENCE_NEEDED** (для точной причины strip)
Дата: 2026-10-05
Задание: Issue #34 [#5998200856](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5998200856). Режим: **READ-ONLY**. Live-аддон не изменялся; live-папки в Git не синхронизировались.

---

## 0. Состояния и идентификаторы

| | ORIGINAL | ASTRA2 | old_pa |
|---|---|---|---|
| путь | `Assets/MP133_AstraShellGraph/` | `Assets/MP133_AstraShellGraph_test/` (корень) | `Assets/MP133_AstraShellGraph_test/old_pa/` |
| AW | `MP133_Astra.aw` `{3BB0BA3983BD5729}` | `astra2.aw` `{019C37AEF4C6EA8A}` | `MP133_AstraShellGraph_test.aw` `{A744E2E9E141725B}` |
| AST | `{FD37F7091A235471}` (1189) | `{BDD6F7ED84814A1E}` (965) | `{6CFA1ACC8873A4B6}` (1143) |
| AGR | `{9A5A46E2D8F8586F}` (2414) | `{AF2491EDB3449EED}` (2426) | `{7E087CCCBFB67045}` (2101) |
| AGF | `{9ABFB44D704F57A9}` (33843) | `{802A8F572DE7F7DD}` (33843) | `{5106627621151975}` (29192) |
| P ASI | `{2629533DCE9A5811}` (14866) | `{A43FF9780FC454A4}` (14872) | `{B7A966A6741EAEE2}` (13764) |
| W ASI | `{AE8E3367177C57BD}` (5300) | `{5F61684997C53048}` (5306) | `{4CF7F797EC1FCA0E}` (4198) |

Все три набора внутренне самосогласованы (AW→свой AST/AGR/ASI, AGR→свой AST/AGF, ASI→свой AST). Дубликатов GUID нет; cross-link на другую копию нет.

---

## 1. Форензик-матрица

| Поле | ORIGINAL | old_pa | ASTRA2 | Значение | Уверенность |
|---|---|---|---|---|---|
| AGF (норм.) | исходный | переписан (Astra) | **== ORIGINAL** | Astra2 — клон рабочего | высокая |
| AST `Reload` группа: 5 фаз | да | да | да | не дискриминатор | высокая |
| AST `Reload`: `Reload_InsertMag/RemoveMag` | **есть** | **нет** | **есть** | удалено Astra | высокая |
| AST `AstraShell` группа | есть | есть | **нет** | не дискриминатор (в ORIGINAL есть) | высокая |
| ASI: 5 фаз P/W | **5/5** | **2/5** (Check/End) | **5/5** | рабочий vs сломанный | высокая |
| ASI: legacy mag строки | **есть** | **нет** | **есть** | удалено Astra | высокая |
| ASI: позиция фаз-строк | вкраплены (L22/25/40/43/58) | сверху (L4/7) | вкраплены (как ORIGINAL) | авторская раскладка Workbench | средняя |
| AGR `ASTRA_*` переменные | 5 | **0** | 5 | AGF old_pa их не использует → согласовано | высокая |
| AGF `ReloadRouteSTM` | нет | **да** | нет | Astra-переписывание | высокая |
| AGF `RackStanceSTM/RackErcG/RackPneG` | нет | **да** | нет | Astra-фикс затвора | высокая |
| AGF legacy `WeaponReloadSTM` | 3 | **0** | 3 | удалено Astra | высокая |
| AGF `AstraShellErcG` | `Group "Reload"`, `Column "Erc"` | `Group "Reload"` | `Group "Reload"` | совпадает | высокая |
| AGF 5 `Source` | `Reload.<phase>` | `Reload.<phase>` | `Reload.<phase>` | совпадает | высокая |
| AW `ChildPreviewModel.Parent` | `{8C8CCC9FC8635548}` | `{6A8947ABB9A94652}` | `{6A8AFD4859CC16BA}` | preview-иерархия, НЕ line-ownership | высокая |

---

## 2. Классификация различий

**1) Заведомо безопасные клон-различия:** все resource GUID (AST/AGR/AGF/AW/P+W ASI) и path-строки; внутренние node/group GUID в AST; `.aw` `PreviewModels`/`ChildPreviewModels`/`Parent` (preview-модель, не строки). `Astra2` сняла `AstraShell` AST-группу — семантически нейтрально для строк.

**2) Намеренные исправления Astra (сохранить):** `RackStanceSTM`/`RackErcG`/`RackPneG`; `ReloadRouteSTM` + CMD1→bolt; безопасные cancel-условия; удаление legacy `Reload_InsertMag/RemoveMag` (AST+ASI) и native `WeaponReloadSTM`; изоляция CMD2-6; вычищенные неиспользуемые `ASTRA_*` переменные (в old_pa AGF они не используются — согласовано).

**3) Различия, коррелирующие с потерей/неперсистентностью строк:** в old_pa — 5 фаз-строк ASI вставлены **сверху** `Lines {}` и из них выжили только последние две (`CheckContinue`,`EndReload`); в рабочих состояниях строки стоят во **вкраплённых** позициях, где их разместил Workbench. Также old_pa лишён legacy mag-строк/native-ветки.

**4) Единое конкретное свойство, присутствующее в ORIGINAL+ASTRA2 и отсутствующее в old_pa:** полный **legacy-набор `Reload_InsertMag/Reload_RemoveMag` в AST `Reload` и в обеих ASI + native-ветка `WeaponReloadSTM` в AGF**. Именно этот набор удалён в old_pa. (Оговорка: удаление legacy-мага само по себе вряд ли удаляет строки фаз; вероятнее сопутствующее изменение раскладки/авторства строк — см. §3.)

**5) Является ли ASTRA2 настоящим клоном known-good:** **ДА.** GUID/путь-нормализованно `ASTRA2.agf` **байт-идентичен ORIGINAL.agf**; `ASTRA2` P/W ASI идентичны ORIGINAL (кроме имени файла); `AGR` идентичен (кроме пути); `AST` = ORIGINAL минус группа `AstraShell`. То есть ASTRA2 — рабочий эталон (5/5 строк), а не «просто похожий в Resource Browser».

**6) Минимальный безопасный план будущего восстановления (НЕ выполнять):** взять за эталон ASTRA2 (или ORIGINAL), перенести в проблемную копию **только** структуру строк в их авторской раскладке (а не текстовой вставкой сверху), при этом сохранив Astra-фиксы (`RackStanceSTM`/`RackErcG`/`RackPneG`, `ReloadRouteSTM`, удаление legacy-мага, CMD2-6 isolation). Точную причину strip подтвердить GUI-экспериментом (создание строк через Create Line/Set Anim в рабочей раскладке).

---

## 3. High-value question: «parent»/line-ownership

Проверены: `.aw` (единственный `Parent` — `AnimSrcWorkspaceChildPreviewModel.Parent`, это **preview-модель**, не строки), ASI-блоки (поля только `AnimSetInstanceSource_Line "name" { Resource "..." }` — **никакого parent/line-ID нет**), AGR/AST/AGF. В установленном Workbench 1.8.0.13 не найдено сериализуемого «parent»-концепта для строк Animation Set. **Гипотеза о «parent» для строк не подтверждается структурой файлов.**

---

## 4. Ограничения / что осталось неподтверждённым

- Точный внутренний критерий Workbench, почему из пяти текстово-вставленных строк выживают именно две последние, **не доказан** (корреляция: авторская раскладка vs вставка сверху). Нужен GUI-эксперимент.
- Статический анализ не заменяет проверку в редакторе.

Статус: **ASTRA2 подтверждён как known-good эталон; причина strip — correlation-only, требуется GUI-подтверждение.** Игровой R/CMD4/5/6 и правки не выполнялись; live в Git не синхронизировался.
