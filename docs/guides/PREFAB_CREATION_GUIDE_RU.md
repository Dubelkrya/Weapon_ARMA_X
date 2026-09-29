# Полный гайд: создание префабов и ассетов для Arma Reforger

**Принцип документа:** всё делается **через наследование по правилам Bohemia Interactive**. Костыли (дублирование логики, добавление компонентов «с новым ID» вместо переопределения, отключение унаследованного как заглушка, ручные правки бинарников, замена `.et` вместо override) — запрещены: это ломает иерархию, ломает обновления и мод-совместимость.

Составлено по официальной вики (`Arma_Reforger:Prefabs_Basics`, `Prefab_Data`, `Data_Modding_Basics`, `Resource_Usage`, `Create_an_Entity`, `Create_a_Component`, `Create_a_Config_Class`, `File_Types`, `Directory_Structure`, `Mod_Project_Setup`, `Mod_Publishing_Process`, `Weapon_*`, `Weapon_Collimator_Creation`, `Weapon_Components`, `Weapon_Stats-Modifing_Attachments`, `Action_Context_Setup`, `Creating_a_User_Action`, `Entity_Catalog`, `Faction_Creation`, `Textures`, `FBX_Import`, `Collision_Layer`, `Diag_Menu`, `Mod_Localisation`, `Startup_Parameters`, `Enfusion Blender Tools*`, `Resource Manager*` — весь корпус `Category:Arma Reforger/Modding`, 234 страницы) и по практическому опыту правок этого аддона.

---

## 0. Кириллицей о главном (TL;DR)

1. **Ассет = файл + `.meta` (GUID).** Нет `.meta` → ассет не зарегистрирован, ссылки «висят».
2. **Префабы не «заменяют», а override'ят** (тот же GUID) или **наследуют** (новый GUID).
3. **Любой префаб сначала наследуем**, и только переопределяем нужное.
4. **Компонент переопределяется по его ID.** Новый ID = **второй экземпляр** (дубль), а не замена.
5. **Унаследованный компонент удалить нельзя** → выбирай правильную базу или делай duplicate-in-addon (рекомендация BI для коллиматора).
6. **Ничего не «докручиваем» в рантайме скриптами**, если это настраивается в префабе.

---

## 1. Модель данных Enfusion

| Термин | Что это |
|---|---|
| **Сущность (Entity)** | объект в мире; класс вида `GenericEntity`, `GameEntity`, … |
| **Компонент (Component)** | блок поведения/данных на сущности (`MeshObject`, `RigidBody`, `WeaponComponent`, …) |
| **Config object** | под-объект внутри сущности/компонента (например `InventoryStorageSlot`, `PointInfo`, `UIInfo`) |
| **Ресурс (Resource)** | файл, зарегистрированный движком (`.et`, `.xob`, `.edds`, `.emat`, `.conf`, `.layout`, …) |
| **GUID** | 16-ричный ID ресурса, хранится в `.meta`; ссылки в игре идут по `{GUID}путь` |
| **Prefab** | шаблон: `.et` — entity prefab, `.ct` — component prefab, `.conf` — config object prefab |
| **Prefab instance** | сущности в сцене, созданные из префаба (точное зеркало префаба) |
| **Prefab Edit Mode** | режим редактора для правки `.et` (`Ctrl+S` — сохранить префаб) |

### 1.1 Типы файлов (кто сохраняет)

`.et` (entity prefab) · `.ct` (component template) · `.conf` (config) · `.ent` (world scene) · `.layer` (world layer) · `.xob`/`.txo` (модель) · `.edds`/`.dds` (текстура) · `.emat` (материал) · `.gamemat` (игровой материал) · `.layout`/`.imageset`/`.styles` (UI) · `.anm`/`.agf`/`.agr`/`.asi`/`.ast`/`.aw`/`.pap`/`.siga` (анимации) · `.acp`/`.sig`/`.wav`/`.snd`/`.afm` (звук) · `.ptc` (партиклы) · `.st` (локализация) · `.rdb` (база ресурсов) · `.pak` (архив аддона) · `.gproj` (проект).

### 1.2 Что можно делать с чужим ассетом (таблица моддифицируемости)

| Расширение | Заменить | Изменить (override) | Наследовать |
|---|---|---|---|
| `.et` (prefab) | ✗ (всегда override) | ✔ | ✔ |
| `.conf` (config) | ✗ | ✔ | ✔ |
| `.emat` (материал) | ✗ | ✔ | ✔ |
| `.layout`, `.ptc` | ✗ (ptc — только через Particle Editor) | ✔ | ✔ |
| `.xob`, `.edds`, `.anm`, `.wav` и пр. | ✔ (совпадение **GUID**) | — | ✗ |
| `.c` (скрипты) | ✔ (тот же путь+имя) | `modded` / `override` / `super` | — |
| `.bt` (behavior tree) | — | — | ✔ |

