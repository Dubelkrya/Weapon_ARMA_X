# Structura — интерьер здания: порталы, BSP, материалы (RU)

Как «оборудовать» простое здание из аддона `Arm_Structura`: внутреннее освещение,
звук, разбиение на комнаты. Всё делается скриптами из `agent/structura/`.

Отработано на `House_Individual_Brus_Modul_1`.

---

## 1. Запуск

В Blender (аддон EBT загружен, **Workbench запущен**):

```python
exec(open(r"C:\Users\yshky\structura_all.py", encoding="utf-8").read())
```

Обёртка `structura_all.py` прогоняет 5 шагов по порядку. Затем — **реимпорт модели
в Workbench** (руками, из скрипта нельзя).

| # | скрипт | что делает |
|---|---|---|
| 1 | `structura_interior.py` | порталы (окна **и двери**) + `BOXVOL_01` |
| 2 | `structura_bsp_shell.py` | BSP-оболочка стен с проёмами |
| 3 | `structura_export.py` | экспорт FBX/XOB через внутренний API EBT |
| 4 | `structura_fix_materials.py --apply` | `MatLightPortal` + локальные `.emat` + привязки в мете |
| 5 | `structura_bsp_meta.py --apply` | `GenerateBSP 1` / `ForceCreatePortals 0` |

Шаги 3–5 идемпотентны — их можно повторять.

---

## 2. Что должно получиться в сцене

| объект | назначение | материал |
|---|---|---|
| `House_Individual_Modul_1_Brus_Lod0` | визуал | родные `.emat` |
| `UTM_*` | коллайдеры (не трогаем) | — |
| `Socket_Door_01..04`, `Socket_Win_01..05` | EMPTY, точки проёмов | — |
| `PRT_01..09` | порталы: 5 окон + наружная дверь + 3 межкомнатные | `PRT_195x72` (`MatLightPortal`) |
| `BOXVOL_01` | объём освещения (probe volume) | `dummyvolume_D3975B51F51E6BD5` |
| `BSP_Shell` | **одно** замкнутое тело: стены + пол + потолок + перегородки с проёмами | `dummyvolume_D3975B51F51E6BD5` |

В Workbench после реимпорта: `Build successful`, без предупреждений.

---

## 3. Правила, которые выяснились на практике

### 3.1 BSP — это СТЕНЫ, а не объём интерьера

Вики `Arma_Reforger:FBX_Import`:
> «The BSP geometry should represent **enclosed space by walls, ceilings, with openings**
> for doors and windows».

Сплошной ящик «по интерьеру» **не работает**: наружный портал оказывается внутри объёма,
и движок не может связать «улицу ↔ помещение»:
```
ProcessAreasAndPortals(): Outside area ... is not reachable!
ExtractConvexEnvelope(): AreaPortal 'PRT_01' doesn't have vertices assigned!
Not all light portals were properly detected, the model is leaking!
```

### 3.2 BSP должен быть ОДНИМ объектом

Этот билд движка стабильно даёт `Build failed`, если BSP состоит из **нескольких
соприкасающихся** объектов (после merge получаются non-manifold рёбра). Проверено:
4 коробки → падение, 9 кусков → падение, один объект → `Build successful`.

Поэтому куски объединяются булевым `UNION` в одно тело. Чтобы union был корректным,
куски строятся **с перекрытием внутрь** (`OVERLAP = 0.05`), а расширяются только
внутренние грани (наружный габарит не раздувается).

### 3.3 Требования к мешу BSP (чек-лист движка)

Полный список — в EBT: `ar_mqa/validation.py`, ветка `EnfusionObjectType.is_bsp`.
Скрипт проверяет то же самое локально через `EnfusionBlenderTools.core.mesh.bmesh_validation`:

- **все грани треугольные** (`is_not_triangulated`) — квады не проходят;
- замкнутость: нет non-manifold рёбер/вершин;
- нет самопересечений, тонких граней, мелких граней, коротких рёбер;
- ровно один материал `dummyvolume_D3975B51F51E6BD5`.

### 3.4 Проём режется ЧУТЬ БОЛЬШЕ портала

`MARGIN = 0.06` в `structura_bsp_shell.py`. Если дыра ровно по порталу, движок пишет:
```
ExtractConvexEnvelope(): AreaPortal 'PRT_01' is larger than input data!
```

### 3.5 LOD0 и коллайдеры СМЕЩЕНЫ — BSP строим по LOD0

У этого здания визуал и коллайдеры разъехались примерно на 0.2 м:

| | x | y |
|---|---|---|
| LOD0 (визуал), стены | −4.42…2.12 | −7.13…7.19 |
| `UTM_..._Brus` | −4.62…2.29 | −7.30…7.39 |

