# MP-133 Astra — Stage 1B execution: минимальная in-place правка группы `Reload`

Статус: **STAGE1B_RELOAD_IN_PLACE_SOURCE_READY_OWNER_WORKBENCH**
Дата: 2026-10-04
Авторизация: Issue #34 [#5982865178](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5982865178) (scope), [#5982917749](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5982917749) (binding instructions), [#5982955713](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5982955713) (start).
Исполнитель: ordinary local T4b agent (единственный писатель).
Целевой аддон: **один** существующий `ARMSTMP133T4B_InstalledMagProbe` (ID `ARMSTMP133T4BInstalledMag`).

---

## 0. Итог

Выполнена ровно одна ограниченная field-wise in-place правка **четырёх существующих текстовых файлов** живого аддона: пять shell-фаз перенесены из новой группы `AstraShell` в существующую `Reload/Erc`; только Astra-ветка перенацелена; в обе `.asi` восстановлены пять P-строк и пять W-строк с прежними importer-owned GUID+path. Никакие копии, второй аддон, новый workspace или дублирующий resource set не создавались и не разворачивались. Артефакты `artifacts/astra-stage1b/` остаются только аналитическими файлами в ignored tool-репозитории.

Проверка владельца в Workbench ещё **не** выполнялась. `SOURCE/STATIC = PASS`, `OWNER GUI = PENDING`.

---

## 1. Что именно изменено (живой аддон, in place)

Только эти четыре файла:

| Файл | Изменение |
|---|---|
| `Assets/MP133_AstraShellGraph/MP133_Astra.ast` | в существующую группу `Reload` (`Columns { Erc Pne }`) добавлены пять строк `"StartReload" "GrabShell" "InsertShell" "CheckContinue" "EndReload"`. Группа `AstraShell` **оставлена как есть**. |
| `Assets/MP133_AstraShellGraph/MP133_Astra.agf` | узел `AnimSrcNodeGroupSelect AstraShellErcG`: `Group "AstraShell"` → `Group "Reload"` (Column остался `Erc`); пять узлов `AnimSrcNodeSource Astra*`: `Source "AstraShell.<Phase>"` → `Source "Reload.<Phase>"`. **Имена узлов, `Child`-ссылки, `ShellReloadSTM`, условия и ASTRA-маркеры не изменялись.** |
| `Assets/MP133_AstraShellGraph/MP133_Astra_player.asi` | добавлены пять строк `Reload.Erc.{StartReload,GrabShell,InsertShell,CheckContinue,EndReload}` с прежними P-ресурсами. |
| `Assets/MP133_AstraShellGraph/MP133_Astra_weapon.asi` | добавлены пять строк `Reload.Erc.{StartReload,GrabShell,InsertShell,CheckContinue,EndReload}` с прежними W-ресурсами. |

Ресурсы (GUID+path importer-owned ANM):

| Фаза | P | W |
|---|---|---|
| StartReload | `{FCB314232D355753}.../Clips/P_Astra_StartReload.anm` | `{979C9964AD7956F5}.../Clips/W_Astra_StartReload.anm` |
| GrabShell | `{1D4C14261EFC54DB}.../Clips/P_Astra_GrabShell.anm` | `{E6534D7B659C59E5}.../Clips/W_Astra_GrabShell.anm` |
| InsertShell | `{D3868FB32BF75DEE}.../Clips/P_Astra_InsertShell.anm` | `{090759CC560C55F2}.../Clips/W_Astra_InsertShell.anm` |
| CheckContinue | `{36BCB6296CAE5334}.../Clips/P_Astra_CheckContinue.anm` | `{5B6872625F3454A4}.../Clips/W_Astra_CheckContinue.anm` |
| EndReload | `{D1B33891A663548D}.../Clips/P_Astra_EndReload.anm` | `{008B42BF7C535275}.../Clips/W_Astra_EndReload.anm` |

Состояние `.agf` после правки: `Group "AstraShell" = 0`, `Group "Reload" = 3`, `Source "AstraShell.* = 0`, `Source "Reload.* = 24` (19 прежних + 5 новых). Имена узлов сохранены (`AstraStartReload` = 2: объявление + `Child`; `ShellReloadSTM` = 2).

Легаси-строки `Reload/Inspection`, включая `Reload.Erc.ReloadActionBolt`, `Reload.*.Reload_InsertMag/Reload_RemoveMag`, все клипы, native cmd1/rack — **не изменялись**. `.agr` и `.aw` **не изменялись**.