---

## 2. Четыре операции над ресурсами (Resource Browser → ПКМ / Addons)

| Операция | Что делает | GUID | Когда применять |
|---|---|---|---|
| **Override in "…"** | создаёт копию в рабочем аддоне с **тем же GUID**, содержащую только ваши изменения | тот же | изменить ванильный `.et/.conf/.emat/.layout` (нельзя удалять элементы) |
| **Duplicate in "…"** | полная копия, **новый GUID**, оригинал не трогает | новый | нужен независимый вариант |
| **Inherit in "…"** | дочерний файл, наследует родителя, **новый GUID** | новый | **основной способ создания префабов/конфигов** |
| **Replacement** | подмена (модели/текстуры/звуки/анимации): совпадающий **GUID** | тот же | подменить модель/текстуру, не трогая префабы |

Полезные действия: `Navigate to Original / Override / Ancestor`, `Copy Resource GUID(s)`.

> **Наследование префабов доступно только в Resource Browser, привязанном к World Editor.**

**Правило выбора:** сначала пробуем **Override** (если правим ваниль) или **Inherit** (если делаем своё от существующей базы). **Duplicate** — только когда осознанно нужен независимый клон. Полная замена `.et/.conf/.emat/.layout` невозможна — движок всё равно переведёт их в override.

### 2.1 Загрузка аддонов и «рабочий аддон»
- Рабочий аддон = **последний** в списке `-addons addon1, addon2, NewAddon` (NewAddon — текущий).
- Действия `Override in "X"` / `Duplicate in "X"` / `Inherit in "X"` создают файлы **в рабочем аддоне**, сохраняя структуру папок.
- При цепочке нескольких override побеждает последний смонтированный.

---

## 3. Проект и структура

- Проект = `.gproj` (настройки, платформы, зависимости). Mod Project Setup → создание аддона в Workbench.
- Структура аддона (рекомендуемая, чтобы работали автоплагины и навигация):
```
Prefabs/...        # .et
Scripts/Game/...   # .c (только Game-модуль виден редактору)
Assets/...         # .xob/.txo + Data/*.emat/*.edds
UI/...             # .layout/.imageset/.styles
Language/...       # .st (локализация)
worlds/...         # .ent/.layer
```
- **Именование**: сущности — `TAG_<Name>Entity` / `TAG_<Name>EntityClass`; слоты меша — `slot_*`; снапы — `snap_*`; кости — `w_*`; текстуры — по суффиксам (`_BCR`, `_NMO`, `_MCR`, `_UI`, `_MASK`).
- **Локализация**: все UI-имена (`Name`, `Description`, `UIInfo`) — ключами `#AR-...`; см. `Mod Localisation`.

---

## 4. Ресурсы: регистрация и корректность

1. Каждый ассет регистрируется через `.meta`; **GUID уникален** в общей загрузке (аддон + ваниль + другие моды).
2. После создания/правки ассета — **Reimport** (Resource Manager) и/или перезапуск Workbench; БД ресурсов `.rdb` обновляется.
3. Ссылка на ассет в тексте — `{GUID}Путь/Файл.ext`. GUID и путь должны совпадать с `.meta` (иначе `Wrong GUID for resource … in property "..."`).
4. **В скриптах всегда держим ссылку на родительский `Resource`**, иначе движок выгрузит ресурс (см. `Resource Usage`).
5. Правки в текстовом редакторе — только для того, что **нельзя задать в Workbench** (например `Refs` в `.emat`), и осторожно: Workbench-файлы легко испортить.

---

## 5. Префабы: наследование (ядро гайда)

### 5.1 Создание
| Способ | Что получаем |
|---|---|
| **Create tab** (GenericEntity и пр.) + drag&drop в вьюпорт | «с нуля», базовая сущность |
| drag&drop существующего `.et` из Resource Browser | **наследованный** префаб (инстанс) |
| drag&drop модели `.xob` | `GenericEntity` с `MeshObject` |
| **Inherit in "…"** (ПКМ по `.et`) | новый дочерний `.et` c новым GUID |
| **Duplicate in "…"** | независимая копия |
| «Настроить в сцене → перетащить корень в Resource Browser → задать имя» | сохранение инстанса как нового префаба (тоже наследование) |

**Правило:** база берётся максимально «глубокая» из подходящих (например для оптики — `WeaponOptic_Base.et`, для оружия — `Rifle_Base.et`), чтобы наследовать готовые компоненты, а не собирать их руками.