Проёмы ищутся по LOD0 (рейкаст), поэтому и оболочка строится **по габариту стен LOD0**
(вершины LOD0 в диапазоне `z` пола…потолка), иначе портал оказывается не в стене,
а внутри комнаты. Толщина стены берётся из разницы коллайдеров (~0.23).

### 3.6 Порталы

- плоскость из **4 вершин без триангуляции**, нормаль внутрь модели;
- размер — чуть больше проёма;
- позиция — **в середине толщины стены** (не на внутренней/наружной поверхности!);
- класс материала обязан быть **`MatLightPortal`**;
- имя `PRT_n`;
- `structura_bsp_shell.py` принудительно ставит наружные порталы в середину толщины
  стены оболочки (внутренние перегородки не трогает).

### 3.7 Материалы: только локальные `.emat` аддона

Мост EBT **не резолвит игровые ресурсы** — попытка сослаться на
`{D3975B51F51E6BD5}Common/Materials/dummyvolume.emat` даёт:
```
Resource linked to material "dummyvolume_D3975B51F51E6BD5" does not exist.
```
Поэтому — как в `97-50_Panelka`: свои `.emat` в `Data\`:

- `PRT_195x72.emat` = `MatLightPortal { ProjectionMap ".../A_window_195_EM.edds" }`
- `dummyvolume_D3975B51F51E6BD5.emat` = `MatPBRBasic {}`

### 3.8 `ebt_resource_name` + `ebt_enfusion_shader_type`

`structura_export.py` проставляет **оба** поля. Если `ebt_enfusion_shader_type` пуст,
EBT вызывает `create_new_material()` (`material_io.py:126`), который **обнуляет**
`ebt_resource_name`, после чего EBT пытается **пересоздать** `.emat` и падает:
```
Material creation attempted an overwrite of the existing material ... This is not supported!
```
Из-за этого же материал портала каждый раз откатывался в `MatPBRBasic`.

### 3.9 Метки BSP в `.xob.meta`

```
Common TXOCommonClass "{...}" : "{...}MeshObjectCommon.conf" {
   GenerateBSP 1
   ForceCreatePortals 0
   BSPDiagnostics BSPDiagnostics "{...}" {
   }
}
```
`ForceCreatePortals 1` **отключает** построение BSP (вики: «BSP geometry is skipped
altogether») — у `97-50_Panelka` он `1`, поэтому там BSP нет и порталы регистрируются
на корневой узел.

### 3.10 Не вызывать `recalc_face_normals` на LOD

Меш дома **не замкнут** (сотни островов, открытые рёбра). Для незамкнутой оболочки
Blender выбирает ориентацию произвольно и **выворачивает часть стен**. Поэтому
`cleanup_mesh()` в `structura_interior.py` делает только `remove_doubles`.

Диагностика нормалей: `structura_fbx_rays.py` (лучи изнутри комнаты и снаружи),
`structura_fbx_islands.py` (знаковый объём по островам), `structura_normals_check.py`
(в самой сцене).

### 3.11 Имена мешей без `.xxx`

Blender-дубли (`BSP_Shell.004`, `PRT_01.005`) попадают в FBX и ломают соответствие
`fbx ↔ xob.meta` (вики предупреждает отдельно). `structura_bsp_shell.py` удаляет
orphan-меши и выравнивает имена mesh-датаблоков по именам объектов.

---

## 4. Диагностика

| скрипт | что показывает |
|---|---|
| `structura_rooms.py` | мировые границы коллайдеров и LOD0 |
| `structura_dump.py` | дамп сцены (имена, типы, габариты) |
| `structura_align_check.py` | (headless) где стены LOD0, где порталы |
| `structura_fbx_islands.py` | (headless) знаковый объём по островам меша |
| `structura_fbx_rays.py` | (headless) куда смотрят нормали стен |

Headless-запуск:
```
"C:\Program Files\Blender Foundation\Blender 4.5\blender.exe" -b --factory-startup ^
  --python C:\Users\yshky\structura_fbx_rays.py -- <путь к fbx>
```

Логи Workbench:
```
…\My Games\ArmaReforgerWorkbench\logs\<сессия>\console.log
```
искать `Build failed` / `Build successful`, `AreaPortal`, `BSP geometry is not closed`.

---

## 5. Известные ограничения

- EBT не работает без запущенного Workbench: импорт не регистрирует материалы,
  экспорт падает на «overwrite existing materials».
- `ar_mqa` в установке пользователя сломан (`No module named 'EnfusionBlenderTools.core.types'`) —
  на экспорт не влияет, но его валидатор из UI недоступен.
- `BSP grid cell size` / `Export opaque leaves` / `Export BSP occupancy` — настройки
  импорта в Workbench; отладочные (`opaque leaves`, `occupancy`) держать **выключенными**,
  они раздувают модель.
- Аддон `Arm_Structura` не под git — бэкапы файлами в `…\ARMST_Backups\Arm_Structura\`
  (`guid_fix\`, `bsp\`, `bsp_meta\`, `materials\`).

---

## 6. Пути (правятся в начале каждого скрипта)

```
ADDON_ROOT / BUILDING = …\addons\Arm_Structura\Arm_Structura\Assets\Structures\Houses\
                        House_Individual\House_Individual_Brus\House_Individual_Brus_Modul_1