---

## 2. Защищённый набор (не изменён)

`PROTECTED_FILES_UNCHANGED=1` — сравнение манифеста SHA-256 до/после правки по **90 файлам** (всё, кроме четырёх правленых), в том числе:

- десять `.anm` и десять genuine importer `.anm.meta` (байт-идентичны);
- все resource `.meta` (`.ast/.agr/.aw/.agf/.asi` metas) — без изменений;
- `Scripts/Game/ARMST_T4B/ARMST_T4B_AstraV2_WeaponAnimationComponent.c`, T4b script, G3B2 источники;
- bridge prefab `Prefabs/Test/ARMST_T4B_AstraV2_Bridge_TestWeapon.et` + `.meta` (`{29AAFC302B134E27}`);
- production/Core/worlds — вне аддона и не трогались.

Манифест: `artifacts/astra-stage1b/protected_hashes_before.json` (до) — после совпал побайтно.

---

## 3. Хэши (live)

| Файл | До (20:58:58) | После (21:18:33) |
|---|---|---|
| `MP133_Astra.ast` | `FC4ABF07…` (1101) | `CF0141EC…` (1189) |
| `MP133_Astra.agf` | `D85971CF…` (33764) | `1EA851EE…` (33740) |
| `MP133_Astra_player.asi` | `C43E0752…` (14115) | `0F7703F1…` (14866) |
| `MP133_Astra_weapon.asi` | `D88A9564…` (4549) | `A6194A78…` (5300) |
| `MP133_Astra.agr` | `424632CF…` | `424632CF…` (не менялся) |
| `MP133_Astra.aw` | `D1057448…` | `D1057448…` (не менялся) |

Файлы записаны LF, UTF-8 без BOM. Рабочая копия Workbench-нормализации (нормализованные пути, анонимный заголовок ASI) сохранена как принятая.

---

## 4. Синхронизация Git

Принятый живой текст четырёх файлов скопирован в существующий snapshot `Weapon_ARMA_X/labs/ARMSTMP133T4B_InstalledMagProbe/Assets/MP133_AstraShellGraph/` (live == labs по SHA-256 для всех четырёх). Коммит — на `t4b/installed-mag-probe` (см. отчёт сессии). Diff: `.ast` +5 строк; `.agf` 6 field-изменений (`Group` + 5 `Source`) плюс уже существовавшая Workbench-нормализация; обе `.asi` — замена пяти `AstraShell.Erc.*` на `Reload.Erc.*` плюс нормализация. Второй аддон/workspace не создавался.

---

## 5. Проверка владельца в Workbench (следующий шаг)

Только после этого отчёта, Workbench закрыт во время правки (процесс не запущен — проверено).

1. Открыть **существующий** `ARMSTMP133T4B_InstalledMagProbe`; standalone Astra/`AstraShellGraph` и прочие лаборатории не подключать.
2. Открыть `Assets/MP133_AstraShellGraph/MP133_Astra.aw`, выполнить штатную пересборку графа.
3. **Главный критерий:** после одного Save + повторного открытия в обеих `.asi` должны физически остаться десять строк `Reload.Erc.{StartReload…EndReload}`; вкладка Errors — ноль **новых** Astra `Invalid source` (прежние семь GroupSelect-предупреждений учитывать отдельно).
4. Открыть `Reload.Erc.StartReload` W и P первыми: наличие ASTRA-маркеров и корректное движение/длительность.
5. Только после разрешения всех пяти источников — один ручной animation-only цикл `ASTRA_ShellRequest` (preview), без записи патронов.
6. **Не** выполнять обычный R/CMD5 (разрушительная нативная смена трубы уже доказана), не трогать ANM/meta/GUID, не запускать перезарядку/донат.

STOP и вернуть первый точный текст ошибки + post-save ASI diff, если:
- строки снова удалены после Save/Reopen;
- пять Astra-ошибок сохраняются;
- любой конфликт/неожиданная перезапись Workbench.

---

## 6. Границы

Stage 1 — только разрешение animation-source. Не выполнялось и не авторизовано: native R/CMD5, перехват ввода, донат-транзакции, боевая перезарядка, production-промоушен, работа в независимой Astra-ветке/PR #35, массовый импорт/перемещение ANM, изменение `.meta`/GUID. Пуш выполнен только в `t4b/installed-mag-probe`.