### 5.2 Редактирование унаследованного
- **Inheritance tree** в Object Properties: переключись с `Entity instance` на нужный родительский префаб → правишь сам префаб (влияет на всех).
- **Apply to prefab** — перенести изменения из инстанса в выбранный префаб (удобно: сначала эксперимент, потом apply).
- **Apply value to prefab** (ПКМ по свойству) — перенести только одно значение.
- **Prefab Edit Mode** (открыть `.et` через Resource Manager → Edit prefab) — правка в отдельном мире; сохранять `Ctrl+S` (`Save prefab`).
- Жирный шрифт у свойства = **переопределено**; `Restore to prefab value` — вернуть к значению префаба.
- ⚠ Правки префабов из обычного World Editor сохраняются на диск **только после сохранения мира** (или `Save world with options`, `Ctrl+Shift+S`).

### 5.3 Сущности и компоненты внутри префаба
- **Добавить сущность в префаб**: зажать **Alt** и перетащить сущность в иерархию инстанса префаба (дети добавляются вместе). Удалить: ПКМ → `Delete from prefab`.
- **Добавить компонент**: `Add component` (пустой) или drag&drop `.ct` (component prefab — наследование).
- **Добавить дочерний компонент**: ПКМ по компоненту → `Add child component` (например `SCR_CollimatorControllerComponent` внутри `SCR_CollimatorSightsComponent`, `MuzzleComponent` внутри `WeaponComponent`).
- **Сменить класс**: ПКМ → `Change class` (только совместимые классы).
- **Удалить компонент**: можно только в том префабе, **где он объявлен** (выбрать его в inheritance tree). **Унаследованный компонент удалить нельзя** — даже `Enabled 0` не удаляет его (остаётся память и логика). Отсюда правило выбора базы.
- **Unprefab**: `Break prefab instance` — отвязать инстанс от префаба (для отладки, не для продакшена).
- Идентификация: колонка `Prefab` в Hierarchy; `Select prefab instance root/members`, `Show prefab in resource manager`.

### 5.4 ⚠ Правило ID компонентов (главное правило этого гайда)

В `.et` компонент пишется как `ComponentClass "{GUID}" { ... }`, где `{GUID}` — **ID экземпляра внутри префаба** (не GUID класса!).

- **Тот же ID, что унаследован** → **переопределение** (правильно).
- **Новый ID** → **второй экземпляр** (дубль; почти всегда ошибка).

Примеры:
```
# ПРАВИЛЬНО: заменяем тип унаследованного BaseSightsComponent, сохраняя его ID
SCR_2DPIPSightsComponent "{5D0CC83435B55855}" { ... }   # ID взят у BaseSightsComponent из WeaponSight_Base

# ПРАВИЛЬНО: переопределение унаследованного ActionsManagerComponent
ActionsManagerComponent "{5284E0EFF569AD07}" { ... }

# ОШИБКА: новый ID = второй ActionsManagerComponent на префабе
ActionsManagerComponent "{774A8675EBC31567}" { ... }
```
**Перед добавлением компонента** — открой Workbench, посмотри список компонентов (включая унаследованные) и **переопределяй существующий ID**, а не создавай новый.

### 5.5 Когда база «не подходит» (нельзя удалить компонент)
Пример от BI (коллиматор): `WeaponOptic_Base.et` содержит `SCR_2DPIPSightsComponent`, который коллиматору не нужен, а удалить унаследованный компонент нельзя. BI предлагает ровно два корректных пути:
1. **Наследоваться от `Attachment_Base.et`** и вручную добавить нужные компоненты;
2. **Duplicate в свой аддон `WeaponOptic_Base.et`** и удалить из него лишний компонент (в большинстве случаев проще).

> Это и есть «правильный костыль» по BI: не плодить лишние компоненты на инстансе, а собрать свой базовый префаб.

### 5.6 Prefab Data
Общие для всех инстансов переменные держим в `...Class`-классе (Prefab Data) и читаем через `GetPrefabData()` (для компонентов — `GetComponentData()`). Оправдано при 100+ инстансах и редком обращении.

---

## 6. Каркас: обязательные компоненты и слоты

| Компонент | Назначение | Заметки |
|---|---|---|
| `MeshObject` | модель | `Object` = путь к `.xob` |
| `RigidBody` | физика/интеракции | требует коллайдер в меше; у **оружия `Layer Preset` пустой**; у предметов — `ItemFireView` |
| `Hierarchy` | иерархия | **обязателен для `RplComponent`** |
| `RplComponent` | сетевая репликация | нужен для действий/синхронизации |
| `SignalsManagerComponent` | сигналы | по необходимости |
| `ActionsManagerComponent` | пользовательские действия | ≠ `ActionManager` (тот про input!) |
| `SCR_WeaponAttachmentsStorageComponent` | инвентарь оружия | атрибуты предмета |
| `WeaponComponent`/`MuzzleComponent` | оружие | см. §8.1 |
| слоты | привязки | см. ниже |

