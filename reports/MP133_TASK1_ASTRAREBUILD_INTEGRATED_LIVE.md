# MP-133 Task #1 — AstraRebuild интегрирован в живой T4b

Статус: **TASK1_ASTRAREBUILD_REGISTERED_NO_LEGACY_MAG_NODES_OWNER_ANIMATION_GATE** (6 анимационных ресурсов зарегистрированы и связаны; регистрация фикстур-префаба — owner Workbench)
Дата: 2026-10-04
Задание: Issue #34 [#5984112925](https://github.com/Dubelkrya/Weapon_ARMA_X/issues/34#issuecomment-5984112925).
База: `t4b/installed-mag-probe` @ `8fa0fb8`. Оригинал не изменялся.

---

## 0. Фактическое расположение (используем owner-копию)
Owner-дубликат Workbench создал в **`Assets/MP133_AstraShellGraph_test/`** (AW basename `MP133_AstraShellGraph_test.aw`). Второй копии не создавалось, переименований нет.

Новые ресурсы и **уникальные** GUID (проверено по `.meta`, старые GUID не совпадают):

| Ресурс (live) | Новый GUID | Старый GUID |
|---|---|---|
| `MP133_Astra.ast` | `6CFA1ACC8873A4B6` | `FD37F7091A235471` |
| `MP133_Astra.agr` | `7E087CCCBFB67045` | `9A5A46E2D8F8586F` |
| `MP133_Astra.agf` | `5106627621151975` | `9ABFB44D704F57A9` |
| `MP133_Astra_player.asi` | `B7A966A6741EAEE2` | `2629533DCE9A5811` |
| `MP133_Astra_weapon.asi` | `4CF7F797EC1FCA0E` | `AE8E3367177C57BD` |
| `MP133_AstraShellGraph_test.aw` | `A744E2E9E141725B` | `3BB0BA3983BD5729` |

Workbench при дублировании сам прописал новые GUID во внутренние ссылки — staged AW/AGR/ASI **не перезаписывались вслепую**.

---

## 1. Что сделано (интеграция)

1. В живой `Assets/MP133_AstraShellGraph_test/MP133_Astra.agf` установлен **очищенный** AGF из `8fa0fb8` (`.meta` сохранён, GUID `{5106627621151975}`). Legacy-ноды отсутствуют (0): `WeaponReloadSTM`, `MagReloadSTM`, `WeaponReloadStanceSTM`, `InsertMagAnim`, `RemoveMagAnim`, `ReloadErcCroG`, `ReloadPneG`, `Blend T 1`. Единственный главный маршрут: `ReloadRouteSTM` — `Bolt→RackBoltAnim` (CMD1), `Shell→AstraShellErcG→ShellReloadSTM` (CMD2-6); 5 фаз Astra; `ASTRA_ShellRequest` отсутствует.
2. Проверена замкнутость ссылок (по фактическим GUID):
   - AW → AST/AGR/W ASI/P ASI = 1/1/1/1;
   - AGR → AST/AGF = 1/1;
   - P ASI/W ASI → AST = 1/1; 10 ANM-ссылок указывают на **исходные** `Assets/MP133_AstraShellGraph/Clips/*.anm` (переиспользование, без дублирования);
   - фикстур → AGR/W ASI/P ASI = 2/1/1.
   - Старые workspace-GUID в новых файлах = 0.
3. Создан новый тестовый префаб **в живом T4b**: `Prefabs/Test/ARMST_T4B_AstraRebuild_TestWeapon.et` — thin child производственного MP-133, фиксированный `Tube3`, lab-probe, `AnimGraph/AnimInstance/AnimInjection` → новые AGR/W+P ASI, **без** ASTRA PROBE, **без** write-G3B2, без глобальных хуков и кнопок.

---

## 2. Осталось (owner Workbench, один проход)

Регистрация нового **префаба** как ресурса (его `.meta`/GUID) — стандартная процедура Workbench; агент GUID не изготавливает. Действия:
1. Открыть проект T4b в Workbench (игру не запускать) — Workbench зарегистрирует `ARMST_T4B_AstraRebuild_TestWeapon.et` и выдаст его resource GUID.
2. **Сохранить и полностью закрыть Workbench.**
3. Прислать GUID нового префаба (или скрин Resource Browser) — при необходимости агент зафиксирует его в Git.

---

## 3. Проверка владельцем (Animation Editor)

1. Открыть новый **`Assets/MP133_AstraShellGraph_test/MP133_AstraShellGraph_test.aw`** независимо от оригинала.
2. Ожидается: ноль **новых** красных ошибок графа/скриптов; 10 строк `Reload/Erc` P/W ASI назначены; в графе — единственный reload-маршрут Astra + сохранённый CMD1 bolt.
3. **Animation-only** preview одного цикла: `StartReload → GrabShell → InsertShell → CheckContinue → EndReload`, repeat `CheckContinue→GrabShell`, выход; CMD1 rack не тронут.
4. **Не** запускать игровой R/CMD4/5/6 — сначала нужно отдельно решить engine-level автономную замену физического `Tube3` (UNRESOLVED).

---

## 4. Сохранность

- Оригинал `Assets/MP133_AstraShellGraph/` (хэши `C9639C5F…`/`D1057448…`/… не изменились), исходные 10 ANM+meta, production/Core/worlds, G3B2, старые фикстуры — **байт-идентичны**.
- Workbench-generated `.meta` новых ресурсов сохранены байт-в-байт.
- Staging `labs/…/MP133_AstraRebuild/` удалён; авторитетный путь в репозитории — `labs/…/Assets/MP133_AstraShellGraph_test/` (избегаем двух неоднозначных копий).
