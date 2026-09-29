# Гайд: создание прицела (оптики) и похожих аттачей — Arma Reforger

Полное практическое руководство: от меша и текстур до калибровки, действий, арсенала и типовых ошибок.
Составлено по официальной вики BI (`Arma_Reforger:Weapon_Optic_Creation`, `Weapon_Creation`, `Weapon_Slots_And_Bones`, `Textures`, `FBX_Import`, `Diag_Menu`, `Collision_Layer`, `Directory_Structure`, `Mod_Localisation`, `Startup_Parameters`), официальным Samples (`SampleMod_NewWeapon`, `SampleMod_ModdedWeapon`) и собственному опыту правок (кейс HK G36 Carry Handle Optic).

> Версия движка на момент составления: `1.0.13` (Workbench), `SCR_2DPIPSightsComponent`.

---

## Содержание
1. [Структура проекта](#1-структура-проекта)
2. [Меш и пивоты](#2-меш-и-пивоты)
3. [Коллайдеры](#3-коллайдеры)
4. [Текстуры](#4-текстуры)
5. [Материалы (в т.ч. HDR — где живёт сетка в PIP)](#5-материалы)
6. [Префаб аттача](#6-префаб-аттача)
7. [Компонент прицела: все поля](#7-компонент-прицела-scr_2dpipsightscomponent)
8. [Два режима прицеливания (оптика + коллиматор)](#8-два-режима-прицеливания)
9. [Калибровка](#9-калибровка)
10. [Сторона оружия](#10-сторона-оружия-префаб-оружия)
11. [Действия/интеракции](#11-действия-и-интеракции)
12. [Арсенал](#12-арсенал-entity-catalog)
13. [Правила ID компонентов](#13-правило-id-компонентов-критично)
14. [Чек-листы](#14-чек-листы)
15. [Troubleshooting](#15-troubleshooting-симптом--причина--решение)
16. [Справочник GUID/путей](#16-справочник-guidпутей)

---

## 1. Структура проекта

Рекомендуемая раскладка (не обязательна движком, но нужна автоплагинам Workbench и удобству):

```
Prefabs/Weapons/Attachments/Optics/<MyOptic>/
    MyOptic.et              # стаб: наследует <MyOptic>_base.et
    MyOptic_base.et         # сам префаб
    MyOptic_base.et.meta    # ОБЯЗАТЕЛЬНО (GUID префаба!)
Assets/Weapons/Attachments/Optics/<MyOptic>/
    <MyOptic>.xob           # меш (+ .xob.meta)
    Data/*.emat, *.edds
UI/Textures/Sights/<MyOptic>/
    <MyOptic>_reticle_UI.edds
Language/<...>              # строки локализации
```

Правила:
- **у каждого префаба/ресурса обязательна `.meta`** — без неё ресурс не регистрируется (`RESOURCES (W): resource not registered: ... Setting null GUID`) и ссылки на него «висят».
- GUID в `.meta` уникален в рамках всей загрузки (ваш аддон + ваниль + другие аддоны). Проверяйте поиском по аддонам.
- Загрузка аддонов: последний смонтированный аддон «перекрывает» ресурс с тем же **путём+GUID** (так можно подменять ванильные базы).

---

## 2. Меш и пивоты

### 2.1 Общее
- Ориентация как у оружия: «лицом» вперёд по оси, как в Samples.
- Задняя часть окуляра очень близко к камере игрока в ADS — не жалейте полигонов на цилиндрах перед глазом (вики: 32+ сегментов), на дальних LOD можно снижать.
- Пивоты — **Empty-объекты**, ориентация (rotation) пивота используется движком, поэтому её тоже надо выставлять.

### 2.2 Обязательные точки

| Пивот | Где | Для чего |
|---|---|---|
| `snap_weapon` | точка зацепа аттача с оружием (контактная поверхность) | без него используется origin модели |
| `eye` | камера основного прицела, в нескольких см за окуляром | `SightsPosition`, `SightsComponent` |
| `optic_rear` | центр окуляра | `SightsPointRear` |
| `optic_front` | передняя линза (объектив) | `SightsPointFront` |
| `eye_ironsight` | по линии резервных/иронсайтов | второй режим прицеливания |
| `collimator_TL` / `collimator_BR` | верх-лево / низ-право окна коллиматора | геометрия коллиматора |
| `ironsight_front` / `ironsight_rear` | линия иронсайтов | `SCR_CollimatorSightsComponent` front/rear |

**`SightsPosition`, `SightsPointRear`, `SightsPointFront` держите на одной оси** (X и Y совпадают) — иначе будет перекос.

### 2.3 PIP-меш
- Отдельная **плоская** деталь на окуляре — на неё рендерится картинка PIP; должна быть достаточно плотная по полигонам.
- **UV этой детали должны занимать целый UV-остров**; если картинка повёрнута на 45° — проверьте поворот UV.
- Материал этой детали — «PIP-материал» (в модели Sample слот называется `Optic_pip`).
- Дополнительно: 2-я, выпуклая деталь впереди PIP (и опционально сзади) — «стекло» (`Optic_lensglass`), только для вида (отражения/тинт).

---

## 3. Коллайдеры

- Аттач обязан иметь коллайдер(ы) с **двумя** Layer Preset: **`Weapon`** и **`FireGeo`**.
  - `Weapon` = CharNoCollide → физика/взаимодействие;
  - `FireGeo` = FireGeometry → пули и **детект инвентарных действий**.
  - **Если в игре нет действий по предмету — в первую очередь проверяйте Layer Preset.**
- Префиксы коллайдеров: `UCX_`/`UBX_` (выпуклый), `UTM_` (тримеш), `USP_`/`UCS_`/`UCL_`.
- Материалы коллайдеров: `weapon_metal.gamemat`, `weapon_plastic.gamemat`, `weapon_wood.gamemat` — иначе аттач «останавливает» пули.
- Простой вариант: один выпуклый коллайдер на оба пресета; сложный: UCX(Weapon) + UTM(FireGeo).
- В `RigidBody` компоненте префаба **включить `Model Geometry`** — иначе сломаны интеракции/подбор.

Полезно (LayerPresets): `Weapon` = CharNoCollide; `FireGeo` = FireGeometry; `ItemFireView` = CharNoCollide+FireGeometry+ViewGeometry.

---

## 4. Текстуры

### 4.1 Сетка (reticle)
- Рекомендуемый размер 1024×1024 (меньше — для простых сеток); сетка занимает **большую часть** полотна.
- Цвет сетки не важен — движок перекрашивает; рисуйте белым.
- Прозрачный фон = **чёрный в альфе**. RGB в прозрачных зонах сохраняйте (некоторые редакторы портят).
- **Суффикс `_UI`** для текстур сеток (+ при импорте EDDS: `Conversion Quality = 100`, `Generate Mips` **снять**).
- Альтернатива — заменить в `.meta` конфигурации на `TextureReticle.conf` (по платформам) и переимпортировать; тогда можно суффикс `_Reticle`:

```
Configurations {
 TGAResourceClass PC : "{33F97FFE35E57E1D}Configs/System/ResourceTypes/PC/TextureReticle.conf" { }
 TGAResourceClass XBOX_ONE : "{0B42FA7CFD77120F}Configs/System/ResourceTypes/XBOX_ONE/TextureReticle.conf" { }
 TGAResourceClass PS4 : "{C1FA7DC8973FA4A1}Configs/System/ResourceTypes/PS4/TextureReticle.conf" { }
 TGAResourceClass HEADLESS : "{9664EF94CE7C4525}Configs/System/ResourceTypes/HEADLESS/TextureReticle.conf" { }
 TGAResourceClass XBOX_SERIES : "{A4AA0C6FDF186747}Configs/System/ResourceTypes/XBOX_SERIES/TextureReticle.conf" { }
}
```
> Для PNG использовать `PNGResourceClass` вместо `TGAResourceClass`.

### 4.2 Остальные карты
Суффиксы решают почти всё: `_BCR` (albedo/roughness), `_NMO` (normal/metal/AO), `_MCR` — особый (albedo/roughness, импортируется иначе), `_MASK` (1/2 канал — цветовое пространство вручную). Правильный суффикс = правильный импорт-профиль по умолчанию.

---

## 5. Материалы

### 5.1 PIP-материал (слот `Optic_pip` в модели)
Присваивается **слоту материала меша**. Можно взять готовый и подправить:
- `{41E4B66721D5F07B}Assets/Weapons/Attachments/Optics/PSO1/Data/Optic_PSO1_PIPMaterial.emat`
- `{F3CC2BBE8FE67602}Assets/Weapons/Attachments/Optics/4x20/Data/Optic_4x20_PIPmaterial.emat`

### 5.2 Стекло (слот `Optic_lensglass`)
- `{39C2A3A521FE9A1B}Assets/Weapons/Attachments/Optics/ARTII/Data/Optic_ARTII_Lensglass.emat`
- `{3C29D4ADAC94D19B}Assets/Weapons/Attachments/Optics/4x20/Data/Optic_4x20_Lensglass.emat`

### 5.3 HDR-материал скопа — **именно он рисует сетку в PIP**
Это главный «подводный камень». Вики (`Weapon_Optic_Creation` → Setting PIP scope → Reticle):

> *«First step in configuring PIP reticle is assigning previously created reticle material … to **Scope HDR Matrial** property in **PiPSights** section.»*
> *«Matrial is known typo of material»* (опечатка в движке)

Как делать:
1. **Скопировать** один из существующих HDR-материалов (класс **HDREffect**) в свой аддон, например `Optic_4x20_HDR.emat`.
2. Открыть его → вкладка **Details** → свойство **`Reticle Map`** → присвоить свою текстуру сетки.
3. Сохранить (Ctrl+S).
4. В префабе прицела в секции **PiPSights** присвоить этот материал в **`m_rScopeHDRMatrial`**.
5. Дополнительно: **отключить `reticle movement`** в материале (иначе сетка «плывёт» при ADS) и подогнать **виньетку**, чтобы PIP выглядел как 2D-режим.

Готовые HDR-материалы (каждый несёт свою сетку) — можно использовать как есть:

| Материал | GUID |
|---|---|
| `Optic_4x20_HDR.emat` | `09B57B6EA6B5EE41` |
| `Optic_PSO1_HDR.emat` | `958809B0DE47E9BF` |
| `Optic_ARTII_HDR.emat` | `63FF28F3F6BB1727` |
| `Optic_1P29_HDR.emat` | `3BD4127D635A335E` |
| `Optic_PGO7V_HDR.emat` | `E8738368ECB4F8FE` |
| `Optic_UK59_4x8_HDR.emat` | `F6F990CCEDF61E3A` |
| `SightsPIPMaterial.emat` (общий) | `1C8A9AC4A0AE4921` |

> ⚠ Если `m_rScopeHDRMatrial` **не задан**, движок берёт общий материал — в прицеле будет **чужая сетка** (в нашем кейсе отображалась сетка ПСО). Если задан материал **без `Reticle Map`** — PIP отрисует картинку, но **без сетки**.

---

## 6. Префаб аттача

### 6.1 База и стаб
- Стаб `<Name>.et`: `GameEntity : "{GUID}<Name>_base.et" { ID "..." }` — чтобы удобно было плодить варианты.
- База: наследуется от **`WeaponOptic_Base.et`** (оптика) или `WeaponCollimator_Base.et` (коллиматор), либо копируется существующая оптика (PSO-1, ART II).

### 6.2 Компоненты
```
MeshObject  { Object "{GUID}Assets/.../<MyOptic>.xob" }
RigidBody   { LayerPreset "ItemFireView"   ModelGeometry 1 }
```
- `ModelGeometry 1` — обязательна для корректных интеракций/подбора.
- `LayerPreset` для предметного RigidBody — `ItemFireView`.

### 6.3 InventoryItemComponent (инвентарь/физика/совместимость)
- `ItemDisplayName` → **Name и Description обязаны быть локализованы** (иначе криво отображается в Attach-действии при осмотре).
- `ItemPhysAttributes`:
  - `Weight` — реальная масса;
  - `SizeSetupStrategy = **Manual**` + `ItemDimensions` и `ItemVolume` (режим Volume для аттачей плох — предмет может «не влезать» никуда);
  - `RestingUP = **Right**`.
- `m_Size` → `SLOT_1x1`.
- **`ItemAnimationAttributes` оставлять пустыми** (в отличие от оружия).
- `PreviewRenderAttributes` — вид в лоадауте (`CameraDistanceToItem`, `CameraOrbitAngles`, `FOV`).

### 6.4 CharacterModifierAttributes
Поведение персонажа с надетым аттачем. `WeaponOptic_Base` уже даёт типовые значения:
- `ADSSpeedLimit` ~ `1.5` м/с (скорость при ADS), `SpeedLimit`, `SpeedLimitHighready`.
- Хотите «шустрее» — увеличить; для тяжёлой/большой оптики — уменьшить.

### 6.5 Тип крепления (совместимость)
В `CustomAttributes → WeaponAttachmentAttributes → AttachmentType`:
- Иерархия RIS (слот «короче» принимает только такой же или короче):
  - `AttachmentOpticsRIS1913` — ≥250 мм (оптика + ПНВ и т.п.);
  - `AttachmentOpticsRIS1913Medium` — до 120 мм (крупные скопы, коллиматор+магнифаер);
  - `AttachmentOpticsRIS1913Short` — до 120 мм;
  - `AttachmentOpticsRIS1913VeryShort` — до 80 мм (мелкие коллиматоры, RIS-иронсайты).
- Для нестандартного оружия тип создаётся так же, как «Magazine Well» (свой класс → используется в слоте оружия).
- Примеры кастомных типов из проекта: `AttachmentOpticsG36`, `AttachmentOpticsDovetailAK`.
- **Совместимость идёт по имени класса**, GUID типа у каждого префаба свой — это нормально (у слота оружия и у аттача GUID'ы могут различаться).

---

## 7. Компонент прицела `SCR_2DPIPSightsComponent`

Компонент включает оба режима: **2D** и **PIP** (переключается настройкой игры / `Toggle 2D optics`). Структура полей — три группы: `BaseSights`, `Sights`/`2DSights` (общие для 2D и PIP), `PIPSights` (только PIP).

### 7.1 BaseSights (общее)
| Поле | Смысл |
|---|---|
| `SightsPosition` (PointInfo) | камера ADS (за окуляром) → `PivotID "eye"` |
| `SightsPointRear` | точка у окуляра → `optic_rear` |
| `SightsPointFront` | точка на объективе → `optic_front` |
| `SightsRanges` | список дальностей прицела (метры) + `X` = значение анимации 0…1 |
| `SightsFOVInfo` | класс `SCR_SightsZoomFOVInfo` (фикс-кратность) или `SCR_VariableSightsFOVInfo` (переменная): `m_fBaseZoom` = минимальная кратность, `m_fZoomMax` = максимальная |
| `SightsPriority` | «включать этот прицел автоматически вместо иронсайтов» |
| `SoundInt` | индекс звука прицела |

### 7.2 2D (секции `Sights` / `2DSights`)
| Поле | Смысл |
|---|---|
| `m_sReticleTexture` / `m_sReticleGlowTexture` | текстуры сетки **для 2D-режима** |
| `m_fObjectiveFov` | FOV объектива, **градусы** (искать реальное значение) |
| `m_fMagnification` | кратность; **должна совпадать с `Base Zoom`** |
| `m_fObjectiveScale` | чтобы оптика не «вылезала» за 16:9 (реком. 1…0.5) |
| `m_fVignetteScale` | виньетка |
| `m_fReticleBaseZoom` | фокальная плоскость: `0` = передняя (сетка масштабируется), `= Magnification` = задняя (сетка неизменна) |
| `m_fReticleAngularSize` | угловой размер опорных меток сетки, **градусы** |
| `m_fReticlePortion` | какая часть ширины текстуры соответствует этому угловому размеру |
| `m_eZeroingType` | `EPZ_NONE` / `EPZ_RETICLE_OFFSET` (пристрелка смещением сетки) |
| `m_fReticleOffsetX` / `m_fReticleOffsetY` | подстройка положения сетки |
| `m_vCameraOffset` / `m_vCameraAngles` | сдвиг/поворот камеры скопа |
| `m_bHasIllumination`, `m_ReticleColor`, `m_ReticleOutlineColor`, `m_cReticleTextureIllumination`, `m_fReticleTextureGlowAlpha`, `m_sFilterTexture` | подсветка/цвет/фильтр сетки |
| `m_fADSActivationPercentage` / `m_fADSDeactivationPercentage` | пороги входа/выхода в ADS |
| `m_fMisalignment*`, `m_fRotation*`, `m_fMovement*`, `m_fRoll*`, `m_fMotionBlur*`, `m_fVignetteMoveSpeed`, `m_fAnimation*` | «живость»/инерция скопа, блюр, анимация входа |
| `m_iOpticDOFDistanceScale`, `m_bForceSimpleDOF` | depth-of-field |
| `m_bShouldHideParentObject` / `m_bShouldHideParentCharacter` | скрывать ли родителя |

### 7.3 PiPSights (только PIP)
| Поле | Смысл |
|---|---|
| **`m_rScopeHDRMatrial`** | **HDR-материал скопа (класс HDREffect) — в нём `Reticle Map` = сетка PIP** |
| `m_sPIPLayoutResource` | layout PIP-режима (см. ниже) |
| `m_sRTTextureWidgetName` / `m_sRTargetWidgetName` | имена виджетов layout'а под render target |
| `m_iCameraIndex` | индекс камеры |
| `m_fNearPlane` / `m_fFarPlane` / `m_fResolutionScale` | ближняя/дальняя плоскость и масштаб рендера PIP |
| `m_fScopeRadius` | **радиус PIP-картинки на экране — главный параметр подгонки под 2D** |
| `m_fCenterDistance` | расстояние от камеры до центра PIP-изображения |
| `m_fDistanceMoveNear` / `m_fDistanceMoveFar` | интерполяция PIP при движении (eye-box) |
| `m_fBasicParallax` / `m_fMaxParallax` | пределы параллакса |
| `m_fCenterOffsetX` / `m_fCenterOffsetY` | смещение центра PIP-картинки |
| `m_fReticlePIPScale` | масштаб сетки именно в PIP |
| `m_fObjectivePIPEdgeMin` / `m_fObjectivePIPEdgeMax` | мягкость края PIP-круга |
| `m_fVignetteParallaxScale` | влияние параллакса на виньетку |
| `m_fADSActivationPercentagePIP` / `m_fADSDeactivationPercentagePIP` | пороги ADS для PIP |
| `m_vMainCameraOffsetUnfocused` | смещение основной камеры вне ADS |
| `m_sUnderwaterPPMaterial` / `m_sRainPPMaterial` | пост-эффекты под водой/в дождь |

Доступные layout'ы (в игре всего два):

| Layout | GUID | Замечание |
|---|---|---|
| `UI/layouts/Sights/PictureInPictureSightsLayout.layout` | `EF091399D840192D` | **PIP работает** (проверено) |
| `UI/layouts/Sights/Optic_Default.layout` | `4CE66FA8219D33D7` | в нашем кейсе **ломал PIP** |

---

## 8. Два режима прицеливания

Классический кейс: «ручка со встроенной оптикой и коллиматором» (HK G36, VHS-2) — ровно то, что делает Sample Optic («primary optical sight … and backup ironsights on top»).

Реализация — **два прицельных компонента в одном префабе**:
1. `SCR_2DPIPSightsComponent` — оптика (PIP);
2. `SCR_CollimatorSightsComponent` (+ вложенный `SCR_CollimatorControllerComponent`) — коллиматор/иронсайты.

Ключевые поля коллиматора:
| Поле | Смысл |
|---|---|
| `SightsPosition` / `SightsPointFront` / `SightsPointRear` | точки линии (`eye_ironsight`, `ironsight_front/rear`) |
| `CollimatorTopLeft` / `CollimatorBottomRight` / `CollimatorCenter` | окно коллиматора (`collimator_TL/BR`) |
| `SightsPriority` | у оптика выше (напр. 1), у коллиматора ниже (0) |
| `ReticleDefaultAngularSize` / `ReticleDefaultTexturePortion` | размер сетки-точки |
| `ReticleColors { BaseCollimatorReticleColor { ReticleColor … GlowColor … } }` | цвет точки |
| `ReticleInfos { BaseCollimatorReticleInfo { ReticleIndex N } }` | выбор формы (атлас) |
| `m_fDaylightBrightness` | яркость днём |

**Переключение режимов даёт HUD-действие**, условие `SCR_WeaponChangeSwitchOpticsCondition`: *«Return true if currently held weapon has more than 1 scopes»* — то есть работает, когда прицелов больше одного (компоненты оптики/коллиматора, либо прицелы оружия+аттача).

> Если в меше уже запечён эмиссивный элемент (например красная точка коллиматора), 2D-сетка коллиматора даст **вторую точку** — тогда сетку коллиматора лучше не рисовать.

---

## 9. Калибровка

### 9.1 Диагностический инструмент: Diag Menu
- Открыть: **`Win + Alt`** в любом 3D-вьюпорте Workbench (вариант `Ctrl + Win` конфликтует с Win11).
- Навигация: **→** — войти в подменю, **Backspace** — выйти, **← / →** — менять значение, **Shift + ↑ / ↓** — быстрее, **Home** — в корень, **Insert** — сброс текущего меню, **Delete** — сброс всего, **F1 / F2** — сохранить/загрузить настройки профиля.
- Стартовый параметр `-diagMenu "file.txt"` — хранить настройки диагностики в файле (Workbench).
- Полезные переключатели — `GameCode → Weapons`:
  - **`Toggle 2D optics`** — переключение 2D ↔ PIP;
  - **`Show optics diag`** — проверка сетки/скопа (рисует крест/насечки/круг FOV в выбранных единицах: MILS_WP/OBJECTIVE);
  - **`Show PIP settings diag`** — окно `2DPIPSights` с живыми параметрами PIP;
  - **`Show sights points`** — точки прицела;
  - **`Disable aim modifiers` / `Disable character aim modifiers` / `Disable weapon offset`** — убрать качание.
- HUD-only: окно видно в ADS.

### 9.2 Порядок калибровки
1. **Точки**: `SightsPosition`/`Rear`/`Front` на одной оси; при необходимости `Camera Offset`/`Camera Angles`.
2. **2D-скоп**: `Objective FOV` (реальный) → `Magnification = Base Zoom` → `Objective Scale` (1…0.5) → `Vignette Scale`. Значения удобно подбирать в Diag Menu и потом переносить в префаб.
3. **Сетка**: `Reticle Base Zoom` (передняя/задняя фокальная плоскость) + `Reticle Angular Size` + `Reticle Portion`.
   - `Angular Size` — угловой размер опорных меток в градусах. Перевод: 1 варшавская мила = 0.06°.
     Пример ПСО-1: 20 мил = `20 × 0.06 = 1.2°`.
   - `Portion` = (расстояние между метками в пикселях) / (ширина текстуры).
     Пример ПСО-1: `304 / 1024 = 0.29687`.
4. **PIP**: сначала закончить 2D (иначе придётся переделывать) → подбирать `Sights Position` (расстояние от задней точки так, чтобы apparent FOV совпал с 2D) → **`m_fScopeRadius`** до совпадения картинки с 2D → `m_fReticlePIPScale`, `m_fCenterOffsetX/Y`, `m_fCenterDistance`. Материал скопа: reticle movement **off**, виньетка как в 2D.
   > Дебажный круг в PIP неточный; точный угловой размер — в 2D-режиме.
5. **Zeroing** (сторона оружия): `Sights Ranges` → `Zeroing Generator` (`BaseZeroingGenerator`) → ПКМ по компоненту → **`Process zeroing data`** → `Apply to prefab`.

---

## 10. Сторона оружия (префаб оружия)

### 10.1 Слот
```
AttachmentSlotComponent "{...}" {
    AttachmentSlot InventoryStorageSlot optics {
        PivotID "slot_optics"          // пивот меша оружия
        ChildPivotID "snap_weapon"
        Offset 0 0 0
        MergePhysics 1
        Prefab ""                       // пусто = ничего не навешено; GUID = навешено по умолчанию
        ShowInInspection 1
    }
    AttachmentType AttachmentOptics<...> "{...}" { }
}
```
- `slot_optics` — конвенция для крепления оптики (по контактной поверхности).
- `Prefab` в слоте — «заводской» дефолтный аттач (у G36 так навешена карабинная оптика).
- Тип слота определяет, что влезет (иерархия RIS).

### 10.2 Прицельные оружия
`WeaponComponent → SightsComponent`:
- своя мушка/иронсайты оружия;
- `Enabled 0` — полностью выключить;
- либо оставить включёнными и поставить **`SightsSwitchSkip 1`** (как в Sample Weapon) — тогда иронсайты исключаются из цикла переключения, а «>1 scopes» набирается прицелами оптики.

### 10.3 Контекст действия «optic»
В `ActionsManagerComponent` оружия добавить `UserActionContext`:
- `ContextName "optic"`, `Position { PivotID "slot_optics" }`, `Radius ~0.1` (иначе действие «дерётся» с подбором оружия и срабатывает слишком рано).

### 10.4 Zeroing
`Sights Ranges` (X = анимация 0…1, Y = метры) + генератор (`BaseZeroingGenerator`) → `Process zeroing data`. Пристрелка привязана к баллистике патрона из магазина. Для проверки — команда `Toggle sight point diag`.

---

## 11. Действия и интеракции

Для аттача (оптики) действия навешиваются на сам аттач:

```
ActionsManagerComponent "{...}" {
    ActionContexts {
        UserActionContext "{...}" { Position PointInfo { Offset 0 0.015 0.006 } Radius 0.1 }
        UserActionContext "{...}" { ContextName "detach"  Position PointInfo { Offset 0 0.014 0 } Radius 0.1 }
    }
    additionalActions {
        SCR_AttachementAction "{...}" {                     // опечатка класса в движке
            ParentContextList { "detach" }
            UIInfo UIInfo { Name "#AR-UserAction_Detach" }
            Duration 2
        }
        SCR_AttachItemFromInventoryAction "{...}" {
            ParentContextList { "optic" }
            Duration 2
            "Inventory action" 1
        }
    }
}
```
- `SCR_AttachItemFromInventoryAction` — «присоединить из инвентаря» (контекст `optic`);
- `SCR_AttachementAction` — «отсоединить» (контекст `detach`).
- Если аттач всегда навешен через `Prefab` слота — действия нужны только для снятия/надевания вручную.

---

## 12. Арсенал (Entity Catalog)

Чтобы оптика была доступна в арсенале/конфликте:
- в Entity Catalog нужной фракции добавить prefab в **Weapon Attachments Entities**;
- `Item Type = **WEAPON_ATTACHMENT**`, `Item Mode = **ATTACHMENT**`;
- `Supply Cost` — по ванильным значениям;
- для стоек (racks) добавить запись в `Arsenal Display Data`;
- может потребоваться `Reload Game Scripts` / перезапуск Workbench.

---

## 13. Правило ID компонентов (критично!)

В Enfusion **GUID после имени компонента — это ID экземпляра внутри префаба**:
- компонент с **новым ID = ВТОРОЙ (лишний) экземпляр**;
- чтобы **переопределить** унаследованный компонент, надо указывать **его же ID**.

Примеры правильного использования:
- `BaseSightsComponent "{5D0CC83435B55855}"` наследуется от `WeaponSight_Base` → чтобы заменить его на `SCR_2DPIPSightsComponent`, берём **тот же** ID `{5D0CC83435B55855}`;
- `ActionsManagerComponent` уже приходит по наследованию (от `Weapon_Base`/`Attachment_Base`) → добавлять с новым ID **нельзя** (получится дубль); если нужны свои действия — брать ID унаследованного (например `{5284E0EFF569AD07}` как в ванильных оптиках).

**Вывод: перед добавлением любого компонента смотрите в Workbench, какие уже есть (в т.ч. унаследованные), и переопределяйте их ID, а не плодите новые.**

---

## 14. Чек-листы

### Создание оптики
- [ ] `.et` + **`.meta`** (уникальный GUID) у всех префабов/ресурсов
- [ ] меш: `snap_weapon`, `eye`, `optic_rear`, `optic_front` (+ `eye_ironsight`, `collimator_TL/BR`, `ironsight_front/rear` при двух режимах)
- [ ] PIP-меш (UV = целый остров) + материал `Optic_pip`; стекло `Optic_lensglass`
- [ ] коллайдеры `Weapon` + `FireGeo`, материалы `weapon_*.gamemat`
- [ ] текстура сетки `_UI` (Quality 100 / Mips off) или `TextureReticle.conf`
- [ ] **HDR-материал с `Reticle Map`** → `m_rScopeHDRMatrial`
- [ ] `RigidBody → Model Geometry`
- [ ] `InventoryItemComponent`: локализованные Name/Description, Manual+размеры, RestingUP Right, `m_Size`
- [ ] `AttachmentType` (совместимость со слотом)
- [ ] `SCR_2DPIPSightsComponent`: точки, FOV Info, ретикл, PiPSights
- [ ] (опц.) `SCR_CollimatorSightsComponent` — второй режим
- [ ] `ActionsManagerComponent` (attach/detach) — **только если нужен** (не дублировать!)
- [ ] Entity Catalog: `WEAPON_ATTACHMENT` / `ATTACHMENT`

### Проверка в игре
- [ ] оптика встаёт в слот, есть действия attach/detach
- [ ] ADS работает, видно увеличение
- [ ] сетка видна и в 2D, и в PIP (`Toggle 2D optics`)
- [ ] переключаются два режима (если есть коллиматор)
- [ ] нет ошибок в логе: `Wrong GUID for resource`, `resource not registered`, `Unknown class`, `Division by zero`

---

## 15. Troubleshooting (симптом → причина → решение)

| Симптом | Причина | Решение |
|---|---|---|
| `RESOURCES (W): resource not registered … Setting null GUID` | у файла **нет `.meta`** | создать `.meta` с GUID |
| `RESOURCES (E): Wrong GUID for resource "@{…}…" in property "Prefab"` | ссылка на GUID, которого нет (файл удалён/без meta) | восстановить файл с этим GUID либо поправить ссылку |
| `Division by zero` в `SCR_2DOpticsDisplay::SetReticleOffset` | у `SCR_2DPIPSightsComponent` не заданы `m_fReticlePortion`/текстура (деление на 0) | задать `m_fReticlePortion`, `m_fReticleAngularSize`, текстуры |
| В PIP **нет сетки** | `m_rScopeHDRMatrial` — материал **без `Reticle Map`** | использовать/скопировать HDR-материал (HDREffect) и положить сетку в `Reticle Map` |
| В прицеле **чужая сетка** (напр. от ПСО) | `m_rScopeHDRMatrial` не задан → движок взял общий материал | задать свой HDR-материал |
| PIP **ломается** | `m_sPIPLayoutResource = Optic_Default.layout` | поставить `PictureInPictureSightsLayout.layout` |
| В Workbench **два** одинаковых компонента | добавлен компонент с **новым ID**, хотя такой уже наследуется | переопределять **ID унаследованного** |
| Нет действий по предмету | неверный `Layer Preset` коллайдера | коллайдеры `Weapon` + `FireGeo` |
| Предмет нельзя подобрать/нет интеракций | `RigidBody` без `Model Geometry` | включить `Model Geometry` |
| Нет контекста на слоте оружия | нет `UserActionContext` с `ContextName "optic"` | добавить контекст, `Radius ~0.1` |
| Правки в префабе «пропадают» | **Workbench перезаписывает файл при сохранении** (у него своя копия в памяти) | закрыть префаб в Workbench → править файл → reload (не сохранять старую копию) |
| Сетка/картинка «плывёт» при ADS | reticle movement в HDR-материале | скопировать материал и **отключить reticle movement**, подогнать виньетку |
| Оптика не появляется в арсенале | нет записи в Entity Catalog | добавить (`WEAPON_ATTACHMENT` / `ATTACHMENT`) |
| Сетка мелкая/неверного размера | `m_fReticlePortion` не соответствует текстуре, `Magnification ≠ Base Zoom` | пересчитать `Portion` (px/width), выровнять `Magnification = Base Zoom` |

---

## 16. Справочник GUID/путей

**Layout'ы PIP**
- `{EF091399D840192D}UI/layouts/Sights/PictureInPictureSightsLayout.layout`
- `{4CE66FA8219D33D7}UI/layouts/Sights/Optic_Default.layout`

**HDR-материалы (Reticle Map)** — см. §5.3.

**PIP/стекло материалы**
- `{41E4B66721D5F07B}…/Optics/PSO1/Data/Optic_PSO1_PIPMaterial.emat`
- `{F3CC2BBE8FE67602}…/Optics/4x20/Data/Optic_4x20_PIPmaterial.emat`
- `{39C2A3A521FE9A1B}…/Optics/ARTII/Data/Optic_ARTII_Lensglass.emat`
- `{3C29D4ADAC94D19B}…/Optics/4x20/Data/Optic_4x20_Lensglass.emat`

**Базовые ресурсы**
- `WeaponOptic_Base.et` = `{966B4E5523D2F166}Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et`
- `WeaponSight_Base.et` = `{3E15C1C882DBB587}Prefabs/Weapons/Core/WeaponSight_Base.et`
- `Attachment_Base.et` = `{2E0E3D7D1DD0FF8F}Prefabs/Weapons/Core/Attachment_Base.et`
- `WeaponPart_Base.et` = `{0A9CD090EE3440E7}Prefabs/Weapons/Core/WeaponPart_Base.et`
- `Rifle_Base.et` = `{911D6C8DC7BA2D63}Prefabs/Weapons/Core/Rifle_Base.et`

**Полезные стартовые параметры (Workbench)**
- `-diagMenu "file.txt"` — файл настроек Diag Menu
- `-wbModule=WorldEditor -run -load "<file>"` — сразу открыть файл
- `-clearSettings` — сбросить настройки Workbench
- `-validate` — проверить компиляцию скриптов

**Источники**
- Вики: `Arma_Reforger:Weapon_Optic_Creation`, `Weapon_Creation` (+/Asset_Preparation, +/Prefab_Configuration), `Weapon_Slots_And_Bones`, `Textures`, `FBX_Import`, `Diag_Menu`, `Collision_Layer`, `Directory_Structure`, `Mod_Localisation`, `Startup_Parameters`
- Samples: `github.com/BohemiaInteractive/Arma-Reforger-Samples` → `SampleMod_NewWeapon`, `SampleMod_ModdedWeapon`

---

## Приложение: кейс HK G36 Carry Handle Optic (что реально пришлось чинить)

1. **Пропали префабы оптики** (Optic + Picatinny); у оптики **никогда не было `.meta`** → `resource not registered` + `Wrong GUID … in property "Prefab"`. Восстановлено из копий, создана `.meta` с GUID, совпадающим со ссылкой в оружии.
2. **Битый GUID родителя** пикатинни (`WeaponPart_Base.et`) — исправлен на `{0A9CD090EE3440E7}`.
3. **Двухрежимность**: добавлены `SCR_2DPIPSightsComponent` (оптика) и `SCR_CollimatorSightsComponent` (коллиматор) на реальных пивотах меша (`eye`, `optic_front/rear`, `eye_ironsight`, `collimator_TL/BR`, `ironsight_front/rear`).
4. **`Division by zero`** — из-за пустых `m_fReticlePortion`/текстуры.
5. **«Сетка ПСО»** — `m_rScopeHDRMatrial` не задан → движок использовал общий `SightsPIPMaterial`; после задания HDR-материала 4x20 сетка стала из его `Reticle Map`.
6. **PIP ломался** с `Optic_Default.layout` → оставлен `PictureInPictureSightsLayout.layout`.
7. **Дубль `ActionsManagerComponent`** — добавлен с новым ID, хотя такой компонент уже наследуется (см. §13).
8. **Workbench перезаписывал префаб** при сохранении — правки с диска «терялись» (см. §15).