**Классы слотов (наследование):**
```
PointInfo                          # Pivot ID (из меша), Offset, Angles
└ EntitySlotInfo                   # + Child Pivot ID, Enabled, Prefab,
                                   #   Inherit Parent Skeleton, Disable Physics Interaction,
                                   #   Activate/Deactivate Physics On Detaching/Attaching
  └ InventoryStorageSlot           # + Name (человекочитаемое)
    └ EquipmentStorageSlot         # + Allowed Item Types, Affected By Occluders
    └ LoadoutSlotInfo              # Area (HeadCover/FaceCover/Jacket/Vest/…)
    └ RegisteringComponentSlotInfo # Register Actions/Damage/Controllers/Weapons/Compartments/Lights
SoundPointInfo / DecalSlotInfo / EmissiveGlassSlot / EmissiveLightSurfaceSlot
```
**UIInfo** обязателен для действий; есть специализации `WeaponUIInfo`, `MuzzleUIInfo`, `MagazineUIInfo`, `GrenadeUIInfo`.

**Правила для интеракций:** сущности нужен `MeshObject` + `RigidBody` **с галочкой `Model Geometry`**, и `RplComponent`. Коллайдеры — с правильным Layer Preset (см. §7.2).

---

## 7. Ассеты

### 7.1 Модель
- Источник — `.fbx`/`.txo`; импорт `FBX Import`; инструменты `Enfusion Blender Tools` (`Objects Tools`, `Model Quality Assurance`, `Batch FBX Export`, `P3D Conversion`, `MLOD Baking`, `Material Library/Preview`).
- **В импорте включить `Export Scene Hierarchy`**, если используете empty/snap-точки — иначе точки не импортируются.
- `Level Of Detail` и `Model Performance` — обязательны для продакшена.
- Ориентация, `slot_*`-точки на оружии, `snap_*`-точки на аттачах.

### 7.2 Коллайдеры и слои
- Коллайдеры: `UCX_`/`UBX_` (выпуклый), `UTM_` (тримеш), `USP_`/`UCS_`/`UCL_`.
- Игровые материалы: `weapon_metal/plastic/wood.gamemat` и т.п.
- **Layer Preset** (свойство `usage` в FBX): оружие — `Weapon` (CharNoCollide); стрельба/пули — `FireGeometry`/`FireGeo`; предметы — `ItemFireView` (CharNoCollide+FireGeometry+ViewGeometry); пропы — `Prop`/`PropFireView`.
- Аттачам нужны **два** пресета: `Weapon` + `FireGeo` — иначе «нет действий в игре» (частая ошибка).
- Полный список слоёв и пресетов — `Collision Layer`.

### 7.3 Текстуры
- Суффиксы: `_BCR` (albedo/roughness), `_NMO` (normal/metal/AO), `_MCR` (спец. albedo/roughness), `_MASK` (каналы, цветовое пространство вручную), **`_UI`** для UI/сеток.
- Сетки: 1024×1024, прозрачный фон чёрный в альфе, `Conversion Quality = 100`, `Generate Mips` **off** (либо конфиг `TextureReticle.conf` в `.meta`).
- Инструменты: `Resource Manager: Texture Editor`, `Batch Texture Processor`.

### 7.4 Материалы
- `Resource Manager: Material Editor`; базовые классы `PBRBasic`, `MatPBRBasic`, `PBRBasicGlass`, `HDREffect`, `MatCommon`.
- **Материалы можно наследовать** (`.emat` — «Can be inherited from»).
- Тонкая настройка, недоступная в Workbench (например `Refs` на скрипт-переменные), делается **в текстовом редакторе**, и помни про `Refs`/перезапуск (см. §8.4).

---

## 8. Рецепты: «от какой базы + что переопределить»

### 8.1 Оружие
- База: **`Prefabs/Weapons/Core/Rifle_Base.et`** (или `Weapon_Base.et`), для своей модели — Inherit.
- Переопределяем: `MeshObject`, `RigidBody` (Layer Preset **пустой**, `Mass`, `ModelGeometry 1`), `SCR_WeaponAttachmentsStorageComponent` (Name/Description, вес, размеры, анимации), `WeaponSoundComponent`, `SCR_WeaponStatsManagerComponent`, `WeaponComponent`:
  - `MuzzleComponent` (FireModes, `MagazineWell`, `MagazineTemplate`, `MagazinePosition` = `slot_magazine` + `snap_weapon`, dispersion, aim modifiers, `CaseEjectingEffect`/`SCR_MuzzleEffectComponent` дочерними);
  - `AttachmentSlotComponent` (дочерний к `WeaponComponent`) для оптики/фонарей, `MuzzleComponent` — для дульных;
  - `SightsComponent` (`eye`, `Sights Ranges`, `Sights FOV Info`, `Sights Point Front/Rear`, `ADS Time`, `Sound Int`) — **дочерний к `MuzzleComponent`**;
  - `WeaponAnimationComponent` (Anim Graph/Instance, Injection).