FBX_PATH              = <BUILDING>\House_Individual_Brus_Modul_1.fbx
BACKUP                = …\ARMST_Backups\Arm_Structura\
```


---

## 7. Обновление: headless-конвейер и BSP для Modul_2 (2026-09-23)

Отработано на `House_Individual_Brus_Modul_2`. Итог: BSP собирается, движок
принимает (`Build successful`), наружные порталы — без замечаний.

### 7.1 Запуск без GUI Blender

Весь конвейер идёт **headless** (GUI Blender не нужен, Workbench — нужен, он запущен):

```
blender.exe -b --factory-startup --python structura_headless.py -- export
```

`structura_headless.py`:
1. `read_factory_settings(use_empty=True)`, включает аддон `EnfusionBlenderTools`;
2. импортирует FBX текущего здания (свойство `usage` у коллайдеров восстанавливается
   из FBX — проверено);
3. прогоняет `interior` -> `bsp_shell` -> (при `export`) `export`, `fix_materials`, `bsp_meta`.

Без аргумента `export` — только проверка, FBX не пишется.

### 7.2 Цель здания задаётся одним файлом

`structura_target.py` — одна строка `MODULE = "..."`, оттуда все скрипты берут пути.
Переключение на Modul_3/4 = поменять одну строку.

### 7.3 Перегородки BSP — пробивкой лучами по объёму

По коллайдерам и сокетам планировку угадать нельзя (сокет двери может стоять не в
стене — у Modul_2 `Socket_Door_03` вообще не в той стене, и ось определилась неверно).
Рабочий способ:

* по сетке внутри интерьера считаем **свободное расстояние** (4 луча ±X ±Y до первой
  поверхности): внутри стены ~0, в центре комнаты — метры;
* линия, где почти везде «стена» — перегородка;
* пробиваем **на трёх высотах** и оставляем только то, что есть на всех — иначе
  ловятся рёбра брёвен (у бревенчатой стены 3 «стены» подряд);
* отрезки, доходящие до края области сканирования, достраиваем до стен (стена на всю длину);
* X-перегородки подрезаем «между» Y-стенами (от граней, не до центров) — иначе union
  даёт незамкнутую топологию.

Диагностика: `structura_roomprobe.py` (карта свободного расстояния),
`structura_wallmap.py`, `structura_inspect_model.py`.

### 7.4 BSP обязан быть ОДНИМ замкнутым телом

Движок (этот билд) роняет сборку (`Build failed`) или отвергает BSP, если она не
замкнута. Проверка — та же, что в EBT (`bmesh_validation`), плюс вердикт движка в логе:
`BSP geometry is not closed` -> `No suitable BSP geometry found! Skipping BSP & portal creation`.

**Что рвёт топологию (проверено по одному вырезу):**

| вырез | non-manifold |
|---|---|
| наружные проёмы (`PRT_01..08`) | 0 рёбер, 0 вершин ✓ |
| внутренние двери (`PRT_09`, `PRT_11`) | 31 и 57 рёбер ✗ |

Причина: вырез двери пересекает стык перегородки с полом (там геометрия раздута на
`OVERLAP`). Лечится не зазором, а отказом от этих вырезов.

**Решение для Modul_2:** режем только наружные проёмы, внутренние двери не вырезаем,
а их порталы не создаём (`DO_INTERIOR_DOORS = False` в `structura_interior.py`).
Иначе движок режет объём и по плоскостям этих порталов — в виде сверху появляются
«лишние блоки» (у нас было два).

### 7.5 Сварка после булевых операций

`weld_and_tri()`: `remove_doubles(0.02)` + `dissolve_degenerate(0.02)` — убирает
«заусенцы» (мелкие/тонкие грани) от булевых объединений. Порог 0.02 м подобран
экспериментально (5-миллиметровые заусенцы на стыке плит).

### 7.6 Галочка `Generate BSP` — в UI, а не в мете

Ключи `GenerateBSP` / `ForceCreatePortals` в `.xob.meta` движок **не читает**:
он ругается `Unknown keyword/data` и перезаписывает мету, выбрасывая их.
Состояние галочки в `Import Settings` метами Modul_1 и Modul_2 по этим ключам
**не отличается**, а галочка разная.

Практический вывод: `Generate BSP` ставится руками в Workbench
(`Import Settings` -> `Common`), `Force Create Portals` — **снята**.
`structura_bsp_meta.py` оставлен (пишет `GenerateBSP 1` / `ForceCreatePortals 0`),
но полагаться на него нельзя.

### 7.7 Мост RWTK (реимпорт запросом)

`structura_bridge.py post` кладёт запрос в
`…\profile\RWTKBridge\inbox\<id>.request.rwtk` (+ `.ready`) и список целей в
`reimport.txt`; обрабатывается плагином Workbench
`RWTK: Process Bridge Queue`. `structura_bridge.py read` показывает результат моста
и свежие ошибки движка из лога.

**Но** при экспорте EBT сам отдаёт XOB в Workbench, и Workbench подхватывает
изменения файлов автоматически — ручной реимпорт для нашего конвейера не нужен.

### 7.8 Чтение логов движка

```
…\My Games\ArmaReforgerWorkbench\logs\<сессия>\console.log
```
Брать каталог по свежести `console.log` (не по времени каталога — свои CLI-запуски
создают пустые каталоги). Искать: `Build failed` / `Build successful`,
`AreaPortal`, `BSP geometry is not closed`, `No suitable BSP geometry found`.

### 7.9 Мелочи

* `BOXVOL_01`, если уже есть в модели, **не пересоздаётся** (могут быть настроенные
  плоскости обрезки).
* Потолок берётся по `Celling`, а если его нет — по низу `Roof` (у Modul_2 `Celling`
  отсутствует).
* `PRT_195x72.emat` / `dummyvolume_...emat` при отсутствии **создаются** вместе с
  `.emat.meta` (свежий GUID). Игровые материалы через мост EBT не резолвятся.
* В мете Modul_2 висит битая ссылка на `DefaultGeneratedMaterial.emat` (файла нет) —
  единственная ошибка в логе, на работу не влияет.


---

## 8. Итоговое решение: BSP границей занятого объёма (по неравномерной сетке)

Отработано на Modul_3. Итог: BSP валидна, порталы привязались, звук отсекается
снаружи и между комнатами. Это **рабочий способ**, в отличие от булевых коробок
(непредсказуемо) и вокселизации (слишком сложная сетка -> движок крошит порталы).

### 8.1 Алгоритм (без Boolean и без вокселя)

`structura_bsp_simple.py`:

1. Собираются сортированные массивы координат `X/Y/Z` из **конструктивных** точек:
   обе стороны стен, границы пола/потолка, все косяки/подоконники/перемычки проёмов.
2. Сетка разбивает пространство на прямоугольные ячейки.
3. Занятость ячейки (по центру): `в оболочке И НЕ в воздухе И НЕ в проёме`.
4. Грань создаётся **только** там, где занятая ячейка граничит с пустой.
5. **Единый индекс вершины на каждый узел `(ix,iy,iz)`** -> нет T-стыков и внутренних граней.
6. Ориентация наружу — `recalc_face_normals`.

Откосы проёма возникают сами на границе «материал -> воздух проёма». Результат —
простая (сотни–тысячи вершин), замкнутая, manifold оболочка.

Опасный случай — два объёма, касающиеся **только ребром/вершиной** (4 грани на ребре):
надо либо соединять с ненулевым сечением, либо оставлять зазор. Сваркой не лечится.

### 8.2 Портал чуть БОЛЬШЕ проёма

Проём режем как `портал − EPS` (портал на ~5 см больше отверстия), портал кладём
в середину толщины стены, не совпадая с внутренней/наружной поверхностью.
Портал — отдельный нетриангулированный квад (`PRT_*`, `MatLightPortal`),
нормаль внутрь для наружных. Он **не** сшивается с BSP.

### 8.3 Volume Cell Size — критично для привязки порталов

`doesn't have vertices assigned` / `orphaned fragments` появляются, если occupancy-сетка
не разрешает тонкую стену. В `Import Settings` (Workbench):

```
Volume Cell Size   1.000  ->  0.250   (<= толщины стены)
Volume Max Cells   128    ->  512
Generate BSP  ✓
```

Это, по сути, последний шаг: после него порталы привязываются. Галочка `Generate BSP`
ставится **в UI** (ключи `GenerateBSP` в `.xob.meta` движок не читает — см. 7.6).

### 8.4 Снэп координат

Близкие координаты (окна на чуть разной высоте) дают тонкие полоски и вырожденные грани.
Координаты сетки округляются до 2 см (`snap`), что убирает `тонких/мелких граней, коротких рёбер`.

### 8.5 Переключение здания

`structura_target.py`: одна строка `MODULE`. Весь конвейер headless:
`structura_headless.py -- export`, BSP-сборщик выбирается `BSP_MODE=simple` (по умолчанию).
Workbench сам подхватывает изменения FBX; остаётся только поставить `Volume Cell Size` + `Generate BSP` в UI.