- Точки меша: `slot_optics`, `slot_barrel_muzzle`, `slot_magazine`, `slot_underbarrel`, `slot_bayonet`, `eye`, `snap_hand_left/right`, кости `w_*`.
- Обстruction: `WeaponComponent` использует **только bounding box из `MeshObject`** — учитывайте модульные приклады/стволы.
- Zeroing: `Process zeroing data` / `Toggle sight point diag` (ПКМ по `SightsComponent`), см. §8.3.

### 8.2 Магазин
- База: `Prefabs/Weapons/Magazines/..._Base.et`.
- Задаём `MagazineWell`-совместимость, `MagazineTemplate` ссылкой в оружии, патрон/трейсер, локализацию.

### 8.3 Оптика (PIP)
> Детальный разбор каждого поля `SCR_2DPIPSightsComponent` (все таблицы BaseSights/2D/PiPSights) — в приложении `docs/OPTIC_ATTACHMENT_GUIDE_RU.md`.

- База: **`WeaponOptic_Base.et`**, стаб + `_base` (Inherit).
- `MeshObject` (модель оптики), `RigidBody ModelGeometry 1`, `InventoryItemComponent` (локализованные Name/Description, `SizeSetupStrategy Manual` + `ItemDimensions/ItemVolume`, `RestingUP Right`, `m_Size SLOT_1x1`, `ItemAnimationAttributes` пусто), `CharacterModifierAttributes` (`ADSSpeedLimit ~1.5`), `WeaponAttachmentAttributes → AttachmentType` (иерархия RIS: `AttachmentOpticsRIS1913` ≥250 мм → `…Medium` → `…Short` → `…VeryShort` ≤80 мм).
- Компонент `SCR_2DPIPSightsComponent` (переопределяем унаследованный `BaseSightsComponent` **по его ID**):
  - **BaseSights**: `SightsPosition` (`eye`), `SightsPointRear` (`optic_rear`), `SightsPointFront` (`optic_front`), `SightsRanges`, `SightsFOVInfo` (`SCR_SightsZoomFOVInfo`: `m_fBaseZoom` = мин. кратность, `m_fZoomMax` = макс.), `SightsPriority`.
  - **2D (`Sights/2DSights`)**: `m_sReticleTexture`/`m_sReticleGlowTexture`, `m_fObjectiveFov` (градусы), `m_fMagnification` **= `m_fBaseZoom`**, `m_fObjectiveScale` (1…0.5), `m_fVignetteScale`, `m_fReticleBaseZoom` (0 = передняя фокальная плоскость, = Magnification = задняя), `m_fReticleAngularSize` (град.), `m_fReticlePortion` = px-метка/ширина текстуры, `m_eZeroingType`, `m_vCameraOffset/Angles`, поля подсветки/инерции/DOF.
  - **PIPSights**: **`m_rScopeHDRMatrial`** (HDR-материал, в его `Reticle Map` лежит сетка — см. §8.4!), `m_sPIPLayoutResource` (PIP = `UI/layouts/Sights/PictureInPictureSightsLayout.layout`), `m_fScopeRadius` (главный параметр совмещения PIP с 2D), `m_fReticlePIPScale`, `m_fCenterDistance`, `m_fCenterOffsetX/Y`, `m_fBasicParallax`/`m_fMaxParallax`, `m_fDistanceMoveNear/Far`, `m_fObjectivePIPEdgeMin/Max`, `m_fVignetteParallaxScale`, `m_fNearPlane/FarPlane`, `m_fResolutionScale`, `m_fADSActivationPercentagePIP`/`…Deactivation…`, `m_vMainCameraOffsetUnfocused`, `m_sUnderwater/RainPPMaterial`.
- Пивоты меша: `eye`, `optic_front`, `optic_rear`, `snap_weapon`, `eye_ironsight`, `ironsight_front/rear`, `collimator_TL/BR`.
- **2D-сетка** берётся из `m_sReticleTexture`, **PIP-сетка — из HDR-материала** (`Reticle Map`). Если материал не задан — движок подставит общий и в прицеле будет **чужая сетка**.
- Калибровка: `Diag Menu` → `GameCode → Weapons` (`Toggle 2D optics`, `Show optics diag`, `Show PIP settings diag`, `Show sights points`, отключить aim modifiers); порядок: точки → 2D → сетка → PIP.
- Zeroing на оружии: `Sights Ranges` (X = анимация 0…1, Y = метры), `Zeroing Generator` → ПКМ `Process zeroing data`.

### 8.4 Коллиматор (второй режим прицеливания)
- База: чистая — **`Attachment_Base.et` + нужные компоненты**, либо **duplicate `WeaponOptic_Base.et` в свой аддон и удалить `SCR_2DPIPSightsComponent`** (нельзя удалить унаследованный компонент!).
- Компоненты: **`SCR_CollimatorSightsComponent`** + **дочерний `SCR_CollimatorControllerComponent`**.
- Точки: `collimator_TL` (верх-лево) и `collimator_BR` (низ-право) — **обязательны**; **`CollimatorCenter` — оставить пустым**; `SightsPointFront/Rear` опциональны (направление берётся из плоскости).
- `Collimator Aspect Ratio` = true (сетки 1:1).
- `Reticle Default Angular Size` (град.; HWS Holo ≈ 68 MOA ≈ 1,13°) и `Reticle Default Texture Portion` (px-сетка/ширина текстуры). **Если любое из них = 0 — сетка берётся «как есть»** без угловой подгонки.
- `Default Reticle Index` + `Reticle Infos` (`BaseCollimatorReticleInfo { Reticle Index, override, angularSize, portion }`), `Reticle Colors` (пусто = цвет из материала), `ADS Activation/Deactivation %` (0,5 = точка «вплывает»), `Daylight/Night brightness`.
- **Материал проекционной плоскости** (`PBRBasic`): `Opacity Map` = серая текстура сетки (чёрное = прозрачно), `ClampU/ClampV` on, `Sort = Translucent`, снять `Cast/Receive Shadow`, `Blend Mode = AlphaBlend`, `AlphaTest/AlphaMul`, массив `TCModFuncs` с `TCModShift` + `TCModScale`.
- **Ручные правки `.emat` (в текстовом редакторе):**
```
TCModFuncs {
 TCModShift { ShiftU 0 ShiftV 0 Refs { "ShiftU" "SCR_CollimatorControllerComponent.m_fUCoord" "ShiftV" "SCR_CollimatorControllerComponent.m_fVCoord" } }
 TCModScale { ScaleU 1 ScaleV 1 CenterU 0.5 CenterV 0.5 Refs { "ScaleU" "SCR_CollimatorControllerComponent.m_fUScale" "ScaleV" "SCR_CollimatorControllerComponent.m_fVScale" } }
}
Refs {
 "Color" "SCR_CollimatorControllerComponent.m_vColor"
 "Emissive" "SCR_CollimatorControllerComponent.m_vEmissive"
 "EmissiveLV" "SCR_CollimatorControllerComponent.m_fEmissiveLV"
 "OpacityMap" "SCR_CollimatorControllerComponent.m_ReticleMap"
}
```
⚠ `Refs` внутри `TCModShift` **не сохраняются** при сохранении через Workbench (добавлять заново); после правок — **полный перезапуск Workbench**.
- **Работает только в игре, в World Editor — нет**; проверка: параллакс на freelook + естественное качание.
- **Два режима** в одном префабе = `SCR_2DPIPSightsComponent` + `SCR_CollimatorSightsComponent`; переключение даёт HUD-действие (`SCR_WeaponChangeSwitchOpticsCondition`: «больше 1 прицела»). `SightsPriority` у оптики выше.

### 8.5 Глушитель
- База из `Prefabs/Weapons/Attachments/Muzzle/...` (`WeaponPart_Base`), компонент дульный слот оружия `MuzzleComponent → AttachmentSlotComponent`, тип `AttachmentMuzzle*`. Детали — `Weapon Suppressor Creation`.

### 8.6 Аттач, меняющий статы оружия
- Механизм `SCR_WeaponStatsManagerComponent` (на оружии) + атрибуты аттача в `CustomAttributes` его `InventoryItemComponent`. Готовые классы: `SCR_WeaponAttachmentSuppressorAttributes`, `SCR_WeaponAttachmentBayonetAttributes`; свои — наследники. Детали — `Weapon Stats-Modifing Attachments`.

### 8.7 Проп/предмет
- База: `Attachment_Base.et` / `GenericEntity` + `InventoryItemComponent`; `RigidBody` с `ItemFireView`; `SCR_ItemAttributeCollection` (Name, вес, размер, `Common Item Type`, `Size`/`Slot Type`). Детали — `Prop Creation`.

### 8.8 Снаряжение персонажа
- Базы `Character Gear Creation` (`/Headgear`, `/Vest`): слоты `LoadoutSlotInfo` (Area), `Affected By Occluders`, `Allowed Item Types`.

### 8.9 Свои классы (сущность/компонент/конфиг)
- **Сущность**: `TAG_<Name>Entity` + `TAG_<Name>EntityClass` с `[EntityEditorProps(category:…, style:…, sizeMin/Max…)]`; файл **обязательно в `Scripts/Game`**, иначе не появится в Create.
- **Компонент**: класс + `...Class` (Prefab Data) — см. `Create a Component`.
- **Конфиг-класс**: `Create a Config Class`.
- После скриптов — **Compile & Reload Scripts** (`Shift+F7`).

---

## 9. Действия и интеракции
1. На сущности: `ActionsManagerComponent` (не дублировать! переопределять по ID), обязательно `RplComponent`, `MeshObject` + `RigidBody` с `Model Geometry`.
2. `Action Contexts`: уникальный **Context Name** + **Position (PointInfo)** + **UIInfo** (обязательны).
3. `Additional Actions` (или слот компонента): у действия `Parent Context List` = имя контекста; `UIInfo`, `Visibility Range`, `Duration`.
4. Свои действия — наследник `ScriptedUserAction` (`PerformAction`, `CanBeShownScript`, `CanBePerformedScript`, `HasLocalEffectOnlyScript`), папка `Scripts/Game/generated/UserAction/...`.
5. Для оружия с оптикой — контекст `optic` с `PointInfo` на `slot_optics`, `Radius ~0.1`.

---

## 10. Арсенал, каталог, фракции
- В **Entity Catalog** фракции: prefab → `Item Type` / `Item Mode`:
  - оружие — `RIFLE` / `WEAPON`; магазины — `RIFLE` / `AMMUNITION`; **аттачи — `WEAPON_ATTACHMENT` / `ATTACHMENT`**;
  - `Supply Cost` — по ваниле; для стоек — `Arsenal Display Data`.
- Новые фракции — `Faction Creation`; свои арсеналы — `SCR_ArsenalComponent` + `SCR_ArsenalItemListConfig`.
- После правок — Reload Game Scripts / перезапуск Workbench.

---

## 11. Публикация
- `Mod Publishing Process`, `Workshop`, `Asset Browser Mod Integration` (видимость в Game Master), `Entity Catalog`.
- Перед публикацией: проверить LOD/Model Performance, `resourceDatabase.rdb`, локализацию, отсутствие «висячих» ссылок.

---

## 12. «Без костылей» — чек-лист архитектуры

- [ ] Каждый ассет имеет `.meta` с **уникальным** GUID.
- [ ] Новый префаб создан **Inherit**, а не Duplicate (duplicate — только осознанно).
- [ ] База выбрана так, чтобы **не пришлось удалять** унаследованные компоненты.
- [ ] Все правки унаследованного — **переопределением по существующему ID**, новых ID у уже существующих компонентов нет.
- [ ] Никаких `Enabled 0` «чтобы отключить унаследованное поведение» (если компонент не нужен — берём другую базу).
- [ ] Логика — в компонентах/атрибутах, а не в скриптах-заплатках.
- [ ] Локализация через ключи, а не хардкод-строки.
- [ ] Правильные Layer Preset'ы и `Model Geometry`.
- [ ] Нет правок бинарных форматов вне Workbench (кроме документированных случаев вроде `Refs` в `.emat`).
- [ ] Все изменения сохранены (`Ctrl+S`, `Apply to prefab`, `Save prefab`).

---

## 13. Проверка и отладка

| Инструмент | Что даёт |
|---|---|
| `Compile & Reload Scripts` (`Shift+F7`) | компиляция скриптов/обновление сущностей |
| `Diag Menu` (`Win + Alt`; `→` войти, `Backspace` выйти, `←/→` менять, `Shift+↑/↓` быстрее, `Home` корень, `Insert/Del` сброс, `F1/F2` save/load) | `GameCode → Weapons`: `Toggle 2D optics`, `Show optics diag`, `Show PIP settings diag`, `Show sights points`, отключение aim modifiers |
| ПКМ по `SightsComponent`/`WeaponComponent` | `Process zeroing data`, `Toggle sight point diag` |
| Логи (`error.log`, `console.log`) | `Wrong GUID for resource`, `resource not registered`, `Unknown class`, `SCRIPT (E)`, `Division by zero` |
| `-diagMenu file.txt`, `-wbModule=… -run -load "…"`, `-validate`, `-clearSettings` | стартовые параметры Workbench |
| `Development Executables` | Diag-сборки (`*SteamDiag.exe`) для debug-функций |

---

## 14. Troubleshooting

| Симптом | Причина | Решение |
|---|---|---|
| `resource not registered … Setting null GUID` | нет `.meta` | создать `.meta` с GUID |
| `Wrong GUID for resource "@{…}" in property "Prefab"` | ссылка на несуществующий GUID | восстановить файл/поправить ссылку |
| Два одинаковых компонента | новый ID вместо переопределения | переопределять по ID унаследованного |
| Изменения «пропадают» | правки префаба сохраняются только с миром / Workbench перезаписал файл из своей копии | `Apply to prefab` / Prefab Edit Mode + `Ctrl+S`; не держать префаб открытым при внешних правках |
| Нельзя удалить компонент | компонент унаследован | выбрать другую базу или duplicate-in-addon |
| Нет действий по предмету | неверный Layer Preset коллайдера | `Weapon` + `FireGeo` |
| Нет интеракций/подбора | `RigidBody` без `Model Geometry` | включить |
| Нет контекста на слоте | нет `UserActionContext` (+ `UIInfo`) | добавить контекст, `Radius ~0.1` |
| В PIP нет сетки | HDR-материал без `Reticle Map` | задать материал с картой сетки |
| В прицеле чужая сетка | `m_rScopeHDRMatrial` не задан | задать свой HDR-материал |
| PIP ломается | layout `Optic_Default` | `PictureInPictureSightsLayout` |
| `Division by zero` в `SCR_2DOpticsDisplay::SetReticleOffset` | `m_fReticlePortion`/текстура не заданы | задать `m_fReticlePortion`, `m_fReticleAngularSize`, текстуры |
| Коллиматор «не работает» | проверка в World Editor | работает **только в игре**; проверить UV плоскости, `collimator_TL/BR`, `Refs` в `.emat` |
| Сетка «плывёт» | reticle movement в HDR-материале | дубль материала, отключить reticle movement |
| Не видно в Create | скрипт не в `Scripts/Game` | перенести туда |

---

## 15. Справочник

**Базовые ресурсы (ванильные)**
| Ресурс | GUID |
|---|---|
| `Prefabs/Weapons/Core/Weapon_Base.et` | `E1F14DB52DBFBC57` |
| `Prefabs/Weapons/Core/Rifle_Base.et` | `911D6C8DC7BA2D63` |
| `Prefabs/Weapons/Core/Attachment_Base.et` | `2E0E3D7D1DD0FF8F` |
| `Prefabs/Weapons/Core/WeaponSight_Base.et` | `3E15C1C882DBB587` |
| `Prefabs/Weapons/Core/WeaponPart_Base.et` | `0A9CD090EE3440E7` |
| `Prefabs/Weapons/Attachments/Optics/WeaponOptic_Base.et` | `966B4E5523D2F166` |

**PIP-layout'ы:** `{EF091399D840192D}UI/layouts/Sights/PictureInPictureSightsLayout.layout`, `{4CE66FA8219D33D7}UI/layouts/Sights/Optic_Default.layout`.

**HDR-материалы скопов (в их `Reticle Map` — сетка):** `Optic_4x20_HDR` `{09B57B6EA6B5EE41}` · `Optic_PSO1_HDR` `{958809B0DE47E9BF}` · `Optic_ARTII_HDR` `{63FF28F3F6BB1727}` · `Optic_1P29_HDR` `{3BD4127D635A335E}` · `Optic_PGO7V_HDR` `{E8738368ECB4F8FE}` · `Optic_UK59_4x8_HDR` `{F6F990CCEDF61E3A}` · общий `SightsPIPMaterial` `{1C8A9AC4A0AE4921}`.

**PIP/стекло:** `Optic_PSO1_PIPMaterial` `{41E4B66721D5F07B}` · `Optic_4x20_PIPmaterial` `{F3CC2BBE8FE67602}` · `Optic_ARTII_Lensglass` `{39C2A3A521FE9A1B}` · `Optic_4x20_Lensglass` `{3C29D4ADAC94D19B}`.

**Ссылки:** вики `community.bistudio.com/wiki/Category:Arma_Reforger/Modding` (234 страницы, локальная копия — `%TEMP%\opencode\wiki\`); Samples `github.com/BohemiaInteractive/Arma-Reforger-Samples` (`SampleMod_NewWeapon`, `SampleMod_ModdedWeapon`).

---

## 16. Кейс: HK G36 Carry Handle Optic (практические грабли)

1. **Пропали префабы оптики**, у оптики **не было `.meta`** → `resource not registered` + `Wrong GUID`. Восстановление + создание `.meta` под GUID из ссылки.
2. **Битый GUID родителя** пикатинни → правильный `WeaponPart_Base` = `{0A9CD090EE3440E7}`.
3. **Двухрежимность** через два компонента (оптика + коллиматор) на реальных пивотах меша.
4. **`Division by zero`** — пустые `m_fReticlePortion`/текстура.
5. **«Сетка ПСО»** — не задан `m_rScopeHDRMatrial` → движок взял общий материал.
6. **PIP ломался** на `Optic_Default.layout` → `PictureInPictureSightsLayout`.
7. **Дубль `ActionsManagerComponent`** — добавлен с новым ID, хотя наследуется (правило §5.4).
8. **Workbench перезаписывал префаб** при сохранении — правки из файла «терялись».
9. **Коллиматор** — не по доке: `CollimatorCenter` не должен заполняться; сетка живёт в материале плоскости через `Refs`; работает только в игре.
